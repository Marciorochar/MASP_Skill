# Relatório de validação — MASP Análise Universal v2

**Data:** 16/11/2026. **Branch:** `feat/masp-analise-universal-v2`. **Base:** `acb33f888bc467c0cd4103f5edba7440539252a9` (`main` na criação da branch).

## Objetivo e mudanças

Transformar o Módulo 03 em análise causal aplicável a problemas industriais, logísticos, de saúde, administração, meio ambiente, educação, serviços, tecnologia e cotidiano. Inclui comparação de hipóteses rivais, evidências favoráveis/contrárias, alternativas, limites de confusão/associação, métodos selecionados e inconclusão legítima.

A v1 descrevia determinação de causas por experimentos, com restrições permanentes do exemplo OTServer e regras resumidas de gate. A v2 introduz dois modos (rápido/aprofundado) e investigação não experimental ou retrospectiva quando pertinente.

**Compatibilidade:** `GATE_REQUIREMENTS["analise"]` preserva exatamente `hypotheses`, `evidence_for_and_against`, `root_cause_or_explicit_inconclusive`. Nenhuma mudança em `src/masp_skill/case.py`, `schema_version`, ledger, papéis/modelos de outros agentes ou módulos 01/02/04–08. O roteamento altera somente o bloco de Análise; os arquivos compartilhados apenas incluem referências ao M03.

## Classificação das evidências

| Evidência | Classe / alcance | Limite |
| --- | --- | --- |
| Inspeção de contrato, matriz e sidecar JSON | **STATIC** | Verifica estrutura e referências declaradas, não a veracidade de fontes ou validade causal |
| `tests/fixtures/analise-v2/casos.json`, nove domínios e vinte casos adversariais | **SIMULATED** | Entradas e invariantes de teste, sem respostas de agente e sem observações de campo |
| GitHub Actions Python/pytest Windows e Ubuntu | **RUNTIME dos comandos** | Testa Python, CLI e contratos; não o comportamento real do LLM Codex |
| Execução do `masp-analista` via `spawn_agent` | **NOT_RUN** | Ferramenta não disponibilizada nesta sessão Chat |
| Verificação independente via `masp-testador` | **NOT_RUN** | Nenhum agente revisor foi criado |
| Modelo e effort efetivos dos agentes | **NÃO COMPROVADOS** | Configuração TOML não equivale a telemetria de execução |

Foram consultadas instruções das skills Superpowers de brainstorming, planning, TDD, writing-skills e verification-before-completion. Consultar uma skill não comprova que o Codex a descobriu ou a carregou em seu próprio runtime. Não foi invocado Astra.

## Testes: RED → GREEN

| Ponto | Evidência | Observação |
| --- | --- | --- |
| RED — módulo inexistente | [Actions 43958209996](https://github.com/Marciorochar/MASP_Skill/actions/runs/43958209996) | `ModuleNotFoundError: No module named 'masp_skill.analysis'` |
| GREEN parcial — código antes dos docs | [Actions 43958848010](https://github.com/Marciorochar/MASP_Skill/actions/runs/43958848010) | 195 testes passaram; contrato documental ausente (esperado nesta etapa) |
| GREEN — contrato e código integrados | [Actions 43959516781](https://github.com/Marciorochar/MASP_Skill/actions/runs/43959516781) | Suíte e matriz de roteamento aprovadas |
| RED — entradas JSON com enums não hashable | [Actions 43959718114](https://github.com/Marciorochar/MASP_Skill/actions/runs/43959718114) | 5 falhas `TypeError: unhashable type: 'list'` reproduzidas |
| GREEN — correção de robustez | [Actions 43959829796](https://github.com/Marciorochar/MASP_Skill/actions/runs/43959829796) | **201 passed, 1 skipped, 0 failed** em Windows e Ubuntu |

Na CI GREEN, `validate-routing` informou **8 fases, 10 papéis, zero erros**, e `validate-case` validou o caso/ledger pré-existente nos dois sistemas.

## Comportamentos estruturais verificados

- IDs de hipóteses e fontes não se repetem; referências a evidências e alternativas existentes são exigidas.
- `CORROBORADA` precisa de fonte declarada `FATO_VERIFICADO` e verificação `performed` com referências. Isso **não comprova que tais fontes são reais**.
- `REFUTADA` precisa de contraevidência declarada verificada e avaliação realizada.
- `supported` só pode referenciar hipóteses `CORROBORADA`; `association_only` e `unknown` são rejeitados como base explícita de causa sustentada.
- Para base declarada `documentary_triangulation`, são exigidas ao menos duas origens textualmente distintas, sem provar sua real independência.
- `inconclusive` aceita análise delimitada sem causa final e pode declarar necessidades de coleta.
- `not_run` não pode alegar resultado de procedimento executado.
- JSON malformado com classes e estados como listas retorna erros de validação, sem derrubar o programa.
- `validate-analysis --record ... --root ...` confere caminho dentro do workspace e reporta `STATIC`.
- Os três critérios do Gate 03, e os cinco e quatro critérios anteriores dos módulos 01 e 02, permanecem intactos.

**O validador não determina causalidade, não calcula confiança, não autentica provas e não pode conceder `PASS` do Gate 03.** A aprovação depende da avaliação contextual do coordenador, autorização aplicável e avaliação independente proporcional ao risco.

## Lacunas e próximos passos

1. Testar uma sessão real e controlada do `masp-analista` em Codex, com telemetria, prompts/respostas integrais e avaliação independente; não executar todos os agentes nem Astra.
2. Obter revisão humana no PR da implementação; classificar ações de segurança e proteção de dados nos casos reais.
3. Se desejado, adicionar posteriormente verificação de autenticidade/proveniência das evidências sob controles de acesso adequados — **fora do escopo atual**.
4. Evitar transpor exemplos OTServer para outros domínios; seleção de métodos é contextual.

**Parecer:** implementação apta a revisão do PR no escopo documental e Python, com execução dos agentes Codex e desempenho causal em campo **não comprovados**. A CI não substitui essa verificação.
