# MASP — Observação Universal v2

**Missão:** descrever de forma verificável o estado atual de um problema de qualquer domínio, com coleta e análise **descritiva** das evidências disponíveis. A Observação não conclui **causa raiz**, não prescreve ações corretivas e não atribui status operacional sem provas. Recebe a ficha da [Identificação v2](../identificacao/ESPECIFICACAO-V2.md).

## Fronteira e modos

O problema pode ser industrial, doméstico, ambiental, de saúde, logístico, social, educacional, administrativo, tecnológico ou de qualquer outra natureza. Não exigir logs, código, equipamentos, KPI numérico ou reprodução experimental para problemas aos quais essas ferramentas não se aplicam.

- **Modo rápido:** fonte/contexto claramente identificados; registrar condição atual, procedimento, referência qualitativa ou quantitativa, incertezas e passagem à Análise em poucas etapas.
- **Modo aprofundado:** problemas complexos, recorrentes, contraditórios ou de alto impacto; planejar amostragem, triangulação, qualidade de dados, estratificação e, quando aplicável, estudo do sistema de medição. Não aplicar todas as técnicas por rotina.

A Identificação define o problema; a Observação documenta o que foi efetivamente observado; a Análise formula e testa hipóteses causais. Informação já fornecida não deve ser solicitada novamente.

## Procedimento adaptativo

1. **Planejar:** explicitar objetivo e perguntas de observação, população/unidade de análise, período, ambiente, riscos, permissões, recursos e lacunas da Identificação.
2. **Inventariar fontes:** registros, medições, relatos atribuídos, entrevistas autorizadas, observações diretas autorizadas, fotografias, bancos, dados históricos, séries temporais ou instrumentos. Registrar ID, tipo, origem, custodiante quando conhecido, data de produção/coleta, método, acesso e limitações. Não declarar acesso não realizado.
3. **Caracterizar a condição:** o que, onde, quando, frequência/magnitude se observável, grupos afetados, condições e variação, preservando relatos conflitantes atribuídos a suas fontes. Não inferir causa.
4. **Baseline:** escolher **quantitativo** (valor/unidade/fórmula/população/período/fonte), **qualitativo** (condição observável, método, contexto, período e fonte) ou **indisponível** (razão e coleta necessária). Não inventar número, unidade, meta, referência ou resultado. Baseline indisponível não é PASS nem BLOCKED automático.
5. **Coletar proporcionalmente:** utilizar folha de verificação, levantamento documental, entrevistas autorizadas, questionários, contagem, amostragem, observação direta ou ensaio controlado seguro conforme o caso. Documentar procedimento e limitações. Não exigir visita/Gemba quando não houver observação física.
6. **Avaliar confiabilidade:** completude, validade, consistência, atualidade, representatividade, comparabilidade, rastreabilidade e, para medições instrumentais relevantes, repetibilidade, reprodutibilidade, estabilidade/calibração e incerteza. Sem notas numéricas arbitrárias.
7. **Organizar resultados descritivos:** tabelas, frequência, tendência, distribuição, estratificação, mapas, fluxogramas ou narrativas estruturadas quando cabíveis. Distinguem-se padrões observados de relações causais: não aplicar Ishikawa, 5 Porquês ou FTA para concluir a causa nesta fase.
8. **Reprodução ou limitação:** reprodução só em ambiente permitido e seguro. Para evento histórico, raro, perigoso ou não reproduzível, documentar por que e quais fontes alternativas sustentam a descrição. Um evento não reproduzível pode ser real.
9. **Handoff:** apresentar dados, baseline, método, inventário de evidências, contradições, qualidade, fontes, riscos, lacunas e perguntas para a Análise. Não sugerir soluções executivas sem fase de planejamento/aprovação.

## Classificações distintas

**Natureza da informação:**
- `FATO_VERIFICADO`: alegação sustentada por fonte efetivamente conferida, com escopo explícito.
- `RELATO_NAO_VERIFICADO`: afirmação atribuída a fonte ainda não confirmada.
- `HIPOTESE`: possibilidade, explicação ou suposição não demonstrada.
- `DESCONHECIDO`: informação não disponível.

**Alcance do registro/executor:** `STATIC` (arquivos/estrutura), `SIMULATED` (casos fictícios ou exercício do ledger) e `RUNTIME` (execução observada, com prova específica). Uma chamada CLI real pode realizar validação `STATIC` de um registro declarado. Nenhum desses rótulos autentica pessoa, fonte, medições ou a autoria de um agente.

## Gate 02 — requisitos de compatibilidade

Preservar **exatamente** as chaves do motor atual:

- `baseline`: condição de referência atribuída e rastreável, **quantitativa, qualitativa ou explicitamente indisponível** com lacuna e próxima coleta.
- `environment`: contexto/ambiente, tempo, objeto e limitações de observação.
- `collection_method`: método utilizado ou proposto claramente identificado, autorizado quando aplicável, com justificativa e procedimento replicável quando adequado.
- `reproducible_result_or_limitation`: resultado de reprodução segura, ou justificativa factual de `não reproduzível`/`não executado`.

**PASS:** requisitos registrados, fontes identificadas e evidências suficientes para formular hipóteses na Análise, com limites materiais conhecidos e risco/autorizações tratados. A presença de quatro nomes de campo ou uma ficha estruturalmente válida **não aprova automaticamente** o gate.

**BLOCKED:** ausência de fontes mínimas, confiança insuficiente para o objetivo, restrições de autorização ou contradições impeditivas; documentar lacuna, risco e forma de desbloqueio. Não forçar coleta perigosa ou reprodução.

**FAIL:** observação/ensaio autorizado executado com resultado contrário a um critério previamente declarado, preservando o resultado real. Falha e ausência de dados não são sinônimos.

O coordenador aplica o gate do caso com evidências; o agente Observador fornece recomendações sobre suficiência, não aprova mudanças nem autentica identidades.

## Registro opcional JSON e CLI

Um `sidecar` JSON separado pode utilizar `validate-observation`, sem alterar `schema_version`, ledger ou transições:

```powershell
python -m masp_skill.cli validate-observation --record .tmp/observacao.json --root .
```

`src/masp_skill/observation.py` verifica **somente estrutura e referências declaradas**. Não realiza coleta, não verifica a existência física de provas citadas apenas por ID e **não decide Gate 02 PASS**.

Campos centrais do sidecar: `case_id`, `problem_reference`, `observation_objective`, `environment`, `observed_condition`, `collection_method`, `sources`, `baseline` e `reproducible_result_or_limitation`. `limitations` é opcional.

`baseline.type`: `quantitative` (valor finito, unidade, definição, período e fonte), `qualitative` (condição textual, definição, período e fonte) ou `unavailable` (motivo e nova coleta necessária). Referências a fontes devem apontar para IDs do próprio registro. Não presume autenticação de origem e não exige metrologia para entrevistas.

Consulte [modelo de coleta](MODELO-COLETA-EVIDENCIAS.md), [referências](REFERENCIAS-METODOLOGICAS.md) e [relatório de testes](RELATORIO-TESTES-V2.md).

## Segurança, privacidade e integridade

- Respeitar `AGENTS.md`, normas locais, consentimento e escopo/autorizações reais.
- Sem coleta invasiva, entrevistas ou observação presencial não autorizadas; sem acesso a dados confidenciais, sistemas de produção, serviços ou instrumentos perigosos.
- Minimizar dados pessoais, preferir agregados e não expor identificadores sensíveis em logs ou GitHub público.
- Não alterar evidências originais, datas, hashes ou resultados; distinguir dados fictícios de ocorrências reais.
- Em risco iminente à saúde, segurança ou meio ambiente, priorizar procedimentos de proteção e profissionais competentes. MASP não substitui resposta a emergências.
- Restrições específicas do OTServer aplicam-se **somente** quando o caso realmente for um OTServer.
