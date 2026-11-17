"""M06 structural/observational verification: synthetic inputs, not real field proof."""
import copy
import importlib
import json
from pathlib import Path

from masp_skill import cli
from masp_skill.case import _gate_errors, GATE_REQUIREMENTS


ROOT = Path(__file__).resolve().parents[1]
GATE_KEYS = sorted(GATE_REQUIREMENTS["verificacao"])


def validator(value):
    return importlib.import_module("masp_skill.verification").validate_verification_record(value)


def record():
    return {
        "case_id": "MASP-SYN-001", "action_reference": "M05-ACTION-1",
        "objective_reference": "M01-OBJ-1", "executor_id": "operator-1",
        "reviewer_id": "auditor-2",
        "baseline": {"kind": "quantitative", "value": 10.0, "unit": "hours",
                     "method": "count", "source_reference": "bl-1"},
        "after": {"kind": "quantitative", "value": 6.0, "unit": "hours",
                  "method": "count", "source_reference": "after-1"},
        "comparison_status": "comparable",
        "acceptance": {"criterion": "at most 8 hours", "status": "met"},
        "regressions": [{"id": "reg-1", "status": "pass",
                         "evidence_reference": "reg-e1"}],
        "independent_review": {"status": "completed", "reviewer_id": "auditor-2",
                               "source_reference": "review-1"},
        "effectiveness_claim": "demonstrated",
        "evidence": [{"id": ref, "classification": "SIMULATED"} for ref in
                     ("bl-1", "after-1", "reg-e1", "review-1")],
    }


def test_quantitative_baseline_is_structurally_comparable():
    assert validator(record()) == []


def test_incompatible_units_are_rejected():
    item = record()
    item["after"]["unit"] = "%"
    assert any("unit" in issue for issue in validator(item))


def test_incompatible_methods_are_rejected():
    item = record()
    item["after"]["method"] = "survey"
    assert any("method" in issue for issue in validator(item))


def test_declared_effectiveness_rejects_not_run_acceptance():
    item = record()
    item["acceptance"]["status"] = "not_run"
    assert any("not_run" in issue or "acceptance" in issue for issue in validator(item))


def test_declared_effectiveness_rejects_regression_failure():
    item = record()
    item["regressions"][0]["status"] = "fail"
    assert any("regress" in issue for issue in validator(item))


def test_declared_effectiveness_rejects_nonindependent_review():
    item = record()
    item["independent_review"]["reviewer_id"] = "operator-1"
    assert any("reviewer" in issue for issue in validator(item))


def test_missing_baseline_is_not_falsified_into_effectiveness():
    item = record()
    item["baseline"] = {"kind": "unavailable", "reason": "No baseline"}
    assert any("baseline" in issue or "comparison" in issue for issue in validator(item))


def test_missing_reference_is_reported():
    item = record()
    item["after"]["source_reference"] = "missing"
    assert any("source_reference" in issue for issue in validator(item))


def test_qualitative_comparison_accepts_supported_inconclusion():
    item = record()
    item["baseline"] = {"kind": "qualitative", "description": "slow", "method": "interview", "source_reference": "bl-1"}
    item["after"] = {"kind": "qualitative", "description": "uncertain", "method": "interview", "source_reference": "after-1"}
    item["comparison_status"] = "comparable"
    item["acceptance"]["status"] = "inconclusive"
    item["effectiveness_claim"] = "inconclusive"
    assert validator(item) == []


def test_percent_change_has_no_denominator_when_baseline_zero():
    item = record()
    item["baseline"]["value"] = 0
    mod = importlib.import_module("masp_skill.verification")
    assert mod.compare_quantitative(item["baseline"]["value"], item["after"]["value"]) == (-6.0, None)


def test_malformed_record_does_not_crash():
    for item in (None, [], {"baseline": []}, record() | {"regressions": [None]}):
        assert validator(item)


def test_cli_is_static_only(tmp_path, capsys):
    path = tmp_path / "verification.json"
    path.write_text(json.dumps(record()), encoding="utf-8")
    assert cli.main(["validate-verification", "--record", str(path), "--root", str(tmp_path)]) == 0
    assert "STATIC" in capsys.readouterr().out


def observational_proof():
    return [{
        "id": "ev-obs", "classification": "RUNTIME",
        "satisfies": GATE_KEYS,
        "procedure_type": "observation", "procedure_status": "performed",
        "method": "inspection of controlled pilot", "source_reference": "field-log",
        "result": "criterion met", "observed_by": "inspector",
        "reviewed_by": "independent-reviewer", "review_reference": "REV-1",
    }]


def gate_errors(evidence):
    return _gate_errors({"high_risk": False}, {"id": "verificacao", "gate": "verify"},
                        evidence, {}, [])


def test_gate_accepts_observational_record_without_fake_shell_command():
    assert gate_errors(observational_proof()) == []


def test_gate_rejects_observation_missing_method():
    evidence = observational_proof()
    evidence[0].pop("method")
    assert gate_errors(evidence)


def test_gate_rejects_self_review_of_observation():
    evidence = observational_proof()
    evidence[0]["reviewed_by"] = "inspector"
    assert gate_errors(evidence)


def test_gate_rejects_failing_command_even_with_valid_observation():
    failure = {"id": "bad-test", "classification": "RUNTIME", "satisfies": [],
               "command": "pytest", "exit_code": 1, "stderr": "failed"}
    assert gate_errors(observational_proof() + [failure])


def test_gate_rejects_not_run_observation():
    evidence = observational_proof()
    evidence[0]["procedure_status"] = "not_run"
    assert gate_errors(evidence)


def test_fixture_has_9_domains_and_30_adversarial_cases():
    p = ROOT / "tests/fixtures/verificacao-v2/casos.json"
    cases = json.loads(p.read_text(encoding="utf-8"))
    assert len(cases["domains"]) == 9 and len(cases["adversarial"]) == 30
    assert len({r["id"] for r in cases["domains"] + cases["adversarial"]}) == 39
