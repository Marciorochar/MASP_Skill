# MASP Padronização Universal v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** transformar melhorias verificadas em controles preventivos, responsáveis, gatilhos, regressões e governança documental, em qualquer domínio, sem falsa alegação de eficácia ou implantação.

**Architecture:** contrato canônico do M07 + fichas humanas e referências, ajustes mínimos nas instruções/roteamento e, somente com aprovação específica e benefício demonstrado, sidecar JSON/CLI de validação `STATIC`. Sem alteração de ledger, aprovações reais ou execução de controles no mundo externo.

**Tech Stack:** Markdown, TOML, Python 3.11+, pytest, GitHub Actions Ubuntu/Windows.

**Spec:** `docs/superpowers/specs/2026-11-16-masp-padronizacao-universal-v2-design.md`

## Global Constraints

- Não iniciar implementação sem aprovação explícita do desenho do M07.
- Preservar os quatro IDs de `GATE_REQUIREMENTS["padronizacao"]`: `preventive_control`, `owner`, `trigger`, `regression`.
- Não alterar `src/masp_skill/case.py`, esquema/ledger/estados, fluxo de retornos ou contratos M01–06 e M08.
- PR #12 (desenho do M06) está em rascunho na base auditada; não pressupor implementação de Verificação Universal v2 nem eficácia real.
- Estados documentais `DRAFT`, `UNDER_REVIEW`, `APPROVED`, `ACTIVE`, `SUSPENDED`, `OBSOLETE` NÃO são estados MASP.
- Campos `APPROVED` e `ACTIVE` não autenticam assinatura, implantação, treinamento ou sustentabilidade.
- Sem ações de produção, treinamento real, alteração de POP institucional, riscos físicos, Astra, `runtime-smoke --all-roles` ou merge automático.
- `STATIC`/ `SIMULATED`/ `RUNTIME`/ `NOT_RUN` sempre com alcance explícito.

## Review Focus

1. M06 ausente ou `SIMULATED`: bloquear pretensão de padronização **realmente eficaz**, sem impedir criação de modelos fictícios rotulados.
2. `owner` sem função atribuída ou duplicação conflitante: sinalizar pendência; não inventar pessoa responsável.
3. `trigger` inespecífico, sem fonte/observabilidade ou reação autorizada: exigir critério, detecção e dono.
4. `regression` ausente ou `NOT_RUN` afirmado como PASS: não aprovar prevenção de recorrência só por documentação.
5. `ACTIVE` ou sustentabilidade baseada apenas em status JSON/treinamento planejado: não transformar declaração em evidência real.

---

### Task 1: Especificar teste RED do contrato e criar corpus adversarial

**Files:**
- Create: `tests/test_standardization_v2.py`
- Create: `tests/fixtures/padronizacao-v2/casos.json`

**Interfaces:** `validate_standardization_record(record: Any) -> list[str]`, somente se sidecar aprovado. `GATE_REQUIREMENTS["padronizacao"]` continua intacto.

- [ ] **Step 1: Write the failing test** — `test_missing_verification_cannot_claim_proven_standard()` exige erro estrutural para `verification_reference` ausente com `effectiveness_claim="demonstrated"`.
- [ ] **Step 2: Run to verify RED** — `python -m pytest -q tests/test_standardization_v2.py`; documentar a falha prevista **pela funcionalidade ausente**, não erro acidental de sintaxe/fixture.
- [ ] **Step 3: Add fixture corpus** — 9 domínios sintéticos (indústria, logística, saúde, administração, ambiente, tecnologia, educação, serviços e cotidiano) mais 30 casos adversariais da especificação, todos com IDs únicos e invariantes testáveis.
- [ ] **Step 4: Test corpus structure** — contagem 39, nenhuma entrada/invariante vazio; declarar `SIMULATED`.
- [ ] **Step 5: Commit** — somente testes e fixtures, sem código de implementação.

### Task 2: Validar apenas estrutura declarada (se aprovado)

**Files:**
- Create: `src/masp_skill/standardization.py`
- Modify: `src/masp_skill/cli.py`
- Test: `tests/test_standardization_v2.py`

**Interfaces:** `validate_standardization_record(record: Any) -> list[str]`; `validate-standardization --record FILE --root WORKSPACE`, retorno 0/1 e classificação `STATIC`, sem side effects.

- [ ] **Step 1: Write focused RED tests** — referências cruzadas, IDs duplicados, estados documentais inválidos, JSON com enum/lista não-hashable, `owner` não declarado, `trigger` sem detecção, `regression` sem método, `APPROVED` sem referência declarada, treino planejado com prova de execução fabricada, caminho fora do workspace.
- [ ] **Step 2: Verify RED** — `python -m pytest -q tests/test_standardization_v2.py` com erro esperado documentado.
- [ ] **Step 3: Implement minimum** — validador determinístico de estrutura/referência, sem inferir competência, eficácia, assinatura, monitoramento real ou autoridade de gate.
- [ ] **Step 4: Verify GREEN** — testes focalizados, suíte integral; verificar códigos e logs.
- [ ] **Step 5: Commit** — módulo + CLI + testes, mantendo demais fases intactas.

### Task 3: Contratos universais e modelos de padronização

**Files:**
- Create: `docs/masp/padronizacao/ESPECIFICACAO-V2.md`
- Create: `docs/masp/padronizacao/REFERENCIAS-METODOLOGICAS.md`
- Create: `docs/masp/padronizacao/MODELO-PADRAO.md`
- Create: `docs/masp/padronizacao/PLANO-CONTROLE.md`
- Create: `docs/masp/padronizacao/MATRIZ-GATILHOS-REGRESSOES.md`
- Create: `docs/masp/padronizacao/CONTROLE-DOCUMENTAL.md`
- Modify: `docs/masp/agentes/07-padronizacao.md`
- Modify: `.codex/agents/masp-padronizador.toml`
- Modify: `docs/masp/masp-routing.toml` (bloco M07 apenas)
- Modify: `.agents/skills/masp/SKILL.md` (item M07 apenas)
- Modify: `docs/masp/modelos/CASO-MASP.md`, `README.md` (ficha/referência M07)

- [ ] **Step 1: Pressure test baseline** — se Codex real disponível, teste o comportamento anterior do `masp-padronizador` diante de pedido de "padronize solução com Verificação inconclusiva"; registrar observações. Se indisponível, `NOT_RUN`, sem alegar teste comportamental.
- [ ] **Step 2: Write the contract** — seleção e tipos de controles, dono, gatilho/reação, monitoramento, regressão, competências, treinamento, governança de versões, estados documentais e limites.
- [ ] **Step 3: Scope compliance** — restrições OTServer condicionais, M06 no estado real, nenhuma intervenção externa ou padrão aprovado ficticiamente, nenhuma alteração de modelo/effort.
- [ ] **Step 4: Run regression and review** — `pytest`, `validate-routing`, `validate-case`, diff dos contratos e prova de que os quatro IDs de Gate 07 permanecem exatos.
- [ ] **Step 5: Commit** — somente documentação/instruções relacionadas ao M07.

### Task 4: Relatório verificável, CI e PR

**Files:**
- Create: `docs/masp/padronizacao/RELATORIO-TESTES-V2.md`

- [ ] **Step 1: Execute tests** — `python -m pytest -q` e registrar contagens reais de PASS/skip/FAIL e código de saída.
- [ ] **Step 2: Validate routing** — `python -m masp_skill.cli validate-routing --routing docs/masp/masp-routing.toml --classification STATIC`.
- [ ] **Step 3: Validate case** — `python -m masp_skill.cli validate-case --case tests/fixtures/cases/valid-case.json --root .`.
- [ ] **Step 4: Check CI** — examinar jobs e logs Ubuntu/Windows para o SHA final; não confiar apenas em badge.
- [ ] **Step 5: Audit PR diff** — nenhum arquivo fora do M07 e referências necessárias; não tocar `case.py` ou modules anteriores.
- [ ] **Step 6: Record limitations** — revisão independente Codex `NOT_RUN` se runtime indisponível, padrões reais `NOT_RUN`; cenários `SIMULATED` e Python `RUNTIME` do validador.
- [ ] **Step 7: Update draft PR** — título `feat(masp): padronização universal v2 com controles preventivos e monitoramento`, sem merge automático e com checklist de revisão humana.
- [ ] **Step 8: Confirm dependency** — integrar funcionalmente a M05/M06 **apenas depois** de entregas verificadas e autorizadas, sem afirmar operações reais por testes sintéticos.

## Parada de aprovação

**Este plano é proposta e não autorização para implementar.** Até o usuário aprovar o desenho, não criar código funcional, não editar TOML/skill, não executar testes RED e não alterar a `main`. O PR de desenho poderá ser usado para revisão e, somente após aprovação, atualizado com a implementação.
