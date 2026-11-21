# MASP — Conclusão Universal v2 (M08)

**Missão:** consolidar oito fases, evidências, objetivos, eficácia comprovada no escopo, resultados negativos, limites, riscos residuais e pendências em um parecer final auditável. Aplicável a quaisquer domínios, sem pressupor software.

## Fronteiras e entradas
Receber caso/ledger, M01 objetivos e escopo, M02 baseline, M03 causa ou inconclusão, M04 plano, M05 ação, M06 verificação e M07 padronização. Conferir referência, fonte, classificação e limite de cada fato. Hash indica **integridade de bytes**, não veracidade, identidade, aprovação ou execução de agentes.

## Método
1. Construir matriz das oito fases com status e pendências, preservando `FAIL`, `BLOCKED`, `NOT_RUN` e divergências.
2. Avaliar cada objetivo no escopo: `achieved`, `partially_achieved`, `not_achieved`, `inconclusive`, `not_evaluated`. Não reescrever metas retroativamente.
3. Distinguir plano, aprovação, ação executada, eficácia verificada, padronização e sustentabilidade observada. Sequência temporal ou um teste verde não provam causa/resultado em campo.
4. Registrar riscos residuais e novos, controles, responsáveis futuros, pendências críticas e transferíveis, limitações e lições sustentadas.
5. Produzir resumo executivo + relatório técnico com fontes, audit opinion e decisões reais por autoridade competente. Sem substituir auditor institucional.
6. Separar resolução `demonstrated/partial/inconclusive/unfavorable` de encerramento `technical/administrative` e decisão `complete/with_reservations/blocked/not_run`.

## Gate 08
Preservar exatamente `complete_ledger`, `results`, `limitations`, `residual_risks`, `pending_items`, `audit_opinion`.

Um Gate 08 `PASS` documental não é prova de sucesso do problema ou autorização para produção. O motor SIMULATED existente exige PASS de gates anteriores para concluir como PASS; encerramento administrativo de caso inconclusivo pode ser descrito **fora desse PASS**, sem alterar registros históricos. Se revisão/autoridade/evidência obrigatória ausente: `BLOCKED`; avaliação negativa: `FAIL`; não executada: `NOT_RUN`.

## Validação auxiliar
`python -m masp_skill.cli validate-conclusion --record .tmp/conclusao.json --root .` confere somente **estrutura STATIC**, sem autenticidade do ledger, eficácia, auditor ou encerramento real. Não executa merge, deploy, notificação ou mudança em terceiros.

**Segurança:** não expor dados pessoais ou segredos em relatórios públicos; não modificar provas originais; política de alto risco/Astra e roteamento existente permanecem. Retornos M08 apenas a Verificação e Padronização quando permitidos.
