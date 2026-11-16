# Desenho técnico — Observação Universal v2 (16/11/2026)

**Objetivo:** permitir observar e documentar problemas de qualquer domínio sem confundir coleta de evidências, diagnóstico causal e decisão de correção.

## Abordagens consideradas

| Alternativa | Ganho | Limitação |
| --- | --- | --- |
| Apenas instruções Markdown | Compatibilidade máxima e custo mínimo | Sem validação de registros |
| Alterar o schema do ledger | Gate mais rico e estritamente executável | Migração e risco de regressão em todos os casos |
| **Ficha Markdown + JSON sidecar opcional (selecionada)** | Orienta pessoas e permite validar estrutura/proveniência declaradas, sem mexer no ledger | Não autentica a coleta nem garante qualidade semântica |

A autorização de aplicar esta evolução foi dada na conversa. Não houve nova autorização para alterar a `main`, executar subagentes ou acessar sistemas reais.

## Contrato mantido

Os quatro IDs de `GATE_REQUIREMENTS["observacao"]` permanecem `baseline`, `environment`, `collection_method` e `reproducible_result_or_limitation`. Não alterar a ordem das oito fases, os contratos de outros módulos, o ledger nem o significado de `PASS`.

## Fluxo universal

1. Receber ficha da Identificação, fontes, contexto, condições conhecidas, restrições e lacunas.
2. Selecionar modo **rápido** ou **aprofundado** conforme materialidade, segurança e qualidade dos dados.
3. Planejar observação proporcional e inventariar fontes reais ou relatos atribuídos.
4. Registrar contexto, o que efetivamente foi observado, método, período e baseline quantitativo, qualitativo ou explicitamente indisponível.
5. Avaliar qualidade, repetibilidade somente quando aplicável, vieses, inconsistências e restrições éticas.
6. Diferenciar `FATO_VERIFICADO`, `RELATO_NAO_VERIFICADO`, `HIPOTESE`, `DESCONHECIDO`; não elevar declarações a fatos.
7. Organizar dados de modo **descritivo**, sem causa raiz nem ação corretiva.
8. Aplicar Gate 02 por revisão informada, não por simples presença de chaves; encaminhar dados e lacunas ao Módulo 03.

## Camada Python opcional

Novo `src/masp_skill/observation.py` com `validate_observation_record(record: Any) -> list[str]`: verifica estrutura dos campos, origem e IDs de fontes, baseline não fictício, referência da fonte e impossibilidade de reproduzir. Não há algoritmo que avalie veracidade, eficácia ou `PASS`.

Novo comando `validate-observation --record <JSON> --root <WORKSPACE>`, que limita a leitura ao workspace e informa `STATIC`.

A ficha humana permanece em Markdown, e o sidecar não altera `schema_version` ou eventos antigos.

## Condições de aceitação e limites

- Testes RED/GREEN para tipos de baseline, referências, duplicatas, valores numéricos inválidos, evento histórico não reproduzível, CLI e preservação do gate 01.
- Corpus de 9 domínios e 18 casos adversariais com rubricas sintéticas, sem atribuir comportamentos reais de LLM.
- Documentar fontes, licenças, métodos, riscos e revisão pendente.
- Não existem ferramentas de `spawn_agent` Codex neste ambiente Chat; uso real de `masp-observador`, modelo efetivo e auditor independente ficam `BLOCKED/NOT_RUN`, sem inventar telemetria.
- GitHub Actions prova testes Python, não execução de agentes nem veracidade dos registros preenchidos.
