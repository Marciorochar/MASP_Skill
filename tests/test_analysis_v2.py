"""Structural and behavioral tests for the optional MASP Analysis v2 sidecar.

These tests do NOT evaluate whether an LLM correctly infers a real root cause.
"""
import copy
import json
from pathlib import Path

import pytest

from masp_skill.analysis import validate_analysis_record
from masp_skill.case import GATE_REQUIREMENTS
from masp_skill.cli import main


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "tests/fixtures/analise-v2/casos.json"


def valid_record(conclusion="supported"):
    record = {
        "case_id": "MASP-ANALISE-EXEMPLO",
        "problem_reference": "MASP-IDENT-EXEMPLO",
        "observation_reference": "MASP-OBS-EXEMPLO",
        "analysis_objective": "Comparar hipóteses sobre um problema fictício",
        "analysis_scope": "Documentos sintéticos, sem coleta real",
        "methods": [{"name": "Triangulação documental", "rationale": "Comparar relatos e registros independentes"}],
        "sources": [
            {"id": "E1", "origin": "Fonte sintética A", "description": "Registro fictício de ocorrência", "fact_class": "FATO_VERIFICADO"},
            {"id": "E2", "origin": "Fonte sintética B", "description": "Leitura fictícia de ambiente", "fact_class": "FATO_VERIFICADO"},
            {"id": "E3", "origin": "Fonte sintética C", "description": "Declaração sobre evento", "fact_class": "RELATO_NAO_VERIFICADO"},
        ],
        "hypotheses": [
            {
                "id": "H1",
                "statement": "Condição A pode contribuir para a ocorrência",
                "mechanism": "Mecanismo proposto sob condições delimitadas",
                "expected_if_true": "Evento observado sob condição A",
                "potential_disconfirmation": "Condição A ausente nos eventos relevantes",
                "evidence_for": ["E1", "E2"],
                "evidence_against": [],
                "counterevidence_review": "Registros contrários revisados, sem achado suficiente; limite permanece",
                "alternative_ids": ["H2"],
                "status": "CORROBORADA",
                "verification": {
                    "status": "performed", "method": "comparação documental",
                    "result": "Comparação documentada e restrita à amostra sintética",
                    "evidence_ids": ["E1", "E2"],
                    "limitations": "Fontes fictícias; causalidade real não demonstrada"
                }
            },
            {
                "id": "H2",
                "statement": "Condição B pode explicar a ocorrência",
                "mechanism": "Outra explicação possível",
                "expected_if_true": "Evento observado sob B",
                "potential_disconfirmation": "Registro contrário a B",
                "evidence_for": ["E3"],
                "evidence_against": ["E1"],
                "counterevidence_review": "Registro E1 contraria esta explicação",
                "alternative_ids": ["H1"],
                "status": "REFUTADA",
                "verification": {
                    "status": "performed", "method": "comparação documental",
                    "result": "E1 diverge de B na amostra fictícia",
                    "evidence_ids": ["E1"],
                    "limitations": "Relação analisada apenas na situação sintética"
                }
            }
        ],
        "conclusion": {
            "type": "supported",
            "supported_hypothesis_ids": ["H1"],
            "evidence_basis": "documentary_triangulation",
            "justification": "Alegação condicionada ao cenário sintético; fontes e alternativas explicitadas",
            "limitations": "Não existe comprovação de ocorrências reais",
            "additional_data_needed": []
        },
        "limitations": ["Caso sintético, não evidência de campo"]
    }
    if conclusion == "inconclusive":
        record["hypotheses"][0]["status"] = "INCONCLUSIVA"
        record["hypotheses"][0]["verification"] = {
            "status": "not_run", "method": "consulta adicional",
            "reason": "Fonte não disponível; comparação parcial",
            "evidence_ids": [],
        }
        record["conclusion"] = {
            "type": "inconclusive",
            "supported_hypothesis_ids": [],
            "evidence_basis": "unknown",
            "justification": "Documentos examinados, mas rivais não diferenciados",
            "limitations": "Fonte que distinguiria hipóteses não está acessível",
            "additional_data_needed": ["Registros históricos autorizados"]
        }
    return record


def test_accepts_attributed_supported_and_legitimately_inconclusive_records():
    assert validate_analysis_record(valid_record()) == []
    assert validate_analysis_record(valid_record("inconclusive")) == []


@pytest.mark.parametrize("record", [None, [], "invalido", 17, True])
def test_rejects_non_object_records_safely(record):
    assert any("object" in error for error in validate_analysis_record(record))


@pytest.mark.parametrize("field", ["case_id", "problem_reference", "observation_reference", "analysis_objective", "analysis_scope", "methods", "sources", "hypotheses", "conclusion"])
def test_required_fields_do_not_disappear(field):
    record = valid_record()
    record.pop(field)
    assert any(field in issue for issue in validate_analysis_record(record))


def test_rejects_duplicate_sources_and_wrong_fact_class():
    record = valid_record()
    record["sources"].append(copy.deepcopy(record["sources"][0]))
    record["sources"][0]["fact_class"] = "RUNTIME"
    errors = validate_analysis_record(record)
    assert any("duplicate source" in x for x in errors)
    assert any("sources[0].fact_class" in x for x in errors)


def test_rejects_duplicate_hypotheses_and_self_alternatives():
    record = valid_record()
    record["hypotheses"][1]["id"] = "H1"
    record["hypotheses"][0]["alternative_ids"] = ["H1"]
    errors = validate_analysis_record(record)
    assert any("duplicate hypothesis" in x for x in errors)
    assert any("alternative_ids" in x for x in errors)


@pytest.mark.parametrize("field", ["evidence_for", "evidence_against"])
def test_hypothesis_evidence_must_reference_declared_sources(field):
    record = valid_record()
    record["hypotheses"][0][field] = ["E-INVENTADA"]
    assert any(field in x for x in validate_analysis_record(record))


def test_verification_sources_must_be_declared():
    record = valid_record()
    record["hypotheses"][0]["verification"]["evidence_ids"] = ["E4"]
    assert any("verification.evidence_ids" in x for x in validate_analysis_record(record))


def test_requires_counterevidence_review_even_with_no_contrary_evidence():
    record = valid_record()
    record["hypotheses"][0]["counterevidence_review"] = ""
    assert any("counterevidence_review" in x for x in validate_analysis_record(record))


@pytest.mark.parametrize("status", ["NAO_TESTADA", "EM_AVALIACAO", "CORROBORADA", "REFUTADA", "INCONCLUSIVA"])
def test_accepts_declared_hypothesis_status_vocabulary(status):
    record = valid_record("inconclusive")
    record["hypotheses"][0]["status"] = status
    if status in {"CORROBORADA", "REFUTADA"}:
        record["hypotheses"][0]["verification"] = {
            "status": "performed", "method": "comparação documental",
            "result": "Registro sintético comparado",
            "evidence_ids": ["E1"],
            "limitations": "Somente teste"
        }
    if status == "REFUTADA":
        record["hypotheses"][0]["evidence_against"] = ["E3"]
    assert validate_analysis_record(record) == []


def test_corroborated_must_not_be_not_run_or_have_no_support():
    record = valid_record()
    record["hypotheses"][0]["verification"] = {
        "status": "not_run", "method": "comparação", "reason": "sem dados", "evidence_ids": []
    }
    record["hypotheses"][0]["evidence_for"] = []
    errors = validate_analysis_record(record)
    assert any("CORROBORADA" in x for x in errors)


def test_corroborated_cause_needs_attributed_verified_observation():
    record = valid_record()
    record["sources"][0]["fact_class"] = "RELATO_NAO_VERIFICADO"
    record["sources"][1]["fact_class"] = "RELATO_NAO_VERIFICADO"
    assert any("CORROBORADA" in x for x in validate_analysis_record(record))


def test_documentary_triangulation_is_not_two_copies_of_same_origin():
    record = valid_record()
    record["sources"][1]["origin"] = record["sources"][0]["origin"]
    assert any("evidence_basis" in x for x in validate_analysis_record(record))


def test_refuted_requires_contrary_evidence():
    record = valid_record()
    record["hypotheses"][1]["evidence_against"] = []
    assert any("REFUTADA" in x for x in validate_analysis_record(record))


def test_performed_check_needs_result_and_evidence_link():
    record = valid_record()
    record["hypotheses"][0]["verification"]["result"] = ""
    record["hypotheses"][0]["verification"]["evidence_ids"] = []
    errors = validate_analysis_record(record)
    assert any("verification.result" in x for x in errors)
    assert any("verification.evidence_ids" in x for x in errors)


def test_not_run_check_requires_reason_and_cannot_fake_result():
    record = valid_record("inconclusive")
    record["hypotheses"][0]["verification"] = {
        "status": "not_run", "method": "avaliação futura",
        "reason": "", "result": "testado"
    }
    errors = validate_analysis_record(record)
    assert any("verification.reason" in x for x in errors)
    assert any("verification.result" in x for x in errors)


def test_supported_cause_cannot_reference_noncorroborated_hypothesis():
    record = valid_record()
    record["conclusion"]["supported_hypothesis_ids"] = ["H2"]
    assert any("supported_hypothesis_ids" in x for x in validate_analysis_record(record))


@pytest.mark.parametrize("invalid_basis", ["association_only", "unknown", "vote", None])
def test_supported_cause_rejects_association_only_or_unsupported_basis(invalid_basis):
    record = valid_record()
    record["conclusion"]["evidence_basis"] = invalid_basis
    assert any("evidence_basis" in x for x in validate_analysis_record(record))


def test_inconclusive_cannot_claim_supported_hypothesis_as_final_cause():
    record = valid_record("inconclusive")
    record["conclusion"]["supported_hypothesis_ids"] = ["H2"]
    assert any("supported_hypothesis_ids" in x for x in validate_analysis_record(record))


def test_inconclusive_requires_explicit_reason_and_limits():
    record = valid_record("inconclusive")
    record["conclusion"]["justification"] = ""
    record["conclusion"]["limitations"] = ""
    errors = validate_analysis_record(record)
    assert any("conclusion.justification" in x for x in errors)
    assert any("conclusion.limitations" in x for x in errors)


def test_cli_check_is_static_and_does_not_certify_cause(tmp_path, capsys):
    path = tmp_path / "analysis.json"
    path.write_text(json.dumps(valid_record(), ensure_ascii=False), encoding="utf-8")
    assert main(["validate-analysis", "--record", str(path), "--root", str(tmp_path)]) == 0
    output = capsys.readouterr().out
    assert "STATIC" in output
    assert "não" in output.lower() or "not" in output.lower()
    record = valid_record()
    record["conclusion"]["evidence_basis"] = "association_only"
    path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
    assert main(["validate-analysis", "--record", str(path), "--root", str(tmp_path)]) == 1
    assert "evidence_basis" in capsys.readouterr().out


def test_cli_rejects_path_outside_workspace(tmp_path, capsys):
    nested = tmp_path / "work"
    nested.mkdir()
    path = tmp_path / "outside.json"
    path.write_text(json.dumps(valid_record(), ensure_ascii=False), encoding="utf-8")
    assert main(["validate-analysis", "--record", str(path), "--root", str(nested)]) == 1
    assert "escapes" in capsys.readouterr().out


def test_ledger_gate_criteria_remain_exactly_unchanged():
    assert GATE_REQUIREMENTS["analise"] == {"hypotheses", "evidence_for_and_against", "root_cause_or_explicit_inconclusive"}
    assert GATE_REQUIREMENTS["identificacao"] == {"problem", "impact", "scope", "exclusions", "success_metric"}
    assert GATE_REQUIREMENTS["observacao"] == {"baseline", "environment", "collection_method", "reproducible_result_or_limitation"}


def test_multidomain_corpus_is_synthetic_and_has_adversarial_cases():
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    cases = corpus["casos"]
    assert len(cases) == 29
    assert len({c["id"] for c in cases}) == 29
    assert len([c for c in cases if c["categoria"] == "dominio"]) == 9
    assert len([c for c in cases if c["categoria"] == "adversarial"]) == 20
    assert all(c["entrada"] and c["invariantes"] for c in cases)
    assert "sintéticos" in corpus["natureza"]


def test_analysis_contract_references_universal_spec_and_methodological_limits():
    spec = (ROOT / "docs/masp/analise/ESPECIFICACAO-V2.md").read_text(encoding="utf-8")
    role = (ROOT / "docs/masp/agentes/03-analise.md").read_text(encoding="utf-8")
    config = (ROOT / ".codex/agents/masp-analista.toml").read_text(encoding="utf-8")
    assert "ESPECIFICACAO-V2.md" in role and "ESPECIFICACAO-V2.md" in config
    for term in ("rápido", "aprofundado", "correlação", "causalidade", "contrárias", "inconclusiva", "BLOCKED", "STATIC", "SIMULATED", "RUNTIME"):
        assert term.lower() in (spec + role).lower()
    for criterion in GATE_REQUIREMENTS["analise"]:
        assert criterion in spec
