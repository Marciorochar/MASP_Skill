# MASP Análise Universal v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans when the active runtime supports them. Neste Chat há GitHub API, mas não execução de subagentes Codex; nenhuma delegação deve ser inventada.

**Goal:** implementar análise causal universal e validação estrutural opcional de matriz de hipóteses/evidências.

**Architecture:** especificação canônica + ficha de análise + contratos existentes, sidecar JSON verificado por Python/CLI, sem mudança no ledger MASP.

**Tech Stack:** Markdown, TOML, Python >=3.11, pytest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-11-16-masp-analise-universal-v2-design.md`

## Global Constraints
- Preservar `hypotheses`, `evidence_for_and_against`, `root_cause_or_explicit_inconclusive`.
- Não modificar `case.py` nem módulos 01/02, 04–08.
- Não executar Astra, `runtime-smoke --all-roles`, intervenções reais ou merge automático.
- Classificar corretamente STATIC, SIMULATED, RUNTIME e NOT_RUN; não autenticar evidências declarativas.
- Sem causalidade automática, pontuações de confiança inventadas ou dados não consultados.

## Review Focus
- `CORROBORADA` com verificação não executada deve falhar na validação estrutural.
- `supported` referindo hipótese não corroborada não pode passar.
- Uma hipótese sem contraevidência deve declarar a revisão e os limites, não dizer que a ausência a confirma.
- IDs duplicados, faltantes ou cruzados devem ser detectados.
- `inconclusive` com análise realmente documentada deve ser admissível; não significa automaticamente PASS do gate.

---

### Task 1: Escrever testes de comportamento e fixtures antes do código
**Files:** `tests/test_analysis_v2.py`, `tests/fixtures/analise-v2/casos.json`
- [ ] Definir registro fictício com evidências e hipóteses concorrentes, sem padrão de correção automática.
- [ ] Escrever casos de invariantes e CLI com entradas válidas e adversariais.
- [ ] Confirmar RED no CI por módulo/função ausente, registrar logs.

### Task 2: Implementar validador e CLI
**Files:** `src/masp_skill/analysis.py`, `src/masp_skill/cli.py`
- [ ] Checar tipos, referências, duplicatas, conclusão e status de verificação; sem exigir experimento físico.
- [ ] Expor `validate-analysis` que retorna STATIC e 0/1; respeitar `--root`.
- [ ] Validar GREEN na suíte integral e checagens existentes.

### Task 3: Documentar metodologia e integrar contratos
**Files:** `docs/masp/analise/*`, `docs/masp/agentes/03-analise.md`, `.codex/agents/masp-analista.toml`, `.agents/skills/masp/SKILL.md`, `docs/masp/masp-routing.toml`, `docs/masp/modelos/CASO-MASP.md`, `README.md`
- [ ] Modo rápido/aprofundado, hipóteses rivais, evidência favorável/contrária, confusão e inconclusão.
- [ ] Documentar referências, limites de licenças, segurança e respeito ao domínio.
- [ ] Alterar apenas o bloco M03 na matriz, mantendo três IDs do gate.

### Task 4: Evidências, revisão e PR
**Files:** `docs/masp/analise/RELATORIO-TESTES-V2.md`
- [ ] Verificar GitHub Actions no SHA final e conferir resultados Windows/Ubuntu.
- [ ] Executar validação de roteamento e case fixture, registrar número real de PASS/skip.
- [ ] Verificar diff e conflitos; revisão de agente Codex e avaliação de LLM ficam NOT_RUN quando indisponíveis.
- [ ] Criar PR rascunho para main, sem merge.
