from copy import deepcopy
from pathlib import Path

from masp_skill.routing import load_routing, validate_routing


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs" / "masp" / "masp-routing.toml"


def test_matrix_has_eight_ordered_phases_and_ten_roles():
    data = load_routing(MATRIX)
    assert [phase["name"] for phase in data["phases"]] == [
        "Identificação", "Observação", "Análise", "Plano de ação",
        "Ação", "Verificação", "Padronização", "Conclusão",
    ]
    assert len(data["roles"]) == 10
    assert validate_routing(data) == []


def test_matrix_has_exact_model_effort_and_skill_references():
    data = load_routing(MATRIX)
    expected = {
        "masp-coordenador": ("gpt-6.1-sol", "medium"),
        "masp-identificador": ("gpt-6-luna", "low"),
        "masp-observador": ("gpt-6-luna", "medium"),
        "masp-analista": ("gpt-6.1-sol", "medium"),
        "masp-planejador": ("gpt-6.1-sol", "medium"),
        "masp-executor": ("gpt-6.1-terra", "medium"),
        "masp-testador": ("gpt-6-luna", "low"),
        "masp-padronizador": ("gpt-6.1-terra", "medium"),
        "masp-relator": ("gpt-6.1-sol", "medium"),
        "masp-especialista-critico": ("gpt-6-astra", "medium"),
    }
    assert {name: (role["model"], role["effort"]) for name, role in data["roles"].items()} == expected
    assert all(phase["skills"] for phase in data["phases"])
    assert all(skill["path"] for phase in data["phases"] for skill in phase["skills"])


def test_matrix_declares_gates_returns_parallelism_audit_and_model_policy():
    data = load_routing(MATRIX)
    assert all(phase["gate"] and phase["returns"] for phase in data["phases"])
    assert data["policies"]["parallelism"]["max_agents"] == 3
    assert data["policies"]["audit"]["independent"] is True
    assert data["policies"]["unavailable_model"]["state"] == "BLOCKED"
    assert data["policies"]["unavailable_model"]["automatic_fallback"] is False
    assert all(phase["inputs"] and phase["outputs"] for phase in data["phases"])
    assert all(phase["tools"] and phase["access_modes"] for phase in data["phases"])
    escalation = data["policies"]["astra_escalation"]
    assert escalation["conditions"]
    assert {"astra_reason", "related_evidence", "coordinator_decision"} <= set(escalation["required_record"])


def test_rejects_invalid_effort_model_missing_phase_and_unregistered_skill():
    base = load_routing(MATRIX)
    data = deepcopy(base)
    data["roles"]["masp-identificador"]["effort"] = "llow"
    assert any("effort" in error.lower() or "esfor" in error.lower() for error in validate_routing(data))

    data = deepcopy(base)
    data["roles"]["masp-identificador"]["model"] = "gpt-fictional"
    assert any("model" in error.lower() or "modelo" in error.lower() for error in validate_routing(data))

    data = deepcopy(base)
    data["phases"].pop(3)
    assert validate_routing(data)

    data = deepcopy(base)
    data["phases"][0]["skills"][0]["path"] = ""
    assert any("skill" in error.lower() for error in validate_routing(data))


def test_rejects_non_table_role_and_invalid_phase_role_reference():
    data = load_routing(MATRIX)
    data["roles"]["masp-identificador"] = "not a table"
    errors = validate_routing(data)
    assert any("masp-identificador" in error and "table" in error.lower() for error in errors)

    data = load_routing(MATRIX)
    data["phases"][0]["role"] = "unknown-role"
    errors = validate_routing(data)
    assert any("role" in error.lower() and "identificacao" in error.lower() for error in errors)


def test_rejects_invalid_return_reference_and_return_types():
    data = load_routing(MATRIX)
    data["phases"][0]["returns"] = ["unknown-phase"]
    errors = validate_routing(data)
    assert any("return" in error.lower() and "identificacao" in error.lower() for error in errors)

    for invalid_returns in ("Observação", [None], [1], []):
        data = load_routing(MATRIX)
        data["phases"][0]["returns"] = invalid_returns
        assert any("return" in error.lower() for error in validate_routing(data))


def test_rejects_missing_phase_contract_fields_and_invalid_types():
    for field, invalid_value in (("inputs", []), ("outputs", "artifact"),
                                 ("tools", ["test_runner", 2]), ("tools", ["imaginary_tool"]),
                                 ("access_modes", ["unknown"])):
        data = load_routing(MATRIX)
        data["phases"][0][field] = invalid_value
        assert any(field.replace("_", " ").split()[0] in error.lower()
                   for error in validate_routing(data))

    data = load_routing(MATRIX)
    data["policies"]["astra_escalation"]["conditions"] = []
    assert any("astra" in error.lower() for error in validate_routing(data))


def test_loader_reads_toml_without_mutating_file(tmp_path):
    copy = tmp_path / "routing.toml"
    copy.write_bytes(MATRIX.read_bytes())
    before = copy.read_bytes()
    assert load_routing(copy)["policies"]["parallelism"]["max_agents"] == 3
    assert copy.read_bytes() == before
