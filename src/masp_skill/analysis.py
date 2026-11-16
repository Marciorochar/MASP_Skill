"""Structural checks for the optional universal MASP causal-analysis sidecar.

Only checks self-declared data. These checks neither authenticate sources nor
prove causality, and they NEVER approve the simulated MASP Gate 03.
"""
from __future__ import annotations

from typing import Any

FACT_CLASSES = {"FATO_VERIFICADO", "RELATO_NAO_VERIFICADO", "HIPOTESE", "DESCONHECIDO"}
HYPOTHESIS_STATUSES = {"NAO_TESTADA", "EM_AVALIACAO", "CORROBORADA", "REFUTADA", "INCONCLUSIVA"}
VERIFICATION_STATUSES = {"performed", "not_run"}
CONCLUSION_TYPES = {"supported", "inconclusive"}
SUPPORTED_BASES = {"documentary_triangulation", "direct_mechanism", "controlled_comparison", "other_evaluation"}
ALL_BASES = SUPPORTED_BASES | {"association_only", "unknown"}


def _text(obj: dict[str, Any], field: str, where: str, errors: list[str]) -> str | None:
    value = obj.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{where}.{field} must be a nonempty string")
        return None
    return value


def _text_list(
    value: Any, where: str, errors: list[str], *, required: bool = False,
) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{where} must be an array of nonempty strings")
        return []
    if required and not value:
        errors.append(f"{where} must not be empty")
    if any(not isinstance(x, str) or not x.strip() for x in value):
        errors.append(f"{where} must contain only nonempty strings")
    strings = [x for x in value if isinstance(x, str) and x.strip()]
    if len(strings) != len(set(strings)):
        errors.append(f"{where} has duplicated entries")
    return strings


def _references(ids: list[str], known: set[str], where: str, errors: list[str]) -> None:
    for item in ids:
        if item not in known:
            errors.append(f"{where} references unknown ID {item}")


def validate_analysis_record(record: Any) -> list[str]:
    """Return structural errors; an empty list does not mean causal proof or PASS.

    In particular, a supplied FATO_VERIFICADO label and a 'performed' test
    status are declarations, not independent attestations.
    """
    if not isinstance(record, dict):
        return ["analysis record must be an object"]

    errors: list[str] = []
    for field in ("case_id", "problem_reference", "observation_reference",
                  "analysis_objective", "analysis_scope"):
        _text(record, field, "analysis", errors)

    methods = record.get("methods")
    if not isinstance(methods, list) or not methods:
        errors.append("methods must be a nonempty array")
    else:
        for i, item in enumerate(methods):
            if not isinstance(item, dict):
                errors.append(f"methods[{i}] must be an object")
                continue
            _text(item, "name", f"methods[{i}]", errors)
            _text(item, "rationale", f"methods[{i}]", errors)

    source_ids: set[str] = set()
    source_data: dict[str, dict[str, Any]] = {}
    sources = record.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("sources must be a nonempty array")
    else:
        for i, source in enumerate(sources):
            where = f"sources[{i}]"
            if not isinstance(source, dict):
                errors.append(f"{where} must be an object")
                continue
            source_id = _text(source, "id", where, errors)
            if source_id:
                if source_id in source_ids:
                    errors.append(f"duplicate source ID {source_id}")
                else:
                    source_data[source_id] = source
                source_ids.add(source_id)
            for field in ("origin", "description"):
                _text(source, field, where, errors)
            if source.get("fact_class") not in FACT_CLASSES:
                errors.append(f"{where}.fact_class must be one of {sorted(FACT_CLASSES)}")

    hypotheses = record.get("hypotheses")
    hypothesis_ids: set[str] = set()
    hypothesis_data: dict[str, dict[str, Any]] = {}
    pending_alternatives: list[tuple[str, list[str]]] = []
    if not isinstance(hypotheses, list) or not hypotheses:
        errors.append("hypotheses must be a nonempty array")
    else:
        for i, hyp in enumerate(hypotheses):
            where = f"hypotheses[{i}]"
            if not isinstance(hyp, dict):
                errors.append(f"{where} must be an object")
                continue
            hid = _text(hyp, "id", where, errors)
            if hid:
                if hid in hypothesis_ids:
                    errors.append(f"duplicate hypothesis ID {hid}")
                else:
                    hypothesis_data[hid] = hyp
                hypothesis_ids.add(hid)
            for field in ("statement", "mechanism", "expected_if_true",
                          "potential_disconfirmation", "counterevidence_review"):
                _text(hyp, field, where, errors)
            status = hyp.get("status")
            if status not in HYPOTHESIS_STATUSES:
                errors.append(f"{where}.status must be one of {sorted(HYPOTHESIS_STATUSES)}")

            support = _text_list(hyp.get("evidence_for"), f"{where}.evidence_for", errors)
            opposition = _text_list(hyp.get("evidence_against"), f"{where}.evidence_against", errors)
            _references(support, source_ids, f"{where}.evidence_for", errors)
            _references(opposition, source_ids, f"{where}.evidence_against", errors)
            alternatives = _text_list(hyp.get("alternative_ids"), f"{where}.alternative_ids", errors)
            if hid:
                pending_alternatives.append((where, alternatives))
                if hid in alternatives:
                    errors.append(f"{where}.alternative_ids must not include itself")

            verification = hyp.get("verification")
            v_status = None
            v_ids: list[str] = []
            if not isinstance(verification, dict):
                errors.append(f"{where}.verification must be an object")
            else:
                v_status = verification.get("status")
                if v_status not in VERIFICATION_STATUSES:
                    errors.append(f"{where}.verification.status must be performed or not_run")
                _text(verification, "method", f"{where}.verification", errors)
                v_ids = _text_list(verification.get("evidence_ids", []),
                                   f"{where}.verification.evidence_ids", errors,
                                   required=v_status == "performed")
                _references(v_ids, source_ids, f"{where}.verification.evidence_ids", errors)
                if v_status == "performed":
                    _text(verification, "result", f"{where}.verification", errors)
                if v_status == "not_run":
                    _text(verification, "reason", f"{where}.verification", errors)
                    if verification.get("result") is not None:
                        errors.append(f"{where}.verification.result cannot claim a test when not_run")

            if status == "CORROBORADA":
                verified_support = [sid for sid in support if
                                    sid in source_data and
                                    source_data[sid].get("fact_class") == "FATO_VERIFICADO"]
                if not support or not verified_support or v_status != "performed" or not v_ids:
                    errors.append(
                        f"{where}.status CORROBORADA requires attributed FATO_VERIFICADO support "
                        "and a documented performed evaluation (declarations only)"
                    )
            if status == "REFUTADA":
                verified_opposition = [sid for sid in opposition if
                                       sid in source_data and
                                       source_data[sid].get("fact_class") == "FATO_VERIFICADO"]
                if not opposition or not verified_opposition or v_status != "performed":
                    errors.append(f"{where}.status REFUTADA requires verified contrary evidence "
                                  "and a documented performed evaluation (declarations only)")

    for where, alternatives in pending_alternatives:
        _references(alternatives, hypothesis_ids, f"{where}.alternative_ids", errors)

    conclusion = record.get("conclusion")
    if not isinstance(conclusion, dict):
        errors.append("conclusion must be an object")
    else:
        kind = conclusion.get("type")
        if kind not in CONCLUSION_TYPES:
            errors.append(f"conclusion.type must be one of {sorted(CONCLUSION_TYPES)}")
        for field in ("justification", "limitations"):
            _text(conclusion, field, "conclusion", errors)
        basis = conclusion.get("evidence_basis")
        if basis not in ALL_BASES:
            errors.append("conclusion.evidence_basis must declare the basis of inference")
        ids = _text_list(conclusion.get("supported_hypothesis_ids"),
                         "conclusion.supported_hypothesis_ids", errors,
                         required=kind == "supported")
        _references(ids, hypothesis_ids, "conclusion.supported_hypothesis_ids", errors)
        _text_list(conclusion.get("additional_data_needed"),
                   "conclusion.additional_data_needed", errors)

        if kind == "inconclusive" and ids:
            errors.append("conclusion.supported_hypothesis_ids must be empty for inconclusive")
        if kind == "supported":
            if basis not in SUPPORTED_BASES:
                errors.append("conclusion.evidence_basis cannot assert a cause from "
                              "association_only, unknown or invalid basis")
            for hid in ids:
                h = hypothesis_data.get(hid)
                if h is not None and h.get("status") != "CORROBORADA":
                    errors.append("conclusion.supported_hypothesis_ids must reference "
                                  f"only CORROBORADA hypotheses ({hid})")
                if h is not None and basis == "documentary_triangulation":
                    supports = h.get("evidence_for")
                    if not isinstance(supports, list):
                        supports = []
                    origins = {
                        source_data[sid].get("origin")
                        for sid in supports if isinstance(sid, str)
                        and sid in source_data
                        and source_data[sid].get("fact_class") == "FATO_VERIFICADO"
                        and isinstance(source_data[sid].get("origin"), str)
                        and source_data[sid]["origin"].strip()
                    }
                    if len(origins) < 2:
                        errors.append("conclusion.evidence_basis documentary_triangulation "
                                      "requires at least two distinct declared source origins")

    if "limitations" in record:
        _text_list(record["limitations"], "limitations", errors)
    return errors
