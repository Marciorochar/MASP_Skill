"""Universal MASP observation sidecar validation.

Validates declared structure and provenance references only. It cannot certify
that observations occurred, approve a MASP gate, or authenticate any identity.
"""
from __future__ import annotations

import math
from typing import Any

FACT_CLASSES = {"FATO_VERIFICADO", "RELATO_NAO_VERIFICADO", "HIPOTESE", "DESCONHECIDO"}
BASELINE_TYPES = {"quantitative", "qualitative", "unavailable"}
REPRO_STATUSES = {"reproduced", "not_reproducible", "not_attempted"}


def _required_text(obj: dict[str, Any], key: str, label: str, errors: list[str]) -> str | None:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}.{key} must be a nonempty string")
        return None
    return value


def validate_observation_record(record: Any) -> list[str]:
    """Return structural errors; an empty list does NOT mean MASP Gate 02 PASS.

    Records may describe measurements, qualitative observations, or a baseline
    that could not be established. Source and authorization assertions are
    user-provided; do not treat them as runtime evidence.
    """
    if not isinstance(record, dict):
        return ["observation record must be an object"]

    errors: list[str] = []
    for key in ("case_id", "problem_reference", "observation_objective", "observed_condition"):
        _required_text(record, key, "observation", errors)
        # Top-level names are included in each error, for machine-readable feedback.

    environment = record.get("environment")
    if not isinstance(environment, dict):
        errors.append("environment must be an object")
    else:
        _required_text(environment, "description", "environment", errors)
        _required_text(environment, "period", "environment", errors)

    method = record.get("collection_method")
    if not isinstance(method, dict):
        errors.append("collection_method must be an object")
    else:
        _required_text(method, "name", "collection_method", errors)
        _required_text(method, "procedure", "collection_method", errors)

    ids: set[str] = set()
    sources = record.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("sources must be a nonempty array of attributed source records")
    else:
        for i, source in enumerate(sources):
            label = f"sources[{i}]"
            if not isinstance(source, dict):
                errors.append(f"{label} must be an object")
                continue
            source_id = _required_text(source, "id", label, errors)
            if source_id:
                if source_id in ids:
                    errors.append(f"duplicate source id {source_id}")
                ids.add(source_id)
            for key in ("kind", "origin", "recorded_at"):
                _required_text(source, key, label, errors)
            fact_class = source.get("fact_class")
            if not isinstance(fact_class, str) or fact_class not in FACT_CLASSES:
                errors.append(f"{label}.fact_class must be one of {sorted(FACT_CLASSES)}")

    baseline = record.get("baseline")
    if not isinstance(baseline, dict):
        errors.append("baseline must be an object")
    else:
        kind = baseline.get("type")
        if not isinstance(kind, str) or kind not in BASELINE_TYPES:
            errors.append(f"baseline.type must be one of {sorted(BASELINE_TYPES)}")
        elif kind == "unavailable":
            _required_text(baseline, "reason", "baseline", errors)
            _required_text(baseline, "collection_needed", "baseline", errors)
        else:
            for key in ("definition", "period", "source_id"):
                _required_text(baseline, key, "baseline", errors)
            source_id = baseline.get("source_id")
            if isinstance(source_id, str) and source_id.strip() and source_id not in ids:
                errors.append("baseline.source_id must reference a declared source")
            value = baseline.get("value")
            if kind == "quantitative":
                is_numeric = isinstance(value, (int, float)) and not isinstance(value, bool)
                try:
                    finite = math.isfinite(value) if is_numeric else False
                except (OverflowError, TypeError, ValueError):
                    finite = False
                if not finite:
                    errors.append("baseline.value must be a finite numeric measurement")
                _required_text(baseline, "unit", "baseline", errors)
            elif not isinstance(value, str) or not value.strip():
                errors.append("baseline.value must be a nonempty qualitative condition")

    reproducibility = record.get("reproducible_result_or_limitation")
    if not isinstance(reproducibility, dict):
        errors.append("reproducible_result_or_limitation must be an object")
    else:
        status = reproducibility.get("status")
        if not isinstance(status, str) or status not in REPRO_STATUSES:
            errors.append(
                "reproducible_result_or_limitation.status must be reproduced, "
                "not_reproducible or not_attempted"
            )
        _required_text(reproducibility, "details", "reproducible_result_or_limitation", errors)

    limitations = record.get("limitations", [])
    if not isinstance(limitations, list) or any(
        not isinstance(item, str) or not item.strip() for item in limitations
    ):
        errors.append("limitations must be a list of nonempty strings when provided")

    return errors
