# Desenho técnico — MASP Módulo 05: Ação Universal v2

**Data:** 2026-11-16  
**Status:** PROPOSTA — aguarda aprovação humana antes de código, contratos ou testes serem alterados  
**Branch:** `feat/masp-acao-universal-v2`  
**Base auditada:** `main` `a8fc77cdc284ceb90611b95b5f9d315193696060`

## 1. Contexto e diagnóstico (auditoria do repositório)

O PR #10 foi mesclado e a `main` contém o Módulo 04 Universal v2. O contrato atual `docs/masp/agentes/05-acao.md` define execução em workspace isolado e saída centrada em `diff/commits`, comandos, testes RED-GREEN e logs. Isso é útil para software, mas insuficiente para processos industriais, logísticos, administrativos, clínicos ou ambientais.

O motor `src/masp_skill/case.py` declara e valida eventos **SIMULATED**, sem autenticação de identidade, aprovação ou execução real. O Gate 05 exige EXATAMENTE `changes`, `diff`, `commands`, `results` e `no_self_approval`. O arquivo `docs/masp/masp-routing.toml` define o executor, `read-only` / `write-approved` / `execute-approved`, retorno ao Plano de Ação e skills Superpowers com caminhos locais Windows. Não se deve tratar a existência desses caminhos como comprovação de skill carregada no Codex.

A fase 06 exige avaliação independente, baseline e testes: a fase 05 deve registrar execução local, **não** declarar eficácia comprovada. O `action_plan.py` do Módulo 04 valida somente declarações, inclusive `human_approval.status`; ele **não autentica pessoas ou assinaturas**.

| Área auditada | Estado atual | Lacuna da v1 | Direção da v2 |
| --- | --- | --- | --- |
| Aprovação | Contrato textual e gate simulado | Nenhum verificador real de identidade/escopo | Falha fechada; aprovação externa efetivamente conferida por processo competente |
| Isolamento | Workspace mencionado | Depende de software | Sandbox/worktree, piloto autorizado, protótipo, área controlada conforme domínio |
| Execução | Diff/comandos/testes RED-GREEN | Registro pouco universal | Evidências de mudança antes/depois por tarefa, comando OU procedimento |
| Riscos/contingência | Restrições OTServer persistentes | Sem modelo de stop/irreversibilidade universal | Controles por ação, rollback parcial, contingência e ponto de não retorno |
| Desvios | Orientação genérica | Sem classificação de incidente/retorno | Stop, preservar evidência, comunicar, revalidar escopo e retornar ao M04 |
| Autoaprovação | Proibição textual | Ledger não comprova identidade | Separar executor, aprovador externo e verificador; não declarar aprovação automática |
| Teste | RED-GREEN centrado em software | Falta plano proporcional a outros domínios | Checks locais seguros; eficácia somente M06 |
| Evidência | `STATIC`, `SIMULATED`, `RUNTIME` | Rótulo pode ser autodeclarado | Explicitar proveniência, ação realmente observada e `NOT_RUN` |

## 2. Alternativas de arquitetura

**A — somente documentos e roteamento:** menor custo e nenhum código; não valida nem consistência de IDs/estado.

**B — estender o ledger/motor para executar ações:** automação atraente em software, mas exige autenticação, privilégios e validação de segurança não existentes; alto risco de regressão e de executar intervenções indevidas. **Não recomendada.**

**C — especificação + fichas humanas + sidecar opcional de registro (recomendada):** preserva os gates e o ledger; um validador Python pode verificar integridade **estrutural declarativa**, sem executar comandos ou autenticar pessoas. Documentação define o processo real de aprovação e isolamento. A CLI permanece sem capacidade de executar intervenções. Este caminho é compatível com a evolução 01–04.

## 3. Fronteiras de confiança e pré-execução

- **Desenvolver a skill não autoriza executar um caso MASP.** Nenhuma rotina da v2 deve executar servidores, procedimentos físicos, operações clínicas, produção, VPS ou modificações de serviços reais.
- **Aprovação externa:** confirmar plano/versão/hash quando disponíveis, pessoa competente, escopo, ambiente, tarefas, limites, janela e validade em sistema ou processo autorizado. Uma string `approved`, um `approved_by` ou SHA-256 de documento **não autentica** aprovação. A CLI poderá validar campos obrigatórios, mas seu resultado será `STATIC`.
- **GO/NO_GO:** decisão operacional separada do ledger, com autoridade real, justificativa e referências protegidas. Sem confirmação independente, `NO_GO`/ `BLOCKED`; não usar `GO` gerado por IA para liberar ação.
- **Isolamento:** software em branch/worktree/sandbox; indústria em bancada/linha piloto/autorizada; serviços em fluxo controlado; saúde/ambiente sob responsabilidade profissional. Se inexistente, registrar limitação/impedimento, não simular isolamento.
- **Critérios de stop:** mudanças não autorizadas, versão divergente, risco novo, evidência ausente, interferência externa, teste imediato reprovado, perda de isolamento, pessoa/competência não disponível.
- **Reversível/parcial/irreversível:** rollback somente quando seguro e autorizado; nas irreversíveis, contingência, ponto de não retorno e autorização especial. Jamais fingir que contingência equivale a restauração da condição original.

## 4. Fluxo universal por tarefa

1. Ler M04, M01–03 e `AGENTS.md` do caso; confirmar plano e evidências disponíveis.
2. Conferir autorização externa/versão/escopo por mecanismo competente; sem prova confiável => `BLOCKED`.
3. Registrar condição inicial e identidade do ambiente de execução aprovado; conferir pré-requisitos.
4. Planejar checkpoints, testes locais e responsáveis; não iniciar ação por simples documento válido.
5. Executor autorizado executa **somente a tarefa** em ambiente isolado/controlado; nenhuma execução real nesta implementação do MASP_Skill.
6. Capturar mudança antes/depois, procedimento/comandos verdadeiros, resultados, código de saída quando aplicável, desvios e evidências.
7. Quando ocorrer stop, interromper, preservar dados, aplicar apenas resposta autorizada; retornar ao M04 se for necessária mudança nova.
8. Documentar rollback/contingência executado ou `NOT_RUN`, sem inventar sucesso.
9. Encaminhar à fase 06 o material para verificação **independente** de eficácia, sem autoaprovação.

## 5. Contrato proposto e compatibilidade

Preservar exatamente `GATE_REQUIREMENTS["acao"] = {"changes", "diff", "commands", "results", "no_self_approval"}`; não alterar `src/masp_skill/case.py`, o ledger, esquemas existentes, modelos ou outras fases.

Ficha Markdown universal (`docs/masp/acao/MODELO-EXECUCAO.md`):

- IDs do caso, plano e tarefa; versão aprovada; referência à aprovação externa (não incluir dados confidenciais no Git público).
- Tipo de ambiente, controle de isolamento e pré-condições; `GO/NO_GO` por autoridade real.
- `changes`: descrição e registros antes/depois com IDs e fontes.
- `diff`: diff Git **ou** registro de alteração equivalente (procedimento/estado anterior e posterior).
- `commands`: execução de comandos ou procedimentos concretos; se inaplicável, razão.
- `results`: observações reais, estado parcial, saídas, falhas e limitações.
- `no_self_approval`: declaração de separação entre executor e responsável por verificar/autorizar, sem tratá-la como prova autenticada.
- Testes imediatos e respectivos estados executado/`NOT_RUN`; critérios de stop; rollback/contingência; próximo responsável M06.

Se o contrato JSON auxiliar for justificado, propor `src/masp_skill/action_execution.py` com `validate_action_execution_record(record: Any) -> list[str]` e CLI `validate-action-execution --record ... --root ...` sem side effects. A existência do comando **não** deverá liberar execução nem aprovar Gate 05.

**STATUS:** `PENDING`, `IN_PROGRESS`, `PASS`, `FAIL`, `BLOCKED`, `NOT_RUN` permanecem as classificações do ledger. `STATIC` é validação estrutural, `SIMULATED` representa casos sintéticos e `RUNTIME` somente eventos observados realmente; valores em JSON continuam declarações.

## 6. Critérios para Gate 05 e limitação do motor

O executor deve entregar evidências suficientes sobre tarefa autorizada, ambiente, alterações, procedimentos, resultados e desvios, sem se autoaprovar. **Gate 05 PASS significa que a execução está documentada e encaminhável ao M06 — NÃO que a medida resolveu o problema.**

`PASS`: conclusão compatível com escopo autorizado, verificações locais adequadas e registros suficientes. `FAIL`: execução/checagem efetuada com requisito não atendido. `BLOCKED`: falta de aprovação externa, isolamento, competência, permissão, recursos ou segurança. `NOT_RUN`: intervenção não executada.

O motor atual é SIMULATED; qualquer `PASS` emitido por esse motor **não deve ser usado como autorização operacional**.

## 7. Arquivos e impactos previstos após aprovação

- Modificar `docs/masp/agentes/05-acao.md`, `.codex/agents/masp-executor.toml`, bloco `acao` de `docs/masp/masp-routing.toml`, item 05 de `.agents/skills/masp/SKILL.md`, ficha `docs/masp/modelos/CASO-MASP.md` e referência M05 em `README.md`.
- Criar `docs/masp/acao/ESPECIFICACAO-V2.md`, `REFERENCIAS-METODOLOGICAS.md`, `MODELO-EXECUCAO.md`, `CHECKLIST-PRE-EXECUCAO.md`, `CONTROLE-DESVIOS-ROLLBACK.md`, `RELATORIO-TESTES-V2.md`.
- **Opcional** código `src/masp_skill/action_execution.py` e registro CLI em `src/masp_skill/cli.py` se os testes demonstrarem ganho claro; nunca uma CLI que execute mudanças de caso.
- Criar `tests/test_action_execution_v2.py` e fixture de **9 domínios + 24 casos adversariais sintéticos**. Separar testes estruturais e testes reais de comportamento do agente.

## 8. Validação e riscos

- RED de testes (antes do código), GREEN em Python, revisão dos contratos por arquivo e regressões em M01–04/M06–08.
- Comandos: `python -m pytest -q`, `python -m masp_skill.cli validate-routing --routing docs/masp/masp-routing.toml --classification STATIC`, `python -m masp_skill.cli validate-case --case tests/fixtures/cases/valid-case.json --root .`.
- GitHub Actions Windows e Ubuntu no SHA final; copiar somente resultados efetivamente verificados. Sintéticos não são execução real de agentes.
- Se não houver `spawn_agent` Codex: `masp-executor` real e `masp-testador` independente = `NOT_RUN`. Modelo/esforço efetivos não comprovados.
- Revisão de segurança de caminhos/credenciais e execução indevida. Não invocar Astra ou `runtime-smoke --all-roles`; não alterar `main` nem dar merge.

**Decisão pendente:** aprovação deste desenho pelo usuário. Até lá, esta branch contém exclusivamente design e plano; nenhum contrato funcional, código Python ou configuração de agentes será modificado.
