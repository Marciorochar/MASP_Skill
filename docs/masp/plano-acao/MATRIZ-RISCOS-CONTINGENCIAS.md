# Matriz de riscos, rollback e contingência — Plano de Ação Universal v2

Usar com o [Modelo 5W2H](MODELO-5W2H.md). A matriz é uma ferramenta de planejamento, não validação em campo ou autorização.

## 1. Inventário de riscos

| Ação | Risco introduzido | Pessoas/processos afetados | Prevenção | Mitigação | Gatilho STOP | Risco residual e limite | Responsável |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T1 | A identificar | A identificar | Controle antes da execução | Resposta caso ocorra | Condição objetiva de parada | Sem nota arbitrária | Função definida |

Método opcional: matriz F×S, FMEA, análise de barreiras ou revisão qualitativa proporcional. Não produzir probabilidades, severidades ou níveis falsos.

## 2. Seleção do tratamento de falha ou mudança

| Reversibilidade | Exigência principal | Confirmação futura |
| --- | --- | --- |
| `reversible` | Estado anterior documentado, procedimento `rollback`, responsável, disparo e verificação | Conferir restauração real |
| `partial` | Delimitar etapas reversíveis e irreversíveis, `irreversible_stage`, controles residuais e `contingency` | Verificar etapa recuperada e impactos residuais |
| `irreversible` | Fundamentar irreversibilidade, `point_of_no_return`, `stop_before_point`, mitigação e `contingency` | Confirmar controles e autorização antes do ponto de não retorno |

**Nunca inventar rollback para decisão irreversível.** O uso de `contingency` não significa que a condição original foi recuperada.

## 3. Teste planejado por tarefa

| Tarefa | Baseline ou lacuna | Indicador/critério | Método | Aceitação | Falha | Parada | Verificador |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T1 | Conhecido/indisponível justificado | Mensurável ou qualitativo observável | Método futuro | Critério definido | Critério definido | Condição objetiva | Responsável atribuído |

Não declarar resultados, aprovação, mudança executada ou eficácia antes das fases seguintes.

## 4. Autorização

- Responsável por autorizar:
- Fonte externa da aprovação (protegida e verificável):
- Escopo autorizado e versão:
- Riscos residuais aceitos e controles:
- Restrições e gatilhos obrigatórios:
- Sem evidência real suficiente: `BLOCKED`, com desbloqueio identificado.

O `Gate 04` usa `tasks`, `owners`, `scope`, `risks`, `rollback`, `tests` e `human_approval`. O JSON opcional não autentica `human_approval`, não autoriza ação e não concede PASS.
