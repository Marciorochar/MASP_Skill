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

from .case import case_revision, create_case, transition_case, validate_case, validate_parallel_tasks
from .routing import load_agent_configs, load_routing, validate_agent_configs, validate_routing
from .observation import validate_observation_record
from .analysis import validate_analysis_record
from .action_plan import validate_action_plan_record
from .action_execution import validate_action_execution_record
from .verification import validate_verification_record


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
    """Text output is not verified structured evidence for effective settings."""
    return {"model": None, "effort": None}


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
            for key in ("command", "process_completed", "stdout", "stderr"):
                if key not in item or item[key] is None:
                    errors.append(f"command {index} is missing {key}")
            if "exit_code" not in item:
                errors.append(f"command {index} is missing exit_code")
            if item.get("process_completed") is True and not isinstance(item.get("exit_code"), int):
                errors.append(f"command {index} completed without an integer exit_code")
            if item.get("process_completed") is False and item.get("exit_code") is not None:
                errors.append(f"command {index} did not complete but has an exit_code")
            if item.get("process_completed") not in (True, False):
                errors.append(f"command {index} has invalid process_completed")
    expected = report.get("expected_model")
    observed = report.get("observed_model")
    if expected and observed and expected != observed:
        errors.append(f"model mismatch: expected {expected}, observed {observed}")
    return errors


def _run_smoke_command(report: dict, command: list[str], root: Path, *, timeout: int = 30) -> dict:
    def normalize_stream(value) -> str:
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        return "" if value is None else str(value)

    try:
        result = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding="utf-8",
                                errors="replace", timeout=timeout, check=False)
        item = {"command": command, "process_completed": True, "exit_code": result.returncode,
                "stdout": normalize_stream(getattr(result, "stdout", "")),
                "stderr": normalize_stream(getattr(result, "stderr", ""))}
    except subprocess.TimeoutExpired as exc:
        item = {"command": command, "process_completed": False, "exit_code": None,
                "stdout": normalize_stream(exc.stdout), "stderr": normalize_stream(exc.stderr),
                "error": f"timed out after {timeout}s"}
    except OSError as exc:
        item = {"command": command, "process_completed": False, "exit_code": None,
                "stdout": "", "stderr": str(exc), "error": str(exc)}
    report["commands"].append(item)
    return item


def _local_smoke_agents(root: Path) -> dict[str, dict]:
    config = tomllib.loads((root / ".codex/config.toml").read_text(encoding="utf-8"))
    result = {}
    for name, entry in config.get("agents", {}).items():
        if name in ("max_threads", "masp-coordenador") or not isinstance(entry, dict):
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


def _local_smoke_max_threads(root: Path) -> int:
    config = tomllib.loads((root / ".codex/config.toml").read_text(encoding="utf-8"))
    value = config.get("agents", {}).get("max_threads", 1)
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ValueError("agents.max_threads must be a positive integer")
    return value


def _agent_config_root(routing_path: Path, workspace: Path) -> Path:
    config_root = Path(workspace).resolve()
    if not (config_root / ".codex/config.toml").is_file():
        candidate = Path(routing_path).resolve().parents[2]
        if (candidate / ".codex/config.toml").is_file():
            config_root = candidate
    return config_root


def _effective_config_errors(routing: dict, routing_path: Path, workspace: Path) -> list[str]:
    errors = validate_routing(routing)
    if errors:
        return errors
    config_root = _agent_config_root(routing_path, workspace)
    if (config_root / ".codex/config.toml").is_file():
        try:
            errors.extend(validate_agent_configs(routing, load_agent_configs(config_root)))
        except (OSError, ValueError, KeyError, tomllib.TOMLDecodeError) as exc:
            errors.append(f"agent config could not be loaded: {exc}")
    else:
        errors.append("agent config .codex/config.toml was not found under workspace or routing root")
    return errors


def _delegation_events(stdout: str, roles: list[str]) -> dict[str, dict]:
    """Accept only structured call, agent, and completion events with matching IDs."""
    calls: list[dict] = []
    agents: list[dict] = []
    completions: list[dict] = []
    receiver_starts: list[dict] = []
    receiver_completions: list[dict] = []
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict) or event.get("type") not in {"item.started", "item.completed", "item.updated"}:
            continue
        item = event.get("item")
        if not isinstance(item, dict) or not isinstance(item.get("type"), str):
            continue
        event_type = item["type"]
        status = item.get("status")
        call_id = item.get("call_id")
        agent_id = item.get("agent_id")
        role = (item.get("agent_name") or item.get("target_agent") or
                item.get("agent_type") or item.get("name") or item.get("agent"))
        arguments = item.get("arguments")
        if not isinstance(role, str) and isinstance(arguments, dict):
            role = arguments.get("agent_type") or arguments.get("agent_name") or arguments.get("name")
        if not isinstance(role, str) or role not in roles:
            role = None
        # Newer Codex CLI JSONL exposes recipients and their states on
        # collab_tool_call. Require an explicit role, one receiver, a start,
        # a matching completion, and a completed receiver state. Never infer
        # a role from the assistant's prose or from a generic wait() call.
        if event_type == "collab_tool_call" and item.get("tool") in {
            "spawn_agent", "spawnAgent", "create_agent", "delegate_to_agent"
        }:
            recipients = item.get("receiver_thread_ids")
            if (isinstance(recipients, list) and len(recipients) == 1
                    and isinstance(recipients[0], str) and recipients[0]):
                record = {"role": role, "thread": recipients[0],
                          "item_id": item.get("id"), "item": item}
                if event.get("type") == "item.started" and role is not None:
                    receiver_starts.append(record)
                elif event.get("type") == "item.completed":
                    receiver_completions.append(record)
        if not isinstance(call_id, str) or not call_id:
            continue
        if event_type == "collab_tool_call" and item.get("tool") in {"spawn_agent", "spawnAgent", "create_agent", "delegate_to_agent"}:
            if isinstance(role, str) and role in roles and status in {"started", "in_progress", "completed", "succeeded"}:
                calls.append({"role": role, "call_id": call_id, "item": item})
        elif event_type in {"agent_started", "collab_agent_started", "agent_spawned"}:
            if (isinstance(agent_id, str) and agent_id and status in {"started", "in_progress", "running"} and
                    (role is None or role in roles)):
                agents.append({"role": role, "call_id": call_id, "agent_id": agent_id, "item": item})
        elif event_type in {"agent_completed", "collab_agent_completed", "agent_result"}:
            if (isinstance(agent_id, str) and agent_id and status in {"completed", "succeeded", "done"} and
                    (role is None or role in roles)):
                completions.append({"role": role, "call_id": call_id, "agent_id": agent_id, "item": item})

    found = {role: {"tool_call": False, "completion": False, "call_id": None, "agent_id": None,
                    "event_excerpt": None, "observed_model": None, "observed_effort": None} for role in roles}
    for call in calls:
        for agent in agents:
            if ((agent["role"] is not None and call["role"] != agent["role"]) or
                    call["call_id"] != agent["call_id"]):
                continue
            found[call["role"]]["tool_call"] = True
            found[call["role"]]["call_id"] = call["call_id"]
            found[call["role"]]["agent_id"] = agent["agent_id"]
            for completion in completions:
                if ((completion["role"] is not None and completion["role"] != call["role"]) or
                        completion["call_id"] != call["call_id"] or
                        completion["agent_id"] != agent["agent_id"]):
                    continue
                found[call["role"]]["completion"] = True
                result = completion["item"].get("result")
                if not isinstance(result, dict):
                    result = completion["item"]
                found[call["role"]]["observed_model"] = result.get("effective_model")
                found[call["role"]]["observed_effort"] = result.get("effective_effort")
                found[call["role"]]["event_excerpt"] = json.dumps(
                    {"call": call["item"], "agent": agent["item"], "completion": completion["item"]},
                    ensure_ascii=False)[:2000]
    for start in receiver_starts:
        for completed in receiver_completions:
            if completed["thread"] != start["thread"]:
                continue
            if completed["role"] is not None and completed["role"] != start["role"]:
                continue
            if (start["item_id"] is not None and completed["item_id"] is not None
                    and start["item_id"] != completed["item_id"]):
                continue
            states = completed["item"].get("agents_states")
            state = states.get(start["thread"]) if isinstance(states, dict) else None
            if not isinstance(state, dict) or state.get("status") not in {
                "completed", "succeeded", "done"
            }:
                continue
            role = start["role"]
            record = found[role]
            record["tool_call"] = True
            record["completion"] = True
            record["call_id"] = start["item_id"]
            record["agent_id"] = start["thread"]
            # Only explicit effective values may be described as observed.
            record["observed_model"] = state.get("effective_model") if isinstance(
                state.get("effective_model"), str
            ) else None
            record["observed_effort"] = state.get("effective_effort") if isinstance(
                state.get("effective_effort"), str
            ) else None
            record["event_excerpt"] = json.dumps({
                "call": start["item"], "completion": completed["item"]
            }, ensure_ascii=False)[:2000]
    return found


def _skill_load_evidence(stdout: str, skill_name: str = "masp") -> dict | None:
    """Return explicit structured skill-load evidence, never an assistant text claim."""
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict) or event.get("type") not in {"item.completed", "item.updated"}:
            continue
        item = event.get("item")
        if not isinstance(item, dict) or item.get("type") not in {"skill_load", "skill_loaded"}:
            continue
        name = item.get("skill_name") or item.get("name")
        if name == skill_name and item.get("status") in {"loaded", "completed", "succeeded"}:
            return item
    return None


def run_codex_smoke(root: Path, output_dir: Path, *, all_roles: bool = False) -> dict:
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
    try:
        max_agents = _local_smoke_max_threads(root)
        report["effective_agent_limit"] = max_agents
    except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        max_agents = 1
        report["checks"].append({"name": "effective agent limit", "classification": "STATIC",
                                 "status": "FAIL", "reason": str(exc)})
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
                critical = role == "masp-especialista-critico"
                report["checks"].append({"name": f"{prefix} {role}", "classification": "RUNTIME",
                                         "status": "NOT_RUN" if critical else "BLOCKED",
                                         "model": configured.get("model"),
                                         "effort": configured.get("effort"),
                                         "reason": ("Astra deliberately excluded from the initial smoke"
                                                    if critical else "Codex CLI executable was not found on PATH")})
    else:
        for args, name in ((["--version"], "version"), (["--help"], "CLI help")):
            item = _run_smoke_command(report, [codex, *args], root)
            report["checks"].append({"name": name, "classification": "RUNTIME",
                                     "status": "BLOCKED" if not item["process_completed"] else
                                     "PASS" if item["exit_code"] == 0 else "FAIL",
                                     "command_index": len(report["commands"]) - 1})
            if name == "version":
                report["version"] = (item["stdout"] or item["stderr"]).strip()
        catalog = _run_smoke_command(report, [codex, "debug", "models", "--bundled"], root, timeout=60)
        report["classification"] = "RUNTIME"
        catalog_status = "FAIL"
        catalog_excerpt = ""
        available = {}
        if catalog["process_completed"] and catalog["exit_code"] == 0:
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
                                 "status": catalog_status if catalog["process_completed"] else "BLOCKED",
                                 "command_index": len(report["commands"]) - 1,
                                 "reason": catalog.get("error")})
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
        configured_roles = [name for name in local_agents
                            if name not in {"masp-coordenador", "masp-especialista-critico"}]
        roles = configured_roles if all_roles else configured_roles[:1]
        unprobed_roles = configured_roles[len(roles):]
        # Astra is inventoried, not invoked: a critical review needs separate
        # authorization and proof of the first noncritical delegation.
        if "masp-especialista-critico" in local_agents:
            unprobed_roles.append("masp-especialista-critico")
        coordinator = local_agents.get("masp-coordenador", {})
        prompt = (
            "You are testing this repository's local MASP coordinator and skill in a read-only smoke. "
            "Try to invoke the local skill named masp (do not read it with shell as a substitute for loading it). "
            f"Then, sequentially and never with more than {max_agents} active agents, use the actual configured local subagent "
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
        skill_evidence = _skill_load_evidence(delegated["stdout"])
        skill_status = ("BLOCKED" if not delegated["process_completed"] or delegated["exit_code"] != 0 or not skill_evidence
                        else "PASS")
        report["checks"].append({"name": "MASP skill load", "classification": "RUNTIME", "status": skill_status,
                                 "command_index": len(report["commands"]) - 1,
                                 "evidence": skill_evidence,
                                 "reason": "no structured skill-load event was emitted" if not skill_evidence else None})
        tool_events = _delegation_events(delegated["stdout"], roles)
        for role in roles:
            configured = local_agents[role]
            event = tool_events[role]
            if not delegated["process_completed"] or delegated["exit_code"] != 0:
                status = "BLOCKED"
                reason = "Codex exec did not complete successfully; see command output"
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
            observed_matches = (event["completion"] and event["observed_model"] == configured.get("model") and
                                event["observed_effort"] == configured.get("effort"))
            observation_status = ("PASS" if observed_matches else "FAIL" if event["completion"] else "BLOCKED")
            report["checks"].append({"name": f"effective model/effort {role}", "classification": "RUNTIME",
                                     "status": observation_status,
                                     "expected_model": configured.get("model"), "expected_effort": configured.get("effort"),
                                     "observed_model": event["observed_model"], "observed_effort": event["observed_effort"],
                                     "reason": None if observed_matches else "no matching effective model/effort in structured completion evidence"})
        for unprobed_role in unprobed_roles:
            for prefix in ("delegation", "effective model/effort"):
                report["checks"].append({
                    "name": f"{prefix} {unprobed_role}",
                    "classification": "RUNTIME",
                    "status": "NOT_RUN",
                    "reason": ("Astra deliberately excluded; independent critical audit requires separate authorization"
                               if unprobed_role == "masp-especialista-critico" else
                               "noncritical role not tested in this run"),
                })
        discovery_status = "BLOCKED" if (
            unprobed_roles or not delegated["process_completed"] or delegated["exit_code"] != 0
        ) else ("PASS" if roles and all(event["tool_call"] and event["completion"] for event in tool_events.values()) else "BLOCKED")
        report["checks"].append({"name": "local agent discovery", "classification": "RUNTIME",
                                 "status": discovery_status,
                                 "reason": "discovery/delegation invocation did not complete successfully" if not delegated["process_completed"] or delegated["exit_code"] != 0 else
                                 "full discovery not tested by minimal smoke" if unprobed_roles else
                                  "not all configured subagents produced explicit tool-call events" if discovery_status == "BLOCKED" else None})
    config = root / ".codex" / "config.toml"
    report["checks"].append({"name": "local config file", "classification": "STATIC",
                             "status": "PASS" if config.is_file() else "FAIL"})
    report["checks"].append({"name": "local skill file", "classification": "STATIC",
                             "status": "PASS" if (root / ".agents/skills/masp/SKILL.md").is_file() else "FAIL"})
    report["limitations"].append("Runtime delegation status requires explicit tool-call and completion events; an assistant claim alone is not accepted")
    report["python"] = sys.version.split()[0]
    errors = validate_codex_smoke_report(report)
    if errors:
        report["validation_errors"] = errors
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
    transition.add_argument("--parallel-tasks", type=Path,
                            help="optional JSON task array with writes paths to validate against concurrency policy")

    revision = commands.add_parser("case-revision", help="print the current manifest revision for compare-and-swap")
    revision.add_argument("--case", type=Path, required=True)

    validate_case_parser = commands.add_parser("validate-case", help="validate a case manifest and ledger")
    validate_case_parser.add_argument("--case", type=Path, required=True)
    validate_case_parser.add_argument("--routing", type=Path, default=Path("docs/masp/masp-routing.toml"))
    validate_case_parser.add_argument("--root", type=Path, default=Path.cwd())

    observation = commands.add_parser("validate-observation", help="check a universal observation JSON sidecar (STATIC only)")
    observation.add_argument("--record", type=Path, required=True)
    observation.add_argument("--root", type=Path, default=Path.cwd())

    analysis = commands.add_parser("validate-analysis", help="check an analysis sidecar (STATIC only, no causal certification)")
    analysis.add_argument("--record", type=Path, required=True)
    analysis.add_argument("--root", type=Path, default=Path.cwd())

    action_plan = commands.add_parser("validate-action-plan", help="check a planning sidecar (STATIC only; no human approval authentication)")
    action_plan.add_argument("--record", type=Path, required=True)
    action_plan.add_argument("--root", type=Path, default=Path.cwd())

    action_execution = commands.add_parser("validate-action-execution", help="check M05 execution record (STATIC, no action execution)")
    action_execution.add_argument("--record", type=Path, required=True)
    action_execution.add_argument("--root", type=Path, default=Path.cwd())

    verify = commands.add_parser("validate-verification", help="check a universal M06 verification record (STATIC only)")
    verify.add_argument("--record", type=Path, required=True)
    verify.add_argument("--root", type=Path, default=Path.cwd())

    smoke = commands.add_parser("runtime-smoke", help="collect low-impact Codex CLI smoke evidence")
    smoke.add_argument("--root", type=Path, default=Path.cwd())
    smoke.add_argument("--output-dir", type=Path, default=Path("docs/masp/evidencias"))
    smoke.add_argument("--strict", action="store_true", help="return nonzero when a check fails or is blocked")
    smoke.add_argument("--all-roles", action="store_true", help="explicitly attempt all noncritical phase roles (excludes Astra); costly and not for initial validation")

    args = parser.parse_args(argv)
    try:
        if args.command == "validate-verification":
            record_path = _within_root(args.record, args.root)
            issues = validate_verification_record(_read_json(record_path))
            if issues:
                print(f"STATIC: {len(issues)} structural verification record error(s)")
                for issue in issues:
                    print(f"- {issue}")
                return 1
            print("STATIC: verification record structurally valid; no real efficacy, review or Gate 06 PASS authenticated")
            return 0
        if args.command == "validate-action-execution":
            record_path = _within_root(args.record, args.root)
            issues = validate_action_execution_record(_read_json(record_path))
            if issues:
                print(f"STATIC: {len(issues)} structural execution record error(s)")
                for issue in issues:
                    print(f"- {issue}")
                return 1
            print("STATIC: record structurally valid; does not authenticate approval, perform actions or pass Gate 05")
            return 0
        if args.command == "validate-action-plan":
            record_path = _within_root(args.record, args.root)
            issues = validate_action_plan_record(_read_json(record_path))
            if issues:
                print(f"STATIC: {len(issues)} problema(s) estruturais no plano de ação")
                for issue in issues:
                    print(f"- {issue}")
                return 1
            print("STATIC: plano estruturalmente válido; não autentica aprovação humana, execução nem gate MASP")
            return 0
        if args.command == "validate-analysis":
            record_path = _within_root(args.record, args.root)
            issues = validate_analysis_record(_read_json(record_path))
            if issues:
                print(f"STATIC: {len(issues)} problema(s) estruturais no registro de Análise")
                for issue in issues:
                    print(f"- {issue}")
                return 1
            print("STATIC: registro de Análise estruturalmente válido; não autentica fontes, causa nem gate MASP")
            return 0
        if args.command == "validate-observation":
            record_path = _within_root(args.record, args.root)
            issues = validate_observation_record(_read_json(record_path))
            if issues:
                print(f"STATIC: {len(issues)} problema(s) estruturais no registro de Observação")
                for issue in issues:
                    print(f"- {issue}")
                return 1
            print("STATIC: estrutura de Observação válida; gate MASP e evidências reais não autenticados")
            return 0
        if args.command == "runtime-smoke":
            report = (run_codex_smoke(args.root, args.output_dir, all_roles=True) if args.all_roles
                      else run_codex_smoke(args.root, args.output_dir))
            print(f"{report['classification']}: relatório salvo em {args.output_dir}")
            if args.strict and any(check.get("status") in {"FAIL", "BLOCKED"} for check in report.get("checks", [])):
                return 1
            return 0
        if args.command == "case-revision":
            print(f"SHA256: {case_revision(args.case.read_bytes())}")
            return 0
        routing = load_routing(args.routing)
        if args.command == "validate-routing":
            errors = _effective_config_errors(routing, args.routing, Path.cwd())
            if errors:
                print(f"{args.classification}: {len(errors)} erro(s)")
                for error in errors:
                    print(f"- {error}")
                return 1
            print(f"{args.classification}: 8 fases, 10 papéis, zero erros")
            return 0
        if args.command == "new-case":
            config_errors = _effective_config_errors(routing, args.routing, args.root)
            if config_errors:
                raise ValueError("invalid routing/agent configuration: " + "; ".join(config_errors))
            case = create_case(args.id, routing, high_risk=args.high_risk)
            output_path = _within_root(args.output, args.root)
            with _case_lock(output_path):
                if output_path.exists():
                    raise ValueError(f"refusing to overwrite existing case file {output_path}")
                _write_json_atomic(output_path, case)
            print(f"SIMULATED: caso {args.id} criado em {output_path}; actor and model identities are not authenticated")
            return 0
        if args.command == "transition":
            config_errors = _effective_config_errors(routing, args.routing, args.root)
            if config_errors:
                raise ValueError("invalid routing/agent configuration: " + "; ".join(config_errors))
            tasks = _read_json(args.parallel_tasks) if args.parallel_tasks else []
            if not isinstance(tasks, list):
                raise ValueError("parallel tasks JSON must contain an array")
            config_root = _agent_config_root(args.routing, args.root)
            effective_limit = _local_smoke_max_threads(config_root)
            parallel_errors = validate_parallel_tasks(tasks, routing, root=args.root, effective_limit=effective_limit)
            if parallel_errors:
                raise ValueError("invalid parallel task assignment: " + "; ".join(parallel_errors))
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
        if args.command == "validate-case":
            config_errors = _effective_config_errors(routing, args.routing, args.root)
            if config_errors:
                print(f"STATIC: {len(config_errors)} erro(s)")
                for error in config_errors:
                    print(f"- {error}")
                return 1
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
