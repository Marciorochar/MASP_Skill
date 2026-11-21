# MASP Verificação Universal v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** construir uma Verificação MASP universal que distingue execução, resultados, eficácia e regressões, sem extrapolar evidências ou autenticar revisões automaticamente.

**Architecture:** especificação canônica + matriz de verificação e baseline + ajustes de contratos M06, e validador Python/CLI exclusivamente estrutural se o desenho opcional for aprovado. Preserve o ledger `SIMULATED` e políticas existentes. O M05 Universal v2 não está implementado na `main` auditada; a integração real depende dessa entrega.

**Tech Stack:** Markdown, TOML, Python >=3.11, pytest, GitHub Actions Ubuntu/Windows.

**Spec:** `docs/superpowers/specs/2026-11-16-masp-verificacao-universal-v2-design.md`

## Global Constraints

- **Aprovação explícita do desenho antes de qualquer implementação.**
- Preservar exatamente `baseline_comparison`, `runtime_tests`, `relevant_regressions`, `independent_review`.
- Não modificar `src/masp_skill/case.py`, schema do ledger, fase ou transições do MASP.
- Não alterar M01–05/M07–08 além de referências estritamente necessárias à fase 06.
- Não autenticar resultados, revisão independente, aprovação ou eficácia a partir de rótulos JSON.
- `validate-verification` (se criado) é apenas `STATIC`, sem acesso a sistemas ou execução de testes físicos.
- Sem Astra, `runtime-smoke --all-roles`, ambientes de produção, intervenções reais, merge automático ou atalhos a gates.
- `NOT_RUN` para delegação Codex indisponível; `SIMULATED` para cenários sintéticos; `RUNTIME` com prova de comando/evento efetivamente observado.
- Branch isolada `feat/masp-verificacao-universal-v2`; nenhuma alteração direta da `main`.

## Review Focus

1. **Baseline incomparável:** números com unidade, período, população ou método diferentes devem produzir erro/limite explícito; jamais "melhoria".
2. **Denominador zero ou valor numérico malformado:** não calcular variação porcentual nem produzir exceção; devolver condição de não aplicabilidade.
3. **Intervenção não comprovada:** só existe relato de execução ou M05 simulado; não emitir conclusão de eficácia demonstrada.
4. **Revisão pelo próprio executor:** segregar funções; string `independent_review=approved` não é comprovação de independência real.
5. **Regressão importante ou teste NOT_RUN:** não emitir PASS por omissão ou por um resultado principal favorável.

---

### Task 1: Testes RED e corpus multidomínio

**Files:**
- Create: `tests/test_verification_v2.py`
- Create: `tests/fixtures/verificacao-v2/casos.json`

**Interfaces:** função proposta `validate_verification_record(record: Any) -> list[str]`; `compare_numeric_baseline(before: float, after: float, direction: str) -> dict` opcional se aprovada. `GATE_REQUIREMENTS["verificacao"]` fica intacto.

- [ ] **Step 1: Write the failing test** — `test_rejects_incomparable_baselines` com `baseline.unit="%" ` e `after.unit="hours"`; resultado deve conter `unit`.
- [ ] **Step 2: Run to verify RED** — `python -m pytest -q tests/test_verification_v2.py`; módulo ainda inexistente, falha identificável e anotada (não utilizar falha de fixture errada).
- [ ] **Step 3: Create 39 synthetic cases** — 9 domínios e 30 adversariais do arquivo de requisitos, com invariantes esperados. Não considerar como avaliação real de LLM.
- [ ] **Step 4: Verify structure** — corpus com IDs exclusivos e cenário/invariante não vazios.
- [ ] **Step 5: Commit** — apenas testes/fixtures.

### Task 2: Verificador estrutural e baseline (se aprovados)

**Files:**
- Create: `src/masp_skill/verification.py`
- Modify: `src/masp_skill/cli.py`
- Test: `tests/test_verification_v2.py`

**Interfaces:** `validate_verification_record(record: Any) -> list[str]`; comando `validate-verification --record PATH --root WORKSPACE`, retorna código 0/1 e imprime `STATIC`. Nenhuma autorização/gate emitido pelo resultado.

- [ ] **Step 1: Write focused RED cases** — baseline quantitativo/qualitativo/indisponível; unidade e período; denom. zero; tipos JSON inválidos; lista/enum não hashable; fonte duplicada; reviewer igual ao executor; `not_run` com resultado fabricado; regressão sem avaliação.
- [ ] **Step 2: Run and record actual RED errors** — confirmar que as falhas são das funcionalidades ainda não implementadas.
- [ ] **Step 3: Implement minimum** — validação apenas estrutural de campos/referências/consistência; cálculo numérico transparente, somente se necessário e aprovado.
- [ ] **Step 4: Execute GREEN** — testes focados e `python -m pytest -q` com saída comprovada.
- [ ] **Step 5: Commit** — código e testes verdes no SHA final.

### Task 3: Contratos da skill e modelos da fase

**Files:**
- Create: `docs/masp/verificacao/ESPECIFICACAO-V2.md`
- Create: `docs/masp/verificacao/REFERENCIAS-METODOLOGICAS.md`
- Create: `docs/masp/verificacao/MATRIZ-VERIFICACAO.md`
- Create: `docs/masp/verificacao/MODELO-COMPARACAO-BASELINE.md`
- Create: `docs/masp/verificacao/CONTROLE-REGRESSOES.md`
- Modify: `docs/masp/agentes/06-verificacao.md`
- Modify: `.codex/agents/masp-testador.toml`
- Modify: `docs/masp/masp-routing.toml` **somente bloco M06**
- Modify: `.agents/skills/masp/SKILL.md` **somente item M06**
- Modify: `docs/masp/modelos/CASO-MASP.md`, `README.md` **somente referências M06**

- [ ] **Step 1: Test old contract** — quando disponível, teste de pressão real do `masp-testador` sem a versão v2; se ferramenta não existir, marcar `NOT_RUN`, não inventar.
- [ ] **Step 2: Write docs** — modos rápido/aprofundado, baseline qualitativo/quantitativo/indisponível, qualidade da comparação, avaliação de eficácia, regressões e parecer independente, sem teste perigoso.
- [ ] **Step 3: Preserve interfaces** — quatro IDs do Gate 06 e retornos atuais (Ação/Análise); tratar Observação via rota válida.
- [ ] **Step 4: Verify integration** — validações routing/case, testes e revisão dos documentos; corrigir apenas regressões reais.
- [ ] **Step 5: Commit** — contrato/documentação M06.

### Task 4: Evidências, revisão independente e PR rascunho

**Files:**
- Create: `docs/masp/verificacao/RELATORIO-TESTES-V2.md`

- [ ] **Step 1:** executar `python -m pytest -q`, capturar número real de PASS/skip/FAIL e código de saída.
- [ ] **Step 2:** executar `python -m masp_skill.cli validate-routing --routing docs/masp/masp-routing.toml --classification STATIC`.
- [ ] **Step 3:** executar `python -m masp_skill.cli validate-case --case tests/fixtures/cases/valid-case.json --root .`.
- [ ] **Step 4:** verificar GitHub Actions Windows e Ubuntu no último SHA e logs de jobs (não só badges); inspeção de diff sem arquivos fora do escopo.
- [ ] **Step 5:** registrar classificação de evidência e limitações: testes Python RUNTIME **do software de validação**, cenários SIMULATED, agente Codex real NOT_RUN se não disponível.
- [ ] **Step 6:** criar PR em rascunho `feat(masp): verificação universal v2 com avaliação de eficácia e regressões`; não fazer merge.
- [ ] **Step 7:** obter revisão humana e confirmar dependência funcional do M05 antes de alegar integração completa.

## Parada de aprovação

**O presente plano é apenas proposta para aprovação.** Não criar testes RED nem editar contratos/implementação do M06 até haver aprovação explícita do desenho. Não realizar intervenções reais; a documentação não equivale a Gate 06 PASS.
