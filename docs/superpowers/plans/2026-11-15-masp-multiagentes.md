# MASP Multiagentes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Entregar uma configuração multiagente MASP local ao repositório, com roteamento verificável, gates executáveis, ledger rastreável, agentes especializados e documentação operacional.

**Architecture:** `.codex/config.toml` registra dez papéis locais; `docs/masp/masp-routing.toml` é a fonte declarativa das oito fases e políticas transversais. Um pacote Python de biblioteca padrão valida configuração e controla transições de caso; testes Pytest distinguem validação estática, simulações e smoke tests reais do CLI.

**Tech Stack:** Codex CLI 0.169.x, TOML, Python 3.14 (`tomllib`, `argparse`, `json`, `pathlib`), Pytest 9.2, Markdown.

**Spec:** `docs/superpowers/specs/2026-11-15-masp-multiagentes-design.md`

## Global Constraints

- Implantação restrita ao repositório `MASP_Skill`; nenhuma alteração em `C:\Users\marci\.codex` ou projetos externos.
- Modelos exatos: `gpt-6.1-sol`, `gpt-6-luna`, `gpt-6.1-terra`, `gpt-6-astra`.
- Esforços padrão exatos: `medium`, `low`, `medium`, `medium` conforme cada papel; `llow` é inválido e vira explicitamente `low`.
- Ordem imutável: Identificação, Observação, Análise, Plano de ação, Ação, Verificação, Padronização, Conclusão.
- Estados fechados: `PENDING`, `IN_PROGRESS`, `PASS`, `FAIL`, `BLOCKED`, `NOT_RUN`.
- Somente o coordenador delega; filhos não criam subagentes; executor não autoaprova.
- Modelo indisponível bloqueia o caso; não há fallback silencioso.
- Astra só é obrigatório para alto risco ou outra condição crítica documentada.
- Máximo inicial de três agentes concorrentes, reduzido ao limite efetivo do runtime.
- Resultados devem ser rotulados `STATIC`, `SIMULATED` ou `RUNTIME`.
- Não fazer push, merge, PR ou publicação.

## Review Focus

- Ledger editado manualmente deve falhar validação de integridade; teste em Task 3.
- Modelo ausente ou esforço inválido deve produzir bloqueio/erro explícito, nunca fallback; testes em Tasks 1 e 3.
- Evidência vazia, inexistente ou classificada como simulação não deve satisfazer gate que exige runtime; testes em Task 3.
- Alto risco sem parecer Astra deve impedir `PASS`; teste em Task 3.
- Dois trabalhos paralelos com o mesmo arquivo de escrita devem ser rejeitados; teste em Task 3.

---

### Task 1: Matriz declarativa e validador estático

**Files:**
- Create: `docs/masp/masp-routing.toml`
- Create: `src/masp_skill/__init__.py`
- Create: `src/masp_skill/routing.py`
- Create: `src/masp_skill/cli.py`
- Create: `tests/test_routing.py`
- Create: `pyproject.toml`

**Interfaces:**
- Consumes: nenhum componente novo.
- Produces: `load_routing(path: Path) -> dict`, `validate_routing(data: dict) -> list[str]`, comando `python -m masp_skill.cli validate-routing`.

- [ ] **Step 1: Escrever testes falhos da matriz**

Cobrir oito fases em ordem, dez papéis, modelos/esforços exatos, skills, gates, retornos, paralelismo três, auditoria, política de indisponibilidade e rejeição de `llow`, modelo fictício, fase ausente e skill sem caminho registrado.

- [ ] **Step 2: Executar os testes e confirmar falha inicial**

Run: `python -m pytest tests/test_routing.py -q`

Expected: FAIL porque o pacote e a matriz ainda não existem.

- [ ] **Step 3: Criar a matriz TOML e implementar carregamento/validação mínima**

Implementar as duas assinaturas em `routing.py`; usar `tomllib`; retornar todos os erros determinísticos sem modificar arquivos.

- [ ] **Step 4: Executar o teste direcionado**

Run: `python -m pytest tests/test_routing.py -q`

Expected: PASS.

- [ ] **Step 5: Executar o CLI estático**

Run: `python -m masp_skill.cli validate-routing --routing docs/masp/masp-routing.toml --classification STATIC`

Expected: exit 0 e relatório `STATIC` com oito fases e zero erros.

- [ ] **Step 6: Commit da unidade**

Run: `git add pyproject.toml src tests/test_routing.py docs/masp/masp-routing.toml && git commit -m "feat: add declarative MASP routing validation"`

### Task 2: Configuração local e contratos dos agentes

**Files:**
- Create: `.codex/config.toml`
- Create: `.codex/agents/masp-coordenador.toml`
- Create: `.codex/agents/masp-identificador.toml`
- Create: `.codex/agents/masp-observador.toml`
- Create: `.codex/agents/masp-analista.toml`
- Create: `.codex/agents/masp-planejador.toml`
- Create: `.codex/agents/masp-executor.toml`
- Create: `.codex/agents/masp-testador.toml`
- Create: `.codex/agents/masp-padronizador.toml`
- Create: `.codex/agents/masp-relator.toml`
- Create: `.codex/agents/masp-especialista-critico.toml`
- Create: `tests/test_agent_config.py`
- Modify: `src/masp_skill/routing.py`

**Interfaces:**
- Consumes: `load_routing`, `validate_routing` da Task 1.
- Produces: `load_agent_configs(root: Path) -> dict[str, dict]`, `validate_agent_configs(routing: dict, agents: dict) -> list[str]`.

- [ ] **Step 1: Escrever testes falhos dos papéis locais**

Verificar nomes, arquivos referenciados, modelo, esforço, proibição de spawn nos filhos, autoridade exclusiva do coordenador, executor sem autoaprovação e auditor sem escrita.

- [ ] **Step 2: Confirmar a falha inicial**

Run: `python -m pytest tests/test_agent_config.py -q`

Expected: FAIL por ausência da configuração.

- [ ] **Step 3: Implementar os dez contratos e o registro local**

Manter instruções pequenas, específicas e coerentes com a matriz; configurar máximo três; não copiar nem alterar defaults globais.

- [ ] **Step 4: Implementar validação cruzada configuração ↔ matriz**

Adicionar as assinaturas declaradas e erros para papel ausente, modelo/esforço divergente e filho com autoridade de delegação.

- [ ] **Step 5: Executar testes direcionados e regressão da Task 1**

Run: `python -m pytest tests/test_agent_config.py tests/test_routing.py -q`

Expected: PASS.

- [ ] **Step 6: Commit da unidade**

Run: `git add .codex src/masp_skill/routing.py tests/test_agent_config.py && git commit -m "feat: configure local MASP agent roles"`

### Task 3: Estado, evidências e gates executáveis

**Files:**
- Create: `src/masp_skill/case.py`
- Create: `src/masp_skill/evidence.py`
- Create: `tests/test_case_transitions.py`
- Create: `tests/fixtures/cases/valid-case.json`
- Modify: `src/masp_skill/cli.py`
- Modify: `docs/masp/modelos/CASO-MASP.md`

**Interfaces:**
- Consumes: matriz validada da Task 1.
- Produces: `create_case(case_id: str, routing: dict) -> dict`, `validate_case(case: dict, routing: dict, root: Path) -> list[str]`, `transition_case(case: dict, target_state: str, actor: str, evidence: list[dict], routing: dict) -> dict`, comandos `new-case`, `transition` e `validate-case`.

- [ ] **Step 1: Escrever testes falhos de transição**

Cobrir caminho feliz, salto de fase, `PASS` sem evidência, executor autoaprovando, plano sem aprovação humana, `BLOCKED`, retorno após `FAIL`, classificação inadequada de evidência, adulteração do ledger e ator não coordenador.

- [ ] **Step 2: Adicionar testes críticos da Review Focus**

Cobrir modelo indisponível, alto risco sem Astra, conflito de escrita paralela e evidência referenciando arquivo inexistente.

- [ ] **Step 3: Confirmar falhas iniciais**

Run: `python -m pytest tests/test_case_transitions.py -q`

Expected: FAIL por ausência do motor.

- [ ] **Step 4: Implementar caso, evidência e transição central**

Persistência deverá ser escrita pelo CLI de forma atômica; cada evento conterá sequência, estado anterior/novo, ator, timestamp, evidências, classificação e hash encadeado do evento anterior.

- [ ] **Step 5: Atualizar o modelo humano de caso**

Alinhar campos Markdown ao manifesto JSON e documentar que edição manual não autoriza transição.

- [ ] **Step 6: Executar testes direcionados e suíte acumulada**

Run: `python -m pytest tests/test_case_transitions.py tests/test_routing.py tests/test_agent_config.py -q`

Expected: PASS.

- [ ] **Step 7: Exercitar um cenário simulado**

Run: `python -m masp_skill.cli new-case --id MASP-TEST --output .tmp/masp-test.json` seguido das transições simuladas até uma tentativa de salto.

Expected: criação rotulada `SIMULATED`; salto rejeitado com exit não zero. Remover apenas o arquivo temporário explicitamente criado após registrar o resultado.

- [ ] **Step 8: Commit da unidade**

Run: `git add src tests docs/masp/modelos/CASO-MASP.md && git commit -m "feat: enforce MASP evidence gates"`

### Task 4: Skill MASP e integração com skills instaladas

**Files:**
- Create: `skills/masp/SKILL.md`
- Create: `skills/masp/references/routing-guide.md`
- Create: `tests/test_skill_contract.py`
- Modify: `docs/masp/LEIA-ME.md`
- Modify: `docs/masp/MASP-ARQUITETURA.md`
- Modify: `docs/masp/agentes/02-observacao.md`
- Modify: `docs/masp/agentes/05-acao.md`

**Interfaces:**
- Consumes: matriz, CLI e papéis das Tasks 1–3.
- Produces: skill principal descoberta por caminho local e contratos documentais sem conflito entre `dispatching-parallel-agents` e `subagent-driven-development`.

- [ ] **Step 1: Ler integralmente `writing-skills` antes de editar a skill**

Expected: checklist e requisitos da versão instalada incorporados ao trabalho.

- [ ] **Step 2: Escrever testes falhos do contrato da skill**

Validar frontmatter, gatilho, referências existentes, oito fases, estados, comandos oficiais, skills Superpowers confirmadas e ausência de REA como requisito.

- [ ] **Step 3: Confirmar a falha inicial**

Run: `python -m pytest tests/test_skill_contract.py -q`

Expected: FAIL por ausência da skill.

- [ ] **Step 4: Criar a skill e reconciliar documentação existente**

Explicar que o coordenador usa `dispatching-parallel-agents` para fan-out e que Ação pode usar `subagent-driven-development` para executar plano. Preservar advertências e limites existentes.

- [ ] **Step 5: Executar testes direcionados e acumulados**

Run: `python -m pytest tests/test_skill_contract.py tests/test_routing.py tests/test_agent_config.py tests/test_case_transitions.py -q`

Expected: PASS.

- [ ] **Step 6: Commit da unidade**

Run: `git add skills docs/masp tests/test_skill_contract.py && git commit -m "feat: integrate MASP skill with Superpowers"`

### Task 5: Descoberta e smoke tests do Codex

**Files:**
- Create: `tests/runtime/test_codex_smoke.py`
- Create: `scripts/run_codex_smoke.ps1`
- Create: `docs/masp/evidencias/.gitkeep`
- Modify: `src/masp_skill/cli.py`

**Interfaces:**
- Consumes: configuração local e CLI das Tasks 1–4.
- Produces: relatório JSON/Markdown rotulado `RUNTIME` quando comandos reais forem executados; `NOT_RUN` quando pré-requisitos não forem satisfeitos.

- [ ] **Step 1: Escrever testes falhos do coletor de smoke**

Testar parser com saídas fixture, rejeição de modelo divergente e proibição de marcar `RUNTIME` sem comando, exit code e stdout/stderr registrados.

- [ ] **Step 2: Confirmar falha inicial**

Run: `python -m pytest tests/runtime/test_codex_smoke.py -q`

Expected: FAIL por ausência do coletor.

- [ ] **Step 3: Implementar runner seguro e classificações**

O script executará validação de catálogo, descoberta local, uma delegação mínima por papel, carregamento da skill e cenários coordenador/filho; não fará alterações externas.

- [ ] **Step 4: Executar testes unitários do coletor**

Run: `python -m pytest tests/runtime/test_codex_smoke.py -q`

Expected: PASS sem depender do Codex real.

- [ ] **Step 5: Executar smoke real no CLI atual**

Run: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_codex_smoke.ps1`

Expected: relatório com cada checagem `PASS`, `FAIL`, `BLOCKED` ou `NOT_RUN`, modelo/esforço observados, comandos e versão. Falha de descoberta local deve ser registrada como bloqueio e não mascarada.

- [ ] **Step 6: Avaliar fallback C somente se necessário**

Se os papéis locais não forem descobertos, documentar evidência e preparar proposta de roteamento explícito; não editar configuração global e não chamar o fallback de equivalente sem teste.

- [ ] **Step 7: Commit da unidade**

Run: `git add scripts tests/runtime src/masp_skill/cli.py docs/masp/evidencias && git commit -m "test: add Codex runtime smoke evidence"`

### Task 6: README, exemplo executado e relatório técnico

**Files:**
- Modify: `README.md`
- Modify: `docs/masp/PROMPT-CODEX.md`
- Create: `docs/masp/RELATORIO-IMPLEMENTACAO.md`
- Create: `docs/masp/exemplos/MASP-CONFIG-SMOKE.md`
- Create: `tests/test_documentation.py`

**Interfaces:**
- Consumes: comandos e evidências das Tasks 1–5.
- Produces: instruções completas para iniciar caso, interpretar classificações, diagnosticar bloqueios e reproduzir testes.

- [ ] **Step 1: Escrever testes falhos de documentação**

Verificar comandos existentes, caminhos reais, matriz final, inventário, diferenciação STATIC/SIMULATED/RUNTIME, ausência de placeholders e proibição de alegar sucesso não comprovado.

- [ ] **Step 2: Confirmar falhas iniciais**

Run: `python -m pytest tests/test_documentation.py -q`

Expected: FAIL enquanto README e relatório não estiverem alinhados.

- [ ] **Step 3: Atualizar documentação e criar relatório**

O relatório deve conter os dez itens solicitados na missão, incluindo inventários, arquivos, testes, riscos, custo/desempenho, início de caso e parecer independente.

- [ ] **Step 4: Executar teste documental e suíte completa**

Run: `python -m pytest -q`

Expected: PASS; testes runtime podem ser explicitamente marcados/skipped somente quando o relatório os classificar `NOT_RUN` com motivo.

- [ ] **Step 5: Executar validações finais**

Run: `python -m masp_skill.cli validate-routing --classification STATIC` e `python -m masp_skill.cli validate-case` sobre o exemplo criado.

Expected: ambos exit 0; classificações preservadas.

- [ ] **Step 6: Commit da unidade**

Run: `git add README.md docs tests/test_documentation.py && git commit -m "docs: document multi-agent MASP operation"`

### Task 7: Auditoria independente e correção

**Files:**
- Modify: somente arquivos associados a achados confirmados, pelo executor responsável.
- Append: `docs/masp/RELATORIO-IMPLEMENTACAO.md`

**Interfaces:**
- Consumes: branch completa e evidências de todas as tasks.
- Produces: parecer independente, mapa achado → correção → revalidação e decisão final.

- [ ] **Step 1: Solicitar auditoria independente ASTRA**

Auditar requisitos, configuração, segurança das transições, testes, classificações de evidência, escopo do diff e ausência de alterações globais.

- [ ] **Step 2: Registrar achados com severidade e evidência**

Expected: nenhum achado é corrigido pelo auditor.

- [ ] **Step 3: Encaminhar achados confirmados ao executor TERRA**

Cada correção deve possuir arquivos exclusivos e teste de regressão pertinente.

- [ ] **Step 4: Revalidar somente achados corrigidos e regressões relacionadas com LUNA**

Expected: vínculo explícito entre achado, mudança, comando e resultado.

- [ ] **Step 5: Executar suíte final e conferir escopo Git**

Run: `python -m pytest -q`, `git status --short`, `git diff main...HEAD --stat`.

Expected: suíte verde ou bloqueios documentados; somente arquivos do MASP_Skill alterados.

- [ ] **Step 6: Commit final de correções e evidências**

Adicionar explicitamente somente os caminhos listados nos achados corrigidos e criar o commit `fix: address independent MASP audit findings`; se não houver correções, versionar apenas o parecer ainda não registrado.

