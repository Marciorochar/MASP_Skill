# Arquitetura MASP de oito agentes

## Coordenador (papel transversal, não é uma nona etapa)

- Confere `AGENTS.md`, skills e ferramenta de multiagentes disponível.
- Cria um `ID` por problema, congela as restrições e controla o ledger.
- Distribui tarefas com escopo, acesso, artefatos esperados, critérios de passagem e proibição de subagentes.
- Revisa entregas e delega uma verificação independente em etapas críticas.
- Proíbe que agentes em fases futuras aleguem conclusão sem evidências da fase anterior.
- Não substitui testes ou auditoria por sua opinião.

## Fluxo

`Identificação → Observação → Análise → Plano de ação → Ação → Verificação → Padronização → Conclusão`

Um gate `BLOCKED` interrompe a passagem. Um `FAIL` faz retornar à fase responsável pelo achado (por exemplo: testes reprovaram após Ação → retornar ao Plano/Ação, com causa documentada).

| Fase | Entrada obrigatória | Saída mínima | Gate de passagem |
|---|---|---|---|
| 01 Identificação | Relato inicial, contexto | Definição mensurável do problema, escopo, impacto | Problema verificável e limite do caso definido |
| 02 Observação | Caso definido | Baseline, inventário, passos de reprodução, logs e proveniência | Evidência suficiente para formular hipóteses; se faltar, BLOCKED |
| 03 Análise | Dados observados | Hipóteses, causa raiz testada ou investigação inconclusiva explícita | Causa sustentada ou plano de coleta adicional |
| 04 Plano de ação | Causa/risco identificado | 5W2H, riscos, dependências, testes, rollback, ordem de tarefas | Aprovação do plano e segurança dos alvos |
| 05 Ação | Plano aprovado, workspace isolado | Diff, testes durante implementação, registro de comandos | Mudanças restritas ao escopo e validadas localmente |
| 06 Verificação | Mudanças e baseline | Evidências recentes, métricas antes/depois, auditoria independente | PASS apenas com testes executados e critérios atendidos |
| 07 Padronização | Verificação aprovada | Procedimento, teste de regressão, padrões/documentação | Controle para evitar repetição definido e testado |
| 08 Conclusão | Gates anteriores fechados | Relatório, lições, riscos residuais e decisão de integração | Declaração precisa: conclusão técnica não significa promoção |

## Regras de validação

- `PASS`: comando/experimento executado, saída preservada, critérios satisfeitos.
- `FAIL`: executado e contrário ao esperado; registrar a causa observável.
- `BLOCKED`: pré-requisitos indisponíveis, autorização pendente ou prova insuficiente.
- `NOT_RUN`: verificação ainda não executada (não inferir resultado).
- `PENDING`: etapa ainda não iniciada.
- `IN_PROGRESS`: trabalho em curso; não permite avanço automático.

## Fronteiras de segurança do OTServer

1. Checkout original: somente leitura.
2. Cópia isolada: mudanças pequenas, reversíveis, autorizadas e auditáveis.
3. EXE/DLL não atribuídos aos fontes: não executar nem modificar, preservar/registrar hash apenas quando autorizado.
4. Nenhum acesso à VPS, banco real, serviços de rede ou cliente em produção sem autorização específica.
5. Nada de update Graphify em pasta histórica; snapshots recebem identificador único e hashes.
6. Não promover enquanto `-c`, harness, build integral, isolamento e proveniência não estiverem validados.

## Critérios de paralelismo

São paralelizáveis leituras independentes (ex.: logs do compilador versus inventário de snapshot). O coordenador pode usar `dispatching-parallel-agents` para decidir o fan-out e preparar contratos independentes. São sequenciais: causa raiz antes de plano, plano antes de modificação, modificação antes de verificação, verificação antes de padronização. Múltiplos agentes não devem alterar o mesmo arquivo.

`subagent-driven-development` tem outra função: quando há plano aprovado e o runtime oferece suporte, o coordenador o usa para atribuir e revisar tarefas de implementação do plano. Não substitui a seleção de trabalhos independentes nem altera a ordem dos gates MASP. Agentes filhos não criam subagentes. Sem suporte ao fluxo, o coordenador trabalha serialmente quando viável; caso contrário, registra `BLOCKED` e o pré-requisito ausente. Consulte `../../skills/masp/SKILL.md` e `../../skills/masp/references/routing-guide.md` para procedimentos e comandos da CLI.
