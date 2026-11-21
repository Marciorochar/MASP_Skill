"""Offline MASP lifecycle characterization. All records are caller-supplied SIMULATED data."""
from pathlib import Path

from masp_skill.case import GATE_REQUIREMENTS, create_case, transition_case, validate_case
from masp_skill.evidence import make_evidence
from masp_skill.routing import load_routing


ROOT = Path(__file__).resolve().parents[1]
ROUTING = load_routing(ROOT / "docs/masp/masp-routing.toml")


def _proof(root, phase_id, state, classification="SIMULATED", **metadata):
    path = root / f"{phase_id}-{state.lower()}.txt"
    path.write_text(f"synthetic MASP fixture: {phase_id} {state}\n", encoding="utf-8")
    return make_evidence(
        path, root, classification=classification,
        description=f"Synthetic fixture only: {phase_id} {state}", **metadata,
    )


def test_eight_phases_complete_in_simulated_ledger_with_valid_gates(tmp_path):
    case = create_case("MASP-PR3-PILOT", ROUTING)
    assert case["classification"] == "SIMULATED"
    assert case["schema_version"] == 2

    for index, phase in enumerate(ROUTING["phases"]):
        phase_id, name = phase["id"], phase["name"]
        starting = _proof(tmp_path, phase_id, "START")
        case = transition_case(
            case, "IN_PROGRESS", "masp-coordenador",
            [starting], ROUTING, phase=name if index else None, root=tmp_path,
        )
        evidence_args = {"satisfies": sorted(GATE_REQUIREMENTS[phase_id])}
        if phase_id == "plano-de-acao":
            evidence_args.update(approval_type="human_plan", approved_by="SIMULATED-OPERATOR-LABEL")
        classification = "SIMULATED"
        if phase_id == "verificacao":
            # Intentionally caller-supplied runtime label, NOT an actual Codex/test execution.
            classification = "RUNTIME"
            evidence_args.update(
                role="masp-testador", command="synthetic-command-not-executed",
                exit_code=0, stdout="synthetic stdout",
            )
        approved = _proof(tmp_path, phase_id, "PASS", classification, **evidence_args)
        case = transition_case(
            case, "PASS", "masp-coordenador", [approved], ROUTING, root=tmp_path,
        )
        assert validate_case(case, ROUTING, tmp_path) == []

    assert case["state"] == "PASS"
    assert case["current_phase"] == "Conclusão"
    assert case["classification"] == "SIMULATED"
    assert len(case["ledger"]) == 16
    passed = [event["phase"] for event in case["ledger"] if event["new_state"] == "PASS"]
    assert passed == [phase["name"] for phase in ROUTING["phases"]]
