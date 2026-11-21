# Módulo 05 — Ação Universal v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** desenvolver contrato universal de Ação MASP com execução controlada e evidências rastreáveis sem criar permissão de executar intervenções reais.

**Architecture:** especificação + fichas de execução + ajustes mínimos nos contratos existentes e, apenas se justificado, um validador JSON/CLI somente `STATIC`. A aprovação operacional permanece externa; o ledger não muda.

**Tech Stack:** Markdown, TOML, Python >=3.11, pytest, GitHub Actions Ubuntu/Windows.

**Spec:** `docs/superpowers/specs/2026-11-16-masp-acao-universal-v2-design.md`

## Global Constraints

- Iniciar implementação **somente após aprovação humana explícita do desenho técnico**.
- Preservar exatamente `changes`, `diff`, `commands`, `results`, `no_self_approval`.
- Não alterar `src/masp_skill/case.py`, schema, ledger, gates e políticas de autorização existentes.
- Não executar ações de casos reais nem permitir CLI de execução de casos.
- Não declarar aprovação autenticada a partir de campos `human_approval`, `approved_by` ou rótulos.
- Separar `STATIC`, `SIMULATED`, `RUNTIME`, `NOT_RUN` de forma auditável.
- Modificar apenas M05 e referências estritamente necessárias à integração.
- Branch isolada `feat/masp-acao-universal-v2`; não fazer merge automático.

## Review Focus

- `approval=approved` em registro autodeclarado não autoriza execução; resultado continua `STATIC`.
- Plano versionado divergente ou ambiente não isolado não pode produzir `GO` operacional.
- Registro físico/administrativo de mudança antes/depois deve satisfazer `diff` sem fabricar comandos Git.
- Execução `NOT_RUN` não pode alegar resultados, testes ou rollback executados.
- Intervenção irreversível não pode registrar reversão fictícia; exige contingência, stop e ponto de não retorno.

---

### Task 1: Testes RED de contrato universal e corpus

**Files:**
- Create: `tests/test_action_execution_v2.py`
- Create: `tests/fixtures/acao-v2/casos.json`

**Interfaces:** definir `validate_action_execution_record(record: Any) -> list[str]` somente se a alternativa JSON for aprovada. Manter `GATE_REQUIREMENTS["acao"]` inalterado.

- [ ] Escrever teste que falha por módulo/contrato ainda inexistente, antes de modificar código.
- [ ] Registrar 9 domínios e 24 casos adversariais: aprovação inexistente/fictícia, versão divergente, perda de isolamento, execução fora de escopo, stop, falha parcial, dado sensível, `NOT_RUN` falsificado, concorrência, rollback inseguro e autoaprovação.
- [ ] Executar `python -m pytest -q tests/test_action_execution_v2.py`; capturar falha RED real no CI e confirmar que é atribuível à funcionalidade ausente.
- [ ] Commit somente dos testes/fixtures.

### Task 2: Verificador declarativo opcional e CLI (se aprovado)

**Files:**
- Create: `src/masp_skill/action_execution.py`
- Modify: `src/masp_skill/cli.py`
- Test: `tests/test_action_execution_v2.py`

**Interfaces:** `validate_action_execution_record(record: Any) -> list[str]` e `validate-action-execution --record FILE --root WORKSPACE`. Nenhum comando executa casos, shell, intervenções ou rollback.

- [ ] Verificar a falha RED de ausência dos contratos/erros de referência.
- [ ] Implementar o mínimo: tipos, IDs, integridade de referências entre registros, estado executado/`NOT_RUN`, status de rollback e checklist.
- [ ] Impedir enums JSON não-hashable de derrubar o validador; rejeitar caminhos fora do workspace.
- [ ] Rodar teste focal e suíte integral; corrigir até GREEN, registrando evidências.
- [ ] Commit somente da funcionalidade validada.

### Task 3: Skill e documentação universal

**Files:**
- Create: `docs/masp/acao/ESPECIFICACAO-V2.md`
- Create: `docs/masp/acao/REFERENCIAS-METODOLOGICAS.md`
- Create: `docs/masp/acao/MODELO-EXECUCAO.md`
- Create: `docs/masp/acao/CHECKLIST-PRE-EXECUCAO.md`
- Create: `docs/masp/acao/CONTROLE-DESVIOS-ROLLBACK.md`
- Modify: `docs/masp/agentes/05-acao.md`, `.codex/agents/masp-executor.toml`, `docs/masp/masp-routing.toml`, `.agents/skills/masp/SKILL.md`, `docs/masp/modelos/CASO-MASP.md`, `README.md`

- [ ] Usar `superpowers:writing-skills` e testar cenário pressionando por execução sem autorização na versão anterior, quando runtime de agentes disponível.
- [ ] Escrever documentação universal, separando aprovação externa real de declaração em arquivo.
- [ ] Movimentar restrições OTServer para regra condicional ao domínio, sem globalizá-las.
- [ ] Preservar os cinco requisitos do Gate 05 e a política de delegação, sem alteração de modelos/effort.
- [ ] Rodar os testes e validadores; revisar diffs para mudanças não intencionais.
- [ ] Commit dos contratos revisados.

### Task 4: Evidências, CI e PR rascunho

**Files:**
- Create: `docs/masp/acao/RELATORIO-TESTES-V2.md`

- [ ] Executar `python -m pytest -q`; registrar números de aprovados, ignorados e falhas realmente observados.
- [ ] Executar `python -m masp_skill.cli validate-routing --routing docs/masp/masp-routing.toml --classification STATIC`.
- [ ] Executar `python -m masp_skill.cli validate-case --case tests/fixtures/cases/valid-case.json --root .`.
- [ ] Verificar Actions em Windows/Ubuntu para SHA final, logs, PR e integridade do branch.
- [ ] Registrar `NOT_RUN` para delegação não disponível e para intervenções físicas/operacionais não executadas.
- [ ] Abrir PR em rascunho sem merge e sem alegar validação comportamental do Codex ausente.

## Parada de implementação

**O plano acima está aprovado apenas como material para revisão.** Nenhum item de execução deve ser iniciado até aprovação explícita do desenho e confirmação do escopo; a existência desta branch e destes documentos não confere autorização de mudança funcional.
