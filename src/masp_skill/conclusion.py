"""M08 conclusion record structural checks; no authenticated closure or gate PASS."""
from __future__ import annotations

from typing import Any

PHASES = ("identificacao", "observacao", "analise", "plano-de-acao",
          "acao", "verificacao", "padronizacao")
EVIDENCE_CLASSES = {"STATIC", "SIMULATED", "RUNTIME", "NOT_RUN"}
OBJECTIVE_STATUSES = {"achieved", "partially_achieved", "not_achieved",
                      "inconclusive", "not_evaluated"}
RESOLUTIONS = {"demonstrated", "partial", "inconclusive", "unfavorable"}
CLOSURES = {"complete", "with_reservations", "blocked", "not_run"}
LEDGER_STATES = {"complete", "incomplete"}
AUDIT_STATES = {"supported", "qualified", "blocked", "not_run"}


def _text(record: dict, field: str, where: str, errors: list[str]) -> str | None:
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{where}.{field} must be nonempty text")
        return None
    return value


def _enum(record: dict, field: str, options: set[str], where: str,
          errors: list[str]) -> str | None:
    value = record.get(field)
    if not isinstance(value, str) or value not in options:
        errors.append(f"{where}.{field} must be one of {sorted(options)}")
        return None
    return value


def _obj(value: Any, where: str, errors: list[str]) -> dict:
    if not isinstance(value, dict):
        errors.append(f"{where} must be an object")
        return {}
    return value


def validate_conclusion_record(record: Any) -> list[str]:
    """Reject contradictory declarations; never authenticate the evidence."""
    if not isinstance(record, dict):
        return ["conclusion record must be an object"]
    errors: list[str] = []
    for name in ("case_id", "case_revision", "author_id"):
        _text(record, name, "record", errors)
    resolution = _enum(record, "resolution_status", RESOLUTIONS, "record", errors)
    _enum(record, "closure_type", {"technical", "administrative"}, "record", errors)
    decision = _enum(record, "closure_decision", CLOSURES, "record", errors)

    evidence = record.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("evidence must be a nonempty array")
        evidence = []
    known: set[str] = set()
    for i, raw in enumerate(evidence):
        item = _obj(raw, f"evidence[{i}]", errors)
        key = _text(item, "id", f"evidence[{i}]", errors)
        _enum(item, "classification", EVIDENCE_CLASSES, f"evidence[{i}]", errors)
        if key:
            if key in known:
                errors.append(f"duplicate evidence ID {key}")
            known.add(key)

    def source(item: dict, key: str, where: str) -> None:
        value = _text(item, key, where, errors)
        if value and value not in known:
            errors.append(f"{where}.{key} references undeclared evidence")

    ledger = _obj(record.get("complete_ledger"), "complete_ledger", errors)
    ledger_status = _enum(ledger, "status", LEDGER_STATES, "complete_ledger", errors)
    _text(ledger, "reference", "complete_ledger", errors)
    phase_states = ledger.get("phase_states")
    if not isinstance(phase_states, dict):
        errors.append("complete_ledger.phase_states must be an object")
        phase_states = {}
    for phase in PHASES:
        value = phase_states.get(phase)
        if not isinstance(value, str) or value not in {"PASS", "FAIL", "BLOCKED", "PENDING", "IN_PROGRESS", "NOT_RUN"}:
            errors.append(f"complete_ledger.phase_states.{phase} invalid or missing")
    if set(phase_states) != set(PHASES):
        errors.append("complete_ledger.phase_states must contain exactly seven prior MASP phases")
    if ledger_status == "complete" and any(phase_states.get(p) != "PASS" for p in PHASES):
        errors.append("complete_ledger.status complete conflicts with incomplete prior phase gate")

    results = record.get("results")
    if not isinstance(results, list) or not results:
        errors.append("results must be a nonempty array")
        results = []
    objective_statuses: list[str | None] = []
    for i, raw in enumerate(results):
        item = _obj(raw, f"results[{i}]", errors)
        for field in ("objective_reference", "expected", "observed"):
            _text(item, field, f"results[{i}]", errors)
        status = _enum(item, "status", OBJECTIVE_STATUSES, f"results[{i}]", errors)
        objective_statuses.append(status)
        source(item, "evidence_reference", f"results[{i}]")
    if resolution == "demonstrated" and any(s != "achieved" for s in objective_statuses):
        errors.append("resolution_status demonstrated contradicts non-achieved or not-evaluated objective")

    limitations = record.get("limitations")
    if not isinstance(limitations, list) or not limitations or any(
            not isinstance(x, str) or not x.strip() for x in limitations):
        errors.append("limitations must be a nonempty array of observations")

    residual_risks = record.get("residual_risks")
    if not isinstance(residual_risks, list):
        errors.append("residual_risks must be an array, including [] if evaluated absent")
        residual_risks = []
    risks: set[str] = set()
    for i, raw in enumerate(residual_risks):
        item = _obj(raw, f"residual_risks[{i}]", errors)
        key = _text(item, "id", f"residual_risks[{i}]", errors)
        for field in ("description", "owner_id"):
            _text(item, field, f"residual_risks[{i}]", errors)
        source(item, "evidence_reference", f"residual_risks[{i}]")
        if key:
            if key in risks:
                errors.append(f"duplicate residual_risks ID {key}")
            risks.add(key)

    pending = record.get("pending_items")
    if not isinstance(pending, list):
        errors.append("pending_items must be an array, even when empty")
        pending = []
    critical = False
    for i, raw in enumerate(pending):
        item = _obj(raw, f"pending_items[{i}]", errors)
        for field in ("id", "description", "owner_id"):
            _text(item, field, f"pending_items[{i}]", errors)
        if not isinstance(item.get("critical"), bool):
            errors.append(f"pending_items[{i}].critical must be boolean")
        if item.get("critical") is True:
            critical = True

    audit = _obj(record.get("audit_opinion"), "audit_opinion", errors)
    audit_status = _enum(audit, "status", AUDIT_STATES, "audit_opinion", errors)
    reviewer = _text(audit, "reviewer_id", "audit_opinion", errors)
    if reviewer and reviewer == record.get("author_id"):
        errors.append("audit_opinion.reviewer_id must be independent from report author")
    source(audit, "evidence_reference", "audit_opinion")

    if decision == "complete":
        if ledger_status != "complete" or any(phase_states.get(p) != "PASS" for p in PHASES):
            errors.append("complete closure requires complete_ledger with prior PASS states")
        if critical:
            errors.append("complete closure cannot ignore critical pending_items")
        if audit_status != "supported":
            errors.append("complete closure requires supported audit_opinion")
        if resolution != "demonstrated":
            errors.append("complete closure cannot imply problem resolved without demonstrated results")
    return errors
