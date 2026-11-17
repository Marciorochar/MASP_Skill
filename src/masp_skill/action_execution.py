"""Structural validation of universal MASP M05 action records.

Does not execute actions, authenticate human approvals, establish provenance
or grant PASS to Gate 05. All fields supplied by the caller remain untrusted.
"""
from __future__ import annotations

from typing import Any

VALID_EVIDENCE_CLASSES = {"STATIC", "SIMULATED", "RUNTIME", "NOT_RUN"}
TASK_STATUSES = {"performed", "partial", "not_run", "blocked", "failed"}
EXECUTION_KINDS = {"procedure", "command", "not_applicable"}
RESULT_STATUSES = {"observed", "failed", "inconclusive", "not_run"}
ROLLBACK_TYPES = {"reversible", "partial", "irreversible"}
ROLLBACK_STATUSES = {"performed", "not_run", "not_applicable", "failed"}


def _required(data: dict[str, Any], key: str, prefix: str, errors: list[str]) -> str | None:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{prefix}.{key} must be a nonempty string")
        return None
    return value


def _choice(data: dict[str, Any], key: str, choices: set[str], prefix: str,
            errors: list[str]) -> str | None:
    value = data.get(key)
    if not isinstance(value, str) or value not in choices:
        errors.append(f"{prefix}.{key} must be one of {sorted(choices)}")
        return None
    return value


def _object(value: Any, prefix: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{prefix} must be an object")
        return {}
    return value


def _reference(data: dict[str, Any], key: str, known: set[str], prefix: str,
               errors: list[str]) -> None:
    value = _required(data, key, prefix, errors)
    if value and value not in known:
        errors.append(f"{prefix}.{key} references undeclared evidence {value}")


def validate_action_execution_record(record: Any) -> list[str]:
    """Return declared-structure errors without verifying external truth or authority."""
    if not isinstance(record, dict):
        return ["action execution record must be an object"]
    errors: list[str] = []
    for name in ("case_id", "plan_reference", "plan_version",
                 "baseline_reference", "approved_scope", "executor_id", "verifier_id"):
        _required(record, name, "record", errors)

    executor = record.get("executor_id")
    verifier = record.get("verifier_id")
    if isinstance(executor, str) and executor.strip() and executor == verifier:
        errors.append("verifier_id must differ from executor_id; independent verification is not authenticated")

    approval = _object(record.get("approval"), "approval", errors)
    approval_status = _choice(approval, "status", {"approved", "pending", "rejected"}, "approval", errors)
    if approval_status == "approved":
        approver = _required(approval, "approver_id", "approval", errors)
        _required(approval, "approval_reference", "approval", errors)
        version = _required(approval, "plan_version", "approval", errors)
        scope = _required(approval, "scope", "approval", errors)
        if approver and approver == executor:
            errors.append("approval approver_id must differ from executor_id: no self approval")
        if version and version != record.get("plan_version"):
            errors.append("approval plan_version mismatch")
        if scope and scope != record.get("approved_scope"):
            errors.append("approval scope mismatch")

    environment = _object(record.get("environment"), "environment", errors)
    for name in ("type", "isolation"):
        _required(environment, name, "environment", errors)

    raw_evidence = record.get("evidence")
    if not isinstance(raw_evidence, list) or not raw_evidence:
        errors.append("evidence must be a nonempty array")
        raw_evidence = []
    known: set[str] = set()
    for i, entry in enumerate(raw_evidence):
        prefix = f"evidence[{i}]"
        item = _object(entry, prefix, errors)
        identifier = _required(item, "id", prefix, errors)
        _choice(item, "classification", VALID_EVIDENCE_CLASSES, prefix, errors)
        if identifier:
            if identifier in known:
                errors.append(f"duplicate evidence ID {identifier}")
            known.add(identifier)
    _reference(environment, "evidence_id", known, "environment", errors)

    raw_tasks = record.get("tasks")
    if not isinstance(raw_tasks, list) or not raw_tasks:
        errors.append("tasks must be a nonempty array")
        raw_tasks = []
    ids: set[str] = set()
    for i, raw in enumerate(raw_tasks):
        prefix = f"tasks[{i}]"
        task = _object(raw, prefix, errors)
        identifier = _required(task, "id", prefix, errors)
        _required(task, "plan_task_id", prefix, errors)
        if identifier:
            if identifier in ids:
                errors.append(f"duplicate task ID {identifier}")
            ids.add(identifier)
        status = _choice(task, "status", TASK_STATUSES, prefix, errors)
        _required(task, "deviation", prefix, errors)
        before = _object(task.get("before"), prefix + ".before", errors)
        after = _object(task.get("after"), prefix + ".after", errors)
        execution = _object(task.get("execution"), prefix + ".execution", errors)
        result = _object(task.get("result"), prefix + ".result", errors)
        rollback = _object(task.get("rollback"), prefix + ".rollback", errors)
        kind = _choice(execution, "kind", EXECUTION_KINDS, prefix + ".execution", errors)
        result_status = _choice(result, "status", RESULT_STATUSES, prefix + ".result", errors)
        rollback_type = _choice(rollback, "type", ROLLBACK_TYPES, prefix + ".rollback", errors)
        rollback_status = _choice(rollback, "status", ROLLBACK_STATUSES,
                                  prefix + ".rollback", errors)
        if rollback_type == "irreversible" and rollback_status == "performed":
            errors.append(f"{prefix}.rollback cannot claim performed rollback for irreversible change")
        if status in {"performed", "partial", "failed"}:
            if approval_status != "approved":
                errors.append(f"{prefix} claimed execution without approved approval reference")
            for section, value in (("before", before), ("after", after),
                                   ("execution", execution), ("result", result)):
                _required(value, "description", prefix + "." + section, errors)
                _reference(value, "evidence_id", known, prefix + "." + section, errors)
            if kind == "not_applicable":
                errors.append(f"{prefix}.execution cannot be not_applicable for performed activity")
            if result_status == "not_run":
                errors.append(f"{prefix}.result not_run contradicts performed activity")
        if status in {"not_run", "blocked"}:
            if result_status != "not_run":
                errors.append(f"{prefix}.status {status} cannot claim an observed result: not_run expected")
            if rollback_status == "performed":
                errors.append(f"{prefix}.rollback cannot be performed when task not_run or blocked")
    return errors
