"""Simulated MASP case lifecycle; this module provides no identity authentication."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from .evidence import validate_evidence

STATES = {"PENDING", "IN_PROGRESS", "PASS", "FAIL", "BLOCKED", "NOT_RUN"}
GATE_REQUIREMENTS = {
    "identificacao": {"problem", "impact", "scope", "exclusions", "success_metric"},
    "observacao": {"baseline", "environment", "collection_method", "reproducible_result_or_limitation"},
    "analise": {"hypotheses", "evidence_for_and_against", "root_cause_or_explicit_inconclusive"},
    "plano-de-acao": {"tasks", "owners", "scope", "risks", "rollback", "tests", "human_approval"},
    "acao": {"changes", "diff", "commands", "results", "no_self_approval"},
    "verificacao": {"baseline_comparison", "runtime_tests", "relevant_regressions", "independent_review"},
    "padronizacao": {"preventive_control", "owner", "trigger", "regression"},
    "conclusao": {"complete_ledger", "results", "limitations", "residual_risks", "pending_items", "audit_opinion"},
}
ALLOWED_TRANSITIONS = {
    "PENDING": {"IN_PROGRESS", "BLOCKED", "NOT_RUN"},
    "IN_PROGRESS": {"PASS", "FAIL", "BLOCKED", "NOT_RUN"},
    "PASS": {"IN_PROGRESS"},
    "FAIL": {"IN_PROGRESS", "BLOCKED", "NOT_RUN"},
    "BLOCKED": set(),
    "NOT_RUN": set(),
}
ASTRA_MODEL = "gpt-6-astra"
ASTRA_EFFORT = "medium"


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def case_revision(raw: bytes) -> str:
    """Return an optimistic-concurrency token for exact manifest bytes."""
    return hashlib.sha256(raw).hexdigest()


def _event_hash(event: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical({key: value for key, value in event.items() if key != "event_hash"})).hexdigest()


def _genesis_payload(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": case.get("schema_version"),
        "case_id": case.get("case_id"),
        "classification": case.get("classification"),
        "origin_phase": case.get("origin_phase"),
        "initial_state": case.get("initial_state"),
        "high_risk": case.get("high_risk"),
    }


def _genesis_hash(case: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical(_genesis_payload(case))).hexdigest()


def _phase(routing: dict[str, Any], name: str) -> dict[str, Any]:
    for phase in routing.get("phases", []):
        if phase.get("name") == name:
            return phase
    raise ValueError(f"unknown phase {name!r}")


def _role_available(routing: dict[str, Any], phase: dict[str, Any]) -> tuple[bool, str]:
    role_name = phase.get("role")
    role = routing.get("roles", {}).get(role_name, {})
    model = role.get("model")
    effort = role.get("effort")
    if not isinstance(model, str) or not model.strip() or effort not in {"low", "medium", "high"}:
        return False, f"BLOCKED: phase {phase.get('name')} has no valid declared model/effort for {role_name}"
    if role.get("available", True) is False or role.get("model_available", True) is False:
        return False, f"BLOCKED: required model {model} for {role_name} is unavailable; no fallback is applied"
    return True, str(model or "")


def current_model_availability(routing: dict[str, Any], phase_name: str) -> tuple[bool, str]:
    """Check present routing availability explicitly; replay uses event snapshots instead."""
    try:
        phase = _phase(routing, phase_name)
    except (AttributeError, TypeError, ValueError):
        return False, f"unknown phase {phase_name!r}"
    return _role_available(routing, phase)


def _astra_contract(routing: dict[str, Any]) -> tuple[bool, str]:
    role = routing.get("roles", {}).get("masp-especialista-critico", {})
    model, effort = role.get("model"), role.get("effort")
    if model != ASTRA_MODEL or effort != ASTRA_EFFORT:
        return False, f"BLOCKED: Astra routing must declare {ASTRA_MODEL}/{ASTRA_EFFORT}, got {model!r}/{effort!r}"
    return True, ASTRA_MODEL


def _astra_current_available(routing: dict[str, Any]) -> bool:
    role = routing.get("roles", {}).get("masp-especialista-critico", {})
    return role.get("available", True) is not False and role.get("model_available", True) is not False


def create_case(case_id: str, routing: dict[str, Any], *, high_risk: bool = False) -> dict[str, Any]:
    """Create a SIMULATED case manifest, not an authenticated authorization object."""
    if not isinstance(case_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{1,63}", case_id):
        raise ValueError("case id must contain 2-64 safe characters")
    phases = routing.get("phases")
    if not isinstance(phases, list) or len(phases) != 8:
        raise ValueError("routing matrix must contain the eight required phases")
    origin = phases[0].get("name")
    role_available, model = _role_available(routing, phases[0])
    initial_state = "PENDING" if role_available else "BLOCKED"
    case = {
        "schema_version": 2,
        "case_id": case_id,
        "classification": "SIMULATED",
        "origin_phase": origin,
        "current_phase": origin,
        "initial_state": initial_state,
        "state": initial_state,
        "high_risk": bool(high_risk),
        "ledger": [],
        "authority_note": "Actor, approval, role, model, classification and opinion fields are caller-supplied simulation labels; no runtime identity or signature is verified.",
    }
    if not role_available:
        case["block_reason"] = f"required model {model} unavailable; no automatic fallback"
    case["genesis_hash"] = _genesis_hash(case)
    return case


def _plan_approval_recorded(case: dict[str, Any], prior_events: list[dict[str, Any]]) -> bool:
    for event in prior_events:
        if not isinstance(event, dict):
            continue
        if event.get("phase") != "Plano de ação" or event.get("new_state") != "PASS":
            continue
        items = event.get("evidence")
        if isinstance(items, list) and any(
            isinstance(item, dict) and item.get("approval_type") == "human_plan"
            and isinstance(item.get("approved_by"), str) and item["approved_by"].strip()
            for item in items
        ):
            return True
    return False


def _gate_errors(
    case: dict[str, Any],
    phase: dict[str, Any],
    evidence: list[dict[str, Any]],
    routing: dict[str, Any],
    prior_events: list[dict[str, Any]],
    required_classification: str | None = None,
    *,
    historical: bool = False,
    astra_snapshot: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    phase_id = phase.get("id")
    required = GATE_REQUIREMENTS.get(phase_id)
    if required is None:
        return [f"no structured gate requirements registered for phase {phase_id!r}"]
    if not isinstance(phase.get("gate"), str) or not phase["gate"].strip():
        errors.append(f"phase {phase_id} is missing the gate declared in the routing matrix")
    declared: set[str] = set()
    for item in evidence:
        values = item.get("satisfies", [])
        if isinstance(values, list):
            declared.update(value for value in values if isinstance(value, str))
    missing = sorted(required - declared)
    if missing:
        errors.append(f"gate {phase_id} missing criteria: {missing}")
    if not evidence:
        errors.append("PASS requires evidence")
    if any(item.get("classification") == "NOT_RUN" for item in evidence):
        errors.append("NOT_RUN evidence cannot satisfy a gate")
    if required_classification and not any(item.get("classification") == required_classification for item in evidence):
        errors.append(f"gate requires {required_classification} evidence")
    if phase_id == "plano-de-acao":
        if not any(item.get("approval_type") == "human_plan" and isinstance(item.get("approved_by"), str) and item["approved_by"].strip() for item in evidence):
            errors.append("plan gate requires a recorded human approval label; identity is not authenticated")
    if phase_id == "acao" and not _plan_approval_recorded(case, prior_events):
        errors.append("Action requires the plan gate to have recorded a simulated human approval")
    if phase_id == "verificacao":
        runtime_records = [item for item in evidence if item.get("classification") == "RUNTIME"]
        if not runtime_records:
            errors.append("verification gate requires declared RUNTIME evidence")
        execution_records = [item for item in runtime_records
                             if item.get("role") != "masp-especialista-critico"
                             and not (item.get("model") == ASTRA_MODEL and "opinion" in item)
                             and ("command" in item or "exit_code" in item)]
        successful_execution = lambda item: (
            isinstance(item.get("command"), str) and item["command"].strip()
            and isinstance(item.get("exit_code"), int) and not isinstance(item.get("exit_code"), bool)
            and item["exit_code"] == 0
            and (bool(item.get("stdout")) or bool(item.get("stderr")))
        )
        failed_execution = [item for item in execution_records if not successful_execution(item)]
        if failed_execution:
            errors.append("verification gate cannot PASS: every test/command execution record must have exit_code 0")
        if not any(successful_execution(item) for item in execution_records):
            errors.append("verification gate requires at least one successful test/command execution record apart from Astra opinion")
    if phase_id == "conclusao":
        prior_phases = [item.get("name") for item in routing.get("phases", []) if item.get("name") != phase.get("name")]
        passed_phases = {event.get("phase") for event in prior_events
                         if isinstance(event, dict) and event.get("new_state") == "PASS"}
        missing_phases = [name for name in prior_phases if name not in passed_phases]
        if missing_phases:
            errors.append(f"conclusion requires preceding phase gates to PASS: {missing_phases}")
    if case.get("high_risk") and phase_id in {"verificacao", "conclusao"}:
        astra_ok, astra_contract_error = _astra_contract(routing)
        if not astra_ok:
            errors.append(astra_contract_error)
        if historical:
            if (not isinstance(astra_snapshot, dict) or astra_snapshot.get("model") != ASTRA_MODEL
                    or astra_snapshot.get("effort") != ASTRA_EFFORT
                    or astra_snapshot.get("available_at_transition") is not True):
                errors.append("historical Astra model availability snapshot is missing or invalid")
        elif not _astra_current_available(routing):
            errors.append(f"BLOCKED: required Astra model {ASTRA_MODEL} is unavailable; no audit substitution is made")
        astra_role = routing.get("roles", {}).get("masp-especialista-critico", {})
        opinions = [item for item in evidence if
            item.get("role") == "masp-especialista-critico"
            and item.get("model") == astra_role.get("model") == ASTRA_MODEL
            and item.get("effort") == astra_role.get("effort") == ASTRA_EFFORT
            and isinstance(item.get("opinion"), str) and item.get("opinion") in {"PASS", "APPROVED"}
            and item.get("classification") == "RUNTIME"
            and isinstance(item.get("command"), str) and item["command"].strip()
            and isinstance(item.get("exit_code"), int)
            and not isinstance(item.get("exit_code"), bool) and item["exit_code"] == 0
            and (bool(item.get("stdout")) or bool(item.get("stderr")))
        ]
        if not opinions:
            errors.append("high-risk gate requires a declared RUNTIME Astra opinion with command and result; the claim is not authenticated")
        escalation = routing.get("policies", {}).get("astra_escalation", {})
        required_record = escalation.get("required_record")
        if not isinstance(required_record, list) or not required_record or any(not isinstance(key, str) or not key.strip() for key in required_record):
            errors.append("routing matrix astra_escalation.required_record must declare required fields")
        elif opinions:
            known_evidence_ids = set()
            for event in prior_events:
                if not isinstance(event, dict):
                    continue
                prior_evidence = event.get("evidence")
                if not isinstance(prior_evidence, list):
                    continue
                known_evidence_ids.update(item["id"] for item in prior_evidence
                                          if isinstance(item, dict) and isinstance(item.get("id"), str))
            known_evidence_ids.update(item.get("id") for item in evidence if isinstance(item.get("id"), str))
            for field in required_record:
                if field not in {"astra_reason", "related_evidence", "coordinator_decision"}:
                    errors.append(f"unsupported Astra required_record field {field!r}")
                    continue
                value = opinions[0].get(field)
                if field == "related_evidence":
                    if not isinstance(value, list) or not value or any(not isinstance(item, str) or item not in known_evidence_ids or item == opinions[0].get("id") for item in value):
                        errors.append("Astra related_evidence must be a non-empty list of existing, related evidence IDs")
                elif not isinstance(value, str) or not value.strip():
                    errors.append(f"Astra {field} must be non-empty")
    return errors


def transition_case(
    case: dict[str, Any],
    target_state: str,
    actor: str,
    evidence: list[dict[str, Any]],
    routing: dict[str, Any],
    *,
    phase: str | None = None,
    required_classification: str | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    """Return a simulated state transition after schema, evidence and gate checks.

    `actor` and evidence role/model labels are untrusted descriptions, not identities.
    """
    evidence_root = Path(root or Path.cwd()).resolve()
    existing_errors = validate_case(case, routing, evidence_root)
    if existing_errors:
        raise ValueError("existing case failed replay validation: " + "; ".join(existing_errors))
    if actor != "masp-coordenador":
        raise ValueError("actor must be labeled masp-coordenador in this simulation; identity is not authenticated")
    if target_state not in STATES:
        raise ValueError(f"invalid state {target_state!r}")
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("each transition requires at least one evidence reference")
    evidence_errors = validate_evidence(evidence, evidence_root)
    if evidence_errors:
        raise ValueError("; ".join(evidence_errors))
    target_phase = phase or case.get("current_phase")
    phase_data = _phase(routing, target_phase)
    current_phase = case.get("current_phase")
    current_state = case.get("state")
    phase_names = [item.get("name") for item in routing["phases"]]
    if target_phase != current_phase:
        previous_index = phase_names.index(current_phase) if current_phase in phase_names else -1
        failed_phase = _phase(routing, current_phase)
        valid_return = current_state == "FAIL" and target_phase in failed_phase.get("returns", [])
        if valid_return:
            target_index = phase_names.index(target_phase) if target_phase in phase_names else len(phase_names)
            valid_return = target_index < previous_index
        valid_next = (
            current_state == "PASS" and previous_index >= 0
            and previous_index + 1 < len(phase_names)
            and phase_names[previous_index + 1] == target_phase
            and target_state == "IN_PROGRESS"
        )
        if not (valid_return or valid_next):
            raise ValueError(f"illegal phase jump to {target_phase!r}")
    if current_state == "BLOCKED":
        raise ValueError("BLOCKED case cannot advance without an explicit, separately recorded resolution")
    if target_state not in ALLOWED_TRANSITIONS.get(current_state, set()):
        raise ValueError(f"illegal state transition {current_state!r} -> {target_state!r}")
    if target_state == "IN_PROGRESS":
        available, model_or_error = _role_available(routing, phase_data)
        if not available:
            raise ValueError(model_or_error)
        if case.get("high_risk") and phase_data.get("id") == "verificacao":
            astra_ok, astra_error = _astra_contract(routing)
            if not astra_ok or not _astra_current_available(routing):
                raise ValueError(astra_error if not astra_ok else f"BLOCKED: required Astra model {ASTRA_MODEL} is unavailable; no audit substitution is made")
        if phase_data.get("id") == "acao" and not _plan_approval_recorded(case, case.get("ledger", [])):
            raise ValueError("Action cannot start until the plan gate records a simulated approval")
    if target_state == "PASS":
        gate_errors = _gate_errors(case, phase_data, evidence, routing, case.get("ledger", []), required_classification)
        if gate_errors:
            raise ValueError("; ".join(gate_errors))

    result = json.loads(json.dumps(case, ensure_ascii=False))
    if result.get("schema_version") == 1:
        result["schema_version"] = 2
        result["genesis_hash"] = _genesis_hash(result)
    previous_hash = result["ledger"][-1]["event_hash"] if result["ledger"] else "0" * 64
    event = {
        "sequence": len(result["ledger"]) + 1,
        "phase": target_phase,
        "previous_state": current_state,
        "new_state": target_state,
        "actor": actor,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "evidence": evidence,
        "model_snapshot": {
            "role": phase_data.get("role"),
            "model": routing.get("roles", {}).get(phase_data.get("role"), {}).get("model"),
            "effort": routing.get("roles", {}).get(phase_data.get("role"), {}).get("effort"),
            "available_at_transition": _role_available(routing, phase_data)[0],
        },
        "astra_snapshot": ({
            "model": routing.get("roles", {}).get("masp-especialista-critico", {}).get("model"),
            "effort": routing.get("roles", {}).get("masp-especialista-critico", {}).get("effort"),
            "available_at_transition": _astra_current_available(routing),
        } if case.get("high_risk") and phase_data.get("id") in {"verificacao", "conclusao"} else None),
        "classification": "SIMULATED",
        "previous_hash": previous_hash,
    }
    event["event_hash"] = _event_hash(event)
    result["ledger"].append(event)
    result["state"] = target_state
    result["current_phase"] = target_phase
    return result


def validate_case(case: dict[str, Any], routing: dict[str, Any], root: Path) -> list[str]:
    """Validate manifest genesis, replay every transition and verify referenced files."""
    if not isinstance(case, dict):
        return ["case must be an object"]
    errors: list[str] = []
    schema_version = case.get("schema_version")
    if schema_version == 1 and case.get("ledger"):
        errors.append("schema_version 1 ledgers require migration to version 2; recreate or explicitly migrate each event with historical model snapshots and evidence SHA-256 hashes")
    elif schema_version not in {1, 2}:
        errors.append(f"unsupported schema_version {schema_version!r}; create a version 2 case")
    if not isinstance(case.get("case_id"), str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{1,63}", case.get("case_id", "")):
        errors.append("case id is missing or invalid")
    if case.get("classification") != "SIMULATED":
        errors.append("case classification must remain SIMULATED; runtime provenance is not authenticated")
    phases = routing.get("phases", [])
    names = [phase.get("name") for phase in phases]
    if not names or case.get("origin_phase") != names[0]:
        errors.append("case origin phase must be the first routing phase")
    if not isinstance(case.get("high_risk"), bool):
        errors.append("high_risk must be a boolean")
    if case.get("genesis_hash") != _genesis_hash(case):
        errors.append("manifest genesis hash mismatch (origin or risk metadata changed)")
    state = case.get("initial_state")
    if state not in {"PENDING", "BLOCKED"}:
        errors.append("initial_state must be PENDING or BLOCKED")
    phase_name = case.get("origin_phase")
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
        try:
            calculated_event_hash = _event_hash(event)
        except (TypeError, ValueError, UnicodeError):
            calculated_event_hash = None
        if event.get("event_hash") != calculated_event_hash:
            errors.append(f"ledger event hash mismatch at event {index}")
        if event.get("classification") != "SIMULATED":
            errors.append(f"ledger event {index} must remain SIMULATED")
        if event.get("actor") != "masp-coordenador":
            errors.append(f"ledger event {index} has an actor label outside coordinator policy")
        if event.get("phase") not in names:
            errors.append(f"ledger event {index} references unknown phase")
            continue
        if event.get("previous_state") != state:
            errors.append(f"ledger replay state mismatch at event {index}")
        if event.get("phase") != phase_name:
            allowed = False
            if state == "PASS" and event.get("new_state") == "IN_PROGRESS":
                current_index = names.index(phase_name) if phase_name in names else -1
                allowed = current_index >= 0 and current_index + 1 < len(names) and names[current_index + 1] == event.get("phase")
            elif state == "FAIL":
                prior_phase = next((item for item in phases if item.get("name") == phase_name), {})
                current_index = names.index(phase_name) if phase_name in names else -1
                target_index = names.index(event.get("phase")) if event.get("phase") in names else len(names)
                allowed = (
                    event.get("phase") in prior_phase.get("returns", [])
                    and target_index < current_index
                    and event.get("new_state") in {"IN_PROGRESS", "BLOCKED", "NOT_RUN"}
                )
            if not allowed:
                errors.append(f"ledger replay phase order mismatch at event {index}")
        if event.get("new_state") not in ALLOWED_TRANSITIONS.get(state, set()):
            errors.append(f"ledger replay has illegal state transition at event {index}")
        try:
            phase_data = _phase(routing, event.get("phase"))
        except ValueError:
            phase_data = {}
        event_evidence = event.get("evidence", [])
        if not isinstance(event_evidence, list) or not event_evidence:
            errors.append(f"ledger event {index} must contain evidence")
        evidence_errors = validate_evidence(event_evidence, root)
        errors.extend(f"event {index}: {issue}" for issue in evidence_errors)
        if event.get("new_state") == "PASS" and phase_data and not evidence_errors:
            errors.extend(f"event {index}: {issue}" for issue in _gate_errors(
                case, phase_data, event_evidence, routing, ledger[:index - 1], historical=True,
                astra_snapshot=event.get("astra_snapshot")))
        if event.get("new_state") == "IN_PROGRESS" and phase_data:
            snapshot = event.get("model_snapshot")
            if (not isinstance(snapshot, dict) or snapshot.get("role") != phase_data.get("role")
                    or not isinstance(snapshot.get("model"), str) or not snapshot["model"]
                    or snapshot.get("effort") not in {"low", "medium", "high"}
                    or snapshot.get("available_at_transition") is not True):
                errors.append(f"event {index} has no valid historical model availability snapshot")
            if case.get("high_risk") and phase_data.get("id") == "verificacao":
                astra_ok, astra_error = _astra_contract(routing)
                astra_snapshot = event.get("astra_snapshot")
                if (not astra_ok or not isinstance(astra_snapshot, dict)
                        or astra_snapshot.get("model") != ASTRA_MODEL
                        or astra_snapshot.get("effort") != ASTRA_EFFORT
                        or astra_snapshot.get("available_at_transition") is not True):
                    errors.append(f"event {index}: {astra_error or 'historical Astra model availability snapshot is missing or invalid'}")
            if phase_data.get("id") == "acao" and not _plan_approval_recorded(case, ledger[:index - 1]):
                errors.append(f"event {index}: action started before plan approval gate")
        state = event.get("new_state") if event.get("new_state") in STATES else state
        phase_name = event.get("phase") if event.get("phase") in names else phase_name
        previous_hash = event.get("event_hash", "")
    if state != case.get("state") or phase_name != case.get("current_phase"):
        errors.append("case summary does not match ledger replay")
    return errors


def validate_parallel_tasks(
    tasks: list[dict[str, Any]],
    routing: dict[str, Any],
    *,
    root: Path | None = None,
    effective_limit: int | None = None,
) -> list[str]:
    """Reject overlapping writes, paths outside the workspace, and excess fan-out."""
    errors: list[str] = []
    workspace = Path(root or Path.cwd()).resolve()
    configured = routing.get("policies", {}).get("parallelism", {}).get("max_agents", 0)
    limit = min(configured, effective_limit) if isinstance(effective_limit, int) and effective_limit >= 0 else configured
    if not isinstance(tasks, list):
        return ["parallel tasks must be a list"]
    if len(tasks) > limit:
        errors.append(f"parallel task count exceeds effective limit {limit}")
    owners: dict[str, str] = {}
    for task in tasks:
        if not isinstance(task, dict) or not isinstance(task.get("writes", []), list):
            errors.append("each parallel task must be an object with a writes list")
            continue
        for raw_path in task.get("writes", []):
            if not isinstance(raw_path, str) or not raw_path.strip():
                errors.append(f"task {task.get('id', '<unknown>')} has an invalid write path")
                continue
            candidate = Path(raw_path)
            resolved = (candidate if candidate.is_absolute() else workspace / candidate).resolve()
            try:
                normalized = resolved.relative_to(workspace).as_posix().casefold()
            except ValueError:
                errors.append(f"write path {raw_path!r} escapes workspace root")
                continue
            if normalized in owners:
                errors.append(f"write conflict on {raw_path!r} between {owners[normalized]} and {task.get('id')}")
            else:
                owners[normalized] = task.get("id", "<unknown>")
    return errors
