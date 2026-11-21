"""Read-only cross-phase consistency checks for four universal MASP v2 sidecars.

These checks inspect caller-supplied declarations only. A successful result
does NOT authenticate field observations, authorization, agent execution,
case-ledger provenance, efficacy, an independent review or any MASP gate.
"""
from __future__ import annotations

from typing import Any

from .action_execution import validate_action_execution_record
from .verification import validate_verification_record
from .standardization import validate_standardization_record
from .conclusion import validate_conclusion_record


VALIDATORS = {
    "acao": validate_action_execution_record,
    "verificacao": validate_verification_record,
    "padronizacao": validate_standardization_record,
    "conclusao": validate_conclusion_record,
}

# Labels from the MASP routing contract; no new phase IDs or ledger states.
PRIOR_PHASES = {
    "identificacao": "Identificação",
    "observacao": "Observação",
    "analise": "Análise",
    "plano-de-acao": "Plano de ação",
    "acao": "Ação",
    "verificacao": "Verificação",
    "padronizacao": "Padronização",
}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _obj(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def validate_universal_cycle(bundle: Any, *, case: Any = None) -> list[str]:
    """Check M05→M06→M07→M08 links and optional *declared* case history.

    Run validate_case separately with routing and on-disk evidence to check
    ledger hashes. This function never reads or writes any external resource.
    """
    if not isinstance(bundle, dict):
        return ["universal cycle bundle must be an object"]
    errors: list[str] = []
    records: dict[str, dict[str, Any]] = {}
    for phase, validator in VALIDATORS.items():
        record = bundle.get(phase)
        if not isinstance(record, dict):
            errors.append(f"{phase} record must be an object")
            continue
        records[phase] = record
        errors.extend(f"{phase}: {issue}" for issue in validator(record))
    if len(records) != len(VALIDATORS):
        return errors

    a = records["acao"]
    v = records["verificacao"]
    s = records["padronizacao"]
    c = records["conclusao"]

    case_id = a.get("case_id")
    if not _nonempty(case_id):
        errors.append("acao.case_id is required")
    for phase, record in records.items():
        if record.get("case_id") != case_id:
            errors.append(f"{phase}.case_id mismatch across MASP phases")

    action_id = a.get("record_id")
    verification_id = v.get("record_id")
    if not _nonempty(action_id) or v.get("action_reference") != action_id:
        errors.append("verificacao.action_reference must match acao.record_id")
    if not _nonempty(verification_id) or s.get("verification_reference") != verification_id:
        errors.append("padronizacao.verification_reference must match verificacao.record_id")
    if not _nonempty(s.get("standard_id")) or c.get("standardization_reference") != s.get("standard_id"):
        errors.append("conclusao.standardization_reference must match padronizacao.standard_id")
    if _obj(v.get("baseline")).get("source_reference") != a.get("baseline_reference"):
        errors.append("verificacao.baseline.source_reference must match acao.baseline_reference")
    if v.get("executor_id") != a.get("executor_id"):
        errors.append("verificacao.executor_id must match acao.executor_id")
    if v.get("reviewer_id") != a.get("verifier_id"):
        errors.append("verificacao.reviewer_id must match acao.verifier_id")

    objective_id = v.get("objective_reference")
    if not _nonempty(objective_id) or not any(
        isinstance(item, dict) and item.get("objective_reference") == objective_id
        for item in (c.get("results") if isinstance(c.get("results"), list) else [])
    ):
        errors.append("conclusao.results.objective_reference must match verificacao.objective_reference")
    effectiveness = v.get("effectiveness_claim")
    if s.get("verification_status") != effectiveness:
        errors.append("padronizacao.verification_status must match verificacao.effectiveness_claim")
    if c.get("resolution_status") == "demonstrated" and effectiveness != "demonstrated":
        errors.append("conclusao.resolution_status demonstrated contradicts verificacao.effectiveness_claim")

    if c.get("closure_decision") == "complete":
        if s.get("document_status") != "ACTIVE" or s.get("implementation_status") != "implemented":
            errors.append("complete closure requires padronizacao ACTIVE with documented implementation")
        task_statuses = [t.get("status") for t in a.get("tasks", []) if isinstance(t, dict)]
        if not task_statuses or any(st != "performed" for st in task_statuses):
            errors.append("complete closure requires recorded performed M05 tasks")
        if effectiveness != "demonstrated":
            errors.append("complete closure requires demonstrated verificacao effectiveness")

    if case is not None:
        if not isinstance(case, dict):
            errors.append("case ledger must be an object")
            return errors
        if case.get("case_id") != case_id:
            errors.append("case ledger case_id mismatch")
        if case.get("classification") != "SIMULATED":
            errors.append("case ledger must remain SIMULATED; external provenance is not authenticated")
        ledger = case.get("ledger")
        if not isinstance(ledger, list):
            errors.append("case ledger events must be an array")
            return errors
        last_states: dict[str, str] = {}
        for event in ledger:
            if not isinstance(event, dict):
                errors.append("case ledger event must be an object")
                continue
            name = event.get("phase")
            state = event.get("new_state")
            if isinstance(name, str) and isinstance(state, str):
                last_states[name] = state
        declared_states = _obj(_obj(c.get("complete_ledger")).get("phase_states"))
        for phase_id, label in PRIOR_PHASES.items():
            state = last_states.get(label)
            if state is None:
                errors.append(f"case ledger missing prior phase {phase_id}")
            elif declared_states.get(phase_id) != state:
                errors.append(f"conclusao.complete_ledger.phase_states.{phase_id} disagrees with case ledger")
            if c.get("closure_decision") == "complete" and state != "PASS":
                errors.append(f"complete conclusion requires PASS in case ledger for {phase_id}")
        if c.get("closure_decision") == "complete" and (
            case.get("state") != "PASS" or case.get("current_phase") != "Conclusão"
        ):
            errors.append("complete conclusion contradicts current case ledger state")
    return errors
