"""Semantic structure checks for Markdown evidence documents against MASP gate criteria."""
from pathlib import Path

import pytest

from masp_skill.case import GATE_REQUIREMENTS, _event_hash, create_case, transition_case, validate_case
from masp_skill.cli import main
from masp_skill.documents import check_markdown_criteria
from masp_skill.evidence import make_evidence
from masp_skill.routing import load_routing

ROOT = Path(__file__).resolve().parents[1]
ROUTING = load_routing(ROOT / "docs/masp/masp-routing.toml")


def _txt_evidence(tmp_path, phase_id, name, **meta):
    target = tmp_path / name
    target.write_text("synthetic non-markdown evidence\n", encoding="utf-8")
    return make_evidence(
        target, tmp_path, classification="SIMULATED",
        description=f"Fixture for {phase_id}", satisfies=sorted(GATE_REQUIREMENTS[phase_id]), **meta,
    )


def _advance_to_phase(tmp_path, target_phase):
    case = create_case("MASP-DOC-CHECK", ROUTING)
    for phase in ROUTING["phases"]:
        pid, pname = phase["id"], phase["name"]
        case = transition_case(
            case, "IN_PROGRESS", "masp-coordenador",
            [_txt_evidence(tmp_path, pid, f"{pid}-start.txt")],
            ROUTING, phase=pname if pid != "identificacao" else None, root=tmp_path,
        )
        if pname == target_phase:
            return case
        extra = {"approval_type": "human_plan", "approved_by": "operator"} if pid == "plano-de-acao" else {}
        case = transition_case(
            case, "PASS", "masp-coordenador",
            [_txt_evidence(tmp_path, pid, f"{pid}-pass.txt", **extra)],
            ROUTING, root=tmp_path,
        )
    return case


def test_check_markdown_criteria_accepts_headings_and_bold_labels():
    doc = (
        "# Análise\n"
        "## Hipóteses\n"
        "- H1: Erro de arredondamento em float.\n"
        "- **Evidências:** Log de execução mostrou 0.30000000000000004.\n"
        "## Causa raiz\n"
        "Uso de float IEEE 754 em vez de Decimal.\n"
    )
    assert check_markdown_criteria(doc, GATE_REQUIREMENTS["analise"]) == []


def test_check_markdown_criteria_rejects_missing_empty_placeholder_and_fenced_sections():
    bad_doc = (
        "# Análise\n"
        "```markdown\n"
        "## Hipóteses\n"
        "Falso cabeçalho dentro de bloco de código.\n"
        "```\n"
        "## Evidências\n"
        "TODO\n"
        "## Causa raiz\n"
        "[preencher]\n"
    )
    errors = check_markdown_criteria(bad_doc, GATE_REQUIREMENTS["analise"])
    assert any("hypotheses" in err and "no heading or label" in err for err in errors)
    assert any("evidence_for_and_against" in err and "empty or only a placeholder" in err for err in errors)
    assert any("root_cause_or_explicit_inconclusive" in err and "empty or only a placeholder" in err for err in errors)


def test_transition_rejects_incomplete_markdown_on_analise_and_plano_de_acao(tmp_path):
    case = _advance_to_phase(tmp_path, "Análise")

    incomplete_analise = tmp_path / "analise-incompleta.md"
    incomplete_analise.write_text("# Análise\n- Hipóteses: apenas uma linha de teste.\n", encoding="utf-8")
    ev_bad = make_evidence(
        incomplete_analise, tmp_path, classification="STATIC",
        description="Análise incompleta", satisfies=sorted(GATE_REQUIREMENTS["analise"]),
    )
    with pytest.raises(ValueError, match="root_cause_or_explicit_inconclusive"):
        transition_case(case, "PASS", "masp-coordenador", [ev_bad], ROUTING, root=tmp_path)

    valid_analise = tmp_path / "analise-completa.md"
    valid_analise.write_text(
        "- **Hipóteses:** H1 confirmada por reprodução local.\n"
        "- **Evidências:** Saída do pytest mostrou divergência de centavos.\n"
        "- **Causa raiz:** Acúmulo em ponto flutuante binário.\n",
        encoding="utf-8",
    )
    ev_ok = make_evidence(
        valid_analise, tmp_path, classification="STATIC",
        description="Análise completa", satisfies=sorted(GATE_REQUIREMENTS["analise"]),
    )
    case = transition_case(case, "PASS", "masp-coordenador", [ev_ok], ROUTING, root=tmp_path)

    case = transition_case(
        case, "IN_PROGRESS", "masp-coordenador",
        [_txt_evidence(tmp_path, "plano-de-acao", "plan-start.txt")],
        ROUTING, phase="Plano de ação", root=tmp_path,
    )
    bad_plan = tmp_path / "plano-sem-rollback.md"
    bad_plan.write_text(
        "- Tarefas: refatorar billing.py para Decimal.\n"
        "- Responsáveis: masp-executor e masp-testador.\n"
        "- Escopo: restrito a billing.py.\n"
        "- Riscos: TBD\n"
        "- Testes: executar pytest após alteração.\n",
        encoding="utf-8",
    )
    ev_bad_plan = make_evidence(
        bad_plan, tmp_path, classification="STATIC",
        description="Plano sem rollback e com risco TBD",
        approval_type="human_plan", approved_by="operator",
        satisfies=sorted(GATE_REQUIREMENTS["plano-de-acao"]),
    )
    with pytest.raises(ValueError, match="risks"):
        transition_case(case, "PASS", "masp-coordenador", [ev_bad_plan], ROUTING, root=tmp_path)


def test_validate_case_replay_catches_rehashed_empty_markdown_section(tmp_path):
    case = _advance_to_phase(tmp_path, "Análise")
    doc = tmp_path / "analise.md"
    doc.write_text(
        "## Hipóteses\nH1 testada com caso mínimo.\n"
        "## Evidências\nLog capturado em execução local.\n"
        "## Causa raiz\nFalta de validação explícita.\n",
        encoding="utf-8",
    )
    ev = make_evidence(doc, tmp_path, classification="STATIC", description="Análise", satisfies=sorted(GATE_REQUIREMENTS["analise"]))
    case = transition_case(case, "PASS", "masp-coordenador", [ev], ROUTING, root=tmp_path)
    assert validate_case(case, ROUTING, tmp_path) == []

    # Simulate tampering with both the Markdown file and its SHA-256 + event_hash.
    doc.write_text("## Hipóteses\nH1 testada.\n## Evidências\nLog capturado.\n## Causa raiz\nTODO\n", encoding="utf-8")
    new_ev = make_evidence(doc, tmp_path, classification="STATIC", description="Análise", evidence_id=ev["id"], satisfies=sorted(GATE_REQUIREMENTS["analise"]))
    case["ledger"][-1]["evidence"] = [new_ev]
    case["ledger"][-1]["event_hash"] = _event_hash(case["ledger"][-1])
    errors = validate_case(case, ROUTING, tmp_path)
    assert any("root_cause_or_explicit_inconclusive" in err for err in errors)


def test_cli_validate_document_command(tmp_path, capsys):
    doc = tmp_path / "plano.md"
    doc.write_text(
        "# Plano\n"
        "- **Tarefas:** atualizar módulo e suíte de testes.\n"
        "- **Responsáveis:** masp-executor.\n"
        "- **Escopo:** apenas src/app.py.\n"
        "- **Riscos:** quebra de compatibilidade mitigada por testes.\n"
        "- **Rollback:** git revert do commit.\n"
        "- **Testes:** python -m pytest -q.\n",
        encoding="utf-8",
    )
    assert main(["validate-document", "--file", "plano.md", "--gate", "plano-de-acao", "--root", str(tmp_path)]) == 0
    assert "cobre as seções" in capsys.readouterr().out

    bad = tmp_path / "analise-vazia.md"
    bad.write_text("# Análise\nSem seções obrigatórias.\n", encoding="utf-8")
    assert main(["validate-document", "--file", "analise-vazia.md", "--gate", "analise", "--root", str(tmp_path)]) == 1
    assert "hypotheses" in capsys.readouterr().out

    outside = tmp_path.parent / "outside-doc.md"
    outside.write_text("# Outside\n", encoding="utf-8")
    assert main(["validate-document", "--file", str(outside), "--gate", "analise", "--root", str(tmp_path)]) == 1
    capsys.readouterr()
