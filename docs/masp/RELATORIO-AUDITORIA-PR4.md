# Auditoria do PR #4 — correções de robustez e preparação runtime

**Base:** `main` em `7f657e8e94e6ea99a01eb0bdde166688d4ed2aff` (PRs #1–#3).
**Branch:** `fix/masp-pr4-robustez-runtime`.
**Origem:** achados A01–A08 do relatório de auditoria fornecido pelo usuário em 16/11/2026.

## Alcance e decisão

Este PR mantém o motor MASP de oito fases, dez contratos e limite configurado de três agentes. Corrige erros de robustez, fortalece testes e prepara uma prova de integração **limitada a um agente**. Não foi executado Codex CLI, inferência de subagentes nem Astra durante sua elaboração.

### Matriz de achados

| Achado | Resultado no PR #4 | Prova ou limitação |
| --- | --- | --- |
| A01 — parser JSONL e delegação | **PASS em teste sintético; RUNTIME BLOCKED** | Suporte cauteloso a `collab_tool_call` com `receiver_thread_ids` e `agents_states`. Exige papel explícito, início e conclusão com mesmo destinatário e estado terminal. Eventos somente `wait` não comprovam spawn. |
| A02 — `TypeError` em retorno após `FAIL` | **Corrigido e testado** | Gate de tipo antes da pertinência; ledger re-hash preservado no teste adversarial. |
| A03 — nomes e IDs de fase inconsistentes | **Corrigido e testado** | Validação rígida da sequência de oito IDs vinculada à sequência de oito nomes. |
| A04 — ausência de Astra no inventário | **Corrigido estaticamente** | Astra consta dos dez papéis, mas `NOT_RUN` por política do smoke inicial. |
| A05 — `--parallel-tasks` opcional | **Limitação registrada** | Valida atribuições fornecidas; não intercepta escrita ou delegação real. Não se afirma enforcement de runtime. |
| A06 — assert genérico nos adversariais | **Fortalecido** | Comparação de erros específicos, com hash de evento recalculado para não confundir corrupção de hash com erro de tipo. |
| A07 — `main` sem proteção | **Pendente fora do PR** | Branch ruleset/required checks exigem configuração administrativa; não foram alterados. |
| A08 — relatório histórico da skill | **Documentação esclarecida** | Skill canônica atual está em `.agents/skills/masp/SKILL.md`; versão antiga permanece preservada como histórico. |

## Testes

- Ciclo inicial RED foi documentado no GitHub Actions da branch; oito regressões falharam antes das correções em ambos os sistemas.
- O ciclo GREEN após as correções está sujeito à confirmação da execução do commit final da branch em Windows e Ubuntu. Não converta logs anteriores em atestado do HEAD final.
- A suíte executada na CI é Python 3.11 e não realiza inferência de subagentes.
- **Um teste SKIP** pode ocorrer quando as skills externas Superpowers não estão instaladas no runner; não o contabilize como aprovado.

## Classificação operacional A–E

- **A. Motor Python:** PASS somente quando CI do HEAD confirmar.
- **B. Fluxo MASP simulado:** PASS somente quando CI do HEAD confirmar.
- **C. Descoberta e carregamento real da skill:** BLOCKED.
- **D. Delegação de `masp-identificador` e modelo efetivo:** BLOCKED.
- **E. Sistema multiagente validado:** BLOCKED.

A documentação de execução local está em `docs/masp/VALIDACAO-RUNTIME-PR4.md`. Não usar `--all-roles`, não invocar Astra nesta fase, não alterar `main` nem produção.

## Segurança e limitações

- `validate_parallel_tasks` impede conflitos em uma lista fornecida, mas não é controle de sistema de arquivos dos agentes.
- Rótulos `approved_by`, `role` e `model` no ledger não representam identidades autenticadas.
- Nenhum relatório de texto, TOML ou mensagem de agente é prova independente de modelo efetivo ou autorização.
- O arquivo histórico `codex-smoke.json` apresenta eventos `wait` sem `spawn_agent` comprovado. A ausência de eventos de spawn não prova que nenhuma delegação ocorreu.
- Revisão independente de runtime e ruleset GitHub continuam pendentes.

**Parecer provisório:** correções de código poderão ser aprovadas após CI do HEAD e revisão independente. **A operação multiagente não está aprovada** sem execução real, visibilidade de delegação e isolamento observável.
