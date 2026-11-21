"""Tests for portable skill paths, Phase 5 scope/diff enforcement, and multi-runtime dispatch."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from masp_skill import ergonomics
from masp_skill.case import GATE_REQUIREMENTS, create_case, transition_case, validate_action_scope, validate_case
from masp_skill.cli import main
from masp_skill.evidence import make_evidence
from masp_skill.routing import load_routing, resolve_routing_skill_paths, resolve_skill_path, validate_routing
from masp_skill.runtime_adapter import plan_phase_dispatch, validate_runtime_dispatch_record

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs/masp/masp-routing.toml"
ROUTING = load_routing(MATRIX)


def _proof(tmp_path, phase_id, name, **meta):
    path = tmp_path / name
    path.write_text("synthetic evidence\n", encoding="utf-8")
    return make_evidence(
        path, tmp_path, classification="SIMULATED",
        description=f"Evidence {phase_id}", satisfies=sorted(GATE_REQUIREMENTS[phase_id]), **meta,
    )


def _to_plano_de_acao(tmp_path):
    case = create_case("MASP-SCOPE-01", ROUTING)
    for pid, pname in (("identificacao", None), ("observacao", "Observação"), ("analise", "Análise")):
        case = transition_case(
            case, "IN_PROGRESS", "masp-coordenador",
            [_proof(tmp_path, pid, f"{pid}-start.txt")], ROUTING, phase=pname, root=tmp_path,
        )
        case = transition_case(
            case, "PASS", "masp-coordenador",
            [_proof(tmp_path, pid, f"{pid}-pass.txt")], ROUTING, root=tmp_path,
        )
    return transition_case(
        case, "IN_PROGRESS", "masp-coordenador",
        [_proof(tmp_path, "plano-de-acao", "plan-start.txt")], ROUTING, phase="Plano de ação", root=tmp_path,
    )


def test_routing_matrix_uses_portable_codex_home_placeholder_and_resolves():
    raw_text = MATRIX.read_text(encoding="utf-8")
    assert "C:/Users/marci" not in raw_text
    assert "${CODEX_HOME}/" in raw_text
    assert validate_routing(ROUTING) == []

    custom_home = str(Path("/tmp/custom-codex"))
    resolved = resolve_routing_skill_paths(ROUTING, env={"CODEX_HOME": custom_home})
    assert resolved["superpowers:brainstorming"] == Path(custom_home) / "plugins/cache/openai-curated-remote/superpowers/7.0.1/skills/brainstorming/SKILL.md"

    default_resolved = resolve_skill_path("${CODEX_HOME}/skills/x/SKILL.md", env={})
    assert default_resolved == Path.home() / ".codex/skills/x/SKILL.md"


def test_routing_rejects_unresolved_or_malformed_skill_placeholder():
    with pytest.raises(ValueError, match="unresolved"):
        resolve_skill_path("${MISSING_VAR}/SKILL.md", env={})
    bad = deepcopy(ROUTING)
    bad["phases"][0]["skills"][0]["path"] = "${UNSET_MASP_VAR}/SKILL.md"
    errors = validate_routing(bad)
    assert any("unresolved" in err for err in errors)


def test_action_scope_validation_enforces_allowed_files_subset(tmp_path):
    assert validate_action_scope(["src/billing.py", "tests/"], ["src/billing.py", "tests/test_billing.py"], tmp_path) == []
    errors = validate_action_scope(["src/billing.py"], ["src/billing.py", "src/other.py"], tmp_path)
    assert any("outside authorized allowed_files" in err for err in errors)
    escape_errors = validate_action_scope(["src/billing.py"], ["../secret.txt"], tmp_path)
    assert any("escapes workspace root" in err for err in escape_errors)


def test_transition_enforces_allowed_files_from_plan_during_acao(tmp_path):
    case = _to_plano_de_acao(tmp_path)
    case = transition_case(
        case, "PASS", "masp-coordenador",
        [_proof(
            tmp_path, "plano-de-acao", "plan-pass.txt",
            approval_type="human_plan", approved_by="operator",
            allowed_files=["src/billing.py", "tests/"],
        )],
        ROUTING, root=tmp_path,
    )
    case = transition_case(
        case, "IN_PROGRESS", "masp-coordenador",
        [_proof(tmp_path, "acao", "acao-start.txt")], ROUTING, phase="Ação", root=tmp_path,
    )

    with pytest.raises(ValueError, match="requires modified_files"):
        transition_case(
            case, "PASS", "masp-coordenador",
            [_proof(tmp_path, "acao", "acao-no-diff.txt")], ROUTING, root=tmp_path,
        )

    with pytest.raises(ValueError, match="outside authorized allowed_files"):
        transition_case(
            case, "PASS", "masp-coordenador",
            [_proof(tmp_path, "acao", "acao-bad-diff.txt", modified_files=["src/billing.py", "README.md"])],
            ROUTING, root=tmp_path,
        )

    passed = transition_case(
        case, "PASS", "masp-coordenador",
        [_proof(tmp_path, "acao", "acao-good-diff.txt", modified_files=["src/billing.py", "tests/test_billing.py"])],
        ROUTING, root=tmp_path,
    )
    assert passed["state"] == "PASS"
    assert validate_case(passed, ROUTING, tmp_path) == []


def test_record_evidence_from_git_diff_populates_modified_files(tmp_path, monkeypatch, capsys):
    class Proc:
        returncode = 0
        stdout = "src/billing.py\ntests/test_billing.py\n"
        stderr = ""

    monkeypatch.setattr(ergonomics.subprocess, "run", lambda *a, **kw: Proc())
    target = tmp_path / "acao.txt"
    target.write_text("diff\n", encoding="utf-8")
    assert main([
        "record-evidence", "--output", "ev.json", "--root", str(tmp_path),
        "--file", "acao.txt", "--classification", "STATIC", "--description", "action diff",
        "--gate", "acao", "--from-git-diff",
    ]) == 0
    capsys.readouterr()
    data = json.loads((tmp_path / "ev.json").read_text(encoding="utf-8"))
    assert data[0]["modified_files"] == ["src/billing.py", "tests/test_billing.py"]


def test_runtime_adapter_plans_codex_and_antigravity_safely(capsys):
    obs_plan = plan_phase_dispatch("observacao", ROUTING, runtime="antigravity")
    assert obs_plan["status"] == "READY"
    assert obs_plan["subagent_type"] == "research"
    assert obs_plan["children_may_spawn"] is False
    assert validate_runtime_dispatch_record(obs_plan, "observacao", ROUTING) == []

    acao_plan = plan_phase_dispatch("acao", ROUTING, runtime="antigravity")
    assert acao_plan["status"] == "BLOCKED"
    assert "write-approved" in acao_plan["reason"]

    codex_plan = plan_phase_dispatch("acao", ROUTING, runtime="codex")
    assert codex_plan["status"] == "READY"
    assert codex_plan["role"] == "masp-executor"
    assert validate_runtime_dispatch_record(codex_plan, "acao", ROUTING) == []

    assert main(["dispatch-plan", "--phase", "observacao", "--runtime", "antigravity", "--routing", str(MATRIX)]) == 0
    assert '"subagent_type": "research"' in capsys.readouterr().out
    assert main(["dispatch-plan", "--phase", "acao", "--runtime", "antigravity", "--routing", str(MATRIX)]) == 1
    assert '"status": "BLOCKED"' in capsys.readouterr().out
