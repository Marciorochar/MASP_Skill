# Desenho técnico — Plano de Ação Universal v2 (16/11/2026)

## Objetivo

Aprimorar exclusivamente o Módulo 04 para elaborar planos de intervenção **proporcionais, delimitados, testáveis e sujeitos à aprovação humana real**, adequados a qualquer domínio. A entrada é o resultado fundamentado do Módulo 03 (inclusive `INCONCLUSIVA`), mais o problema, baseline e restrições dos módulos 01–02.

**Não objetivos:** executar ações de caso, aprovar planos por conta própria, inventar pessoas/custos/prazos/metas, criar autorização humana fictícia, alterar o ledger e os gates, exigir rollback fisicamente impossível, invocar Astra ou executar todos os agentes.

## Alternativas

| Opção | Benefícios | Limites |
| --- | --- | --- |
| Apenas documentação 5W2H | Simples, sem novo código | Incoerências estruturais de aprovação/reversão passam despercebidas |
| Alterar `case.py` e schema do ledger | Regras centralizadas | Migração cara e risco para todos os módulos |
| **Contrato humano + sidecar JSON opcional (selecionado)** | Checks estruturais de ações, riscos, contingência e aprovação declarada, sem mexer no ledger | Não autentica autorização real nem determina viabilidade |

## Contrato universal

1. Registro em Markdown: análise de alternativas, justificativa da mudança mínima **adequada**, plano 5W2H, recursos, responsáveis, riscos preventivos e mitigadores, rollback/contingência, critérios de teste, condições de interrupção e autorização.
2. JSON auxiliar **opcional**: `validate_action_plan_record(record) -> list[str]` em `src/masp_skill/action_plan.py`, exposto por `validate-action-plan --record <JSON> --root <workspace>`.
3. Validar IDs e vínculos: alternativas, tarefas, responsáveis, riscos, testes e plano de reversão por tarefa. `human_approval.status=pending` não produz `PASS`; `approved` requer justificativa e referência declarada, mas o aplicativo **não autentica** quem aprovou ou a prova.
4. Se a análise for `inconclusive`, impedir no sidecar uma medida rotulada `corrective` como solução definitiva; permitir avaliação, contenção/proteção e monitoramento, sempre com limites e aprovação se exigível.
5. Rollback `reversible` exige procedimento, gatilho, dono e verificação; `partial` exige delimitação e contingência; `irreversible` exige justificativa, ponto de não retorno, mitigação, stop antes da etapa irreversível e autorização. Um texto "rollback pronto" nunca torna irreversibilidade reversível.
6. Testes por tarefa com baseline `known` ou `unavailable` documentado, resultado esperado, método, aceitação, falha, stop e responsável independente quando possível. O plano **não** registra teste executado.
7. As sete chaves já existentes permanecem exatamente: `tasks`, `owners`, `scope`, `risks`, `rollback`, `tests`, `human_approval`. Nenhum ajuste em `src/masp_skill/case.py`, ledger ou módulos 01–03/05–08.

## Status e segurança

`STATIC`: checagens de estrutura declarada; `SIMULATED`: testes e casos sintéticos; `RUNTIME`: comando de CI realmente executado, sem prova da veracidade de autorizações ou execução de agentes. O gate 04 só pode dar PASS com autorização externa real, avaliada no processo competente, e risco tratado. A aprovação textual em JSON não tem autoridade.

Restrições de OTServer são **condicionais ao domínio**, jamais aplicadas universalmente. Segurança/saúde/ambiente exigem responsáveis competentes. Não executar intervenções reais ou acessar produção.

## Validação

- TDD: testes RED para ausências, IDs inválidos, ação inconclusiva inadequada, rollback irreversível sem contingência, risco/stop/teste faltantes, falso status de aprovação e CLI.
- 9 domínios + 20 cenários adversariais **sintéticos** (inventário com invariantes, sem respostas reais de LLM).
- CI GitHub Actions Windows/Ubuntu, testes totais, `validate-routing`, `validate-case` e revisão de diff.
- Não há ação de `spawn_agent` Codex neste Chat; marcação `NOT_RUN` para delegação e avaliação comportamental.
