# Matriz universal — hipóteses e evidências (MASP M03 v2)

**Preencher apenas com informações efetivamente disponíveis.** Este documento complementa o ledger MASP e não comprova execução ou aprovação. Não colocar dados pessoais, segredos ou resultados sensíveis em GitHub público.

## 1. Contexto e método

- Caso / ID:
- Referência à Identificação v2:
- Referência à Observação v2 (incluindo baseline quantitativo, qualitativo ou indisponível):
- Objetivo, escopo e exclusões da análise:
- Modo **rápido** / **aprofundado** e justificativa:
- Método(s) de análise escolhidos, por quê e seus limites:
- Restrições e autorizações:

## 2. Inventário de evidências

| ID | Origem e data conhecida | O que foi efetivamente consultado | Classe | Independência e limitações |
| --- | --- | --- | --- | --- |
| E1 | Atribuir | Atribuir | FATO_VERIFICADO / RELATO_NAO_VERIFICADO / HIPOTESE / DESCONHECIDO | Atribuir |

`FATO_VERIFICADO` exige conferência real da fonte e registro de sua extensão; não transformar um relato em prova. `STATIC`, `SIMULATED` e `RUNTIME` caracterizam o alcance do procedimento, não a verdade da fonte.

## 3. Matriz de hipóteses concorrentes

| ID | Hipótese e mecanismo | Evidências favoráveis (IDs) | Evidências contrárias (IDs) | Contraevidência procurada e não localizada | Rivais | Avaliação realizada ou NOT_RUN | Status e limites |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | Delimitar condição, mecanismo e efeito | E1 | E2 ou desconhecido | Fontes analisadas e lacunas | H2 | Método, data, resultado, referências / NOT_RUN justificado | NAO_TESTADA / EM_AVALIACAO / CORROBORADA / REFUTADA / INCONCLUSIVA |

Para cada hipótese, registrar também uma observação esperada se verdadeira e outra que possa contrariá-la. Não concluir causa de diagramas, votações, p-valores, correlações isoladas ou ausência de oposição.

## 4. Viés, confusão e limites

- Potenciais fatores de confusão e limitações da amostra:
- Fontes duplicadas ou dependentes:
- Consequências da falta de baseline, dado ou medição:
- Explicações não descartadas:
- Verificações seguras e autorizadas já **realizadas**:
- Testes **não executados** (`NOT_RUN`) e motivo:
- Segurança, privacidade e competência envolvidas:

## 5. Conclusão delimitada ou inconclusiva

- `root_cause_or_explicit_inconclusive`: **causa(s) sustentada(s) no contexto** / **INCONCLUSIVA**.
- Quais hipóteses são sustentadas por que IDs de evidência e procedimentos:
- Evidências contrárias consideradas e alternativas não excluídas:
- A conclusão depende apenas de **associação**? Se sim, não afirmar causa raiz.
- Limitações relevantes, fator(es) contribuinte(s) e novas coletas necessárias:
- Perguntas de retorno à Observação:
- Recomendação ao coordenador: `PASS` / `FAIL` / `BLOCKED`, com decisão fundamentada sobre **hypotheses**, **evidence_for_and_against**, **root_cause_or_explicit_inconclusive**.
- Autorização para Plano de Ação: apenas mediante gate do coordenador; **nenhuma mudança nesta fase**.

## Exemplo de uso do validador (registro JSON separado)

O contrato JSON opcional está documentado em [ESPECIFICACAO-V2.md](ESPECIFICACAO-V2.md). Guarde o registro fora do ledger e execute:

```powershell
python -m masp_skill.cli validate-analysis --record .tmp/analise.json --root .
```

`STATIC` indica que campos e referências declaradas podem ser analisados. **Não** indica que um LLM realizou a análise ou que a causa tenha sido comprovada. Casos hipotéticos são `SIMULATED`, não evidência real.
