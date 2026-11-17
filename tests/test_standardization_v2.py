"""Structural and adversarial tests for M07; all examples are synthetic."""
import copy
import importlib
import json
from pathlib import Path

from masp_skill import cli

ROOT = Path(__file__).resolve().parents[1]


def validator(data):
    return importlib.import_module("masp_skill.standardization").validate_standardization_record(data)


def record():
    return {
        "case_id": "MASP-SYN-001", "verification_reference": "M06-V1",
        "verification_status": "demonstrated",
        "standard_id": "STD-SYN-1", "standard_version": "v1",
        "document_status": "DRAFT", "implementation_status": "not_run",
        "applicability": "controlled service process", "exclusions": "production",
        "owner_id": "owner-1",
        "preventive_control": {"id": "ctl-1", "type": "preventive",
                               "description": "controlled checklist",
                               "cause_reference": "M03-H1"},
        "trigger": {"event": "quality deviation", "detection": "audit record",
                    "reaction": "stop and notify owner", "owner_id": "owner-1"},
        "regression": {"method": "weekly controlled inspection",
                       "criterion": "no recurrence", "evidence_reference": "r1",
                       "status": "planned"},
        "monitoring": {"indicator": "deviations", "source_reference": "r1",
                       "cadence": "weekly"},
        "training": {"required": False, "status": "not_required"},
        "approval": {"status": "pending"},
        "evidence": [{"id": "r1", "classification": "SIMULATED"}],
    }


def test_draft_standard_with_controls_is_structurally_valid():
    assert validator(record()) == []


def test_missing_verification_cannot_claim_proven_standard():
    item = record()
    item["verification_reference"] = ""
    item["document_status"] = "ACTIVE"
    assert any("verification_reference" in e for e in validator(item))


def test_inconclusive_verification_cannot_be_approved_as_effective():
    item = record()
    item["verification_status"] = "inconclusive"
    item["document_status"] = "APPROVED"
    assert any("verification" in e for e in validator(item))


def test_standard_requires_owner_id():
    item = record()
    item["owner_id"] = ""
    assert any("owner" in e for e in validator(item))


def test_trigger_must_have_reaction_and_detection():
    item = record()
    item["trigger"]["reaction"] = ""
    assert any("trigger" in e for e in validator(item))


def test_trigger_owner_must_match_declared_owner():
    item = record()
    item["trigger"]["owner_id"] = "other"
    assert any("owner" in e for e in validator(item))


def test_regression_must_have_method_criterion_and_source():
    item = record()
    item["regression"]["method"] = ""
    assert any("regression" in e for e in validator(item))


def test_active_requires_implementation_proof_reference():
    item = record()
    item["document_status"] = "ACTIVE"
    item["approval"] = {"status": "approved", "approval_reference": "AUTH-1"}
    item["implementation_status"] = "implemented"
    assert any("implementation" in e for e in validator(item))


def test_training_planned_is_not_claimed_completed():
    item = record()
    item["training"] = {"required": True, "status": "completed"}
    assert any("training" in e for e in validator(item))


def test_obsolete_standard_cannot_be_active_implementation():
    item = record()
    item["document_status"] = "OBSOLETE"
    item["implementation_status"] = "implemented"
    assert any("obsolete" in e.lower() or "OBSOLETE" in e for e in validator(item))


def test_missing_monitoring_reference_is_rejected():
    item = record()
    item["monitoring"]["source_reference"] = "missing"
    assert any("source_reference" in e for e in validator(item))


def test_malformed_nested_data_not_crash():
    for item in ([], None, {"trigger": []}, record() | {"evidence": [None]}):
        assert validator(item)


def test_cli_is_static_only(tmp_path, capsys):
    p = tmp_path / "standard.json"
    p.write_text(json.dumps(record()), encoding="utf-8")
    assert cli.main(["validate-standardization", "--record", str(p), "--root", str(tmp_path)]) == 0
    assert "STATIC" in capsys.readouterr().out


def test_fixture_corpus_is_simulated():
    doc = json.loads((ROOT / "tests/fixtures/padronizacao-v2/casos.json").read_text(encoding="utf-8"))
    assert len(doc["domains"]) == 9 and len(doc["adversarial"]) == 30
    assert len({x["id"] for x in doc["domains"] + doc["adversarial"]}) == 39
