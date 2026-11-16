"""Structural validation of a MASP universal action-plan sidecar.

Checks only declarations and cross-references. Does NOT authenticate approval,
confirm plan viability, prove risk controls, execute actions or pass Gate 04.
"""
from __future__ import annotations

from typing import Any


ANALYSIS_STATUSES = {"supported", "inconclusive"}
INTERVENTION_TYPES = {"corrective", "investigative", "containment", "protective", "monitoring"}
COST_STATUSES = {"known", "unknown"}
BASELINE_TYPES = {"known", "unavailable"}
ROLLBACK_TYPES = {"reversible", "partial", "irreversible"}
APPROVAL_STATUSES = {"pending", "approved", "rejected"}


def _text(obj: dict[str, Any], field: str, where: str, errors: list[str]) -> str | None:
    value = obj.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{where}.{field} must be a nonempty string")
        return None
    return value


def _enum(obj: dict[str, Any], field: str, allowed: set[str], where: str,
          errors: list[str]) -> str | None:
    value = obj.get(field)
    if not isinstance(value, str) or value not in allowed:
        errors.append(f"{where}.{field} must be one of {sorted(allowed)}")
        return None
    return value


def _array(record: dict[str, Any], key: str, errors: list[str],
           *, nonempty: bool = True) -> list[Any]:
    value = record.get(key)
    if not isinstance(value, list) or (nonempty and not value):
        errors.append(f"{key} must be {'nonempty ' if nonempty else ''}array")
        return []
    return value


def _strings(value: Any, where: str, errors: list[str],
             *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{where} must be an array of nonempty strings")
        return []
    if nonempty and not value:
        errors.append(f"{where} must not be empty")
    data = [v for v in value if isinstance(v, str) and v.strip()]
    if len(data) != len(value):
        errors.append(f"{where} entries must be nonempty strings")
    if len(data) != len(set(data)):
        errors.append(f"{where} has duplicate values")
    return data


def _ref(values: list[str], known: set[str], where: str, errors: list[str]) -> None:
    for value in values:
        if value not in known:
            errors.append(f"{where} references undeclared ID {value}")


def _members(data: list[Any], label: str, errors: list[str]) -> list[dict[str, Any]]:
    valid = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            errors.append(f"{label}[{i}] must be an object")
        else:
            valid.append(item)
    return valid


def _id_catalog(items: list[dict[str, Any]], label: str,
                errors: list[str]) -> set[str]:
    result: set[str] = set()
    for i, item in enumerate(items):
        value = _text(item, "id", f"{label}[{i}]", errors)
        if value:
            if value in result:
                errors.append(f"duplicate {label[:-1]} ID {value}")
            result.add(value)
    return result


def validate_action_plan_record(record: Any) -> list[str]:
    """Check a JSON plan's declared structure, not external authorization."""
    if not isinstance(record, dict):
        return ["action plan record must be an object"]
    errors: list[str] = []

    for key in ("case_id", "problem_reference", "analysis_reference", "plan_objective"):
        _text(record, key, "plan", errors)
    analysis_status = _enum(record, "analysis_status", ANALYSIS_STATUSES, "plan", errors)

    scope = record.get("scope")
    if not isinstance(scope, dict):
        errors.append("scope must be an object with explicit included/excluded limits")
    else:
        _text(scope, "included", "scope", errors)
        _text(scope, "excluded", "scope", errors)

    owners = _members(_array(record, "owners", errors), "owners", errors)
    owner_ids = _id_catalog(owners, "owners", errors)
    for i, owner in enumerate(owners):
        _text(owner, "role", f"owners[{i}]", errors)

    alternatives = _members(_array(record, "alternatives", errors), "alternatives", errors)
    alt_ids = _id_catalog(alternatives, "alternatives", errors)
    alt_types: dict[str, str] = {}
    for i, alt in enumerate(alternatives):
        where = f"alternatives[{i}]"
        for key in ("description", "rationale", "evidence_reference",
                    "feasibility", "selection_rationale"):
            _text(alt, key, where, errors)
        kind = _enum(alt, "intervention_type", INTERVENTION_TYPES, where, errors)
        if isinstance(alt.get("id"), str) and kind:
            alt_types[alt["id"]] = kind

    selected = _strings(record.get("selected_actions"), "selected_actions", errors, nonempty=True)
    _ref(selected, alt_ids, "selected_actions", errors)
    selected_ids = set(selected)
    if analysis_status == "inconclusive":
        for aid in selected:
            if alt_types.get(aid) == "corrective":
                errors.append("plan.analysis_status inconclusive cannot select definitive corrective intervention")

    tasks = _members(_array(record, "tasks", errors), "tasks", errors)
    task_ids = _id_catalog(tasks, "tasks", errors)
    chosen_with_tasks: set[str] = set()
    for i, task in enumerate(tasks):
        where = f"tasks[{i}]"
        alternative = _text(task, "alternative_id", where, errors)
        if alternative and alternative not in selected_ids:
            errors.append(f"{where}.alternative_id must reference a selected action")
        if alternative:
            chosen_with_tasks.add(alternative)
        for key in ("what", "why", "where", "when", "how", "expected_result"):
            _text(task, key, where, errors)
        who = _text(task, "who", where, errors)
        if who and who not in owner_ids:
            errors.append(f"{where}.who must reference a declared owner")
        deps = _strings(task.get("dependencies"), f"{where}.dependencies", errors)
        _ref(deps, task_ids, f"{where}.dependencies", errors)
        if task.get("id") in deps:
            errors.append(f"{where}.dependencies must not include itself")
        cost = task.get("how_much")
        if not isinstance(cost, dict):
            errors.append(f"{where}.how_much must be an object")
        else:
            state = _enum(cost, "status", COST_STATUSES, f"{where}.how_much", errors)
            if state == "known":
                _text(cost, "details", f"{where}.how_much", errors)
            elif state == "unknown":
                _text(cost, "reason", f"{where}.how_much", errors)
    for aid in selected:
        if aid in alt_ids and aid not in chosen_with_tasks:
            errors.append(f"selected_actions {aid} has no planned task")

    risks = _members(_array(record, "risks", errors), "risks", errors)
    _id_catalog(risks, "risks", errors)
    risk_tasks: set[str] = set()
    for i, risk in enumerate(risks):
        where = f"risks[{i}]"
        target = _text(risk, "task_id", where, errors)
        if target:
            risk_tasks.add(target)
            _ref([target], task_ids, f"{where}.task_id", errors)
        for key in ("description", "preventive_control", "mitigation",
                    "stop_condition", "residual_risk"):
            _text(risk, key, where, errors)

    rollback = _members(_array(record, "rollback", errors), "rollback", errors)
    rollback_tasks: set[str] = set()
    for i, item in enumerate(rollback):
        where = f"rollback[{i}]"
        target = _text(item, "task_id", where, errors)
        if target:
            if target in rollback_tasks:
                errors.append(f"duplicate rollback task_id {target}")
            rollback_tasks.add(target)
            _ref([target], task_ids, f"{where}.task_id", errors)
        owner = _text(item, "owner_id", where, errors)
        if owner and owner not in owner_ids:
            errors.append(f"{where}.owner_id must reference a declared owner")
        _text(item, "trigger", where, errors)
        kind = _enum(item, "type", ROLLBACK_TYPES, where, errors)
        if kind == "reversible":
            for key in ("procedure", "verification"):
                _text(item, key, where, errors)
        elif kind == "partial":
            for key in ("procedure", "verification", "contingency", "irreversible_stage"):
                _text(item, key, where, errors)
        elif kind == "irreversible":
            for key in ("justification", "point_of_no_return",
                        "stop_before_point", "contingency"):
                _text(item, key, where, errors)

    tests = _members(_array(record, "tests", errors), "tests", errors)
    _id_catalog(tests, "tests", errors)
    test_tasks: set[str] = set()
    for i, test in enumerate(tests):
        where = f"tests[{i}]"
        target = _text(test, "task_id", where, errors)
        if target:
            test_tasks.add(target)
            _ref([target], task_ids, f"{where}.task_id", errors)
        for key in ("indicator", "method", "expected_result",
                    "acceptance", "failure", "stop_condition"):
            _text(test, key, where, errors)
        owner = _text(test, "verification_owner_id", where, errors)
        if owner and owner not in owner_ids:
            errors.append(f"{where}.verification_owner_id must reference a declared owner")
        baseline = test.get("baseline")
        if not isinstance(baseline, dict):
            errors.append(f"{where}.baseline must be an object")
        else:
            kind = _enum(baseline, "type", BASELINE_TYPES, f"{where}.baseline", errors)
            if kind == "known":
                _text(baseline, "description", f"{where}.baseline", errors)
                _text(baseline, "source", f"{where}.baseline", errors)
            elif kind == "unavailable":
                _text(baseline, "reason", f"{where}.baseline", errors)
                _text(baseline, "collection_needed", f"{where}.baseline", errors)
        if "result" in test or "executed" in test or "execution_status" in test:
            errors.append(f"{where}.result is execution evidence, not a plan; record in later phases")

    for tid in task_ids:
        if tid not in risk_tasks:
            errors.append(f"risks missing for task {tid}")
        if tid not in rollback_tasks:
            errors.append(f"rollback missing for task {tid}")
        if tid not in test_tasks:
            errors.append(f"tests missing for task {tid}")

    approval = record.get("human_approval")
    if not isinstance(approval, dict):
        errors.append("human_approval must be an object")
    else:
        status = _enum(approval, "status", APPROVAL_STATUSES, "human_approval", errors)
        if status == "approved":
            for key in ("approved_by", "approval_reference", "approved_scope", "approved_at"):
                _text(approval, key, "human_approval", errors)
        elif status in {"pending", "rejected"}:
            _text(approval, "reason", "human_approval", errors)
            if any(k in approval for k in
                   ("approved_by", "approval_reference", "approved_at", "approved_scope")):
                errors.append("human_approval pending/rejected must not claim an approver or approval reference")

    if "limitations" in record:
        _strings(record["limitations"], "limitations", errors)
    return errors
