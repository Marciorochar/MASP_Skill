"""MASP case lifecycle and tamper-evident transition ledger."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from .evidence import validate_evidence

STATES = {"PENDING", "IN_PROGRESS", "PASS", "FAIL", "BLOCKED", "NOT_RUN"}


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _event_hash(event: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical({key: value for key, value in event.items() if key != "event_hash"})).hexdigest()


def create_case(case_id: str, routing: dict[str, Any], *, high_risk: bool = False) -> dict[str, Any]:
    if not isinstance(case_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{1,63}", case_id):
        raise ValueError("case id must contain 2-64 safe characters")
    phases = routing.get("phases")
    if not isinstance(phases, list) or not phases:
        raise ValueError("routing matrix has no phases")
    phase = phases[0]
    role = routing.get("roles", {}).get(phase.get("role"), {})
    unavailable = role.get("available", True) is False or role.get("model_available", True) is False
    state = "BLOCKED" if unavailable else "PENDING"
    case = {
        "schema_version": 1,
        "case_id": case_id,
        "classification": "SIMULATED",
        "current_phase": phase["name"],
        "state": state,
        "high_risk": bool(high_risk),
        "approvals": {},
        "ledger": [],
    }
    if unavailable:
        case["block_reason"] = f"required model {role.get('model')} unavailable; no fallback applied"
    return case


def _phase(routing: dict[str, Any], name: str) -> dict[str, Any]:
    for phase in routing.get("phases", []):
        if phase.get("name") == name:
            return phase
    raise ValueError(f"unknown phase {name!r}")


def transition_case(
    case: dict[str, Any],
    target_state: str,
    actor: str,
    evidence: list[dict[str, Any]],
    routing: dict[str, Any],
    *,
    phase: str | None = None,
    required_classification: str | None = None,
) -> dict[str, Any]:
    """Return a transitioned copy, requiring coordinator authority and valid gates."""
    if actor == "masp-executor" and (phase or case.get("current_phase")) == "Ação" and target_state == "PASS":
        raise ValueError("executor cannot self-approve action")
    if actor != "masp-coordenador":
        raise ValueError("only masp-coordenador may authorize a transition")
    if target_state not in STATES:
        raise ValueError(f"invalid state {target_state!r}")
    current_phase = phase or case.get("current_phase")
    phase_data = _phase(routing, current_phase)
    if current_phase != case.get("current_phase"):
        phase_names = [item.get("name") for item in routing.get("phases", [])]
        previous_name = case.get("current_phase")
        previous_index = phase_names.index(previous_name) if previous_name in phase_names else -1
        failed_phase = _phase(routing, case.get("failed_phase") or previous_name)
        permitted_return = case.get("state") == "FAIL" and current_phase in failed_phase.get("returns", [])
        permitted_next = (
            case.get("state") == "PASS"
            and previous_index >= 0
            and previous_index + 1 < len(phase_names)
            and phase_names[previous_index + 1] == current_phase
            and target_state == "IN_PROGRESS"
        )
        if not (permitted_return or permitted_next):
            raise ValueError(f"illegal phase jump to {current_phase!r}")
    if case.get("state") == "BLOCKED":
        raise ValueError("BLOCKED case cannot advance without an explicit external resolution")
    current_state = case.get("state")
    allowed_transitions = {
        "PENDING": {"IN_PROGRESS", "BLOCKED", "NOT_RUN"},
        "IN_PROGRESS": {"PASS", "FAIL", "BLOCKED", "NOT_RUN"},
        "PASS": {"IN_PROGRESS"},
        "FAIL": {"IN_PROGRESS", "BLOCKED", "NOT_RUN"},
        "BLOCKED": set(),
        "NOT_RUN": set(),
    }
    if target_state not in allowed_transitions.get(current_state, set()):
        raise ValueError(f"illegal state transition {current_state!r} -> {target_state!r}")
    if current_state in {"PENDING", "FAIL"} and target_state not in {"IN_PROGRESS", "BLOCKED", "NOT_RUN"}:
        raise ValueError("phase must enter IN_PROGRESS before completion")
    if current_state == "IN_PROGRESS" and target_state == "IN_PROGRESS":
        raise ValueError("phase is already IN_PROGRESS")
    if target_state == "PASS":
        if not evidence:
            raise ValueError("PASS requires evidence")
        issues = validate_evidence(evidence, Path.cwd())
        if issues:
            raise ValueError("; ".join(issues))
        if any(item.get("classification") == "NOT_RUN" for item in evidence):
            raise ValueError("NOT_RUN evidence cannot satisfy a gate")
        if required_classification and not any(item.get("classification") == required_classification for item in evidence):
            raise ValueError(f"gate requires {required_classification} evidence")
        if phase_data.get("id") == "acao":
            approval = case.get("approvals", {}).get("plan", {})
            if not approval.get("approved_by") or not any(item.get("id") == approval.get("evidence_id") for item in evidence):
                raise ValueError("Action requires human plan approval and its referenced evidence")
        if case.get("high_risk") and not any(
            item.get("role") == "masp-especialista-critico" and item.get("opinion") in {"PASS", "APPROVED"}
            for item in evidence
        ):
            raise ValueError("high-risk PASS requires independent Astra opinion")
    if phase_data.get("id") == "acao" and target_state == "IN_PROGRESS":
        approval = case.get("approvals", {}).get("plan", {})
        if not approval.get("approved_by") or not any(item.get("id") == approval.get("evidence_id") for item in evidence):
            raise ValueError("Action requires human plan approval and its referenced evidence")

    result = json.loads(json.dumps(case, ensure_ascii=False))
    previous_hash = result["ledger"][-1]["event_hash"] if result["ledger"] else "0" * 64
    event = {
        "sequence": len(result["ledger"]) + 1,
        "phase": current_phase,
        "previous_state": current_state,
        "new_state": target_state,
        "actor": actor,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "evidence": evidence,
        "classification": "SIMULATED",
        "previous_hash": previous_hash,
    }
    event["event_hash"] = _event_hash(event)
    result["ledger"].append(event)
    result["state"] = target_state
    result["current_phase"] = current_phase
    if target_state == "FAIL":
        result["failed_phase"] = current_phase
    return result


def validate_case(case: dict[str, Any], routing: dict[str, Any], root: Path) -> list[str]:
    """Validate case summary, evidence references, and the complete hash chain."""
    if not isinstance(case, dict):
        return ["case must be an object"]
    errors: list[str] = []
    if not isinstance(case.get("case_id"), str) or not case.get("case_id"):
        errors.append("case id is required")
    if case.get("state") not in STATES:
        errors.append("case has invalid state")
    if case.get("classification") not in {"STATIC", "SIMULATED", "RUNTIME"}:
        errors.append("case has invalid classification")
    try:
        _phase(routing, case.get("current_phase"))
    except ValueError as exc:
        errors.append(str(exc))
    ledger = case.get("ledger")
    if not isinstance(ledger, list):
        return errors + ["ledger must be an array"]
    previous_hash = "0" * 64
    for index, event in enumerate(ledger, start=1):
        if not isinstance(event, dict):
            errors.append(f"ledger event {index} must be an object")
            continue
        if event.get("sequence") != index:
            errors.append(f"ledger sequence mismatch at event {index}")
        if event.get("previous_hash") != previous_hash:
            errors.append(f"ledger hash chain mismatch at event {index}")
        if event.get("event_hash") != _event_hash(event):
            errors.append(f"ledger event hash mismatch at event {index}")
        if event.get("new_state") not in STATES or event.get("previous_state") not in STATES:
            errors.append(f"ledger event {index} has invalid state")
        if event.get("actor") != "masp-coordenador":
            errors.append(f"ledger event {index} has unauthorized actor")
        if event.get("classification") not in {"STATIC", "SIMULATED", "RUNTIME"}:
            errors.append(f"ledger event {index} has invalid classification")
        try:
            _phase(routing, event.get("phase"))
        except ValueError:
            errors.append(f"ledger event {index} references unknown phase")
        errors.extend(f"event {index}: {issue}" for issue in validate_evidence(event.get("evidence", []), root))
        previous_hash = event.get("event_hash", "")
    if ledger and (ledger[-1].get("new_state") != case.get("state") or ledger[-1].get("phase") != case.get("current_phase")):
        errors.append("case summary does not match final ledger event")
    return errors


def validate_parallel_tasks(tasks: list[dict[str, Any]], routing: dict[str, Any]) -> list[str]:
    """Reject fan-out plans with overlapping write ownership or excess concurrency."""
    errors: list[str] = []
    limit = routing.get("policies", {}).get("parallelism", {}).get("max_agents", 0)
    if len(tasks) > limit:
        errors.append(f"parallel task count exceeds limit {limit}")
    owners: dict[str, str] = {}
    for task in tasks:
        for path in task.get("writes", []):
            normalized = str(Path(path)).replace("\\", "/").casefold()
            if normalized in owners:
                errors.append(f"write conflict on {path!r} between {owners[normalized]} and {task.get('id')}")
            else:
                owners[normalized] = task.get("id", "<unknown>")
    return errors
