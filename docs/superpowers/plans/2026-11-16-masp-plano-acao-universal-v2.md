# MASP Plano de Ação Universal v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans task-by-task, quando houver runtime Codex real; este Chat só possui edição pelo conector do GitHub.

**Goal:** criar o Plano de Ação Universal v2 com 5W2H, avaliação de alternativas, controles de riscos, reversão/contingência, testes e autorização externa.

**Architecture:** instruções universais + modelos humanos + sidecar JSON opcional verificado por CLI STATIC, sem migração do ledger.

**Tech Stack:** Markdown, TOML, Python 3.11+, pytest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-11-16-masp-plano-acao-universal-v2-design.md`

## Global Constraints

- Preservar exatamente `tasks`, `owners`, `scope`, `risks`, `rollback`, `tests`, `human_approval` no gate 04.
- Não alterar `case.py`, schema do ledger, ordem de fases nem módulos 01–03/05–08.
- O sidecar não autentica aprovador, custo, risco ou critério de sucesso e não concede `PASS`.
- Sem execução, sem acesso a produção, sem ações perigosas, sem Astra e sem merge automático.
- Separar `STATIC`, `SIMULATED`, `RUNTIME` e `NOT_RUN` com prova material.
- Registro de causa inconclusiva **não** autoriza ação corretiva definitiva.

## Review Focus

- Ação sem dono, risco, reversão/contingência ou teste => erro estrutural.
- Plano irreversível que alega rollback simples => erro; exigir ponto de não retorno e mitigação.
- Aprovação `approved` sem referência de origem => erro; com referência continua não autenticada.
- Custos/despesas indisponíveis => `unknown` com motivo, não números inventados.
- Baseline indisponível => documentação de coleta e critério verificável, sem falso sucesso.

---

### Task 1: Testes RED e fixture de cenários

**Files:** `tests/test_action_plan_v2.py`, `tests/fixtures/plano-acao-v2/casos.json`

- [ ] Escrever testes de invariantes e CLI antes do código.
- [ ] Confirmar RED pelo módulo ausente no GitHub Actions.
- [ ] Registrar 9 domínios e 20 situações adversariais sem alegar execução de agentes.

### Task 2: Validador de registro e CLI

**Files:** `src/masp_skill/action_plan.py`, `src/masp_skill/cli.py`

- [ ] Implementar validação estrutural com referências cruzadas e classes de intervenção/rollback.
- [ ] Adicionar comando `validate-action-plan --record ... --root ...`; imprimir `STATIC`.
- [ ] Obter GREEN na suíte completa.

### Task 3: Contratos e documentação

**Files:** `docs/masp/plano-acao/*`, `docs/masp/agentes/04-plano-de-acao.md`, `.codex/agents/masp-planejador.toml`, `docs/masp/masp-routing.toml`, `.agents/skills/masp/SKILL.md`, `docs/masp/modelos/CASO-MASP.md`, `README.md`

- [ ] Registrar seleção de alternativas, 5W2H, riscos, rollback e testes sem execução.
- [ ] Separar aprovação humana real de campo declarativo de JSON.
- [ ] Preservar contratos de módulos vizinhos; limitar OTServer a contextos OTServer.

### Task 4: Verificação, relatório e PR

**Files:** `docs/masp/plano-acao/RELATORIO-TESTES-V2.md`

- [ ] Confirmar CI Windows+Ubuntu, `validate-routing` e caso/ledger no SHA final.
- [ ] Revisar diff e registrar resultados reais, incluindo RED e GREEN.
- [ ] Abrir PR em rascunho para a `main`, sem merge.
- [ ] Marcar delegação `masp-planejador` e testes comportamentais Codex como `NOT_RUN`, pois ferramentas não estão disponíveis neste Chat.
