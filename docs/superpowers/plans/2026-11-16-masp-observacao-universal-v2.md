# Observação Universal v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans task-by-task. Esta sessão não disponibiliza spawn de agentes Codex; nenhuma delegação será inventada.

**Goal:** Criar uma metodologia universal de observação e um verificador estrutural opcional de registros, preservando o MASP anterior.

**Architecture:** Contratos Markdown e TOML de M02 + sidecar JSON validado separadamente via Python/CLI; `case.py` e ledger sem alterações.

**Tech Stack:** Markdown, TOML, Python 3.11+, pytest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-11-16-masp-observacao-universal-v2-design.md`

## Global Constraints

- Preservar exatamente `baseline`, `environment`, `collection_method`, `reproducible_result_or_limitation`.
- Não alterar Identificação v2, módulos 03–08, `case.py`, schema do ledger ou modelos de agentes.
- Não executar Astra, smoke `--all-roles`, experimentos perigosos nem operações em produção.
- Separar `STATIC`, `SIMULATED`, `RUNTIME` e fatos, relatos, hipóteses e desconhecidos.
- Não declarar revisão independente quando não ocorreu.

## Review Focus

- A ausência de baseline numérico não impede registro qualitativo.
- Nenhuma reprodução forçada de um evento histórico ou perigoso.
- Referências de fontes inválidas não devem ser aceitas.
- `NaN`, `Infinity` e booleanos não são medições quantitativas válidas.
- `validate-observation` não pode produzir PASS do Gate 02 por simples presença de campos.

---

### Task 1: Testes RED de contrato e sidecar

**Files:**
- Create: `tests/test_observation_v2.py`
- Create: `tests/fixtures/observacao-v2/casos.json`

- [x] Escrever testes de comportamento e contrato antes da implementação.
- [x] Executar CI RED e conferir erro esperado de importação do módulo inexistente.
- [ ] Criar inventário sintético de 9 domínios e 18 entradas adversariais.

### Task 2: Implementar validador e CLI

**Files:**
- Create: `src/masp_skill/observation.py`
- Modify: `src/masp_skill/cli.py`

- [ ] Validar forma e proveniência atribuída, baselines, reprodução/limitações e estados malformados.
- [ ] Implementar `validate-observation --record ... --root ...` como `STATIC`.
- [ ] Confirmar GREEN no teste focado e suíte.

### Task 3: Contrato universal e documentação

**Files:**
- Create: `docs/masp/observacao/ESPECIFICACAO-V2.md`
- Create: `docs/masp/observacao/REFERENCIAS-METODOLOGICAS.md`
- Create: `docs/masp/observacao/MODELO-COLETA-EVIDENCIAS.md`
- Modify: `docs/masp/agentes/02-observacao.md`, `.codex/agents/masp-observador.toml`, `docs/masp/masp-routing.toml`
- Modify: `.agents/skills/masp/SKILL.md`, `docs/masp/modelos/CASO-MASP.md`, `README.md`

- [ ] Adaptar fontes, modo rápido/aprofundado, classes de fatos e Gate 02.
- [ ] Limitar restrições OTServer ao seu caso, não a todos os domínios.
- [ ] Preservar outros contratos e IDs existentes.

### Task 4: Verificação e Pull Request

**Files:**
- Create: `docs/masp/observacao/RELATORIO-TESTES-V2.md`

- [ ] Confirmar CI em Python 3.11/Ubuntu+Windows no commit final.
- [ ] Validar roteamento e caso de referência.
- [ ] Revisar diff por escopo, testes e documentação; reportar ausência de auditor independente.
- [ ] Criar PR em rascunho `feat(masp): observação universal v2 com coleta e validação de evidências`; não realizar merge.
