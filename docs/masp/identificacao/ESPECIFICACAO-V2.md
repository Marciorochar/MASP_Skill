# Identificação universal — especificação v2

A Identificação caracteriza um desvio em qualquer domínio e prepara a Observação. Aplica-se o AGENTS.md e demais regras do caso. Não estabelece causa raiz nem prescreve solução; uma causa ou solução sugerida é registrada como relato ou hipótese, com atribuição, e não substitui o problema.

## Segurança e modos

Diante de risco imediato, priorize orientação de segurança dentro da própria competência e os procedimentos de emergência aplicáveis antes do fluxo MASP. A segurança imediata não substitui a investigação MASP.

- **Rápido:** registre o mínimo suficiente para decidir o gate, com incertezas e pendências explícitas. Use quando o relato já permite delimitar o trabalho.
- **Profundo:** amplie contexto, fontes, afetados, impactos e contradições quando a complexidade ou o risco justificar. Não converta profundidade em exigência de dados indisponíveis.

Faça perguntas apenas quando a resposta puder alterar materialmente a delimitação, segurança ou decisão do gate. Agrupe perguntas essenciais e use informações já disponíveis; não peça números ou detalhes por rotina. Preserve relatos contraditórios com suas fontes e marque a divergência como pendente.

## Ficha complementar

Registre em Markdown, junto ao caso, sem acrescentar campos ao JSON ou ledger:

- ID e título; condição observada versus esperada, contexto, local e período conhecidos.
- Pessoas, processos ou elementos afetados; impactos conhecidos e potenciais, sem atribuir gravidade não demonstrada.
- Escopo e exclusões explícitos; se ainda não houver exclusões identificadas, registre isso e a limitação.
- Critério de sucesso verificável, numérico **ou qualitativo**, com condição e método de verificação; não invente meta ou números.
- Baseline conhecido ou `PENDENTE_DE_OBSERVACAO`; a ausência de baseline, isoladamente, não bloqueia o gate.
- Para cada informação relevante, fonte, data e limitações quando conhecidas, além da classe: `FATO_VERIFICADO` (sustentado por evidência conferida), `RELATO_NAO_VERIFICADO` (atribuído a fonte, ainda não conferido), `HIPOTESE` (explicação ou possibilidade a avaliar) ou `DESCONHECIDO` (sem informação suficiente).
- Pendências, contradições e o que a Observação precisa coletar, incluindo método sugerido quando conhecido. Não invente baseline, causa, meta, fatos ou solução.

### Comparação opcional

Use **IS / IS NOT** quando houver dados suficientes e comparadores disponíveis: registre as dimensões o quê, onde, quando, extensão e afetados em que o problema ocorre e aquelas em que não foi observado. Atribua fontes e limitações. Quando um comparador estiver ausente ou desconhecido, registre-o como `DESCONHECIDO` ou não disponível, sem inferir ausência real do problema. Essas distinções delimitam a coleta na Observação: não inferir causa a partir delas.

## Gate e handoff

As cinco chaves existentes permanecem exatamente: `problem`, `impact`, `scope`, `exclusions`, `success_metric`. Não há pontuação compensatória: cada critério deve estar satisfeito por registro verificável e coerente, incluindo incertezas explicitamente identificadas quando apropriado. `problem` descreve condição observada e esperada; `impact` registra impactos conhecidos ou potenciais atribuídos, ou desconhecidos; `scope` delimita o contexto investigável; `exclusions` registra limites ou ausência de exclusões identificadas; `success_metric` define condição verificável numérica ou qualitativa e como verificá-la.

**PASS:** os cinco critérios estão registrados de forma suficiente para orientar a Observação, sem contradição material impeditiva; fontes e lacunas estão atribuídas e o próximo passo é claro. **BLOCKED:** falta informação essencial para formular o problema, delimitar o escopo ou definir um critério verificável, ou há contradição material que impede uma dessas decisões; indique exatamente a lacuna e o desbloqueio necessário. Ausência de baseline, dado quantitativo ou causa comprovada isoladamente não é bloqueio automático. Uma hipótese não vira fato para obter PASS.

No handoff à Observação, entregue ficha, fontes, classes, limitações, pendências, baseline conhecido ou `PENDENTE_DE_OBSERVACAO`, e as perguntas de coleta. A Observação coleta e caracteriza evidências; a Análise avalia causas em fase posterior.
