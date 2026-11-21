# MASP — Plano de Ação Universal v2

**Missão:** transformar resultados dos módulos de [Identificação](../identificacao/ESPECIFICACAO-V2.md), [Observação](../observacao/ESPECIFICACAO-V2.md) e [Análise](../analise/ESPECIFICACAO-V2.md) em **intervenções planejadas**, adequadas a qualquer domínio. **Planejar não é autorizar nem executar.**

## Modos e fronteiras

- **Rápido:** problema delimitado, ações simples, baixo risco; plano mínimo com escopo, alternativa considerada, 5W2H, risco, rollback ou contingência, teste e autorização.
- **Aprofundado:** múltiplas áreas, riscos relevantes, medidas parcialmente irreversíveis, custos, incertezas ou dependências; comparar alternativas e envolver especialistas competentes conforme necessidade.
- A técnica escolhida é proporcional ao contexto: 5W2H, RACI, SMART, 8D/D5, PDSA, FMEA ou matriz de riscos podem ajudar, mas **não são obrigatórias** para todos os problemas.
- Aplicável à indústria, logística, saúde, administração, meio ambiente, educação, tecnologia, serviços, sociedade e cotidiano; não pressupor arquivos, código, deploy ou teste de software.
- Restrições técnicas do caso OTServer somente quando o caso for OTServer.
- **A Análise inconclusiva não autoriza ação corretiva definitiva.** Planejar investigação adicional, contenção, proteção ou monitoramento somente com limites, riscos e aprovação apropriados. Não converter hipótese em causa provada.

## Procedimento universal

1. **Verificar entradas:** problema/impacto/escopo do M01, baseline e fontes do M02 (quantitativo, qualitativo ou indisponível), conclusões/hipóteses/limites do M03, critérios de sucesso, autorizações e capacidade de execução. Não inventar causas ou dados.
2. **Comparar alternativas:** explicar relação causal, risco atendido ou propósito investigativo; viabilidade, benefício, custo, prazo, dependência, reversibilidade, impactos sobre terceiros e testes-piloto. Incluir não intervenção monitorada se pertinente. Nenhuma matriz de notas substitui requisito legal ou de segurança.
3. **Selecionar mudança mínima adequada:** menor intervenção **suficiente para o resultado e os controles necessários**, não simplesmente a mais barata ou curta. Pode ser um conjunto coordenado de ações. Justificar rejeições e limites; evitar mudanças fora de escopo.
4. **Planejar 5W2H:** What, Why, Where, When, Who, How e How much de cada tarefa, com responsável por função, prazo ou condição de início, evidências, dependências, custo conhecido ou pendência fundamentada. Não inventar nomes, datas, orçamento ou valores.
5. **Avaliar riscos:** possíveis consequências novas, pessoas/processos afetados, prevenção, mitigação, proteção, risco residual e gatilho de interrupção. Usar método de avaliação proporcional; não atribuir probabilidades ou classes de criticidade sem critérios.
6. **Planejar retorno/contingência:** reversível exige estado inicial, procedimento, responsável, gatilho e verificação; parcialmente reversível exige distinção das etapas e impactos residuais, com controles; irreversível exige justificativa, ponto de não retorno, condição de parada **antes** dele, contingência, mitigação e autorização. Nunca chamar contingência de rollback executável.
7. **Definir testes futuros:** objetivo, baseline conhecido ou indisponível justificado, indicador qualitativo/quantitativo, método, resultado esperado, aceitação, falha, efeitos colaterais, condição de interrupção e responsável pela verificação. Teste não é executado nesta fase.
8. **Formalizar autorização necessária:** versão, aprovador por função, escopo, condições, riscos, recursos e evidência de aprovação **real**. Ausência de confirmação é pendência/BLOCKED; texto produzido por IA não é assinatura.
9. **Handoff ao coordenador:** alternativas, plano, riscos, reversão/contingência, verificação planejada, pendências e gate recomendado. Somente a fase Ação pode executar intervenção realmente autorizada.

## Gate 04 — sete critérios de compatibilidade

Preservar as sete chaves existentes da CLI/ledger:

- `tasks`: ações e 5W2H executáveis e delimitados, com dependências.
- `owners`: responsáveis identificados por função e atribuição pertinente.
- `scope`: inclusões e exclusões explícitas.
- `risks`: riscos de ação, prevenção, mitigação, condição de parada e residual.
- `rollback`: reversão viável **ou contingência fundamentada** quando parcial/irreversível.
- `tests`: avaliação futura, baseline/pendência, aceite, falha, monitoramento e critérios de interrupção.
- `human_approval`: autorização humana **efetivamente conferida** pelo processo competente, sem simular autoria.

**PASS:** proposta coerente e implementável, com riscos e critérios verificáveis e aprovação realmente comprovada. **BLOCKED:** autorização, responsável, recursos, dados ou controles essenciais ausentes. **FAIL:** plano avaliado e comprovadamente incapaz de atender requisito obrigatório, com registro do problema e da correção necessária.

Um documento tecnicamente completo com autorização pendente **não avança para Ação**. A decisão de gate não é produzida apenas pela presença de campos nem por pontuação compensatória.

## Sidecar opcional e suas limitações

O validador `src/masp_skill/action_plan.py` recebe um registro JSON separado e verifica apenas **estrutura e vínculos declarados**, por `validate_action_plan_record(record) -> list[str]`:

```powershell
python -m masp_skill.cli validate-action-plan --record .tmp/plano-acao.json --root .
```

O registro inclui `case_id`, `problem_reference`, `analysis_reference`, `analysis_status` (`supported`/`inconclusive`), `plan_objective`, `alternatives`, `selected_actions`, `tasks`, `owners`, `scope`, `risks`, `rollback`, `tests` e `human_approval`.

Cada tarefa `tasks` tem `alternative_id`, `what`, `why`, `where`, `when`, `who` (ID de função), `how`, `how_much` (conhecido ou desconhecido justificado), `dependencies` e `expected_result`. Cada tarefa selecionada deve ter risco, rollback/contingência e teste planejado. `tests.baseline.type` pode ser `known` ou `unavailable`, com motivo e coleta necessária. Resultados de teste executado pertencem às fases posteriores.

Aprovação declarada: `human_approval.status` pode ser `pending`, `approved` ou `rejected`. Mesmo `approved` com referência textual **não autentica pessoa, assinatura, origem ou autoridade**. O comando retorna `STATIC`, não valida viabilidade/causalidade, **não concede PASS do Gate 04** e nunca autoriza execução. O manifesto/ledger `SIMULATED` mantém seu schema atual, sem migração.

## Integridade e segurança

- `STATIC`: checagem documental/JSON; `SIMULATED`: casos fictícios; `RUNTIME`: evento de execução comprovado com escopo da prova explícito. `NOT_RUN` não é aprovação.
- Sem alteração de processos, banco, VPS, máquinas, serviço clínico ou infraestrutura de produção na etapa Plano de Ação; sem intervenção potencialmente perigosa.
- Respeitar proteção de dados pessoais, competência profissional, segurança, licenças e autorizações. Em perigo imediato, executar protocolos competentes fora do rito MASP; a skill não substitui resposta emergencial.
- Ver [ficha 5W2H](MODELO-5W2H.md), [matriz de riscos](MATRIZ-RISCOS-CONTINGENCIAS.md), [referências](REFERENCIAS-METODOLOGICAS.md) e [testes](RELATORIO-TESTES-V2.md).
