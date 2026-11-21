# MASP — Análise Universal v2

**Missão:** formular, comparar e avaliar hipóteses causais em **qualquer domínio**, utilizando dados da [Identificação v2](../identificacao/ESPECIFICACAO-V2.md) e da [Observação v2](../observacao/ESPECIFICACAO-V2.md). Uma hipótese plausível, um diagrama, uma correlação ou um voto de agentes **não comprova causa raiz**. Não executar ação corretiva nesta fase.

## Fronteiras, modo e preparo

- **Rápido:** poucas hipóteses, evidências já acessíveis, baixo impacto; comparar também hipóteses rivais e contraevidências, sem burocracia desnecessária.
- **Aprofundado:** fenômenos multifatoriais, recorrentes, contraditórios, de alta criticidade ou com inferência causal difícil. Estratificar, triangular fontes, investigar viés e condições relevantes, conforme competência e autorização.
- Receba problema, escopo, impacto, condição observada/esperada, baseline (inclusive qualitativo ou indisponível), fontes, classes de informação e lacunas dos módulos 01–02. Falta de baseline não autoriza inventar números.
- Não reclassificar relato de fonte não verificada como fato. Se evidência essencial faltar, registrar solicitação de retorno à Observação, preservando a continuidade do caso.

## Procedimento de investigação causal

1. **Formular hipótese verificável:** identificador, afirmação causal delimitada, mecanismo proposto, condição esperada se verdadeira, observação potencialmente refutadora, fontes e limitações. Não gerar quantidade arbitrária de explicações.
2. **Procurar alternativas reais:** explicações concorrentes ou fatores contribuintes, inclusive combinações. Não culpar pessoas sem evidências. Preservar hipóteses equiplausíveis.
3. **Matriz de comparação:** listar para cada hipótese evidências **favoráveis**, evidências **contrárias**, buscas por contraevidência sem resultados, dados faltantes, distinções IS / IS NOT quando disponíveis, possível confusão e fontes compartilhadas. Uma mesma fonte copiada não equivale a evidências independentes.
4. **Selecionar método proporcional:** 5 Porquês para explorar elos; Ishikawa/mapa causal para estruturar hipóteses; FTA em falhas técnicas quando adequado; análise de barreiras em acidentes; documentos e entrevistas autorizadas para processos sociais; estatística para dados adequados. FMEA, FTA e Bow-Tie têm objetivos diferentes. Não tratar qualquer diagrama, frequência, associação ou p-valor isolado como comprovação.
5. **Testar ou avaliar:** documentar o que foi realmente examinado, por qual método, condições, resultado, registro, incerteza e contraevidências. Experimentos somente seguros, autorizados e pertinentes. Acidentes passados, fenômenos raros ou irreproduzíveis podem ser avaliados retrospectivamente, sem tentar reproduzi-los.
6. **Revisar mecanismos:** verificar temporalidade e plausibilidade no contexto, fontes independentes, possibilidade de viés, explicações alternativas, fatores de confusão e evidências que enfraquecem a hipótese. Não presumir relação causal onde só se observou associação.
7. **Classificar hipóteses:** `NAO_TESTADA`, `EM_AVALIACAO`, `CORROBORADA`, `REFUTADA`, `INCONCLUSIVA`. São **estados de avaliação** distintos dos estados do ledger. `CORROBORADA` representa uma avaliação sustentada no contexto, não uma certeza universal.
8. **Concluir com limites:** apresentar uma ou mais causas **sustentadas no alcance investigado**, fatores contribuintes e limitações **ou** `INCONCLUSIVA`, justificando a avaliação realizada, rivais não diferenciadas e novos dados necessários. Não atribuir uma causa artificial para avançar.
9. **Handoff:** entregar a matriz, links das evidências, avaliação, confiança qualitativa justificada, riscos, lacunas e eventuais retornos à Observação. Não prescrever ações ou executar correções: responsabilidade de fases posteriores.

## Revisão da conclusão

- `CORROBORADA`: exige evidências favoráveis atribuídas e revisão de alternativas/contraevidências, além de procedimento efetivamente realizado e documentado. Pode haver causas múltiplas ou fatores contribuintes.
- `REFUTADA`: evidências contrárias pertinentes realmente avaliadas; não simplesmente ausência de dados favoráveis.
- `INCONCLUSIVA`: investigação ocorreu, mas as evidências não diferenciam explicações ou são insuficientes. Não transformar trabalho não iniciado em inconclusão examinada.
- Associação estatística, ainda que significativa, **não demonstra causalidade sozinha**. Não inventar valores de p, intervalos, estimativas, medições, classificações de confiança ou dados de experimentos.
- As classes `FATO_VERIFICADO`, `RELATO_NAO_VERIFICADO`, `HIPOTESE` e `DESCONHECIDO` devem permanecer atribuídas. Uma declaração de classe não é autenticação.

## Gate 03: compatibilidade exata

Preservar os três identificadores do motor atual:

- `hypotheses`: hipóteses e alternativas explicitadas e delimitadas.
- `evidence_for_and_against`: registros com evidências favoráveis, **contrárias**, inexistentes e fontes, sem confirmação seletiva.
- `root_cause_or_explicit_inconclusive`: causa(s) sustentada(s) na investigação, **ou** inconclusão legítima fundamentada após avaliação relevante, com limitações e próximos dados.

**PASS:** hipóteses relevantes comparadas, avaliação metodológica efetuada, evidências suficientes para sustentar conclusão delimitada ou inconclusão fundamentada que possa orientar decisão posterior. A identificação de uma causa não é pré-requisito universal para PASS; a análise realmente efetuada e a suficiência do registro são.

**BLOCKED:** ausência de dados indispensáveis, incoerência material, autorização/permissão/competência inexistente ou situação ainda não analisada. Registrar claramente o que falta e a forma de desbloqueio.

**FAIL:** procedimento ou avaliação executado que não atende critério predefinido; manter resultados reais, referência e condição de reavaliação. Não confundir hipótese `REFUTADA` com falha do MASP.

O gate é decidido pelo coordenador com evidências; presença de chaves ou validação JSON **não** determina PASS.

## Sidecar JSON e limite da CLI

`src/masp_skill/analysis.py` fornece `validate_analysis_record(record) -> list[str]`, exposto pelo comando:

```powershell
python -m masp_skill.cli validate-analysis --record .tmp/analise.json --root .
```

Verifica **somente estrutura declarada**: IDs únicos, vínculos das fontes/hipóteses, classificação de fatos, estado de avaliação e coerência básica das declarações de conclusão. Exige fonte atribuída `FATO_VERIFICADO` e registro de avaliação `performed` para `CORROBORADA`/`REFUTADA`, mas isso NÃO atesta que a verificação ocorreu. `documentary_triangulation` requer pelo menos duas origens textualmente distintas, o que também NÃO comprova independência real.

`conclusion.type`: `supported` (IDs de hipóteses CORROBORADA e `evidence_basis` metodológica) ou `inconclusive` (nenhuma causa final afirmada, justificativa e limites). `association_only` e `unknown` não podem ser usados para uma conclusão `supported`.

A classificação do comando é **STATIC**: registro declarativo não autentica pessoa, medição, causa ou Gate 03. A simulação do caso é **SIMULATED**; testes reais com logs correlacionados podem constituir **RUNTIME** restrito à execução observada. Nenhum rótulo prova o comportamento de LLM.

## Segurança e ética

- Não coletar dados pessoais ou acessar produção sem autorização; não reproduzir acidentes, vazamentos ou outros eventos perigosos.
- Não atribuir culpa ou causalidade a pessoas apenas por relatos. Em risco imediato, acionar procedimentos competentes; MASP não substitui resposta profissional.
- Restrições de OTServer somente em casos de OTServer; generalizar o método, não os procedimentos do exemplo.
- Evidências originais não devem ser sobrescritas. Não registrar dados inventados como observados.
- Ver [matriz e ficha](MATRIZ-HIPOTESES-EVIDENCIAS.md), [referências](REFERENCIAS-METODOLOGICAS.md) e relatório de testes.
