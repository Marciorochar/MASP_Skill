# Caso MASP — manifesto JSON e ledger

O manifesto JSON é uma trilha de validação **SIMULATED**. Ele exercita ordem, critérios de gate, referências e consistência do fluxo MASP; não concede autoridade de segurança, não autentica pessoas ou agentes e não prova que um modelo executou o trabalho. O programa não dispõe de uma identidade runtime ou assinatura confiável para coordenador, aprovador humano ou Astra. Campos `actor`, `approved_by`, `role`, `model`, `opinion` e classificação de evidência são declarações fornecidas por quem chama a CLI.

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

Cada objeto de evidência tem `id`, `path`, `classification`, `description` e `satisfies`, com critérios do gate que a evidência declara cobrir. Os caminhos são normalizados e devem existir dentro da raiz informada. Cada fase usa critérios próprios derivados do identificador da fase na matriz. `NOT_RUN` nunca satisfaz `PASS`. Verificação exige evidência declarada `RUNTIME` com comando, código de saída inteiro e stdout ou stderr; esses campos continuam sem autenticação independente.

## Transições e autoridade

Use `transition` para acrescentar uma mudança simulada. O ator precisa estar rotulado `masp-coordenador`; isso é uma checagem de fluxo, não autenticação. O gate Plano de ação requer uma evidência declarando aprovação humana; a evidência e seu campo `approved_by` não verificam a identidade do aprovador. Em caso de alto risco, Verificação e Conclusão exigem uma evidência declarada como parecer `PASS`/`APPROVED` de `gpt-6-astra`, com comando e resultado. O programa não comprova que Astra produziu o parecer e não deve ser usado como controle de segurança ou aprovação real.

`BLOCKED` impede avanço até que outro processo registre uma resolução. `FAIL` só permite retorno a uma fase listada em `returns` para a fase que falhou; o replay permite que esse retorno termine em `IN_PROGRESS`, `BLOCKED` ou `NOT_RUN`. Ao iniciar uma fase, o motor confere o modelo e esforço declarados e bloqueia valores marcados como indisponíveis; isso não consulta o catálogo runtime. Em caso de alto risco, a matriz precisa declarar `masp-especialista-critico` como `gpt-6-astra` com esforço `medium`, e a evidência precisa declarar o mesmo modelo e esforço. O parecer Astra ainda é uma declaração não autenticada. O validador de tarefas normaliza caminhos sob a raiz, aplica o menor limite entre configuração e limite runtime fornecido e rejeita caminhos fora da raiz e conflito de escrita.

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

[Condição verificável, baseline, resultado esperado e método de medição.]

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
