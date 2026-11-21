"""CLI conveniences: build evidence records and summarize a case.

Nothing here authenticates people, roles or approvals. A command run through
``build_evidence_record`` is recorded as caller-triggered RUNTIME evidence.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shlex
import subprocess
from typing import Any

from .case import GATE_REQUIREMENTS, case_revision, validate_case
from .evidence import CLASSIFICATIONS, make_evidence

RESERVED_KEYS = {
    "id", "path", "classification", "description", "sha256",
    "command", "exit_code", "stdout", "stderr", "satisfies",
}
STREAM_LIMIT = 20000


def _inside(path: Path, root: Path) -> Path:
    resolved_root = Path(root).resolve()
    candidate = Path(path)
    resolved = (candidate if candidate.is_absolute() else resolved_root / candidate).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"path {path} escapes workspace root {resolved_root}") from exc
    return resolved


def parse_meta(pairs: list[str] | None) -> dict[str, Any]:
    """Parse KEY=VALUE pairs; VALUE is decoded as JSON when valid, else kept as text."""
    meta: dict[str, Any] = {}
    for pair in pairs or []:
        key, sep, raw = pair.partition("=")
        key = key.strip()
        if not sep or not key:
            raise ValueError(f"--meta expects KEY=VALUE, got {pair!r}")
        if key in RESERVED_KEYS:
            raise ValueError(f"--meta key {key!r} is reserved; use the dedicated option")
        try:
            meta[key] = json.loads(raw)
        except json.JSONDecodeError:
            meta[key] = raw
    return meta


def _satisfies(gate: str | None, extra: str | None) -> list[str]:
    values: set[str] = set()
    if gate:
        if gate not in GATE_REQUIREMENTS:
            raise ValueError(f"unknown gate {gate!r}; expected one of {sorted(GATE_REQUIREMENTS)}")
        values |= GATE_REQUIREMENTS[gate]
    if extra:
        values |= {item.strip() for item in extra.split(",") if item.strip()}
    return sorted(values)


def _display_command(command: list[str]) -> str:
    return subprocess.list2cmdline(command) if os.name == "nt" else shlex.join(command)


def _cap(text: str) -> str:
    return text if len(text) <= STREAM_LIMIT else text[:STREAM_LIMIT] + "\n...[truncated]"


def git_diff_modified_files(root: Path) -> list[str]:
    """Return paths reported by ``git diff --name-only`` inside ``root``."""
    resolved_root = Path(root).resolve()
    try:
        proc = subprocess.run(
            ["git", "diff", "--name-only"],
            cwd=resolved_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError(f"git diff could not be executed: {exc}") from exc
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip() or f"exit_code {proc.returncode}"
        raise ValueError(f"git diff --name-only failed: {detail}")
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def build_evidence_record(
    root: Path,
    *,
    description: str,
    file: Path | None = None,
    classification: str | None = None,
    evidence_id: str | None = None,
    gate: str | None = None,
    satisfies: str | None = None,
    meta: list[str] | None = None,
    command: list[str] | None = None,
    log: Path | None = None,
    timeout: int = 300,
    from_git_diff: bool = False,
) -> dict[str, Any]:
    """Return one evidence object with SHA-256, optionally from a command run in ``root``.

    With ``command`` the process is executed without a shell, its output is saved
    to ``log`` and the record is RUNTIME with the real command, exit code and
    streams, whatever the exit code. A command that cannot finish (timeout, not
    found) raises ValueError instead of fabricating an exit code.
    """
    root = Path(root).resolve()
    if not isinstance(description, str) or not description.strip():
        raise ValueError("description must be non-empty")
    metadata = parse_meta(meta)
    criteria = _satisfies(gate, satisfies)
    if criteria:
        metadata["satisfies"] = criteria
    if from_git_diff:
        metadata["modified_files"] = git_diff_modified_files(root)

    if command:
        if classification not in (None, "RUNTIME"):
            raise ValueError("a recorded command is always RUNTIME; omit --classification or use RUNTIME")
        if log is None:
            raise ValueError("a log path is required to record a command")
        log_path = _inside(log, root)
        try:
            result = subprocess.run(
                command, cwd=root, capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=timeout, check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise ValueError(f"command timed out after {timeout}s; no evidence recorded") from exc
        except OSError as exc:
            raise ValueError(f"command could not be started: {exc}") from exc
        shown = _display_command(command)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(
            f"$ {shown}\n--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}\n"
            f"exit_code: {result.returncode}\n",
            encoding="utf-8",
        )
        metadata.update(command=shown, exit_code=result.returncode,
                        stdout=_cap(result.stdout), stderr=_cap(result.stderr))
        return make_evidence(log_path, root, classification="RUNTIME", description=description,
                             evidence_id=evidence_id, **metadata)

    if file is None:
        raise ValueError("provide --file or a command after '--'")
    if classification is None or classification not in CLASSIFICATIONS:
        raise ValueError(f"--classification is required and must be one of {sorted(CLASSIFICATIONS)}")
    target = _inside(file, root)
    if not target.is_file():
        raise ValueError(f"evidence file does not exist: {file}")
    return make_evidence(target, root, classification=classification, description=description,
                         evidence_id=evidence_id, **metadata)


def merge_evidence(existing: Any, record: dict[str, Any], *, reset: bool = False) -> list[dict[str, Any]]:
    """Append ``record`` to an existing evidence array, refusing duplicate ids."""
    if reset or existing is None:
        return [record]
    if not isinstance(existing, list):
        raise ValueError("existing evidence file must contain a JSON array")
    if any(isinstance(item, dict) and item.get("id") == record["id"] for item in existing):
        raise ValueError(f"evidence id {record['id']!r} already exists in the output file; pass --id or --reset")
    return [*existing, record]


def next_log_name(output: Path, existing: Any, reset: bool) -> str:
    count = 1 if reset or not isinstance(existing, list) else len(existing) + 1
    return f"{output.stem}-run-{count}.log"


def summarize_case(case: dict[str, Any], routing: dict[str, Any], root: Path, raw: bytes) -> list[str]:
    """Human-readable status of a case with the next step and a command template."""
    phases = routing.get("phases", [])
    names = [phase.get("name") for phase in phases]
    current = case.get("current_phase")
    state = case.get("state")
    phase = next((item for item in phases if item.get("name") == current), {})
    ledger = case.get("ledger") if isinstance(case.get("ledger"), list) else []
    errors = validate_case(case, routing, Path(root))
    revision = case_revision(raw)

    lines = [
        f"Caso: {case.get('case_id')}  | classificação: {case.get('classification')}  | alto risco: {case.get('high_risk')}",
        f"Fase atual: {current} ({phase.get('id', '?')})  | Estado: {state}",
        f"Papel da fase: {phase.get('role', '?')}",
        f"Gate: {phase.get('gate', '?')}",
        f"Critérios exigidos no PASS (satisfies): {', '.join(sorted(GATE_REQUIREMENTS.get(phase.get('id'), []))) or '-'}",
    ]
    hints = []
    if phase.get("id") == "plano-de-acao":
        hints.append("evidência com approval_type=human_plan e approved_by (rótulo, não autenticado)")
    if phase.get("id") == "verificacao":
        hints.append("evidência RUNTIME com comando real e exit_code 0 (use record-evidence -- <comando>)")
    if case.get("high_risk") and phase.get("id") in {"verificacao", "conclusao"}:
        hints.append("parecer RUNTIME de Astra com astra_reason, related_evidence e coordinator_decision")
    lines.extend(f"Exigência extra: {hint}" for hint in hints)
    lines.append(f"Ledger: {len(ledger)} evento(s); " + ("íntegro" if not errors else f"{len(errors)} erro(s) de validação"))
    lines.extend(f"  ! {error}" for error in errors[:5])
    lines.append(f"Revisão atual: {revision}")

    base = "python -m masp_skill.cli transition --case <CASO> --actor masp-coordenador --evidence <EVIDENCIAS.json> " \
           f"--expected-revision {revision} --root <RAIZ>"
    index = names.index(current) if current in names else -1
    if errors:
        lines.append("Próximo passo: corrija os erros acima; transições são recusadas com ledger inválido.")
    elif state == "PENDING":
        lines.append(f"Próximo passo: iniciar a fase.\n  {base} --state IN_PROGRESS")
    elif state == "IN_PROGRESS":
        lines.append("Próximo passo: concluir com PASS (evidência cobrindo todos os critérios), ou FAIL / BLOCKED.\n"
                     f"  {base} --state PASS")
    elif state == "PASS" and 0 <= index + 1 < len(names):
        lines.append(f"Próximo passo: iniciar a fase seguinte.\n  {base} --state IN_PROGRESS --phase \"{names[index + 1]}\"")
    elif state == "PASS":
        lines.append("Próximo passo: nenhum — todas as fases em PASS (registro SIMULATED, sem autenticação).")
    elif state == "FAIL":
        returns = [name for name in phase.get("returns", []) if name in names and names.index(name) < index]
        if returns:
            lines.append("Próximo passo: retornar por aresta declarada: " + ", ".join(returns) +
                         f"\n  {base} --state IN_PROGRESS --phase \"{returns[0]}\"")
        else:
            lines.append("Próximo passo: esta fase não declara retorno anterior; registre BLOCKED ou NOT_RUN.")
    else:
        lines.append(f"Próximo passo: nenhum — {state} é terminal e a CLI não tem comando de resolução.")
    if ledger:
        lines.append("Últimos eventos:")
        for event in ledger[-5:]:
            if isinstance(event, dict):
                lines.append(f"  #{event.get('sequence')} {event.get('phase')}: {event.get('previous_state')} -> {event.get('new_state')}")
    return lines
