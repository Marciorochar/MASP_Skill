"""Load and statically validate the repository's MASP routing matrix."""

from pathlib import Path
import tomllib
from typing import Any


PHASES = (
    "Identificação", "Observação", "Análise", "Plano de ação",
    "Ação", "Verificação", "Padronização", "Conclusão",
)
ROLE_MODELS = {
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
VALID_MODELS = {model for model, _ in ROLE_MODELS.values()}
VALID_EFFORTS = {"low", "medium", "high"}
VALID_ACCESS_MODES = {"read-only", "write-approved", "execute-approved", "delegate"}
VALID_TOOLS = {"filesystem", "version_control", "test_runner"}
ASTRA_CONDITIONS = {
    "concurrency_or_deadlock", "security", "complex_reverse_engineering",
    "critical_architecture_decision", "grave_contradictory_evidence",
    "high_risk_change", "persistent_problem_after_systematic_diagnosis",
}


def load_agent_configs(root: Path) -> dict[str, dict[str, Any]]:
    """Load repository-local agent contracts referenced by .codex/config.toml."""
    root = Path(root)
    config_path = root / ".codex" / "config.toml"
    with config_path.open("rb") as stream:
        config = tomllib.load(stream)
    registry = config.get("agents", {})
    result: dict[str, dict[str, Any]] = {}
    for name, entry in registry.items():
        if name == "max_threads" or not isinstance(entry, dict):
            continue
        relative_path = entry.get("config_file")
        if not isinstance(relative_path, str):
            result[name] = {}
            continue
        agent_path = root / ".codex" / relative_path
        with agent_path.open("rb") as stream:
            result[name] = tomllib.load(stream)
    return result


def validate_agent_configs(routing: dict[str, Any], agents: dict[str, dict[str, Any]]) -> list[str]:
    """Validate local agent contracts against routing roles and authority rules."""
    errors: list[str] = []
    expected_roles = routing.get("roles", {})
    if not isinstance(expected_roles, dict):
        return ["routing roles must be a table"]
    for name in sorted(set(expected_roles) - set(agents)):
        errors.append(f"missing agent config for {name}")
    for name in sorted(set(agents) - set(expected_roles)):
        errors.append(f"unexpected agent config for {name}")
    for name, expected in expected_roles.items():
        agent = agents.get(name)
        if not isinstance(agent, dict):
            continue
        if agent.get("name") != name:
            errors.append(f"agent {name} has mismatched name")
        if agent.get("model") != expected.get("model"):
            errors.append(f"agent {name} model does not match routing")
        if agent.get("model_reasoning_effort") != expected.get("effort"):
            errors.append(f"agent {name} effort does not match routing")
        instructions = str(agent.get("developer_instructions", "")).lower()
        if not instructions.strip():
            errors.append(f"agent {name} is missing developer instructions")
        if name != "masp-coordenador" and not any(
            phrase in instructions for phrase in ("não crie subagentes", "não delegue", "must not spawn", "must not delegate")
        ):
            errors.append(f"agent {name} must prohibit spawning or delegation")
    coordinator = str(agents.get("masp-coordenador", {}).get("developer_instructions", "")).lower()
    if "deleg" not in coordinator or "somente" not in coordinator:
        errors.append("coordinator must be the exclusive delegator")
    executor = str(agents.get("masp-executor", {}).get("developer_instructions", "")).lower()
    if "não aprov" not in executor:
        errors.append("executor must not self-approve")
    auditor = str(agents.get("masp-especialista-critico", {}).get("developer_instructions", "")).lower()
    if "não implement" not in auditor or not ("não edit" in auditor or "sem escrita" in auditor):
        errors.append("critical auditor must be read-only")
    return errors


def load_routing(path: Path) -> dict[str, Any]:
    """Load a TOML routing matrix from *path*."""
    with Path(path).open("rb") as stream:
        return tomllib.load(stream)


def validate_routing(data: dict[str, Any]) -> list[str]:
    """Return deterministic schema and policy errors without changing data."""
    errors: list[str] = []
    phases = data.get("phases")
    if not isinstance(phases, list):
        errors.append("phases must be an array of phase tables")
        phases = []
    names = [phase.get("name") for phase in phases if isinstance(phase, dict)]
    if names != list(PHASES):
        errors.append("phases must contain the eight required names in order")
    if len(phases) != 8:
        errors.append("phases must contain exactly eight entries")
    for index, phase in enumerate(phases):
        if not isinstance(phase, dict):
            errors.append(f"phase {index + 1} must be a table")
            continue
        for key in ("id", "name", "role", "gate"):
            if not isinstance(phase.get(key), str) or not phase[key].strip():
                errors.append(f"phase {index + 1} is missing {key}")
        phase_id = phase.get("id") if isinstance(phase.get("id"), str) else str(index + 1)
        role_ref = phase.get("role")
        if isinstance(role_ref, str) and role_ref not in ROLE_MODELS:
            errors.append(f"phase {phase_id} references unknown role {role_ref!r}")
        returns = phase.get("returns")
        if not isinstance(returns, list) or not returns:
            errors.append(f"phase {phase_id} must declare permitted returns as a non-empty list")
        elif any(not isinstance(target, str) or target not in PHASES for target in returns):
            errors.append(f"phase {phase_id} has invalid return phase reference(s)")
        for field in ("inputs", "outputs"):
            value = phase.get(field)
            if not isinstance(value, list) or not value or any(
                not isinstance(item, str) or not item.strip() for item in value
            ):
                errors.append(f"phase {phase_id} {field} must be a non-empty list of strings")
        tools = phase.get("tools")
        if not isinstance(tools, list) or not tools or any(
            not isinstance(tool, str) or tool not in VALID_TOOLS for tool in tools
        ):
            errors.append(f"phase {phase_id} tools contains an invalid or missing tool")
        access_modes = phase.get("access_modes")
        if not isinstance(access_modes, list) or not access_modes or any(
            not isinstance(mode, str) or mode not in VALID_ACCESS_MODES for mode in access_modes
        ):
            errors.append(f"phase {phase_id} access_modes contains an invalid or missing mode")
        skills = phase.get("skills")
        if not isinstance(skills, list) or not skills:
            errors.append(f"phase {index + 1} must declare registered skills")
        else:
            for skill in skills:
                if (not isinstance(skill, dict) or not isinstance(skill.get("name"), str)
                        or not skill["name"].strip() or not isinstance(skill.get("path"), str)
                        or not skill["path"].strip()):
                    errors.append(f"phase {phase_id} has a skill without a registered name and path")

    roles = data.get("roles")
    if not isinstance(roles, dict):
        errors.append("roles must be a table")
        roles = {}
    if set(roles) != set(ROLE_MODELS):
        missing = sorted(set(ROLE_MODELS) - set(roles))
        extra = sorted(set(roles) - set(ROLE_MODELS))
        errors.append(f"roles mismatch; missing={missing}, extra={extra}")
    for name, expected in ROLE_MODELS.items():
        role = roles.get(name)
        if not isinstance(role, dict):
            if name in roles:
                errors.append(f"role {name} must be a table")
            continue
        model, effort = role.get("model"), role.get("effort")
        if not isinstance(model, str) or model not in VALID_MODELS or model != expected[0]:
            errors.append(f"role {name} has invalid model {model!r}; expected {expected[0]}")
        if not isinstance(effort, str) or effort not in VALID_EFFORTS or effort != expected[1]:
            errors.append(f"role {name} has invalid effort {effort!r}; expected {expected[1]}")
        if not isinstance(role.get("responsibility"), str) or not role["responsibility"].strip():
            errors.append(f"role {name} is missing responsibility")

    policies = data.get("policies")
    if not isinstance(policies, dict):
        errors.append("policies must be a table")
        return errors
    parallelism = policies.get("parallelism", {})
    if not isinstance(parallelism, dict) or parallelism.get("max_agents") != 3:
        errors.append("parallelism max_agents must be 3")
    elif parallelism.get("effective_runtime_limit_applies") is not True or parallelism.get("same_write_file") != "reject":
        errors.append("parallelism must apply the effective runtime limit and reject same-file writers")
    unavailable = policies.get("unavailable_model", {})
    if (not isinstance(unavailable, dict) or unavailable.get("state") != "BLOCKED"
            or unavailable.get("automatic_fallback") is not False):
        errors.append("unavailable model policy must block and prohibit automatic fallback")
    audit = policies.get("audit", {})
    if not isinstance(audit, dict) or audit.get("independent") is not True:
        errors.append("audit policy must require independent review")
    astra = policies.get("astra_escalation")
    if not isinstance(astra, dict):
        errors.append("astra escalation policy must be a table")
    else:
        conditions = astra.get("conditions")
        if (not isinstance(conditions, list) or any(not isinstance(item, str) for item in conditions)
                or set(conditions) != ASTRA_CONDITIONS):
            errors.append("astra escalation policy must declare all supported conditions")
        required_record = astra.get("required_record")
        if (not isinstance(required_record, list)
                or any(not isinstance(item, str) for item in required_record)
                or not {"astra_reason", "related_evidence", "coordinator_decision"} <= set(required_record)):
            errors.append("astra escalation policy must require reason, evidence, and coordinator decision")
        if astra.get("high_risk_requires_astra") is not True:
            errors.append("astra escalation must be required for high-risk cases")
        if astra.get("astra_unavailable_state") != "BLOCKED":
            errors.append("astra unavailability must block the case")
        if astra.get("substitution_requires_human_approval") is not True:
            errors.append("astra substitution must require human approval")
        if astra.get("first_test_failure_triggers") is not False:
            errors.append("first test failure must not trigger astra automatically")
    states = policies.get("states", {})
    if not isinstance(states, dict) or not isinstance(states.get("values"), list) or set(states["values"]) != {
        "PENDING", "IN_PROGRESS", "PASS", "FAIL", "BLOCKED", "NOT_RUN"
    }:
        errors.append("policies must declare the six supported states")
    return errors
