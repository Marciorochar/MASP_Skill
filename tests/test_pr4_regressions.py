"""PR4 regression tests: malformed replays, gate IDs, and auditable role inventory.

These tests do not execute the Codex CLI or make claims about real agent execution.
"""
from copy import deepcopy
from pathlib import Path

import pytest

from masp_skill.case import (
    GATE_REQUIREMENTS, _event_hash, create_case, transition_case, validate_case,
)
from masp_skill.cli import _local_smoke_agents, _delegation_events
from masp_skill.evidence import make_evidence
from masp_skill.routing import load_routing, validate_routing


ROOT = Path(__file__).resolve().parents[1]
ROUTING = load_routing(ROOT / "docs/masp/masp-routing.toml")


def _proof(root, phase_id, suffix):
    path = root / f"{phase_id}-{suffix}.txt"
    path.write_text("Synthetic test evidence only\n", encoding="utf-8")
    return make_evidence(path, root, classification="SIMULATED",
                         description="PR4 simulated evidence",
                         satisfies=sorted(GATE_REQUIREMENTS[phase_id]))


def _failed_analysis_case(tmp_path):
    case = create_case("PR4-RETURN-TYPES", ROUTING)
    for phase_id, phase_name in (
        ("identificacao", "Identificação"),
        ("observacao", "Observação"),
        ("analise", "Análise"),
    ):
        case = transition_case(
            case, "IN_PROGRESS", "masp-coordenador",
            [_proof(tmp_path, phase_id, "start")],
            ROUTING, phase=phase_name, root=tmp_path,
        )
        case = transition_case(
            case, "FAIL" if phase_id == "analise" else "PASS",
            "masp-coordenador", [_proof(tmp_path, phase_id, "end")],
            ROUTING, root=tmp_path,
        )
    assert case["state"] == "FAIL" and case["current_phase"] == "Análise"
    assert validate_case(case, ROUTING, tmp_path) == []
    return case


@pytest.mark.parametrize("malformed", [[], {}, ["IN_PROGRESS"], {"state": "IN_PROGRESS"}])
def test_rehashed_return_after_fail_rejects_unhashable_new_state_without_crash(tmp_path, malformed):
    case = _failed_analysis_case(tmp_path)
    event = {
        "sequence": len(case["ledger"]) + 1,
        "phase": "Observação",
        "previous_state": "FAIL",
        "new_state": malformed,
        "actor": "masp-coordenador",
        "timestamp": "2026-11-16T12:00:00+00:00",
        "evidence": [_proof(tmp_path, "observacao", "malformed")],
        "classification": "SIMULATED",
        "previous_hash": case["ledger"][-1]["event_hash"],
    }
    event["event_hash"] = _event_hash(event)
    case["ledger"].append(event)
    errors = validate_case(case, ROUTING, tmp_path)
    assert any("illegal state transition" in error for error in errors)
    assert not any("hash mismatch" in error for error in errors)


def test_routing_rejects_unknown_id_even_with_correct_phase_names():
    changed = deepcopy(ROUTING)
    changed["phases"][0]["id"] = "not-identificacao"
    errors = validate_routing(changed)
    assert any("identificacao" in e and "id" in e for e in errors)


def test_routing_rejects_swapped_ids_even_with_correct_phase_names():
    changed = deepcopy(ROUTING)
    changed["phases"][0]["id"], changed["phases"][1]["id"] = (
        changed["phases"][1]["id"], changed["phases"][0]["id"],
    )
    errors = validate_routing(changed)
    assert any("id" in e and "phase" in e for e in errors)


def test_static_inventory_includes_critical_astra_without_invoking_it():
    agents = _local_smoke_agents(ROOT)
    assert len(agents) == 10
    assert agents["masp-especialista-critico"]["model"] == "gpt-6-astra"


def test_unattributed_wait_events_cannot_prove_spawn_or_completion():
    # Shape taken from the repository's historical Codex JSONL (wait without recipients).
    records = [
        {"type": "item.started", "item": {"type": "collab_tool_call",
         "tool": "wait", "receiver_thread_ids": [], "agents_states": {},
         "status": "in_progress"}},
        {"type": "item.completed", "item": {"type": "collab_tool_call",
         "tool": "wait", "receiver_thread_ids": [], "agents_states": {},
         "status": "completed"}},
    ]
    import json
    result = _delegation_events("\n".join(json.dumps(x) for x in records),
                                ["masp-identificador"])["masp-identificador"]
    assert result["tool_call"] is False
    assert result["completion"] is False


def test_collab_spawn_with_correlated_receiver_and_completed_state_is_recognized():
    # Synthetic schema compatibility test, NOT evidence of a real Codex delegation.
    import json
    records = [
        {"type": "item.started", "item": {"type": "collab_tool_call",
         "tool": "spawn_agent", "agent_type": "masp-identificador",
         "receiver_thread_ids": ["child-1"],
         "agents_states": {"child-1": {"status": "in_progress"}},
         "status": "in_progress"}},
        {"type": "item.completed", "item": {"type": "collab_tool_call",
         "tool": "spawn_agent", "agent_type": "masp-identificador",
         "receiver_thread_ids": ["child-1"],
         "agents_states": {"child-1": {"status": "completed"}},
         "status": "completed"}},
    ]
    result = _delegation_events("\n".join(json.dumps(x) for x in records),
                                ["masp-identificador"])["masp-identificador"]
    assert result["tool_call"] is True
    assert result["completion"] is True
    assert result["agent_id"] == "child-1"
    assert result["observed_model"] is None
    assert result["observed_effort"] is None


def test_collab_spawn_without_explicit_role_must_not_be_attributed():
    import json
    record = {"type": "item.completed", "item": {"type": "collab_tool_call",
              "tool": "spawn_agent", "receiver_thread_ids": ["child-1"],
              "agents_states": {"child-1": {"status": "completed"}},
              "status": "completed"}}
    result = _delegation_events(json.dumps(record), ["masp-identificador"])["masp-identificador"]
    assert result["tool_call"] is False
    assert result["completion"] is False
