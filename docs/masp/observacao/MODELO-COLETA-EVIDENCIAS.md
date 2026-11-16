# Modelo de coleta de evidências — MASP Observação Universal v2

**Complementar ao manifesto JSON do caso.** Não concede aprovação, autenticação ou acesso a sistemas. Não inserir dados pessoais ou sigilosos em repositórios públicos.

## 1. Identificação e vínculo

- Caso MASP / ID:
- Ficha de Identificação usada, data e versão:
- Objetivo e pergunta da observação:
- Modo: rápido / aprofundado; justificativa:
- Unidade ou população de análise:
- Ambiente / contexto / período:
- Restrições e permissões aplicáveis:

## 2. Fontes e proveniência

| ID | Tipo | Origem / custodiante | Data da fonte/coleta | Método | Classe da alegação | Limites / acesso |
| --- | --- | --- | --- | --- | --- | --- |
| S1 | Relato/documento/medição/observação | A preencher | A preencher | A preencher | FATO_VERIFICADO / RELATO_NAO_VERIFICADO / HIPOTESE / DESCONHECIDO | A preencher |

Se uma data for desconhecida, marcar explicitamente `DESCONHECIDO`. Nunca inventar data ou atribuir autoria a uma fonte não conferida.

## 3. Plano de coleta e condição observada

- Perguntas e variáveis:
- Método utilizado/proposto e por quê:
- Instrumento, amostragem ou roteiro, quando aplicável:
- Condição observada versus relatada:
- Critérios de inclusão/exclusão dos dados:
- Frequência, amplitude, distribuição e variação observadas:
- Evidências consultadas, IDs e links/caminhos locais:

## 4. Baseline

| Aspecto | Registro |
| --- | --- |
| Tipo | quantitativo / qualitativo / indisponível |
| Definição operacional | |
| Valor ou condição observável | |
| Unidade (se pertinente) | |
| Objeto, população e período | |
| Fonte e método de obtenção | |
| Incerteza, limitações e comparabilidade | |
| Se indisponível: motivo e coleta necessária | |

A ausência de baseline não produz `PASS` automático nem obriga números fictícios.

## 5. Qualidade, limitações e reprodução

- Completude e confiabilidade das fontes:
- Consistência/contradições entre fontes:
- Atualidade, representatividade e comparabilidade:
- Metrologia (apenas se pertinente):
- Resultado reproduzível, `não reproduzível` ou reprodução não tentada:
- Procedimento autorizado, condições e resultados, quando realmente executado:
- Fontes não consultadas ou dados insuficientes:
- Riscos, privacidade e autorização:

## 6. Encaminhamento à Análise

- Padrões descritivos observados (não inferir causa raiz):
- Perguntas e lacunas para a fase Análise:
- Critérios `baseline`, `environment`, `collection_method`, `reproducible_result_or_limitation`:
- Recomendação fundamentada do Observador ao coordenador: `PASS` / `FAIL` / `BLOCKED`
- Evidência para cada critério:
- Se bloqueado: lacuna, risco e condição de desbloqueio:

**Classificação da evidência:** `STATIC` / `SIMULATED` / `RUNTIME`, com alcance explícito. A ficha, por si só, não constitui prova de execução.

## Exemplo de sidecar JSON — inteiramente sintético

```json
{
  "case_id": "MASP-OBS-EXEMPLO",
  "problem_reference": "MASP-IDENTIFICACAO-EXEMPLO",
  "observation_objective": "Descrever o relato sem atribuir causa",
  "environment": {"description": "Unidade ilustrativa", "period": "2026-10"},
  "observed_condition": "Relato de demora; frequência não confirmada",
  "collection_method": {
    "name": "Consulta ao relato recebido",
    "procedure": "Ler o texto disponível, sem executar coleta externa"
  },
  "sources": [{
    "id": "S1",
    "kind": "relato",
    "origin": "Relato ilustrativo",
    "recorded_at": "2026-10-01",
    "fact_class": "RELATO_NAO_VERIFICADO"
  }],
  "baseline": {
    "type": "unavailable",
    "reason": "Sem dados confiáveis de tempo de atendimento",
    "collection_needed": "Solicitar registros autorizados"
  },
  "reproducible_result_or_limitation": {
    "status": "not_reproducible",
    "details": "Não se aplica reprodução a esse relato histórico"
  },
  "limitations": ["Exemplo fictício, não representa coleta real"]
}
```

Salvar em arquivo JSON separado no workspace e executar:

```powershell
python -m masp_skill.cli validate-observation --record .tmp/observacao.json --root .
```

A CLI valida apenas **estrutura declarada** (`STATIC`). Não verifica veracidade, hash de artefatos externos, completude semântica ou decisão de Gate 02.
