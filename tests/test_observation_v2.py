"""Observation v2: behavioral JSON-sidecar checks and separate static contracts.

These tests exercise Python validation, not agent execution or field evidence.
"""
import copy
import json
import math
from pathlib import Path

import pytest

from masp_skill.case import GATE_REQUIREMENTS
from masp_skill.cli import main
from masp_skill.observation import validate_observation_record


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "tests/fixtures/observacao-v2/casos.json"


def valid_record(kind="qualitative"):
    baseline = {
        "type": kind,
        "definition": "Satisfação relatada segundo registro de entrevista",
        "period": "2026-10",
        "source_id": "s1",
        "value": "atendimento descrito como demorado",
    }
    if kind == "quantitative":
        baseline.update({
            "definition": "Proporção de entregas fora do prazo",
            "value": 18.0,
            "unit": "%",
        })
    if kind == "unavailable":
        baseline = {
            "type": "unavailable",
            "reason": "Série histórica não foi disponibilizada",
            "collection_needed": "Solicitar relatório do período, com autorização",
        }
    return {
        "case_id": "MASP-OBS-001",
        "problem_reference": "Identificação MASP-OBS-001",
        "observation_objective": "Descrever frequência e contexto do problema sem atribuir causa",
        "environment": {"description": "Unidade em estudo", "period": "2026-10"},
        "observed_condition": "Atrasos relatados, frequência ainda desconhecida",
        "collection_method": {
            "name": "Revisão documental",
            "procedure": "Conferir o registro fornecido, sem executar intervenções",
        },
        "sources": [{
            "id": "s1", "kind": "relato", "origin": "Documento recebido",
            "recorded_at": "2026-10-15",
            "fact_class": "RELATO_NAO_VERIFICADO",
        }],
        "baseline": baseline,
        "reproducible_result_or_limitation": {
            "status": "not_reproducible",
            "details": "Registro retrospectivo; evento não pode ser repetido eticamente",
        },
        "limitations": ["Fonte indireta não confirmada"],
    }


@pytest.mark.parametrize("kind", ["quantitative", "qualitative", "unavailable"])
def test_accepts_explicit_baseline_types_without_demanding_numeric_measurement(kind):
    assert validate_observation_record(valid_record(kind)) == []


@pytest.mark.parametrize("field", [
    "case_id", "problem_reference", "observation_objective",
    "observed_condition", "environment", "collection_method",
    "baseline", "reproducible_result_or_limitation",
])
def test_rejects_missing_core_fields(field):
    record = valid_record()
    record.pop(field)
    errors = validate_observation_record(record)
    assert any(field in issue for issue in errors)


@pytest.mark.parametrize("invalid", [[], None, "x", 23])
def test_rejects_non_object_record_without_crashing(invalid):
    assert any("object" in x for x in validate_observation_record(invalid))


@pytest.mark.parametrize("invalid_value", [True, float("nan"), float("inf"), "18%", None])
def test_quantitative_baseline_rejects_nonfinite_or_non_numeric_values(invalid_value):
    record = valid_record("quantitative")
    record["baseline"]["value"] = invalid_value
    assert any("baseline.value" in x for x in validate_observation_record(record))


def test_quantitative_baseline_requires_unit_and_period():
    record = valid_record("quantitative")
    record["baseline"]["unit"] = ""
    record["baseline"]["period"] = ""
    errors = validate_observation_record(record)
    assert any("baseline.unit" in e for e in errors)
    assert any("baseline.period" in e for e in errors)


def test_baseline_requires_existing_source_and_rejects_duplicates():
    record = valid_record()
    record["baseline"]["source_id"] = "invented"
    record["sources"].append(copy.deepcopy(record["sources"][0]))
    errors = validate_observation_record(record)
    assert any("duplicate source" in e for e in errors)
    assert any("baseline.source_id" in e for e in errors)


def test_source_requires_origin_and_fact_class_without_invented_provenance():
    record = valid_record()
    record["sources"][0]["origin"] = ""
    record["sources"][0]["fact_class"] = "RUNTIME"
    errors = validate_observation_record(record)
    assert any("sources[0].origin" in e for e in errors)
    assert any("sources[0].fact_class" in e for e in errors)


def test_unavailable_baseline_requires_reason_and_collection_next_step():
    record = valid_record("unavailable")
    record["baseline"]["reason"] = ""
    record["baseline"]["collection_needed"] = ""
    errors = validate_observation_record(record)
    assert any("baseline.reason" in e for e in errors)
    assert any("baseline.collection_needed" in e for e in errors)


def test_observation_does_not_require_reproducing_historical_event():
    record = valid_record()
    assert validate_observation_record(record) == []


def test_reproduction_requires_status_and_documented_details():
    record = valid_record()
    record["reproducible_result_or_limitation"] = {
        "status": "automatically_passed", "details": ""
    }
    errors = validate_observation_record(record)
    assert any("reproducible_result_or_limitation.status" in e for e in errors)
    assert any("reproducible_result_or_limitation.details" in e for e in errors)


def test_cli_validates_optional_sidecar_without_changing_masp_ledger(tmp_path, capsys):
    record = tmp_path / "observation.json"
    record.write_text(json.dumps(valid_record(), ensure_ascii=False), encoding="utf-8")
    assert main(["validate-observation", "--record", str(record), "--root", str(tmp_path)]) == 0
    assert "STATIC" in capsys.readouterr().out
    bad = valid_record()
    bad["baseline"]["source_id"] = "missing"
    record.write_text(json.dumps(bad), encoding="utf-8")
    assert main(["validate-observation", "--record", str(record), "--root", str(tmp_path)]) == 1
    assert "baseline.source_id" in capsys.readouterr().out


def test_preserves_existing_four_gate_requirements_and_identification():
    assert GATE_REQUIREMENTS["observacao"] == {
        "baseline", "environment", "collection_method",
        "reproducible_result_or_limitation",
    }
    assert GATE_REQUIREMENTS["identificacao"] == {
        "problem", "impact", "scope", "exclusions", "success_metric",
    }


def test_universal_contract_docs_and_synthetic_corpus():
    spec = (ROOT / "docs/masp/observacao/ESPECIFICACAO-V2.md").read_text(encoding="utf-8")
    role = (ROOT / "docs/masp/agentes/02-observacao.md").read_text(encoding="utf-8")
    config = (ROOT / ".codex/agents/masp-observador.toml").read_text(encoding="utf-8")
    template = (ROOT / "docs/masp/observacao/MODELO-COLETA-EVIDENCIAS.md").read_text(encoding="utf-8")
    assert "ESPECIFICACAO-V2.md" in role and "ESPECIFICACAO-V2.md" in config
    for word in ("rápido", "aprofundado", "qualitativo", "quantitativo",
                 "não reproduzível", "PASS", "BLOCKED", "STATIC",
                 "SIMULATED", "RUNTIME", "causa raiz"):
        assert word.lower() in (spec + role + template).lower()
    for key in GATE_REQUIREMENTS["observacao"]:
        assert key in spec
    cases = json.loads(CORPUS.read_text(encoding="utf-8"))
    assert len(cases["casos"]) >= 25
    assert len({c["id"] for c in cases["casos"]}) == len(cases["casos"])
    assert all(c["entrada"].strip() and c["invariantes"] for c in cases["casos"])
    assert "sintéticas" in cases["natureza"]


def test_extremely_large_quantitative_measurement_is_rejected_without_crash():
    record = valid_record("quantitative")
    record["baseline"]["value"] = 10 ** 400
    errors = validate_observation_record(record)
    assert any("baseline.value" in issue for issue in errors)
