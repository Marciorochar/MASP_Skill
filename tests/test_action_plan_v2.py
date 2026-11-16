"""Tests for the optional MASP universal action-plan sidecar.

Checks declared structure only. Does not verify true approvals or interventions.
"""
import copy
import json
from pathlib import Path

import pytest

from masp_skill.action_plan import validate_action_plan_record
from masp_skill.case import GATE_REQUIREMENTS
from masp_skill.cli import main


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "tests/fixtures/plano-acao-v2/casos.json"


def valid_plan(*, analysis_status="supported", approval="pending", rollback_type="reversible"):
    intervention = "corrective" if analysis_status == "supported" else "investigative"
    action = {
        "id": "A1", "description": "Medida ilustrativa de baixa interferência",
        "rationale": "Alternativa delimitada pelas fontes, sem intervenção real",
        "evidence_reference": "M03-H1", "intervention_type": intervention,
        "feasibility": "Viável somente mediante autorização e recursos",
        "selection_rationale": "Menor mudança adequada aos riscos e às informações"
    }
    rollback = {
        "task_id": "T1", "type": rollback_type, "owner_id": "P1",
        "trigger": "Critério de interrupção alcançado"
    }
    if rollback_type == "reversible":
        rollback.update({"procedure": "Retornar configuração/documento ao estado inicial autorizado",
                         "verification": "Conferir condição original após reversão"})
    elif rollback_type == "partial":
        rollback.update({"procedure": "Restaurar parcela reversível",
                         "contingency": "Isolar impactos residuais",
                         "irreversible_stage": "Etapa física final",
                         "verification": "Inspecionar condição residual"})
    else:
        rollback.update({"justification": "A mudança envolve alteração física não revertível",
                         "point_of_no_return": "Antes da modificação física",
                         "stop_before_point": "Interromper se condições de segurança não forem comprovadas",
                         "contingency": "Aplicar medidas mitigadoras sob supervisão"})

    record = {
        "case_id": "MASP-PLANO-001",
        "problem_reference": "MASP-ID-001",
        "analysis_reference": "MASP-ANALISE-001",
        "analysis_status": analysis_status,
        "plan_objective": "Preparar intervenção controlada, sem executá-la",
        "alternatives": [
            action,
            {
                "id": "A2", "description": "Monitoramento adicional",
                "rationale": "Alternativa considerada com menor interferência",
                "evidence_reference": "M03-H1",
                "intervention_type": "monitoring",
                "feasibility": "Depende dos registros disponíveis",
                "selection_rationale": "Não selecionada em face das evidências"
            }
        ],
        "selected_actions": ["A1"],
        "tasks": [{
            "id": "T1", "alternative_id": "A1",
            "what": "Preparar modificação aprovada", "why": "Relacionada à hipótese avaliada",
            "where": "Processo ilustrativo", "when": "Após autorização formal",
            "who": "P1", "how": "Seguir procedimento controlado",
            "how_much": {"status": "unknown", "reason": "Orçamento pendente"},
            "dependencies": [], "expected_result": "Condição verificável em teste futuro"
        }],
        "owners": [
            {"id": "P1", "role": "Responsável pela intervenção"},
            {"id": "P2", "role": "Responsável independente pela verificação"}
        ],
        "scope": {"included": "Uma unidade ilustrativa", "excluded": "Produção, terceiros e outras unidades"},
        "risks": [{
            "id": "R1", "task_id": "T1", "description": "Impacto indesejado",
            "preventive_control": "Conferir condições antes da ação",
            "mitigation": "Isolar a etapa afetada",
            "stop_condition": "Desvio do controle previsto",
            "residual_risk": "Risco não quantificado, com avaliação pendente"
        }],
        "rollback": [rollback],
        "tests": [{
            "id": "V1", "task_id": "T1",
            "baseline": {"type": "known", "description": "Situação inicial documentada",
                         "source": "Registro ilustrativo M02"},
            "indicator": "Condição observável", "method": "Comparação documentada",
            "expected_result": "Critério melhorado em escala-piloto",
            "acceptance": "Comparação demonstra a condição requerida",
            "failure": "Condição requerida não demonstrada",
            "stop_condition": "Agravamento ou efeito colateral",
            "verification_owner_id": "P2"
        }],
        "human_approval": {"status": approval, "reason": "Aguardando autorização externa"},
        "limitations": ["Exemplo sintético sem autorização ou execução real"]
    }
    if approval == "approved":
        record["human_approval"] = {
            "status": "approved", "approved_by": "Responsável humano declarado",
            "approval_reference": "DOCUMENTO-APROVACAO-FICTICIO",
            "approved_scope": "Unidade ilustrativa",
            "approved_at": "2026-11-16"
        }
    return record


@pytest.mark.parametrize("status", ["supported", "inconclusive"])
def test_valid_contexts_accept_planning_with_pending_approval(status):
    assert validate_action_plan_record(valid_plan(analysis_status=status)) == []


@pytest.mark.parametrize("kind", ["reversible", "partial", "irreversible"])
def test_accepts_rollback_and_contingency_variants(kind):
    assert validate_action_plan_record(valid_plan(rollback_type=kind)) == []


def test_explicitly_declared_approval_is_only_structurally_valid_not_authentication():
    assert validate_action_plan_record(valid_plan(approval="approved")) == []


@pytest.mark.parametrize("bad", [None, [], True, "texto", 17])
def test_non_object_plan_is_rejected(bad):
    assert any("object" in issue for issue in validate_action_plan_record(bad))


@pytest.mark.parametrize("key", [
    "case_id", "problem_reference", "analysis_reference", "analysis_status",
    "plan_objective", "alternatives", "selected_actions", "tasks",
    "owners", "scope", "risks", "rollback", "tests", "human_approval"
])
def test_required_plan_fields_are_checked(key):
    record = valid_plan()
    record.pop(key)
    assert any(key in issue for issue in validate_action_plan_record(record))


def test_unknown_and_duplicate_action_ids_rejected():
    record = valid_plan()
    record["alternatives"].append(copy.deepcopy(record["alternatives"][0]))
    record["selected_actions"] = ["A42"]
    errors = validate_action_plan_record(record)
    assert any("duplicate alternative" in x for x in errors)
    assert any("selected_actions" in x for x in errors)


def test_each_task_requires_selected_action_and_existing_owner():
    record = valid_plan()
    record["tasks"][0]["alternative_id"] = "A2"
    record["tasks"][0]["who"] = "P3"
    errors = validate_action_plan_record(record)
    assert any("alternative_id" in x for x in errors)
    assert any("tasks[0].who" in x for x in errors)


def test_duplicate_task_and_unresolvable_dependency_are_rejected():
    record = valid_plan()
    record["tasks"][0]["dependencies"] = ["T-missing"]
    record["tasks"].append(copy.deepcopy(record["tasks"][0]))
    errors = validate_action_plan_record(record)
    assert any("duplicate task" in x for x in errors)
    assert any("dependencies" in x for x in errors)


def test_5w2h_requires_all_fields():
    record = valid_plan()
    for field in ("what", "why", "where", "when", "how"):
        record["tasks"][0][field] = ""
    errors = validate_action_plan_record(record)
    for field in ("what", "why", "where", "when", "how"):
        assert any(field in x for x in errors)


def test_unknown_cost_requires_explanation_not_invented_amount():
    record = valid_plan()
    record["tasks"][0]["how_much"] = {"status": "unknown", "reason": ""}
    assert any("how_much.reason" in x for x in validate_action_plan_record(record))


def test_inconclusive_analysis_cannot_select_definitive_corrective_action():
    record = valid_plan(analysis_status="inconclusive")
    record["alternatives"][0]["intervention_type"] = "corrective"
    assert any("analysis_status" in x for x in validate_action_plan_record(record))


def test_risk_control_mitigation_and_stop_condition_are_required():
    record = valid_plan()
    for field in ("preventive_control", "mitigation", "stop_condition"):
        record["risks"][0][field] = ""
    errors = validate_action_plan_record(record)
    assert all(any(field in x for x in errors) for field in ("preventive_control", "mitigation", "stop_condition"))


def test_task_cannot_lack_risk_or_test_or_rollback():
    record = valid_plan()
    record["risks"] = []
    record["tests"] = []
    record["rollback"] = []
    errors = validate_action_plan_record(record)
    assert any("risks" in x for x in errors)
    assert any("tests" in x for x in errors)
    assert any("rollback" in x for x in errors)


def test_irreversible_change_cannot_claim_rollback_without_contingency():
    record = valid_plan(rollback_type="irreversible")
    record["rollback"][0].pop("contingency")
    record["rollback"][0].pop("point_of_no_return")
    errors = validate_action_plan_record(record)
    assert any("contingency" in x for x in errors)
    assert any("point_of_no_return" in x for x in errors)


def test_partial_change_needs_reversibility_boundary():
    record = valid_plan(rollback_type="partial")
    record["rollback"][0]["irreversible_stage"] = ""
    assert any("irreversible_stage" in x for x in validate_action_plan_record(record))


def test_test_design_requires_acceptance_failure_and_stop_without_claiming_execution():
    record = valid_plan()
    record["tests"][0]["acceptance"] = ""
    record["tests"][0]["failure"] = ""
    record["tests"][0]["stop_condition"] = ""
    record["tests"][0]["result"] = "PASS!"
    errors = validate_action_plan_record(record)
    assert all(any(field in x for x in errors) for field in
               ("acceptance", "failure", "stop_condition", "result"))


def test_unavailable_baseline_must_include_reason_and_collection_step():
    record = valid_plan()
    record["tests"][0]["baseline"] = {
        "type": "unavailable", "reason": "", "collection_needed": ""
    }
    errors = validate_action_plan_record(record)
    assert any("baseline.reason" in x for x in errors)
    assert any("baseline.collection_needed" in x for x in errors)


def test_pending_human_approval_may_not_claim_approver_or_reference():
    record = valid_plan()
    record["human_approval"]["approved_by"] = "Fictitious"
    assert any("human_approval" in x for x in validate_action_plan_record(record))


def test_approved_declaration_without_reference_rejected():
    record = valid_plan(approval="approved")
    record["human_approval"]["approval_reference"] = ""
    assert any("approval_reference" in x for x in validate_action_plan_record(record))


@pytest.mark.parametrize("path,value", [
    ("analysis_status", []), ("alternatives[0].intervention_type", []),
    ("tasks[0].how_much.status", []), ("rollback[0].type", []),
    ("human_approval.status", []), ("tests[0].baseline.type", [])
])
def test_malformed_enums_generate_errors_not_typeerrors(path, value):
    record = valid_plan()
    if path == "analysis_status": record["analysis_status"] = value
    elif path == "alternatives[0].intervention_type": record["alternatives"][0]["intervention_type"] = value
    elif path == "tasks[0].how_much.status": record["tasks"][0]["how_much"]["status"] = value
    elif path == "rollback[0].type": record["rollback"][0]["type"] = value
    elif path == "human_approval.status": record["human_approval"]["status"] = value
    elif path == "tests[0].baseline.type": record["tests"][0]["baseline"]["type"] = value
    assert validate_action_plan_record(record)


def test_cli_only_checks_static_structure_and_respects_workspace(tmp_path, capsys):
    work = tmp_path / "work"
    work.mkdir()
    path = work / "plan.json"
    path.write_text(json.dumps(valid_plan(), ensure_ascii=False), encoding="utf-8")
    assert main(["validate-action-plan", "--record", str(path), "--root", str(work)]) == 0
    output = capsys.readouterr().out
    assert "STATIC" in output and "não autentica" in output
    bad = valid_plan()
    bad["human_approval"]["approved_by"] = "Agente"
    path.write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8")
    assert main(["validate-action-plan", "--record", str(path), "--root", str(work)]) == 1
    assert "human_approval" in capsys.readouterr().out
    assert main(["validate-action-plan", "--record", str(path), "--root", str(tmp_path / "elsewhere")]) == 1
    assert "escapes" in capsys.readouterr().out


def test_preserves_gates_of_first_four_modules():
    assert GATE_REQUIREMENTS["plano-de-acao"] == {
        "tasks", "owners", "scope", "risks", "rollback", "tests", "human_approval"
    }
    assert GATE_REQUIREMENTS["analise"] == {
        "hypotheses", "evidence_for_and_against", "root_cause_or_explicit_inconclusive"
    }


def test_corpus_and_contract_are_universal_and_not_llm_behavior_claims():
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    assert len(corpus["casos"]) == 29
    assert len({c["id"] for c in corpus["casos"]}) == 29
    assert sum(c["categoria"] == "dominio" for c in corpus["casos"]) == 9
    assert sum(c["categoria"] == "adversarial" for c in corpus["casos"]) == 20
    assert all(c["entrada"].strip() and c["invariantes"] for c in corpus["casos"])
    assert "SINTÉTICAS" in corpus["natureza"]
    spec = (ROOT / "docs/masp/plano-acao/ESPECIFICACAO-V2.md").read_text(encoding="utf-8")
    role = (ROOT / "docs/masp/agentes/04-plano-de-acao.md").read_text(encoding="utf-8")
    config = (ROOT / ".codex/agents/masp-planejador.toml").read_text(encoding="utf-8")
    assert "ESPECIFICACAO-V2.md" in role and "ESPECIFICACAO-V2.md" in config
    for word in ("5W2H", "risco", "reversão", "contingência", "aprovação",
                 "BLOCKED", "STATIC", "SIMULATED", "RUNTIME", "irreversível"):
        assert word.lower() in (spec + role).lower()
