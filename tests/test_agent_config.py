from pathlib import Path

from masp_skill.routing import (
    load_agent_configs,
    load_routing,
    validate_agent_configs,
)


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs" / "masp" / "masp-routing.toml"
AGENTS = ROOT / ".codex" / "agents"


def test_local_agent_registry_references_ten_existing_role_files():
    import tomllib

    with (ROOT / ".codex" / "config.toml").open("rb") as stream:
        config = tomllib.load(stream)
    routing = load_routing(MATRIX)
    agents = load_agent_configs(ROOT)

    assert config["agents"]["max_threads"] == 3
    assert set(agents) == set(routing["roles"])
    assert validate_agent_configs(routing, agents) == []
    for name in agents:
        assert (AGENTS / f"{name}.toml").is_file()


def test_agent_configs_match_routing_model_and_effort():
    routing = load_routing(MATRIX)
    agents = load_agent_configs(ROOT)

    for name, role in routing["roles"].items():
        assert agents[name]["model"] == role["model"]
        assert agents[name]["model_reasoning_effort"] == role["effort"]


def test_children_cannot_spawn_coordinator_is_only_delegator_and_executor_cannot_self_approve():
    agents = load_agent_configs(ROOT)

    for name, agent in agents.items():
        if name != "masp-coordenador":
            assert "não cri" in agent["developer_instructions"].lower() or "não deleg" in agent["developer_instructions"].lower()
    coordinator = agents["masp-coordenador"]["developer_instructions"].lower()
    executor = agents["masp-executor"]["developer_instructions"].lower()
    assert "somente" in coordinator and "deleg" in coordinator
    assert "não aprove" in executor and ("própria" in executor or "si mesmo" in executor)


def test_critical_auditor_has_no_write_authority():
    instructions = load_agent_configs(ROOT)["masp-especialista-critico"]["developer_instructions"].lower()
    assert "não implement" in instructions
    assert "não edit" in instructions or "sem escrita" in instructions


def test_cross_validation_rejects_missing_role_model_effort_and_child_delegation(tmp_path):
    routing = load_routing(MATRIX)
    configs = load_agent_configs(ROOT)

    missing = dict(configs)
    missing.pop("masp-observador")
    assert any("masp-observador" in error for error in validate_agent_configs(routing, missing))

    wrong_model = {key: dict(value) for key, value in configs.items()}
    wrong_model["masp-observador"]["model"] = "gpt-6.1-sol"
    assert any("model" in error.lower() for error in validate_agent_configs(routing, wrong_model))

    wrong_effort = {key: dict(value) for key, value in configs.items()}
    wrong_effort["masp-observador"]["model_reasoning_effort"] = "low"
    assert any("effort" in error.lower() for error in validate_agent_configs(routing, wrong_effort))

    child_spawn = {key: dict(value) for key, value in configs.items()}
    child_spawn["masp-observador"]["developer_instructions"] = "You may delegate and spawn subagents."
    assert validate_agent_configs(routing, child_spawn)
