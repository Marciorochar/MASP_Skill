"""Static checks of the v2 documents and rubric, not agent runtime behavior."""

import json
from pathlib import Path
import unicodedata

from masp_skill.case import GATE_REQUIREMENTS


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/masp/identificacao/ESPECIFICACAO-V2.md"
ROLE = ROOT / "docs/masp/agentes/01-identificacao.md"
CONFIG = ROOT / ".codex/agents/masp-identificador.toml"
WORKSHEET = ROOT / "docs/masp/modelos/CASO-MASP.md"
CORPUS = ROOT / "tests/fixtures/identificacao-v2/casos.json"

DOMAINS = {"industria", "logistica", "servicos_saude", "administracao", "meio_ambiente", "tecnologia", "educacao", "domestico"}
ADVERSARIAL = {"relato_vago", "solucao_embutida", "causa_presumida", "dados_quantitativos_ausentes", "informacao_contraditoria", "escopo_indefinido", "criterio_qualitativo", "risco_imediato"}
CLASSES = {"FATO_VERIFICADO", "RELATO_NAO_VERIFICADO", "HIPOTESE", "DESCONHECIDO"}
GATE_IDS = {"problem", "impact", "scope", "exclusions", "success_metric"}


def normalized(text):
    return "".join(c for c in unicodedata.normalize("NFKD", text.casefold()) if not unicodedata.combining(c))


def read(path):
    return path.read_text(encoding="utf-8")


def test_corpus_inventory_and_rubric_are_synthetic():
    corpus = json.loads(read(CORPUS))
    cases = corpus["casos"]
    assert len(cases) == 16
    assert len({case["id"] for case in cases}) == len(cases)
    assert {c["tipo"] for c in cases if c["categoria"] == "dominio"} == DOMAINS
    assert {c["tipo"] for c in cases if c["categoria"] == "adversarial"} == ADVERSARIAL
    assert all(c["entrada"].strip() and c["invariantes"] and all(i.strip() for i in c["invariantes"]) for c in cases)
    assert all(set(c) == {"id", "categoria", "tipo", "entrada", "invariantes"} for c in cases)
    assert "não são respostas observadas" in corpus["natureza"]


def test_existing_gate_ids_remain_compatible():
    assert GATE_REQUIREMENTS["identificacao"] == GATE_IDS


def test_specification_covers_identification_contract():
    text = read(SPEC)
    folded = normalized(text)
    for term in ("rápido", "profundo", "perguntas", "fonte", "data", "limitações", "observação", "segurança", "qualitativo"):
        assert normalized(term) in folded, term
    for term in CLASSES | GATE_IDS | {"PENDENTE_DE_OBSERVACAO", "PASS", "BLOCKED"}:
        assert term in text, term
    assert "causa" in folded and "solucao" in folded
    assert "baseline" in folded


def test_identifier_instructions_point_to_v2_and_state_boundaries():
    text = read(ROLE) + "\n" + read(CONFIG)
    folded = normalized(text)
    assert "ESPECIFICACAO-V2.md" in text
    for term in ("causa", "solução", "observação", "baseline", "segurança"):
        assert normalized(term) in folded, term
    for term in CLASSES | {"PENDENTE_DE_OBSERVACAO", "PASS", "BLOCKED"}:
        assert term in text, term


def test_human_worksheet_contains_universal_fields():
    text = normalized(read(WORKSHEET))
    for field in ("problema", "impacto", "escopo", "exclusões", "critério de sucesso", "baseline", "fonte", "data", "limitações", "observação"):
        assert normalized(field) in text, field



def test_optional_is_is_not_delimits_without_inferring_cause():
    text = normalized(read(SPEC))
    assert "is / is not" in text or "is/is not" in text
    assert "quando houver dados suficientes" in text
    assert "nao observado" in text or "nao disponivel" in text
    assert "nao inferir causa" in text or "nao conclui causa" in text
