"""Command line interface for MASP routing and case ledger operations."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager

from .case import case_revision, create_case, transition_case, validate_case
from .routing import load_routing, validate_routing


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _within_root(path: Path, root: Path) -> Path:
    resolved_root = Path(root).resolve()
    candidate = Path(path)
    resolved_path = (candidate if candidate.is_absolute() else resolved_root / candidate).resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"path {path} escapes workspace root {resolved_root}") from exc
    return resolved_path


@contextmanager
def _case_lock(path: Path):
    """Serialize writers through a persistent sidecar lock on Windows and POSIX."""
    lock_path = path.resolve().with_name(path.name + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    stream = lock_path.open("a+b")
    locked = False
    try:
        if os.name == "nt":
            import msvcrt
            stream.seek(0, os.SEEK_END)
            if stream.tell() == 0:
                stream.write(b"\0")
                stream.flush()
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        locked = True
        yield
    finally:
        if locked and os.name == "nt":
            import msvcrt
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
        elif locked:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        stream.close()


def _write_json_atomic(path: Path, value) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def parse_codex_smoke_output(text: str) -> dict[str, str | None]:
    """Extract observed model and effort fields from Codex diagnostic output."""
    model_match = re.search(r"(?im)^\s*(?:model|model_id)\s*[:=]\s*([\w.-]+)\s*$", text)
    effort_match = re.search(r"(?im)^\s*(?:reasoning[ _]effort|effort)\s*[:=]\s*(low|medium|high)\s*$", text)
    return {
        "model": model_match.group(1) if model_match else None,
        "effort": effort_match.group(1) if effort_match else None,
    }


def validate_codex_smoke_report(report: dict) -> list[str]:
    """Reject runtime claims that are not backed by captured process evidence."""
    errors: list[str] = []
    if report.get("classification") == "RUNTIME":
        commands = report.get("commands")
        if not isinstance(commands, list) or not commands:
            return ["RUNTIME requires at least one recorded command"]
        for index, item in enumerate(commands):
            if not isinstance(item, dict):
                errors.append(f"command {index} is not an object")
                continue
            for key in ("command", "exit_code", "stdout", "stderr"):
                if key not in item or item[key] is None:
                    errors.append(f"command {index} is missing {key}")
    expected = report.get("expected_model")
    observed = report.get("observed_model")
    if expected and observed and expected != observed:
        errors.append(f"model mismatch: expected {expected}, observed {observed}")
    return errors


def run_codex_smoke(root: Path, output_dir: Path) -> dict:
    """Collect low-impact CLI evidence; never invokes agents or changes external state."""
    root = Path(root).resolve()
    output_dir = _within_root(Path(output_dir), root)
    output_dir.mkdir(parents=True, exist_ok=True)
    codex = shutil.which("codex")
    report = {
        "classification": "NOT_RUN",
        "version": None,
        "commands": [],
        "checks": [],
        "expected_model": None,
        "observed_model": None,
        "limitations": [],
    }
    if not codex:
        report["limitations"].append("Codex CLI executable was not found on PATH")
        report["checks"].append({"name": "CLI availability", "status": "BLOCKED"})
    else:
        for args, name in ((["--version"], "version"), (["--help"], "CLI help")):
            command = [codex, *args]
            try:
                result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=30, check=False)
                item = {"command": command, "exit_code": result.returncode,
                        "stdout": result.stdout, "stderr": result.stderr}
                report["commands"].append(item)
                report["checks"].append({"name": name, "status": "PASS" if result.returncode == 0 else "FAIL"})
                if name == "version":
                    report["version"] = (result.stdout or result.stderr).strip()
            except (OSError, subprocess.TimeoutExpired) as exc:
                report["checks"].append({"name": name, "status": "BLOCKED", "detail": str(exc)})
        report["classification"] = "RUNTIME" if report["commands"] else "NOT_RUN"
    config = root / ".codex" / "config.toml"
    report["checks"].append({"name": "local config file", "classification": "STATIC",
                             "status": "PASS" if config.is_file() else "FAIL"})
    report["checks"].append({"name": "local skill file", "classification": "STATIC",
                             "status": "PASS" if (root / "skills/masp/SKILL.md").is_file() else "FAIL"})
    # A real fan-out would incur model calls; it is intentionally not run by this low-impact collector.
    for role in ("masp-identificador", "masp-observador", "masp-analista", "masp-planejador",
                 "masp-executor", "masp-testador", "masp-padronizador", "masp-relator"):
        report["checks"].append({"name": f"delegation {role}", "classification": "RUNTIME",
                                 "status": "NOT_RUN",
                                 "reason": "would invoke a model; not included in the low-impact smoke"})
    report["checks"].append({"name": "local agent discovery", "classification": "RUNTIME",
                             "status": "NOT_RUN", "reason": "no non-interactive read-only discovery command was confirmed"})
    report["checks"].append({"name": "active model and effort", "classification": "RUNTIME",
                             "status": "NOT_RUN", "reason": "requires an agent invocation to observe"})
    report["limitations"].append("Local config/skill file checks are STATIC and do not prove Codex discovery")
    report["limitations"].append("Eight-role delegation, local agent discovery, and active model/effort were not invoked; no safe read-only path was confirmed")
    report["python"] = sys.version.split()[0]
    errors = validate_codex_smoke_report(report)
    if errors:
        raise ValueError("invalid smoke report: " + "; ".join(errors))
    (output_dir / "codex-smoke.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Codex smoke evidence", "", f"Classification: **{report['classification']}**", "",
             f"CLI version: `{report['version'] or 'unavailable'}`", "", "## Checks", ""]
    lines.extend(f"- {check['name']} ({check.get('classification', 'RUNTIME')}): **{check['status']}**"
                 + (f" — {check['reason']}" if check.get("reason") else "") for check in report["checks"])
    lines.extend(["", "## Limitations", "", *[f"- {item}" for item in report["limitations"]], ""])
    (output_dir / "codex-smoke.md").write_text("\n".join(lines), encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="masp-skill")
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate-routing", help="validate the routing matrix")
    validate.add_argument("--routing", type=Path, default=Path("docs/masp/masp-routing.toml"))
    validate.add_argument("--classification", choices=("STATIC",), default="STATIC")

    new_case = commands.add_parser("new-case", help="create a simulated case manifest")
    new_case.add_argument("--id", required=True)
    new_case.add_argument("--output", type=Path, required=True)
    new_case.add_argument("--routing", type=Path, default=Path("docs/masp/masp-routing.toml"))
    new_case.add_argument("--high-risk", action="store_true")
    new_case.add_argument("--root", type=Path, default=Path.cwd())

    transition = commands.add_parser("transition", help="append a simulated case transition")
    transition.add_argument("--case", type=Path, required=True)
    transition.add_argument("--state", required=True)
    transition.add_argument("--actor", required=True)
    transition.add_argument("--evidence", type=Path, required=True, help="JSON file containing an evidence array")
    transition.add_argument("--phase")
    transition.add_argument("--required-classification")
    transition.add_argument("--routing", type=Path, default=Path("docs/masp/masp-routing.toml"))
    transition.add_argument("--expected-revision", required=True, help="SHA-256 returned by case-revision")
    transition.add_argument("--root", type=Path, default=Path.cwd(), help="workspace root for evidence references")

    revision = commands.add_parser("case-revision", help="print the current manifest revision for compare-and-swap")
    revision.add_argument("--case", type=Path, required=True)

    validate_case_parser = commands.add_parser("validate-case", help="validate a case manifest and ledger")
    validate_case_parser.add_argument("--case", type=Path, required=True)
    validate_case_parser.add_argument("--routing", type=Path, default=Path("docs/masp/masp-routing.toml"))
    validate_case_parser.add_argument("--root", type=Path, default=Path.cwd())

    smoke = commands.add_parser("runtime-smoke", help="collect low-impact Codex CLI smoke evidence")
    smoke.add_argument("--root", type=Path, default=Path.cwd())
    smoke.add_argument("--output-dir", type=Path, default=Path("docs/masp/evidencias"))

    args = parser.parse_args(argv)
    try:
        if args.command == "runtime-smoke":
            report = run_codex_smoke(args.root, args.output_dir)
            print(f"{report['classification']}: relatório salvo em {args.output_dir}")
            return 0
        if args.command == "case-revision":
            print(f"SHA256: {case_revision(args.case.read_bytes())}")
            return 0
        routing = load_routing(args.routing)
        if args.command == "validate-routing":
            errors = validate_routing(routing)
            if errors:
                print(f"{args.classification}: {len(errors)} erro(s)")
                for error in errors:
                    print(f"- {error}")
                return 1
            print(f"{args.classification}: 8 fases, 10 papéis, zero erros")
            return 0
        if args.command == "new-case":
            case = create_case(args.id, routing, high_risk=args.high_risk)
            output_path = _within_root(args.output, args.root)
            with _case_lock(output_path):
                if output_path.exists():
                    raise ValueError(f"refusing to overwrite existing case file {output_path}")
                _write_json_atomic(output_path, case)
            print(f"SIMULATED: caso {args.id} criado em {output_path}; actor and model identities are not authenticated")
            return 0
        if args.command == "transition":
            case_path = _within_root(args.case, args.root)
            evidence_path = _within_root(args.evidence, args.root)
            with _case_lock(case_path):
                raw = case_path.read_bytes()
                revision_now = case_revision(raw)
                if revision_now != args.expected_revision:
                    raise ValueError(f"stale case revision; current={revision_now}")
                case = json.loads(raw.decode("utf-8-sig"))
                existing_errors = validate_case(case, routing, args.root)
                if existing_errors:
                    raise ValueError("existing case is invalid: " + "; ".join(existing_errors))
                evidence = _read_json(evidence_path)
                if not isinstance(evidence, list):
                    raise ValueError("evidence JSON must contain an array")
                result = transition_case(
                    case, args.state, args.actor, evidence, routing,
                    phase=args.phase, required_classification=args.required_classification,
                    root=args.root,
                )
                _write_json_atomic(case_path, result)
            print(f"SIMULATED: {result['current_phase']} -> {result['state']}; role and approval labels are not authenticated")
            return 0
        case_path = _within_root(args.case, args.root)
        case = _read_json(case_path)
        errors = validate_case(case, routing, args.root)
        if errors:
            print(f"STATIC: {len(errors)} erro(s)")
            for error in errors:
                print(f"- {error}")
            return 1
        print(f"STATIC: caso e ledger válidos; revision={case_revision(case_path.read_bytes())}")
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"{args.command}: erro: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
