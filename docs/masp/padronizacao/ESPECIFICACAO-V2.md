# MASP — Padronização Universal v2 (M07)

**Missão:** transformar melhoria suficientemente verificada em controles proporcionais e sustentáveis, sem confundir documento, aprovação, implantação e sustentabilidade. Aplicável a indústria, serviços, saúde, administração, logística, educação, ambiente, tecnologia e cotidiano.

## Pré-requisito
Receber Verificação M06 com resultado e escopo, limitações, revisão independente, riscos e fontes. Um `PASS` do ledger SIMULATED não autentica eficácia real. Se Verificação inconclusiva, `NOT_RUN`, `FAIL` ou sem prova essencial, não consolidar padrão como eficaz: `BLOCKED` ou padrão provisório somente com autorização competente e ressalvas explícitas.

## Padronizar
Selecionar **controle preventivo**, quando pertinente complementado por detectivo, mitigador e acompanhamento; registrar problema e causa tratados, escopo/exclusões, procedimento proporcional, proprietário, treinamento necessário, revisão e gestão documental. Um checklist pode bastar para baixo risco; POP formal exige autoridade institucional onde aplicável.

Definir **gatilho observável**, fonte/método, ação inicial segura, autoridade e limite de reação. Registrar **regressão** com método, critério, frequência justificada, fonte e resultado `planned`, `performed` ou `not_run`. Monitorar sem inventar metas, datas, resultados ou sustentabilidade.

## Gate 07
Preservar exatamente `preventive_control`, `owner`, `trigger`, `regression`. `PASS` documental só quando evidências/controle/responsabilidade/reação/regressão suficientes; **não significa** que padrão foi implantado ou aderido. `FAIL` para critério avaliado e não atendido; `BLOCKED` para prova ou autoridade essencial ausente; `NOT_RUN` para avaliação não executada.

## Estado documental (não é estado MASP)
`DRAFT`, `UNDER_REVIEW`, `APPROVED`, `ACTIVE`, `SUSPENDED`, `OBSOLETE`. Campos não autenticam aprovação, implantação ou execução. Controlar versão, evidências, revisão/retirada, histórico e pendências.

## Sidecar e handoff
`validate-standardization --record .tmp/padrao.json --root .` verifica estrutura `STATIC` (responsável, gatilho, regressão, fontes, versão e coerência declarada), não autentica eficácia, operação, treinamento, aprovação ou Gate 07. Passar a M08: padrão/versionamento/limites, controles, responsável, gatilho, regressões, monitoramento, riscos, status real e pendências. Retorno permitido M07 → M06.

Não executar procedimentos industriais, clínicos, ambientais ou sistemas reais sem processo competente; restrições OTServer apenas quando caso OTServer.
