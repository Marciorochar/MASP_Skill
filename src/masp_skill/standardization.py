"""M07 STATIC standardization checks. Does not approve operational adoption."""
from __future__ import annotations

from typing import Any

DOCUMENT_STATES = {"DRAFT", "UNDER_REVIEW", "APPROVED", "ACTIVE", "SUSPENDED", "OBSOLETE"}
VERIFICATION = {"demonstrated", "partial", "inconclusive", "not_demonstrated", "not_run"}
IMPLEMENTATION = {"not_run", "planned", "implemented"}
CONTROL_TYPES = {"preventive", "detective", "mitigating", "monitoring"}
EVIDENCE = {"STATIC", "SIMULATED", "RUNTIME", "NOT_RUN"}


def _text(data: dict, key: str, name: str, errors: list[str]) -> str | None:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{name}.{key} must be nonempty text")
        return None
    return value


def _enum(data: dict, key: str, options: set[str], name: str,
          errors: list[str]) -> str | None:
    value = data.get(key)
    if not isinstance(value, str) or value not in options:
        errors.append(f"{name}.{key} must be one of {sorted(options)}")
        return None
    return value


def _obj(value: Any, name: str, errors: list[str]) -> dict:
    if not isinstance(value, dict):
        errors.append(f"{name} must be an object")
        return {}
    return value


def validate_standardization_record(record: Any) -> list[str]:
    """Check declared relationships, not real verification, approval or sustainability."""
    if not isinstance(record, dict):
        return ["standardization record must be an object"]
    errors: list[str] = []
    for field in ("case_id", "verification_reference", "standard_id",
                  "standard_version", "applicability", "exclusions", "owner_id"):
        _text(record, field, "standard", errors)
    verified = _enum(record, "verification_status", VERIFICATION, "standard", errors)
    state = _enum(record, "document_status", DOCUMENT_STATES, "standard", errors)
    implementation = _enum(record, "implementation_status", IMPLEMENTATION, "standard", errors)

    evidence = record.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("evidence must be a nonempty array")
        evidence = []
    known: set[str] = set()
    for i, raw in enumerate(evidence):
        item = _obj(raw, f"evidence[{i}]", errors)
        key = _text(item, "id", f"evidence[{i}]", errors)
        _enum(item, "classification", EVIDENCE, f"evidence[{i}]", errors)
        if key:
            if key in known:
                errors.append(f"duplicate evidence ID {key}")
            known.add(key)

    def ref(data: dict, key: str, name: str) -> None:
        value = _text(data, key, name, errors)
        if value and value not in known:
            errors.append(f"{name}.{key} references undeclared evidence")

    control = _obj(record.get("preventive_control"), "preventive_control", errors)
    for field in ("id", "description", "cause_reference"):
        _text(control, field, "preventive_control", errors)
    _enum(control, "type", CONTROL_TYPES, "preventive_control", errors)

    trigger = _obj(record.get("trigger"), "trigger", errors)
    for field in ("event", "detection", "reaction", "owner_id"):
        _text(trigger, field, "trigger", errors)
    if trigger.get("owner_id") and trigger.get("owner_id") != record.get("owner_id"):
        errors.append("trigger.owner_id must match standard owner_id")

    regression = _obj(record.get("regression"), "regression", errors)
    for field in ("method", "criterion"):
        _text(regression, field, "regression", errors)
    _enum(regression, "status", {"planned", "performed", "not_run"}, "regression", errors)
    ref(regression, "evidence_reference", "regression")

    monitoring = _obj(record.get("monitoring"), "monitoring", errors)
    for field in ("indicator", "cadence"):
        _text(monitoring, field, "monitoring", errors)
    ref(monitoring, "source_reference", "monitoring")

    training = _obj(record.get("training"), "training", errors)
    required = training.get("required")
    if not isinstance(required, bool):
        errors.append("training.required must be boolean")
    _enum(training, "status", {"not_required", "planned", "completed", "not_run"},
          "training", errors)
    if training.get("status") == "completed":
        ref(training, "completion_evidence_reference", "training")
    if required is True and training.get("status") == "not_required":
        errors.append("training required cannot be not_required")

    approval = _obj(record.get("approval"), "approval", errors)
    approval_status = _enum(approval, "status", {"pending", "approved", "rejected"},
                            "approval", errors)
    if approval_status == "approved":
        _text(approval, "approval_reference", "approval", errors)

    if state in {"APPROVED", "ACTIVE"}:
        if verified != "demonstrated":
            errors.append("verification_status must be demonstrated for finalized standard")
        if approval_status != "approved":
            errors.append("approval required for finalized standard")
    if state == "ACTIVE":
        if implementation != "implemented":
            errors.append("ACTIVE standard requires implementation_status implemented")
        ref(record, "implementation_evidence_reference", "standard")
    if state == "OBSOLETE" and implementation == "implemented":
        errors.append("OBSOLETE standard cannot claim current implementation")
    if implementation == "implemented" and state not in {"ACTIVE", "SUSPENDED"}:
        errors.append("implementation_status implemented must be ACTIVE or SUSPENDED")
    return errors
