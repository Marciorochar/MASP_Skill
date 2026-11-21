# Relatório — Plano de Ação Universal v2

**Data:** 16/11/2026. **Branch:** `feat/masp-plano-acao-universal-v2` baseada na `main` `8ee8545596375bc40dcc45eb0030c6c1d1d6e4d1`.

## Resultado e limites

Esta evolução aborda problemas de qualquer domínio, vinculando opções de intervenção às evidências dos módulos 01–03. Introduz comparação de alternativas, **mudança mínima adequada**, 5W2H, responsabilidades, riscos, prevenção e mitigação, reversão/contingência, critérios futuros de teste e autorização humana.

O motor `src/masp_skill/case.py` e `schema_version` do ledger **não foram modificados**. Preservados exatamente os requisitos `tasks`, `owners`, `scope`, `risks`, `rollback`, `tests`, `human_approval`.

## Evidências de TDD e CI

| Etapa | Execução verificável | Resultado |
| --- | --- | --- |
| RED — módulo ausente | [GitHub Actions 43962690955](https://github.com/Marciorochar/MASP_Skill/actions/runs/43962690955) | `ModuleNotFoundError: masp_skill.action_plan` no início da suíte |
| GREEN parcial — verificador, sem documentação | [GitHub Actions 43962989967](https://github.com/Marciorochar/MASP_Skill/actions/runs/43962989967) | `248 passed, 1 skipped, 1 failed` no Ubuntu; documentação `ESPECIFICACAO-V2.md` ainda não criada |
| GREEN — implementação e contratos | [GitHub Actions 43963644219](https://github.com/Marciorochar/MASP_Skill/actions/runs/43963644219) | **249 passed, 1 skipped, 0 failed** no Ubuntu e Windows; `validate-routing` e `validate-case` aprovados |

`validate-routing`: 8 fases, 10 papéis, zero erros. `validate-case`: caso e ledger válidos, com revisões SHA-256 exibidas pela CLI. O teste ignorado não é contabilizado como aprovação.

A validação Python é de estrutura e referências declaradas, não de viabilidade real, segurança em campo, execução humana ou capacidade do LLM de escolher corretamente uma intervenção.

## Validador opcional

`src/masp_skill/action_plan.py` expõe `validate_action_plan_record(record) -> list[str]`, com CLI:

```powershell
python -m masp_skill.cli validate-action-plan --record .tmp/plano.json --root .
```

Verifica: referências de alternativas/tarefas/responsáveis, campos 5W2H, custos `known` ou `unknown` com motivo, risco e teste por tarefa, rollback `reversible`, `partial` ou `irreversible` e contingências, `analysis_status` inconclusivo sem ação corretiva definitiva, baseline conhecido/indisponível, critério de aceitação e falha e coerência de `human_approval` **declarado**.

**Não autentica autorização humana.** Uma ficha com `human_approval.status=approved` e campos preenchidos pode ser estruturalmente válida, mas o programa não confirma quem aprovou e **não emite PASS do Gate 04**. O status `pending` também é estruturalmente válido, sem liberar Ação. A decisão real depende de autoridade externa competente.

## Corpus e fontes

`tests/fixtures/plano-acao-v2/casos.json` contém **9 domínios** (indústria, logística, saúde, administração, meio ambiente, tecnologia, educação, serviços e cotidiano) e **20 cenários adversariais**, no total **29 entradas sintéticas com invariantes**. Não há 29 respostas de agente, 29 autorizações ou 29 intervenções verificadas.

Referências de princípios gerais: 5W2H/Sebrae, 8D-D5/ASQ, PDSA/IHI, gestão de riscos/ISO 31000, FMEA, RACI/SMART e Superpowers. Consulte `REFERENCIAS-METODOLOGICAS.md`. Não foi importado código ou conteúdo protegido dessas fontes.

## Execução multiagente e autorizações

| Verificação | Resultado |
| --- | --- |
| Leitura de instruções Superpowers (brainstorming, plans, TDD, writing-skills, verification) | **Consultadas** nesta sessão |
| Execução de testes Python por GitHub Actions | **RUNTIME dos comandos**, com saídas verificadas |
| Testes do sidecar | **STATIC** — estrutura, não mundo real |
| 29 cenários | **SIMULATED**, sem saídas de agente |
| `masp-planejador` criado por runtime Codex nesta sessão | **NOT_RUN**: não há `spawn_agent` disponível |
| `masp-testador` como revisor independente | **NOT_RUN** |
| Modelo/effort real dos agentes | **NÃO COMPROVADO** |
| Aprovação humana real de qualquer plano MASP | **NOT_RUN** |
| Implementação de mudanças em processo real | **NOT_RUN** |
| Astra | **NOT_RUN** |

As ferramentas de GitHub foram usadas apenas para editar o **próprio repositório da skill** em branch isolada. Essas alterações não são a execução de uma intervenção de um caso MASP.

## Revisão recomendada antes de merge

1. Obter revisão humana do PR e avaliar se as condições de aprovação estão suficientemente claras.
2. Verificar uma execução controlada **de um único** `masp-planejador` no runtime Codex, em somente leitura, preservando eventos de criação/conclusão e transcrições pertinentes sem divulgar dados sensíveis.
3. Fazer avaliação comportamental de casos multidomínio com rubrica independente: planos propostos realmente vinculados à causa ou inconclusão, riscos/controles proporcionais, não execução de ações e não invenção de aprovação.
4. Confirmar compatibilidade com exigências específicas dos domínios críticos quando aplicável. A documentação geral não substitui especialistas ou protocolos de segurança.

**Parecer:** apto à revisão de PR no escopo Python e documental; eficácia do agente e autorizações em ambiente real não comprovadas.
