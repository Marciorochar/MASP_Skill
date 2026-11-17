"""Universal M08 closure tests; case and evidence remain synthetic."""
import copy
import importlib
import json
from pathlib import Path

from masp_skill import cli

ROOT = Path(__file__).resolve().parents[1]
PHASES = ("identificacao", "observacao", "analise", "plano-de-acao",
          "acao", "verificacao", "padronizacao")


def validator(record):
    return importlib.import_module("masp_skill.conclusion").validate_conclusion_record(record)


def record():
    return {
        "case_id": "MASP-SYN-001", "case_revision": "rev-sim-1",
        "author_id": "reporter-1", "resolution_status": "demonstrated",
        "closure_type": "technical", "closure_decision": "complete",
        "complete_ledger": {"status": "complete", "reference": "ledger-1",
                            "phase_states": {p: "PASS" for p in PHASES}},
        "results": [{"objective_reference": "M01-OBJ-1", "status": "achieved",
                     "expected": "at most 8 hours", "observed": "6 hours",
                     "evidence_reference": "obs-1"}],
        "limitations": ["Synthetic controlled example only"],
        "residual_risks": [{"id": "risk-1", "description": "future drift",
                            "owner_id": "owner-1", "evidence_reference": "risk-e1"}],
        "pending_items": [],
        "audit_opinion": {"status": "supported", "reviewer_id": "auditor-1",
                          "evidence_reference": "audit-1"},
        "evidence": [{"id": e, "classification": "SIMULATED"}
                     for e in ("obs-1", "risk-e1", "audit-1")],
    }


def test_complete_synthetic_report_is_structurally_valid():
    assert validator(record()) == []


def test_missing_ledger_reference_rejects_full_closure():
    item = record()
    item["complete_ledger"]["reference"] = ""
    assert any("complete_ledger" in e for e in validator(item))


def test_failed_prior_gate_blocks_full_closure():
    item = record()
    item["complete_ledger"]["phase_states"]["verificacao"] = "FAIL"
    assert any("ledger" in e or "phase" in e for e in validator(item))


def test_incomplete_ledger_cannot_claim_full_close():
    item = record()
    item["complete_ledger"]["status"] = "incomplete"
    assert any("complete" in e for e in validator(item))


def test_negative_objective_is_not_renamed_demonstrated():
    item = record()
    item["results"][0]["status"] = "not_achieved"
    assert any("resolution" in e or "objective" in e for e in validator(item))


def test_critical_pending_item_blocks_full_close():
    item = record()
    item["pending_items"] = [{"id": "p-1", "description": "essential review missing",
                              "critical": True, "owner_id": "owner-1"}]
    assert any("pending" in e for e in validator(item))


def test_residual_risk_requires_owner_and_source():
    item = record()
    item["residual_risks"][0]["owner_id"] = ""
    assert any("owner" in e for e in validator(item))


def test_audit_opinion_cannot_be_self_approval():
    item = record()
    item["audit_opinion"]["reviewer_id"] = item["author_id"]
    assert any("reviewer" in e for e in validator(item))


def test_administrative_closure_can_report_inconclusion_without_false_success():
    item = record()
    item["closure_type"] = "administrative"
    item["closure_decision"] = "with_reservations"
    item["resolution_status"] = "inconclusive"
    item["results"][0]["status"] = "inconclusive"
    item["complete_ledger"]["status"] = "incomplete"
    item["complete_ledger"]["phase_states"]["verificacao"] = "BLOCKED"
    item["audit_opinion"]["status"] = "qualified"
    assert validator(item) == []


def test_not_run_claim_cannot_close_as_resolved():
    item = record()
    item["results"][0]["status"] = "not_evaluated"
    assert validator(item)


def test_missing_result_evidence_is_reported():
    item = record()
    item["results"][0]["evidence_reference"] = "unknown"
    assert any("evidence" in e for e in validator(item))


def test_missing_limitations_is_rejected():
    item = record()
    item["limitations"] = []
    assert any("limitations" in e for e in validator(item))


def test_invalid_nested_structure_is_reported_not_crashed():
    for item in (None, [], {"complete_ledger": []}, record() | {"results": [None]}):
        assert validator(item)


def test_cli_validates_static_report_only(tmp_path, capsys):
    path = tmp_path / "conclusion.json"
    path.write_text(json.dumps(record()), encoding="utf-8")
    assert cli.main(["validate-conclusion", "--record", str(path), "--root", str(tmp_path)]) == 0
    assert "STATIC" in capsys.readouterr().out


def test_corpus_has_nine_domains_and_32_adversarial_cases():
    path = ROOT / "tests/fixtures/conclusao-v2/casos.json"
    cases = json.loads(path.read_text(encoding="utf-8"))
    assert len(cases["domains"]) == 9 and len(cases["adversarial"]) == 32
    assert len({r["id"] for r in cases["domains"] + cases["adversarial"]}) == 41
