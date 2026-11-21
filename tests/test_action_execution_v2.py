"""Behavioral structural tests for M05 sidecar; no real interventions."""
import copy
import importlib
import json
from pathlib import Path

from masp_skill import cli

ROOT = Path(__file__).resolve().parents[1]


def validator(record):
    module = importlib.import_module("masp_skill.action_execution")
    return module.validate_action_execution_record(record)


def valid_record():
    return {
        "case_id": "MASP-SYN-001", "plan_reference": "M04-PLAN-1",
        "plan_version": "v1", "baseline_reference": "M02-BL",
        "approved_scope": "controlled order-registration exercise",
        "approval": {"status": "approved", "plan_version": "v1",
                     "scope": "controlled order-registration exercise",
                     "approver_id": "external-supervisor",
                     "approval_reference": "AUTH-SYN-1"},
        "executor_id": "worker-1", "verifier_id": "reviewer-2",
        "environment": {"type": "administration", "isolation": "controlled_simulation",
                        "evidence_id": "env-1"},
        "evidence": [
            {"id": "env-1", "classification": "SIMULATED"},
            {"id": "before-1", "classification": "SIMULATED"},
            {"id": "after-1", "classification": "SIMULATED"},
        ],
        "tasks": [{
            "id": "action-1", "plan_task_id": "task-M04-1", "status": "performed",
            "before": {"description": "manual records", "evidence_id": "before-1"},
            "after": {"description": "controlled checklist", "evidence_id": "after-1"},
            "execution": {"kind": "procedure", "description": "simulated checklist exercise",
                          "evidence_id": "after-1"},
            "result": {"status": "observed", "description": "synthetic observation",
                       "evidence_id": "after-1"},
            "rollback": {"type": "reversible", "status": "not_run"},
            "deviation": "none",
        }],
    }


def test_valid_nonsoftware_procedure_is_structurally_accepted():
    assert validator(valid_record()) == []


def test_declared_approval_does_not_allow_version_mismatch():
    record = valid_record()
    record["approval"]["plan_version"] = "v2"
    assert any("version" in e for e in validator(record))


def test_declared_approval_does_not_allow_scope_mismatch():
    record = valid_record()
    record["approval"]["scope"] = "production"
    assert any("scope" in e for e in validator(record))


def test_missing_approval_cannot_claim_performed_action():
    record = valid_record()
    record["approval"] = {"status": "pending"}
    assert any("approval" in e for e in validator(record))


def test_executor_must_not_approve_own_action():
    record = valid_record()
    record["approval"]["approver_id"] = record["executor_id"]
    assert any("self" in e or "approver" in e for e in validator(record))


def test_verifier_must_be_independent_of_executor():
    record = valid_record()
    record["verifier_id"] = record["executor_id"]
    assert any("verifier" in e for e in validator(record))


def test_not_run_task_rejects_observed_result():
    record = valid_record()
    record["tasks"][0]["status"] = "not_run"
    assert any("not_run" in e for e in validator(record))


def test_performed_task_requires_before_after_proof():
    record = valid_record()
    record["tasks"][0]["after"]["evidence_id"] = "missing"
    assert any("evidence" in e for e in validator(record))


def test_procedure_is_valid_without_fake_shell_command():
    record = valid_record()
    assert "command" not in record["tasks"][0]["execution"]
    assert validator(record) == []


def test_irreversible_change_cannot_claim_rollback_completed():
    record = valid_record()
    record["tasks"][0]["rollback"] = {"type": "irreversible", "status": "performed"}
    assert any("rollback" in e or "irreversible" in e for e in validator(record))


def test_duplicate_task_ids_are_rejected():
    record = valid_record()
    record["tasks"].append(copy.deepcopy(record["tasks"][0]))
    assert any("duplicate" in e for e in validator(record))


def test_malformed_types_are_reported_without_crashing():
    for item in ([], None, {"case_id": []}, valid_record() | {"tasks": [None]}):
        assert validator(item)


def test_cli_reports_static_only_and_rejects_workspace_escape(tmp_path, capsys):
    record = tmp_path / "execution.json"
    record.write_text(json.dumps(valid_record()), encoding="utf-8")
    assert cli.main(["validate-action-execution", "--record", str(record), "--root", str(tmp_path)]) == 0
    assert "STATIC" in capsys.readouterr().out
    assert cli.main(["validate-action-execution", "--record", str(record), "--root", str(tmp_path / "other")]) == 1


def test_fixture_domains_and_adversarial_cases_are_synthetic():
    path = ROOT / "tests/fixtures/acao-v2/casos.json"
    corpus = json.loads(path.read_text(encoding="utf-8"))
    assert len(corpus["domains"]) == 9
    assert len(corpus["adversarial"]) == 24
    assert len({item["id"] for item in corpus["domains"] + corpus["adversarial"]}) == 33
    assert all(item["classification"] == "SIMULATED" and item["invariant"]
               for item in corpus["domains"] + corpus["adversarial"])
