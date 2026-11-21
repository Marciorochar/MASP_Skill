"""Runtime-agnostic subagent dispatch contracts for MASP phases.

Supports planning and validating dispatches for:
- ``codex``: Codex CLI local subagents declared in ``.codex/config.toml``.
- ``antigravity``: Antigravity ``research`` read-only subagent for read-only
  phases (Identificação, Observação, Análise, Conclusão) and execution-gated
  phases (Verificação, etc.) only when write access is not required.

This module produces dispatch contracts and validates dispatch records; it does
not invoke any external agent runtime by itself.
"""

from __future__ import annotations

from typing import Any

SUPPORTED_RUNTIMES = ("codex", "antigravity")
READ_ONLY_ONLY_RUNTIMES = frozenset({"antigravity"})


def _find_phase(routing: dict[str, Any], phase_ref: str) -> dict[str, Any]:
    for phase in routing.get("phases", []):
        if isinstance(phase, dict) and (phase.get("id") == phase_ref or phase.get("name") == phase_ref):
            return phase
    raise ValueError(f"unknown phase {phase_ref!r}")


def plan_phase_dispatch(
    phase_ref: str,
    routing: dict[str, Any],
    *,
    runtime: str = "codex",
    objective: str = "",
) -> dict[str, Any]:
    """Build a dispatch contract for ``phase_ref`` on ``runtime`` respecting access_modes."""
    if runtime not in SUPPORTED_RUNTIMES:
        raise ValueError(f"unsupported runtime {runtime!r}; expected one of {SUPPORTED_RUNTIMES}")
    phase = _find_phase(routing, phase_ref)
    role_name = phase.get("role", "")
    role_cfg = routing.get("roles", {}).get(role_name, {})
    access_modes = list(phase.get("access_modes", []))
    requires_write = "write-approved" in access_modes

    if runtime == "codex":
        return {
            "runtime": "codex",
            "status": "READY",
            "phase_id": phase.get("id"),
            "phase_name": phase.get("name"),
            "role": role_name,
            "model": role_cfg.get("model"),
            "effort": role_cfg.get("effort"),
            "access_modes": access_modes,
            "children_may_spawn": False,
            "tool": "spawn_agent",
            "prompt_contract": {
                "objective": objective or f"Execute MASP phase {phase.get('name')} as {role_name}.",
                "inputs": list(phase.get("inputs", [])),
                "expected_outputs": list(phase.get("outputs", [])),
                "gate": phase.get("gate"),
            },
        }

    # Antigravity runtime: read-only phases map to invoke_subagent(TypeName="research").
    if requires_write:
        return {
            "runtime": "antigravity",
            "status": "BLOCKED",
            "reason": (
                f"phase {phase.get('name')!r} requires write-approved access; "
                "Antigravity read-only 'research' subagent cannot perform approved writes"
            ),
            "phase_id": phase.get("id"),
            "phase_name": phase.get("name"),
            "role": role_name,
            "access_modes": access_modes,
            "children_may_spawn": False,
            "subagent_type": None,
        }

    return {
        "runtime": "antigravity",
        "status": "READY",
        "phase_id": phase.get("id"),
        "phase_name": phase.get("name"),
        "role": role_name,
        "access_modes": ["read-only"],
        "children_may_spawn": False,
        "tool": "invoke_subagent",
        "subagent_type": "research",
        "role_title": f"MASP {phase.get('name')} ({role_name})",
        "prompt_contract": {
            "objective": objective or f"Investigate MASP phase {phase.get('name')} in read-only mode.",
            "inputs": list(phase.get("inputs", [])),
            "expected_outputs": list(phase.get("outputs", [])),
            "gate": phase.get("gate"),
            "prohibitions": [
                "read-only only: do not modify workspace files",
                "do not spawn child subagents",
                "do not self-approve gates",
            ],
        },
    }


def validate_runtime_dispatch_record(
    record: dict[str, Any],
    phase_ref: str,
    routing: dict[str, Any],
) -> list[str]:
    """Validate a recorded subagent dispatch contract against routing policies."""
    if not isinstance(record, dict):
        return ["dispatch record must be a JSON object"]
    errors: list[str] = []
    runtime = record.get("runtime")
    if runtime not in SUPPORTED_RUNTIMES:
        errors.append(f"unsupported runtime {runtime!r}")
        return errors
    try:
        phase = _find_phase(routing, phase_ref)
    except ValueError as exc:
        return [str(exc)]
    if record.get("role") != phase.get("role"):
        errors.append(f"dispatch role {record.get('role')!r} does not match phase role {phase.get('role')!r}")
    if record.get("children_may_spawn") is not False:
        errors.append("dispatch contract must set children_may_spawn=false")
    if runtime == "antigravity":
        if "write-approved" in phase.get("access_modes", []) and record.get("status") == "READY":
            errors.append("antigravity read-only 'research' subagent cannot be READY for write-approved phases")
        if record.get("status") == "READY" and record.get("subagent_type") != "research":
            errors.append("antigravity read-only dispatch must use subagent_type='research'")
    return errors
