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
            if not phase.get(key):
                errors.append(f"phase {index + 1} is missing {key}")
        if not isinstance(phase.get("returns"), list) or not phase.get("returns"):
            errors.append(f"phase {index + 1} must declare permitted returns")
        skills = phase.get("skills")
        if not isinstance(skills, list) or not skills:
            errors.append(f"phase {index + 1} must declare registered skills")
        else:
            for skill in skills:
                if not isinstance(skill, dict) or not skill.get("name") or not skill.get("path"):
                    errors.append(f"phase {index + 1} has a skill without a registered name and path")

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
            continue
        model, effort = role.get("model"), role.get("effort")
        if model not in VALID_MODELS or model != expected[0]:
            errors.append(f"role {name} has invalid model {model!r}; expected {expected[0]}")
        if effort not in VALID_EFFORTS or effort != expected[1]:
            errors.append(f"role {name} has invalid effort {effort!r}; expected {expected[1]}")
        if not role.get("responsibility"):
            errors.append(f"role {name} is missing responsibility")

    policies = data.get("policies")
    if not isinstance(policies, dict):
        errors.append("policies must be a table")
        return errors
    parallelism = policies.get("parallelism", {})
    if not isinstance(parallelism, dict) or parallelism.get("max_agents") != 3:
        errors.append("parallelism max_agents must be 3")
    unavailable = policies.get("unavailable_model", {})
    if (not isinstance(unavailable, dict) or unavailable.get("state") != "BLOCKED"
            or unavailable.get("automatic_fallback") is not False):
        errors.append("unavailable model policy must block and prohibit automatic fallback")
    audit = policies.get("audit", {})
    if not isinstance(audit, dict) or audit.get("independent") is not True:
        errors.append("audit policy must require independent review")
    states = policies.get("states", {})
    if not isinstance(states, dict) or not isinstance(states.get("values"), list) or set(states["values"]) != {
        "PENDING", "IN_PROGRESS", "PASS", "FAIL", "BLOCKED", "NOT_RUN"
    }:
        errors.append("policies must declare the six supported states")
    return errors
