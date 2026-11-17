"""Synthetic end-to-end checks of the four M05-M08 contracts and MASP ledger.

No human approval, field measurement, agent run, or RUNTIME provenance is
authenticated. The gate's RUNTIME *label* below is deliberately simulated.
"""
import copy
import importlib
import json
from pathlib import Path

import pytest

from masp_skill.case import GATE_REQUIREMENTS, create_case, transition_case, validate_case
from masp_skill.evidence import make_evidence
from masp_skill.routing import load_routing
from masp_skill.action_execution import validate_action_execution_record
from masp_skill.verification import validate_verification_record
from masp_skill.standardization import validate_standardization_record
from masp_skill.conclusion import validate_conclusion_record
from test_action_execution_v2 import valid_record as action_example
from test_verification_v2 import record as verification_example
from test_standardization_v2 import record as standardization_example
from test_conclusion_v2 import record as conclusion_example

ROOT = Path(__file__).resolve().parents[1]
ROUTING = load_routing(ROOT / "docs/masp/masp-routing.toml")


def validate(bundle, case=None):
    return importlib.import_module("masp_skill.universal_cycle").validate_universal_cycle(bundle, case=case)


def example_bundle():
    action = action_example()
    action["record_id"] = "M05-ACTION-1"
    verification = verification_example()
    verification["record_id"] = "M06-V1"
    verification["action_reference"] = action["record_id"]
    verification["executor_id"] = action["executor_id"]
    verification["reviewer_id"] = action["verifier_id"]
    verification["baseline"]["source_reference"] = action["baseline_reference"]
    verification["evidence"].append({"id": action["baseline_reference"], "classification": "SIMULATED"})

    standardization = standardization_example()
    standardization["verification_reference"] = verification["record_id"]
    standardization["document_status"] = "ACTIVE"
    standardization["implementation_status"] = "implemented"
    standardization["approval"] = {"status": "approved", "approval_reference": "SIMULATED-AUTH"}
    standardization["implementation_evidence_reference"] = "r1"
    standardization["regression"]["status"] = "performed"

    conclusion = conclusion_example()
    conclusion["standardization_reference"] = standardization["standard_id"]
    assert all(record["case_id"] == action["case_id"] for record in
               (verification, standardization, conclusion))
    return {"acao": action, "verificacao": verification,
            "padronizacao": standardization, "conclusao": conclusion}


def simulated_full_case(tmp_path, bundle):
    case = create_case(bundle["acao"]["case_id"], ROUTING)
    for index, phase in enumerate(ROUTING["phases"]):
        phase_id = phase["id"]
        start_file = tmp_path / f"{phase_id}-start.txt"
        start_file.write_text(f"SIMULATED start {phase_id}\n", encoding="utf-8")
        case = transition_case(case, "IN_PROGRESS", "masp-coordenador",
                               [make_evidence(start_file, tmp_path, classification="SIMULATED",
                                              description="Synthetic phase start")],
                               ROUTING, phase=phase["name"] if index else None,
                               root=tmp_path)
        if phase_id == "conclusao":
            # Snapshot before closing: actual reference is only to this SIMULATED ledger.
            last_hash = case["ledger"][-2]["event_hash"]  # M07 PASS, before M08 start.
            bundle["conclusao"]["complete_ledger"]["reference"] = last_hash
            bundle["conclusao"]["case_revision"] = last_hash
            bundle["conclusao"]["complete_ledger"]["phase_states"] = {
                item["id"]: "PASS" for item in ROUTING["phases"][:7]
            }
        done_file = tmp_path / f"{phase_id}-completed.json"
        done_file.write_text(
            json.dumps(bundle[phase_id] if phase_id in bundle else
                       {"case_id": case["case_id"], "classification": "SIMULATED",
                        "phase": phase_id}, ensure_ascii=False),
            encoding="utf-8",
        )
        metadata = {"satisfies": sorted(GATE_REQUIREMENTS[phase_id])}
        if phase_id == "plano-de-acao":
            metadata.update(approval_type="human_plan",
                            approved_by="SIMULATED-APPROVER-NOT-A-REAL-PERSON")
        classification = "SIMULATED"
        if phase_id == "verificacao":
            # Required by the existing gate; this is a caller-supplied simulated
            # RUNTIME label, NOT an observed real-world or Codex execution.
            classification = "RUNTIME"
            metadata.update(procedure_type="observation", procedure_status="performed",
                            method="fictional pilot observation",
                            source_reference="SIMULATED-SOURCE", result="fictional criterion met",
                            observed_by="SIMULATED-OBSERVER",
                            reviewed_by="SIMULATED-DIFFERENT-REVIEWER",
                            review_reference="SIMULATED-REVIEW")
        evidence = make_evidence(done_file, tmp_path, classification=classification,
                                 description="Synthetic contract JSON, not operational proof",
                                 **metadata)
        case = transition_case(case, "PASS", "masp-coordenador",
                               [evidence], ROUTING, root=tmp_path)
        assert validate_case(case, ROUTING, tmp_path) == []
    return case


def test_four_individual_contracts_and_simulated_eight_phase_ledger_are_consistent(tmp_path):
    bundle = example_bundle()
    validators = (validate_action_execution_record, validate_verification_record,
                  validate_standardization_record, validate_conclusion_record)
    assert all(validator(bundle[phase]) == [] for phase, validator in
               zip(("acao", "verificacao", "padronizacao", "conclusao"), validators))
    case = simulated_full_case(tmp_path, bundle)
    assert case["classification"] == "SIMULATED"
    assert case["state"] == "PASS"
    assert case["current_phase"] == "Conclusão"
    assert len(case["ledger"]) == 16
    assert validate(bundle, case) == []


@pytest.mark.parametrize("change,fragment", [
    ("wrong_case", "case_id"),
    ("wrong_action", "action_reference"),
    ("wrong_baseline", "baseline"),
    ("wrong_verification", "verification_reference"),
    ("wrong_standard", "standardization_reference"),
    ("wrong_objective", "objective_reference"),
    ("wrong_reviewer", "reviewer_id"),
])
def test_cross_phase_mismatch_is_rejected(change, fragment):
    bundle = example_bundle()
    if change == "wrong_case":
        bundle["verificacao"]["case_id"] = "WRONG-CASE"
    elif change == "wrong_action":
        bundle["verificacao"]["action_reference"] = "UNKNOWN-ACTION"
    elif change == "wrong_baseline":
        bundle["verificacao"]["baseline"]["source_reference"] = "other-baseline"
        bundle["verificacao"]["evidence"].append({"id":"other-baseline","classification":"SIMULATED"})
    elif change == "wrong_verification":
        bundle["padronizacao"]["verification_reference"] = "UNKNOWN-VERIFICATION"
    elif change == "wrong_standard":
        bundle["conclusao"]["standardization_reference"] = "UNKNOWN-STANDARD"
    elif change == "wrong_objective":
        bundle["conclusao"]["results"][0]["objective_reference"] = "WRONG-OBJECTIVE"
    elif change == "wrong_reviewer":
        bundle["verificacao"]["reviewer_id"] = "OTHER-REVIEWER"
        bundle["verificacao"]["independent_review"]["reviewer_id"] = "OTHER-REVIEWER"
    assert any(fragment in issue for issue in validate(bundle))


def test_complete_closure_rejects_only_draft_standardization():
    bundle = example_bundle()
    bundle["padronizacao"]["document_status"] = "DRAFT"
    bundle["padronizacao"]["implementation_status"] = "not_run"
    bundle["padronizacao"]["approval"] = {"status":"pending"}
    assert any("standardization" in issue or "padronizacao" in issue
               for issue in validate(bundle))


def test_masquerading_not_run_as_demonstrated_is_rejected():
    bundle = example_bundle()
    bundle["verificacao"]["effectiveness_claim"] = "not_run"
    bundle["verificacao"]["acceptance"]["status"] = "not_run"
    assert any("effectiveness" in issue or "resolution" in issue
               for issue in validate(bundle))


def test_conclusion_cannot_invent_passes_missing_from_actual_ledger(tmp_path):
    bundle = example_bundle()
    case = simulated_full_case(tmp_path, bundle)
    corrupted = copy.deepcopy(case)
    corrupted["ledger"] = [event for event in corrupted["ledger"]
                           if event["phase"] != "Padronização"]
    assert any("ledger" in issue or "padronizacao" in issue
               for issue in validate(bundle, corrupted))


def test_integrated_validator_does_not_accept_malformed_input():
    assert validate(None)
    assert validate({"acao": [], "verificacao": None, "padronizacao": {},
                     "conclusao": "fake"})
