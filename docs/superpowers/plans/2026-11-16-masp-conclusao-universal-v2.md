# MASP Conclusão Universal v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** criar o Módulo 08 de Conclusão Universal v2 para consolidar as oito fases com rastreabilidade, resultados honestos, riscos residuais, pendências, lições e parecer, sem confundir encerramento com resolução ou autorização de produção.

**Architecture:** especificação/ficha humana e matrizes de decisão, correções localizadas nas instruções M08, e validador Python/CLI opcional exclusivamente `STATIC`. O ledger existente, os seis critérios do Gate 08, políticas de alto risco e transições permanecem intactos. M05/M06 ainda não têm execução universal funcional; M07 permanece em PR #13 de desenho na data da auditoria.

**Tech Stack:** Markdown, TOML, Python 3.11+, pytest, GitHub Actions Ubuntu/Windows.

**Spec:** `docs/superpowers/specs/2026-11-16-masp-conclusao-universal-v2-design.md`

## Global Constraints

- **Não iniciar implementação funcional antes da aprovação explícita do desenho.**
- Preservar literalmente `complete_ledger`, `results`, `limitations`, `residual_risks`, `pending_items`, `audit_opinion` em `GATE_REQUIREMENTS["conclusao"]`.
- Não modificar `src/masp_skill/case.py`, schema do ledger, transições ou contratos dos M01–07.
- Não converter `STATIC`/`SIMULATED` em `RUNTIME`; não autenticar aprovações humanas, auditoria independente ou eficácia com JSON.
- Separar encerramento técnico, administrativo, conclusão do problema, implantação, merge e promoção à produção; nenhuma CLI de execução/encerramento automático.
- Preservar retorno M08 apenas para M06 (Verificação) e M07 (Padronização). Respeitar política `high_risk_requires_astra`; sem Astra nesta sessão e `BLOCKED` quando requerido e indisponível.
- Somente branch `feat/masp-conclusao-universal-v2`; não alterar `main`, não realizar merge/implantações nem modificar dados externos.
- `superpowers:finishing-a-development-branch` só em software, se disponível e pertinente; não usar como aprovação de deploy.
- Testes de agentes reais só se houver ferramenta de subagentes com evidência verificável; senão `NOT_RUN`.

## Review Focus

1. **Ledger ausente/bloqueado/incompleto:** relatório não pode declarar ciclo plenamente concluído nem inventar registros faltantes.
2. **Hash válido com declaração falsa:** validação de integridade não prova aprovação, execução, eficácia ou responsabilidade.
3. **Resultado negativo/inconclusivo omitido:** parecer deve preservar resultados contrários mesmo diante de pressão para dizer “resolvido”.
4. **Risco ou pendência crítica sem dono:** documentar e impedir conclusão sem ressalva ou gate apropriado.
5. **Encerramento administrativo ≠ resolução ou implantação:** não emitir `PASS` automático ou autorização operacional a partir de arquivamento.

---

### Task 1: Testes RED e corpus multidomínio (se JSON aprovado)

**Files:**
- Create: `tests/test_conclusion_v2.py`
- Create: `tests/fixtures/conclusao-v2/casos.json`

**Interfaces:** `validate_conclusion_record(record: Any) -> list[str]` em `src/masp_skill/conclusion.py` (somente validará estrutura), caso a proposta de sidecar seja aprovada. Manter `GATE_REQUIREMENTS["conclusao"]` inalterado.

- [ ] **Step 1: Write failing test** — `test_missing_ledger_reference_rejects_full_closure()`: `closure_decision=complete` sem `complete_ledger` válido precisa gerar erro, não PASS.
- [ ] **Step 2: Verify RED** — executar `python -m pytest -q tests/test_conclusion_v2.py`; registrar falha esperada pela ausência do módulo/contrato, sem erro acidental de fixture.
- [ ] **Step 3: Build corpus** — 9 domínios sintéticos (indústria, logística, saúde, administração, ambiente, tecnologia, educação, serviços, cotidiano) e 32 cenários adversariais explícitos da especificação do usuário, cada um com ID único, entrada, invariante e status.
- [ ] **Step 4: Verify corpus** — 41 casos completos, classificação `SIMULATED`, nenhum dado real ou prova de comportamento de agente.
- [ ] **Step 5: Commit tests** — somente testes e fixtures.

### Task 2: Validação estrutural opcional e CLI sem side effects

**Files:**
- Create: `src/masp_skill/conclusion.py`
- Modify: `src/masp_skill/cli.py`
- Test: `tests/test_conclusion_v2.py`

**Interfaces:** `validate_conclusion_record(record: Any) -> list[str]` e `validate-conclusion --record PATH --root WORKSPACE`, stdout `STATIC`, retorno 0/1; nunca assinar, autenticar, fechar gates ou executar ações.

- [ ] **Step 1: Add RED cases** — IDs duplicados, referências incoerentes entre fases, hash inconsistente quando arquivo conhecido, status `NOT_RUN` com resultado falsamente comprovado, fonte sem proveniência, caso de alto risco com auditoria exigida ausente, campos obrigatórios nulos, tipos JSON não-hashable e path fora de workspace.
- [ ] **Step 2: Verify RED** — rodar suíte focal e preservar saída da falha esperada.
- [ ] **Step 3: Implement minimum** — conferir estrutura declarada, listas de evidência, enumerações e coerência entre estados e conclusão, sem atribuir veracidade aos dados.
- [ ] **Step 4: Verify GREEN** — teste focal e suíte integral; impedir regressões dos módulos anteriores.
- [ ] **Step 5: Commit implementation** — somente código/CLI/testes aprovados.

### Task 3: Contratos universais, modelos e matriz de fechamento

**Files:**
- Create: `docs/masp/conclusao/ESPECIFICACAO-V2.md`
- Create: `docs/masp/conclusao/REFERENCIAS-METODOLOGICAS.md`
- Create: `docs/masp/conclusao/MODELO-RELATORIO-FINAL.md`
- Create: `docs/masp/conclusao/MATRIZ-RASTREABILIDADE.md`
- Create: `docs/masp/conclusao/MATRIZ-RISCOS-PENDENCIAS.md`
- Create: `docs/masp/conclusao/LICOES-APRENDIDAS.md`
- Create: `docs/masp/conclusao/CRITERIOS-ENCERRAMENTO.md`
- Modify: `docs/masp/agentes/08-conclusao.md`
- Modify: `.codex/agents/masp-relator.toml`
- Modify: `docs/masp/masp-routing.toml` (bloco M08, sem mudar retornos)
- Modify: `.agents/skills/masp/SKILL.md` (somente item M08)
- Modify: `docs/masp/modelos/CASO-MASP.md` e `README.md` (somente referência/ficha M08)

- [ ] **Step 1: Pressure test current behavior** — quando runtime Codex disponível, pedir ao `masp-relator` que conclua como resolvido apesar de `BLOCKED`/simulação; obter observação factual. Senão, `NOT_RUN`.
- [ ] **Step 2: Author M08 universal contract** — matriz das oito fases, comparativo de objetivos, preservação de resultados negativos, riscos, pendências, lições, decisão de encerramento, segregação de aprovações e resumo executivo versus relatório técnico.
- [ ] **Step 3: Respect scope** — restrições OTServer somente se caso OTServer; não mudar modelo/effort nem fazer o relator promover sistemas.
- [ ] **Step 4: Verify contracts** — gates exatos, transições intactas, `validate-routing`, `validate-case`, revisão do diff e ausência de novos estados no ledger.
- [ ] **Step 5: Commit docs** — mudanças só na fase M08 e referências necessárias.

### Task 4: Relatório de provas, revisão e PR

**Files:**
- Create: `docs/masp/conclusao/RELATORIO-TESTES-V2.md`

- [ ] **Step 1: Execute suite** — `python -m pytest -q` e registrar contagens e exit code reais de PASS/skip/FAIL.
- [ ] **Step 2: Validate routing** — `python -m masp_skill.cli validate-routing --routing docs/masp/masp-routing.toml --classification STATIC`.
- [ ] **Step 3: Validate case** — `python -m masp_skill.cli validate-case --case tests/fixtures/cases/valid-case.json --root .`.
- [ ] **Step 4: Verify CI** — ler jobs/logs Ubuntu e Windows no SHA final (não apenas sucesso geral).
- [ ] **Step 5: Audit diff** — não modificar `case.py`, gates M01–07, retorno da Conclusão, políticas de segurança ou arquivos fora do escopo.
- [ ] **Step 6: Record limitations** — `masp-relator` Codex e revisão independente `NOT_RUN` quando não observados; 41 cenários `SIMULATED`; testes Python `RUNTIME` somente da ferramenta.
- [ ] **Step 7: Update draft PR** — após aprovação, atualizar título para `feat(masp): conclusão universal v2 com auditoria, riscos residuais e lições aprendidas`; sem merge automático.
- [ ] **Step 8: Check M05–M07** — registrar dependências, PR #13 e implementação real antes de alegar funcionamento completo MASP.

## Parada de aprovação

**Este plano é para revisão, não é autorização de implementação.** Até aprovação explícita do desenho, não iniciar RED, não alterar TOML/skill/código/gates, não declarar M08 operacional e não acessar sistemas reais. O PR rascunho contém apenas os dois documentos de concepção.
