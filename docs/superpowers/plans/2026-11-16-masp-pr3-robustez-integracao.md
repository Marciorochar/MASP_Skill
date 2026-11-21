# PR #3 MASP — Plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Garantir entrada robusta, rastreabilidade, testes portáveis e observabilidade honesta do MASP multiagente.

**Architecture:** Manter CLI e motor Python atuais, aplicar validação nas fronteiras JSON/TOML, centralizar a skill em diretório descoberto pelo Codex e isolar smoke real da CI. Novas mudanças por testes de regressão sem alterar o modelo MASP.

**Tech Stack:** Python >=3.11, pytest, TOML, GitHub Actions Windows e Ubuntu.

**Spec:** `docs/superpowers/specs/2026-11-16-masp-pr3-robustez-integracao-design.md`

## Global Constraints
- Oito fases, dez papéis, limite máximo três agentes, sem fallback e sem autoaprovação.
- Preservar classificação STATIC/SIMULATED/RUNTIME e schema v2.
- Nunca acessar OTServer/VPS/produção ou modificar `main`.
- PR aberto sem merge, commits verificáveis; runtime sem evidência permanece BLOCKED.

## Review Focus
- `schema_version: []`, `state: []`, `event.new_state: {}`: rejeição controlada.
- `policies.states.values` com itens não hashable: erro de validação sem traceback.
- Evidências com `path` não string, IDs inadequados e hashes adulterados: sem crash.
- Smoke sem eventos estruturados: `BLOCKED`, não `PASS`.
- Duas skills divergentes: arquivo descobrível e documentação coerentes.

### Task 1 — Validar manifestos e matriz com tipos hostis
**Files:** Modify `src/masp_skill/case.py`, `src/masp_skill/routing.py`; test `tests/test_case_transitions.py`, `tests/test_routing.py`.
**Interfaces:** `validate_case(case, routing, root) -> list[str]`, `validate_routing(data) -> list[str]`.
- [ ] Escrever teste que verifica erro controlado para schema array e estados/eventos não hashable.
- [ ] Executar teste isolado e confirmar RED.
- [ ] Adicionar checagens de tipo antes de operações de pertinência/conjuntos.
- [ ] Executar teste isolado GREEN e suite completa.
- [ ] Commit com referência às falhas.

### Task 2 — Replay, evidências e isolamento
**Files:** Modify `src/masp_skill/case.py`, `src/masp_skill/evidence.py`; tests `tests/test_case_transitions.py`.
**Interfaces:** manter hashes de conteúdo, CAS e `validate_parallel_tasks(...)`.
- [ ] Testar evidência adversarial, conflito de escrita, symlink e histórico de modelo.
- [ ] Confirmar RED em problemas reproduzíveis, corrigir a menor causa.
- [ ] Executar testes focados e suite completa; commit.

### Task 3 — Skill MASP única e testada
**Files:** Modify `.agents/skills/masp/SKILL.md` e `skills/masp/SKILL.md`, `tests/test_skill_contract.py`, docs.
**Interfaces:** descoberta em `.agents/skills/masp/SKILL.md`; referências profundas sem contradição.
- [ ] Teste identifica divergências e referências inválidas no arquivo descoberto.
- [ ] RED, consolidar instruções e vincular arquivo detalhado sem cópia divergente.
- [ ] GREEN, suite, commit.

### Task 4 — Smoke mínimo e classificação runtime
**Files:** Modify `src/masp_skill/cli.py`, `tests/runtime/test_codex_smoke.py`.
**Interfaces:** `run_codex_smoke(root, output_dir)` e `runtime-smoke --strict`.
- [ ] Testar que o smoke não marque sucesso sem eventos estruturados e cheque `.agents/skills/masp/`.
- [ ] RED, corrigir verificação e limitar delegação de teste a um filho por padrão.
- [ ] GREEN, suite; só executar inferência real read-only se ambiente seguro e disponível; commit.

### Task 5 — Política efetiva e CI
**Files:** Modify `.github/workflows/ci.yml`, tests existentes e contratos.
- [ ] Testar regras declaradas de limite/arquivos; registrar o que é apenas instrução textual.
- [ ] Atualizar actions para versões atuais verificadas, mínimo `permissions: contents: read`.
- [ ] Testar Windows/Ubuntu em GitHub Actions; não executar inferência paga automaticamente.
- [ ] Commit.

### Task 6 — Piloto SIMULATED e relatório
**Files:** New `tests/test_masp_end_to_end.py`, `docs/masp/RELATORIO-AUDITORIA-PR3.md`; atualizar README e documentação afetada.
- [ ] Criar cenário sintético isolado de oito fases com evidências e gates reais da CLI.
- [ ] Verificar regressões de FAIL/BLOCKED e sequência; marcar sempre SIMULATED.
- [ ] Executar suite e validações de roteamento/fixture.
- [ ] Documentar execução e limitações, revisar diff, abrir PR sem merge.

## Verification
- `python -m pytest -q`
- `python -m masp_skill.cli validate-routing --routing docs/masp/masp-routing.toml --classification STATIC`
- `python -m masp_skill.cli validate-case --case tests/fixtures/cases/valid-case.json --root .`
- Dois jobs de CI concluídos (Windows/Ubuntu). Runtime multiagente somente PASS com correlação estruturada de eventos.
