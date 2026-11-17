"""STATIC-only verification of universal M06 records; all input claims are untrusted."""
from __future__ import annotations

import math
from typing import Any

KINDS = {"quantitative", "qualitative", "unavailable"}
CLAIMS = {"demonstrated", "partial", "inconclusive", "not_demonstrated", "not_run"}
STATUSES = {"met", "not_met", "inconclusive", "not_run"}
REVIEWS = {"completed", "not_run", "blocked"}
EVIDENCE = {"STATIC", "SIMULATED", "RUNTIME", "NOT_RUN"}


def _text(data: dict, field: str, where: str, errors: list[str]) -> str | None:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{where}.{field} must be a nonempty string")
        return None
    return value


def _enum(data: dict, field: str, values: set[str], where: str,
          errors: list[str]) -> str | None:
    value = data.get(field)
    if not isinstance(value, str) or value not in values:
        errors.append(f"{where}.{field} must be one of {sorted(values)}")
        return None
    return value


def _object(value: Any, where: str, errors: list[str]) -> dict:
    if not isinstance(value, dict):
        errors.append(f"{where} must be an object")
        return {}
    return value


def compare_quantitative(before: float, after: float) -> tuple[float, float | None]:
    """Reduction before-after; undefined percentage for a zero baseline."""
    if isinstance(before, bool) or isinstance(after, bool):
        raise ValueError("boolean is not a number")
    before, after = float(before), float(after)
    if not math.isfinite(before) or not math.isfinite(after):
        raise ValueError("finite measurements required")
    reduction = before - after
    return reduction, (reduction / abs(before) * 100 if before else None)


def validate_verification_record(record: Any) -> list[str]:
    """Validate structure, not causal efficacy, authentic provenance or gate PASS."""
    if not isinstance(record, dict):
        return ["verification record must be an object"]
    errors: list[str] = []
    for field in ("case_id", "action_reference", "objective_reference",
                  "executor_id", "reviewer_id"):
        _text(record, field, "record", errors)
    if isinstance(record.get("executor_id"), str) and record["executor_id"] == record.get("reviewer_id"):
        errors.append("reviewer_id must differ from executor_id")

    known: set[str] = set()
    evidence = record.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("evidence must be a nonempty array")
        evidence = []
    for i, raw in enumerate(evidence):
        item = _object(raw, f"evidence[{i}]", errors)
        key = _text(item, "id", f"evidence[{i}]", errors)
        _enum(item, "classification", EVIDENCE, f"evidence[{i}]", errors)
        if key:
            if key in known:
                errors.append(f"duplicate evidence ID {key}")
            known.add(key)

    def check_ref(item: dict, field: str, label: str) -> None:
        value = _text(item, field, label, errors)
        if value and value not in known:
            errors.append(f"{label}.{field} references undeclared evidence")

    baseline = _object(record.get("baseline"), "baseline", errors)
    after = _object(record.get("after"), "after", errors)
    kind_before = _enum(baseline, "kind", KINDS, "baseline", errors)
    kind_after = _enum(after, "kind", KINDS, "after", errors)
    for name, item, kind in (("baseline", baseline, kind_before),
                            ("after", after, kind_after)):
        if kind == "unavailable":
            _text(item, "reason", name, errors)
        elif kind in {"quantitative", "qualitative"}:
            _text(item, "method", name, errors)
            check_ref(item, "source_reference", name)
            if kind == "qualitative":
                _text(item, "description", name, errors)
            else:
                _text(item, "unit", name, errors)
                value = item.get("value")
                try:
                    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                        raise ValueError()
                except (ValueError, TypeError, OverflowError):
                    errors.append(f"{name}.value must be a finite number")

    comparison = _enum(record, "comparison_status", {"comparable", "incomparable", "unavailable"},
                       "record", errors)
    if comparison == "comparable":
        if kind_before == "unavailable" or kind_after == "unavailable":
            errors.append("comparison cannot be comparable without baseline and after")
        if kind_before != kind_after:
            errors.append("comparison kind mismatch")
        if kind_before in {"qualitative", "quantitative"} and kind_before == kind_after:
            if baseline.get("method") != after.get("method"):
                errors.append("comparison method mismatch")
            if kind_before == "quantitative" and baseline.get("unit") != after.get("unit"):
                errors.append("comparison unit mismatch")
    if "percent_change" in record and kind_before == "quantitative" and baseline.get("value") == 0:
        errors.append("percent_change undefined for baseline zero")

    acceptance = _object(record.get("acceptance"), "acceptance", errors)
    _text(acceptance, "criterion", "acceptance", errors)
    result = _enum(acceptance, "status", STATUSES, "acceptance", errors)
    claim = _enum(record, "effectiveness_claim", CLAIMS, "record", errors)

    regression = record.get("regressions")
    if not isinstance(regression, list) or not regression:
        errors.append("regressions must be a nonempty array")
        regression = []
    rids: set[str] = set()
    rstatus: list[str | None] = []
    for i, raw in enumerate(regression):
        item = _object(raw, f"regressions[{i}]", errors)
        identifier = _text(item, "id", f"regressions[{i}]", errors)
        state = _enum(item, "status", {"pass", "fail", "not_run"}, f"regressions[{i}]", errors)
        rstatus.append(state)
        check_ref(item, "evidence_reference", f"regressions[{i}]")
        if identifier:
            if identifier in rids:
                errors.append(f"duplicate regression ID {identifier}")
            rids.add(identifier)
    review = _object(record.get("independent_review"), "independent_review", errors)
    review_status = _enum(review, "status", REVIEWS, "independent_review", errors)
    if review_status == "completed":
        reviewer = _text(review, "reviewer_id", "independent_review", errors)
        if reviewer and reviewer == record.get("executor_id"):
            errors.append("independent_review reviewer_id cannot equal executor")
        if reviewer and reviewer != record.get("reviewer_id"):
            errors.append("independent_review reviewer_id mismatch")
        check_ref(review, "source_reference", "independent_review")
    if claim == "demonstrated":
        if comparison != "comparable" or kind_before == "unavailable":
            errors.append("demonstrated claim requires comparable baseline")
        if result != "met":
            errors.append("demonstrated claim requires acceptance met; not_run cannot qualify")
        if not rstatus or any(s != "pass" for s in rstatus):
            errors.append("demonstrated claim cannot ignore regressions fail/not_run")
        if review_status != "completed":
            errors.append("demonstrated claim requires independent review")
    return errors
