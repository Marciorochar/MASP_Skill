# Caso MASP — manifesto JSON e ledger

O manifesto JSON é uma trilha de validação **SIMULATED**. Ele exercita ordem, critérios de gate, referências e consistência do fluxo MASP; não concede autoridade de segurança, não autentica pessoas ou agentes e não prova que um modelo executou o trabalho. O programa não dispõe de uma identidade runtime ou assinatura confiável para coordenador, aprovador humano ou Astra. Campos `actor`, `approved_by`, `role`, `model`, `opinion` e classificação de evidência são declarações fornecidas por quem chama a CLI.

Casos novos usam `schema_version: 2`, que registra snapshots históricos de disponibilidade e hashes SHA-256 de evidências. O validador aceita versão 1 somente para manifestos sem eventos (como fichas ainda não iniciadas). Ledgers de versão 1 são rejeitados com orientação de migração porque não registram snapshots verificáveis; recalcule/recrie cada evento no schema 2 com as evidências originais disponíveis. Evidências sem hash também falham na validação para impedir que conteúdo alterado seja aceito sem aviso.

## Campos do manifesto

| Campo | Uso |
|---|---|
| `case_id` | Identificador seguro e estável do caso. |
| `current_phase` | Uma das oito fases da matriz, na ordem declarada. |
| `state` | `PENDING`, `IN_PROGRESS`, `PASS`, `FAIL`, `BLOCKED` ou `NOT_RUN`. |
| `classification` | Permanece `SIMULATED`; rótulos `RUNTIME` em evidências são declarações e não atestações. |
| `high_risk` | Metadado incluído no hash de origem e usado para exigir alegação de parecer Astra nos gates Verificação e Conclusão. |
| `origin_phase`, `initial_state`, `genesis_hash` | Ancoram o manifesto usado pelo replay estrutural. O hash não é assinado. |
| `ledger` | Eventos ordenados, ligados por SHA-256 sem chave secreta. Detecta inconsistências acidentais e parte das edições, mas não autentica autoria. |

Cada objeto de evidência tem `id`, `path`, `classification`, `description`, `sha256` e `satisfies`, com critérios do gate que a evidência declara cobrir. O SHA-256 é recalculado sobre o conteúdo do arquivo em cada validação; arquivos alterados após o registro são rejeitados. Os caminhos são normalizados e devem existir dentro da raiz informada. Cada fase usa critérios próprios derivados do identificador da fase na matriz. `NOT_RUN` nunca satisfaz `PASS`. Verificação exige evidência declarada `RUNTIME` com comando, código de saída inteiro e stdout ou stderr; esses campos continuam sem autenticação independente.

## Transições e autoridade

Use `transition` para acrescentar uma mudança simulada. O ator precisa estar rotulado `masp-coordenador`; isso é uma checagem de fluxo, não autenticação. O gate Plano de ação requer uma evidência declarando aprovação humana; a evidência e seu campo `approved_by` não verificam a identidade do aprovador. Em caso de alto risco, Verificação e Conclusão exigem uma evidência declarada como parecer `PASS`/`APPROVED` de `gpt-6-astra`, com comando e resultado, além dos campos definidos em `policies.astra_escalation.required_record`: `astra_reason` e `coordinator_decision` não vazios e `related_evidence` como lista não vazia de IDs de evidências existentes. O programa não comprova que Astra produziu o parecer e não deve ser usado como controle de segurança ou aprovação real.

`BLOCKED` impede avanço até que outro processo registre uma resolução. `FAIL` só permite retorno a uma fase anterior listada em `returns`; não pode saltar para uma fase posterior que ainda esteja pendente. O replay permite que o retorno termine em `IN_PROGRESS`, `BLOCKED` ou `NOT_RUN`. A fase Conclusão só pode passar quando todas as fases anteriores têm eventos `PASS` válidos. Cada evento de início registra um snapshot do papel, modelo, esforço e disponibilidade declarados naquele momento; o replay valida esse registro histórico sem reconsultar a disponibilidade atual. `current_model_availability` é a consulta explícita do estado de disponibilidade atual. Ao iniciar uma fase, o motor confere o modelo e esforço declarados e bloqueia valores marcados como indisponíveis; isso não consulta o catálogo runtime. Em caso de alto risco, a matriz precisa declarar `masp-especialista-critico` como `gpt-6-astra` com esforço `medium`, e a evidência precisa declarar o mesmo modelo e esforço. O parecer Astra ainda é uma declaração não autenticada. O validador de tarefas normaliza caminhos sob a raiz, aplica o menor limite entre configuração e limite runtime fornecido e rejeita caminhos fora da raiz e conflito de escrita.

`validate-case` recalcula o hash de origem e os hashes encadeados, reaplica a máquina de estados e a ordem de fases, revalida gates e confere os caminhos de evidência. O encadeamento SHA-256 não é assinatura: alguém que reescreva o manifesto e recalcule todos os hashes pode forjar a trilha. Para autorização real seriam necessários identidade autenticada e assinatura/chave protegida, que não fazem parte desta entrega.

O comando `transition` exige compare-and-swap por revisão SHA-256, usa um lock sidecar persistente `<caso>.lock`, relê o manifesto sob lock, valida a revisão e só então faz substituição atômica. O lock serializa escritores que usam este CLI; processos que ignorem o lock ainda podem editar o arquivo. A revisão protege contra atualização obsoleta quando o chamador fornece o token corrente.

## Uso

```powershell
python -m masp_skill.cli new-case --id MASP-001 --output casos/MASP-001.json
python -m masp_skill.cli case-revision --case casos/MASP-001.json
python -m masp_skill.cli transition --case casos/MASP-001.json --state IN_PROGRESS --actor masp-coordenador --evidence evidencias/abertura.json --expected-revision <sha256>
python -m masp_skill.cli validate-case --case casos/MASP-001.json --root .
```

O arquivo passado a `--evidence` é um JSON com uma lista de referências. `transition` exige a revisão exata impressa por `case-revision`; após uma escrita bem-sucedida, consulte a nova revisão antes da próxima transição. O sidecar de lock é mantido ao lado do caso. A classificação `SIMULATED` não equivale a resultado de runtime.

## Ficha humana de acompanhamento

Esta ficha complementa o manifesto JSON para planejamento e leitura humana. Seu preenchimento manual não altera o estado executável do caso.

- Título do problema:
- Criado em:
- Coordenador:
- Workspace:
- Fonte do relato (arquivo/caminho e data):
- Objetivo quantitativo:
- Fora do escopo:

### Ficha de Identificação universal v2

Ficha Markdown complementar ao manifesto, sem novos campos no JSON ou ledger. Siga [a especificação](../identificacao/ESPECIFICACAO-V2.md).

- Condição observada e condição esperada do problema:
- Contexto, local e período:
- Afetados:
- Impacto conhecido ou potencial (e fonte):
- Escopo e exclusões:
- Critério de sucesso verificável numérico ou qualitativo e método:
- Baseline conhecido ou `PENDENTE_DE_OBSERVACAO`:
- Fontes, data e limitações:
- Classificação de cada informação: `FATO_VERIFICADO`, `RELATO_NAO_VERIFICADO`, `HIPOTESE` ou `DESCONHECIDO`:
- Contradições e pendências para Observação:
- Gate `PASS` ou `BLOCKED`, justificativa e desbloqueio se aplicável:

### Ficha de Observação universal v2

Esta ficha complementa a Identificação v2 sem alterar o manifesto nem o ledger. Siga [a especificação](../observacao/ESPECIFICACAO-V2.md) e o [modelo de coleta](../observacao/MODELO-COLETA-EVIDENCIAS.md).

- Objetivo, perguntas, objeto, contexto, ambiente, local, período e modo rápido/aprofundado:
- Fontes atribuídas (ID, tipo, origem, data e acesso), classe `FATO_VERIFICADO`/`RELATO_NAO_VERIFICADO`/`HIPOTESE`/`DESCONHECIDO` e limitações:
- Método de coleta, justificativa, condições e autorização quando aplicável:
- Condição atual e registros descritivos, com contradições preservadas:
- Baseline **quantitativo**, **qualitativo** ou **indisponível** (razão e coleta necessária):
- Qualidade das fontes, incerteza e comparabilidade:
- Resultado **reproduzível** ou limitação **não reproduzível** / **não tentada**:
- Evidências efetivamente consultadas e classificação `STATIC`/`SIMULATED`/`RUNTIME`:
- Pendências e perguntas para Módulo 03, sem concluir causa raiz:
- Quatro critérios `baseline`, `environment`, `collection_method`, `reproducible_result_or_limitation` e justificativa de `PASS`/`FAIL`/`BLOCKED`:

O registro opcional em JSON pode ser validado por `python -m masp_skill.cli validate-observation --record .tmp/observacao.json --root .`. Este comando **não comprova observação de campo nem aprova o gate**.

### Ficha de Análise universal v2

Este registro humano complementa o manifesto existente, sem alterar `schema_version` ou ledger. Siga [a especificação](../analise/ESPECIFICACAO-V2.md) e [a matriz de evidências](../analise/MATRIZ-HIPOTESES-EVIDENCIAS.md).

- Referências ao problema/Identificação v2, à Observação v2, ao baseline e às fontes:
- Modo rápido/aprofundado, objetivos, escopo e técnicas escolhidas com justificativa:
- `hypotheses`: hipóteses concorrentes, mecanismo, observação esperada e potencialmente refutadora:
- `evidence_for_and_against`: IDs, origem, classe, evidências favoráveis e contrárias, buscas sem achados e vieses:
- Método realmente executado, resultado e limites, ou `NOT_RUN` justificado:
- Conclusões: `root_cause_or_explicit_inconclusive` — causa(s) sustentada(s) no escopo ou `INCONCLUSIVA`, com alternativas ainda abertas:
- Fatores contribuintes, confusão, incertezas, dados adicionais e retorno à Observação:
- Gate 03 recomendado `PASS`/`FAIL`/`BLOCKED`, razão e evidência para cada critério:
- Comando opcional: `python -m masp_skill.cli validate-analysis --record .tmp/analise.json --root .`. Esta saída STATIC não aprova o gate nem autentica causas.

### Ficha de Plano de Ação universal v2

Usar [a especificação](../plano-acao/ESPECIFICACAO-V2.md), [o modelo 5W2H](../plano-acao/MODELO-5W2H.md) e [a matriz de riscos/contingências](../plano-acao/MATRIZ-RISCOS-CONTINGENCIAS.md) para produzir um plano humano sem alterar manifesto ou ledger:

- Problema M01, baseline M02, causa sustentada ou inconclusão M03, objetivo, escopo e exclusões:
- Alternativas comparadas, mudança mínima **adequada** e justificativa:
- `tasks` 5W2H, `owners`, dependências, recursos e `scope`:
- `risks`, prevenção, mitigação, stop e riscos residuais:
- `rollback` reversível, parcial ou **contingência** para mudança irreversível:
- `tests` futuros, baseline ou pendência, aceitação, falha, verificador e stop:
- `human_approval`: pessoa/função realmente autorizada, decisão, referência, escopo e limites:
- Gate 04 `PASS` / `FAIL` / `BLOCKED`, evidências e limitações. Sem prova real de autorização, **não iniciar Ação**.

CLI opcional `python -m masp_skill.cli validate-action-plan --record .tmp/plano.json --root .`: valida estrutura `STATIC`, mas **não** autentica aprovação ou libera a intervenção.

### Ledger resumido dos gates

| Fase | Estado | Evidência/IDs | Revisão independente | Próxima decisão |
|---|---|---|---|---|
| 01 Identificação | PENDING | | | |
| 02 Observação | PENDING | | | |
| 03 Análise | PENDING | | | |
| 04 Plano de ação | PENDING | | | |
| 05 Ação | PENDING | | | |
| 06 Verificação | NOT_RUN | | | |
| 07 Padronização | PENDING | | | |
| 08 Conclusão | PENDING | | | |

### Critério de sucesso

[Condição verificável numérica ou qualitativa, baseline conhecido ou PENDENTE_DE_OBSERVACAO, resultado esperado e método de verificação.]

### Registro humano de evidências

Para cada evidência, registrar data/hora, responsável, arquivo alvo, comando completo, diretório, toolchain, stdout/stderr, código de saída, hash/commit quando relevante, classificação do fato (`FATO | HIPÓTESE | INFERÊNCIA`) e ID correspondente no manifesto.

### Plano 5W2H

| O quê | Por quê | Onde | Quando/ordem | Quem | Como | Quanto/custo/risco |
|---|---|---|---|---|---|---|
| | | | | | | |

### Decisões e exceções

- [data] [decisão; justificativa; risco; autorização humana se aplicável]

### Auditoria e encerramento

- Resultado dos testes:
- Limitações:
- Retorno a uma fase anterior:
- Mudanças realizadas:
- Riscos residuais e pendências:
- Gate de promoção: BLOQUEADO até aprovação separada.
