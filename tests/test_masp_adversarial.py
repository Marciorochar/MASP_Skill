"""Adversarial input contract: malformed manifests and TOML must not crash validators."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from masp_skill.case import create_case, transition_case, validate_case
from masp_skill.evidence import make_evidence
from masp_skill.routing import load_routing, validate_routing


ROOT = Path(__file__).resolve().parents[1]
ROUTING = load_routing(ROOT / "docs/masp/masp-routing.toml")


@pytest.mark.parametrize("value", [[], {}, ["2"], {"version": 2}, None, True])
def test_malformed_schema_version_is_reported_without_exception(value):
    case = create_case("MASP-TYPES", ROUTING)
    case["schema_version"] = value
    errors = validate_case(case, ROUTING, ROOT)
    assert any("schema_version" in msg for msg in errors)


@pytest.mark.parametrize("field,value", [
    ("initial_state", []),
    ("initial_state", {"state": "PENDING"}),
    ("state", []),
    ("current_phase", {"phase": "Identificação"}),
])
def test_malformed_case_state_fields_are_reported_without_exception(field, value):
    case = create_case("MASP-STATE-TYPES", ROUTING)
    case[field] = value
    errors = validate_case(case, ROUTING, ROOT)
    assert errors


@pytest.mark.parametrize("field,value", [
    ("new_state", []),
    ("new_state", {"state": "PASS"}),
    ("phase", ["Identificação"]),
])
def test_malformed_event_state_fields_are_reported_without_exception(field, value, tmp_path):
    path = tmp_path / "event-proof.txt"
    path.write_text("observed", encoding="utf-8")
    proof = make_evidence(path, tmp_path, classification="SIMULATED", description="Start record")
    case = transition_case(
        create_case("MASP-EVENT-TYPES", ROUTING), "IN_PROGRESS",
        "masp-coordenador", [proof], ROUTING, root=tmp_path,
    )
    case["ledger"][0][field] = value
    errors = validate_case(case, ROUTING, tmp_path)
    assert errors


@pytest.mark.parametrize("value", [
    ["PASS", []], ["PASS", {"state": "FAIL"}],
])
def test_unhashable_states_in_routing_are_validation_errors(value):
    routing = deepcopy(ROUTING)
    routing["policies"]["states"]["values"] = value
    errors = validate_routing(routing)
    assert any("states" in msg for msg in errors)


@pytest.mark.parametrize("value", [[], {}, {"role": "masp-identificador"}])
def test_unhashable_phase_role_is_validation_error(value):
    routing = deepcopy(ROUTING)
    routing["phases"][0]["role"] = value
    errors = validate_routing(routing)
    assert any("role" in msg for msg in errors)
