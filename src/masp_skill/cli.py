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
import tomllib
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


def _run_smoke_command(report: dict, command: list[str], root: Path, *, timeout: int = 30) -> dict:
    try:
        result = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding="utf-8",
                                errors="replace", timeout=timeout, check=False)
        item = {"command": command, "exit_code": result.returncode,
                "stdout": result.stdout, "stderr": result.stderr}
    except subprocess.TimeoutExpired as exc:
        item = {"command": command, "exit_code": None, "stdout": exc.stdout or "",
                "stderr": exc.stderr or "", "error": f"timed out after {timeout}s"}
    except OSError as exc:
        item = {"command": command, "exit_code": None, "stdout": "", "stderr": str(exc), "error": str(exc)}
    report["commands"].append(item)
    return item


def _local_smoke_agents(root: Path) -> dict[str, dict]:
    config = tomllib.loads((root / ".codex/config.toml").read_text(encoding="utf-8"))
    result = {}
    for name, entry in config.get("agents", {}).items():
        if name in ("max_threads", "masp-coordenador", "masp-especialista-critico") or not isinstance(entry, dict):
            continue
        path = (root / ".codex" / entry["config_file"]).resolve()
        path.relative_to((root / ".codex").resolve())
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        result[name] = {"model": data.get("model"), "effort": data.get("model_reasoning_effort"),
                        "config_file": entry["config_file"]}
    coordinator_entry = config.get("agents", {}).get("masp-coordenador")
    if isinstance(coordinator_entry, dict):
        coordinator_path = (root / ".codex" / coordinator_entry["config_file"]).resolve()
        coordinator_path.relative_to((root / ".codex").resolve())
        coordinator = tomllib.loads(coordinator_path.read_text(encoding="utf-8"))
        result["masp-coordenador"] = {"model": coordinator.get("model"),
                                      "effort": coordinator.get("model_reasoning_effort"),
                                      "config_file": coordinator_entry["config_file"]}
    return result


def _delegation_events(stdout: str, roles: list[str]) -> dict[str, dict]:
    """Find explicit subagent tool events; plain assistant claims are not proof."""
    found = {role: {"tool_call": False, "completion": False, "event_excerpt": None,
                    "observed_model": None, "observed_effort": None} for role in roles}
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item", {}) if isinstance(event, dict) else {}
        serialized = json.dumps(item, ensure_ascii=False)
        lower = serialized.lower()
        is_spawn = any(marker in lower for marker in ("spawn_agent", "spawnagent", "create_agent", "delegate_to_agent"))
        is_result = any(key in item for key in ("agent_id", "agentId", "subagent_id")) or "subagent" in lower
        for role in roles:
            if role in serialized:
                found[role]["tool_call"] |= is_spawn
                found[role]["completion"] |= is_result and not is_spawn
                if is_spawn or is_result:
                    found[role]["event_excerpt"] = serialized[:1000]
                    model_match = re.search(r"(?i)\bmodel\s*[:=]\s*([\w.-]+)", serialized) if is_spawn or is_result else None
                    effort_match = re.search(r"(?i)(?:reasoning[_ ]effort|effort)\s*[:=]\s*(low|medium|high)", serialized) if is_spawn or is_result else None
                    if model_match:
                        found[role]["observed_model"] = model_match.group(1)
                    if effort_match:
                        found[role]["observed_effort"] = effort_match.group(1)
    return found


def run_codex_smoke(root: Path, output_dir: Path) -> dict:
    """Run read-only CLI probes and an ephemeral, read-only role delegation attempt."""
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
        "role_models": {},
        "limitations": [],
    }
    if not codex:
        report["limitations"].append("Codex CLI executable was not found on PATH")
        report["checks"].append({"name": "CLI availability", "status": "BLOCKED"})
        try:
            local_agents = _local_smoke_agents(root)
        except (OSError, ValueError, KeyError, tomllib.TOMLDecodeError):
            local_agents = {}
        report["role_models"] = local_agents
        for name in ("model catalog", "MASP skill load", "local agent discovery", "role model/effort catalog compatibility"):
            report["checks"].append({"name": name, "classification": "RUNTIME", "status": "BLOCKED",
                                     "reason": "Codex CLI executable was not found on PATH"})
        for role, configured in local_agents.items():
            if role == "masp-coordenador":
                continue
            for prefix in ("delegation", "effective model/effort"):
                report["checks"].append({"name": f"{prefix} {role}", "classification": "RUNTIME",
                                         "status": "BLOCKED", "model": configured.get("model"),
                                         "effort": configured.get("effort"),
                                         "reason": "Codex CLI executable was not found on PATH"})
    else:
        for args, name in ((["--version"], "version"), (["--help"], "CLI help")):
            item = _run_smoke_command(report, [codex, *args], root)
            report["checks"].append({"name": name, "classification": "RUNTIME",
                                     "status": "PASS" if item["exit_code"] == 0 else "FAIL",
                                     "command_index": len(report["commands"]) - 1})
            if name == "version":
                report["version"] = (item["stdout"] or item["stderr"]).strip()
        catalog = _run_smoke_command(report, [codex, "debug", "models", "--bundled"], root, timeout=60)
        report["classification"] = "RUNTIME"
        catalog_status = "FAIL"
        catalog_excerpt = ""
        available = {}
        if catalog["exit_code"] == 0:
            try:
                raw_catalog = json.loads(catalog["stdout"])
                for model in raw_catalog.get("models", []):
                    slug = model.get("slug")
                    if slug:
                        available[slug] = sorted({level.get("effort") for level in model.get("supported_reasoning_levels", [])
                                                  if level.get("effort")})
                catalog_excerpt = json.dumps({"models": [{"slug": name, "supported_efforts": efforts}
                                                           for name, efforts in sorted(available.items())]}, ensure_ascii=False)
                catalog["stdout"] = catalog_excerpt
                catalog["stdout_capture"] = "filtered model/effort metadata; omitted embedded prompt instructions"
                catalog_status = "PASS"
            except (json.JSONDecodeError, AttributeError, TypeError) as exc:
                catalog["error"] = f"catalog JSON could not be parsed: {exc}"
        report["checks"].append({"name": "model catalog", "classification": "RUNTIME",
                                 "status": catalog_status, "command_index": len(report["commands"]) - 1})
        try:
            local_agents = _local_smoke_agents(root)
            report["role_models"] = local_agents
            report["checks"].append({"name": "local agent config parse", "classification": "STATIC", "status": "PASS"})
        except (OSError, ValueError, KeyError, tomllib.TOMLDecodeError) as exc:
            local_agents = {}
            report["checks"].append({"name": "local agent config parse", "classification": "STATIC",
                                     "status": "FAIL", "reason": str(exc)})
        phases = {name: {"model": info.get("model"), "effort": info.get("effort"),
                         "catalog_status": "PASS" if info.get("model") in available and
                         info.get("effort") in available.get(info.get("model"), []) else "FAIL"}
                  for name, info in local_agents.items()}
        report["checks"].append({"name": "role model/effort catalog compatibility", "classification": "RUNTIME",
                                 "status": "PASS" if phases and all(x["catalog_status"] == "PASS" for x in phases.values()) else "FAIL",
                                 "roles": phases})
        roles = [name for name in local_agents if name != "masp-coordenador"]
        coordinator = local_agents.get("masp-coordenador", {})
        prompt = (
            "You are testing this repository's local MASP coordinator and skill in a read-only smoke. "
            "Try to invoke the local skill named masp (do not read it with shell as a substitute for loading it). "
            "Then, sequentially and never with more than three active agents, use the actual configured local subagent "
            "for each listed role to return only the marker ROLE:<name> and its effective model and reasoning effort. "
            "Do not use shell or other tools; do not edit files. If a configured role or subagent tool is unavailable, "
            "report that plainly. Roles: " + ", ".join(roles) + ". When finished, include MASP_SKILL_LOADED only if "
            "the MASP skill was actually loaded."
        )
        exec_command = [codex, "exec", "--ephemeral", "--sandbox", "read-only", "--json", "-C", str(root)]
        if coordinator.get("model"):
            exec_command += ["--model", coordinator["model"]]
        if coordinator.get("effort"):
            exec_command += ["-c", f'model_reasoning_effort="{coordinator["effort"]}"']
        exec_command.append(prompt)
        delegated = _run_smoke_command(report, exec_command, root, timeout=240)
        skill_status = ("BLOCKED" if delegated["exit_code"] != 0 else
                        "PASS" if "MASP_SKILL_LOADED" in delegated["stdout"] else "FAIL")
        report["checks"].append({"name": "MASP skill load", "classification": "RUNTIME", "status": skill_status,
                                 "command_index": len(report["commands"]) - 1,
                                 "reason": "Codex exec failed before checking skill load" if delegated["exit_code"] != 0 else None})
        tool_events = _delegation_events(delegated["stdout"], roles)
        for role in roles:
            configured = local_agents[role]
            event = tool_events[role]
            if delegated["exit_code"] != 0:
                status = "BLOCKED"
                reason = "Codex exec returned nonzero; see command output"
            elif not event["tool_call"]:
                status = "BLOCKED"
                reason = "no explicit subagent tool call for this role was observed in JSONL"
            elif not event["completion"]:
                status = "FAIL"
                reason = "subagent invocation event observed but no verifiable completion event"
            else:
                status = "PASS"
                reason = None
            report["checks"].append({"name": f"delegation {role}", "classification": "RUNTIME", "status": status,
                                     "model": configured.get("model"), "effort": configured.get("effort"),
                                     "reason": reason, "evidence": event})
            observed_matches = (event["observed_model"] == configured.get("model") and
                                event["observed_effort"] == configured.get("effort"))
            report["checks"].append({"name": f"effective model/effort {role}", "classification": "RUNTIME",
                                     "status": "PASS" if observed_matches else "BLOCKED",
                                     "expected_model": configured.get("model"), "expected_effort": configured.get("effort"),
                                     "observed_model": event["observed_model"], "observed_effort": event["observed_effort"],
                                     "reason": None if observed_matches else "no verifiable effective model/effort was emitted by a completed subagent event"})
        discovery_status = "BLOCKED" if delegated["exit_code"] != 0 else (
            "PASS" if roles and all(event["tool_call"] for event in tool_events.values()) else "BLOCKED")
        report["checks"].append({"name": "local agent discovery", "classification": "RUNTIME",
                                 "status": discovery_status,
                                 "reason": "discovery/delegation invocation did not start" if delegated["exit_code"] != 0 else
                                 "not all configured subagents produced explicit tool-call events" if discovery_status == "BLOCKED" else None})
    config = root / ".codex" / "config.toml"
    report["checks"].append({"name": "local config file", "classification": "STATIC",
                             "status": "PASS" if config.is_file() else "FAIL"})
    report["checks"].append({"name": "local skill file", "classification": "STATIC",
                             "status": "PASS" if (root / "skills/masp/SKILL.md").is_file() else "FAIL"})
    report["limitations"].append("Runtime delegation status requires explicit tool-call and completion events; an assistant claim alone is not accepted")
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
