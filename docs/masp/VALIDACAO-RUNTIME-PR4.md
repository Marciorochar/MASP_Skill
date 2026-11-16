# PR #4 — Validação mínima de runtime Codex

**Objetivo:** obter evidência real de **um** subagente `masp-identificador`, em modo somente leitura. Este documento é um procedimento local; **não representa um teste executado no PR #4**.

## Pré-condições

1. Abra um clone atualizado do `MASP_Skill`, em ambiente de teste, sem alterações pendentes.
2. Confirme `git status --short`, `git rev-parse HEAD`, `codex --version` e `python --version`.
3. Confirme que a skill `.agents/skills/masp/SKILL.md` aparece no catálogo de skills da sessão Codex. Presença em disco não equivale a carregamento.
4. Confirme permissões de sandbox `read-only`, disponibilidade do coordenador e do modelo do identificador. Não modifique configurações globais nem faça fallback.
5. **Não use `--all-roles`**, não invoque Astra, nem toque em VPS, OTServer, bancos ou sistemas de produção. A sondagem poderá consumir tokens de uma sessão Codex.

## Execução única autorizada

Depois da conferência anterior e de autorizar a inferência, execute a partir da raiz:

```powershell
python -m pip install -e ".[test]"
python -m pytest -q
python -m masp_skill.cli validate-routing --routing docs/masp/masp-routing.toml --classification STATIC
python -m masp_skill.cli runtime-smoke --root . --output-dir .tmp/masp-pr4-runtime --strict
```

O smoke faz sondagens do CLI e solicita **somente o primeiro agente de fase**. A exclusão do Astra é intencional. `--strict` pode retornar 1 em caso de `BLOCKED` ou `FAIL` mesmo quando o processo Codex retorna 0; examine os checks individualmente. **Não repita cegamente.**

## Como interpretar as provas

- **STATIC:** arquivo de skill e dez contratos de agentes encontrados. Nenhum agente foi necessariamente carregado.
- **RUNTIME/skill:** somente se houver evento de carregamento ou outra evidência técnica verificável da versão instalada. Mensagens `MASP_SKILL_LOADED` escritas pelo assistente não são prova.
- **RUNTIME/delegação:** `collab_tool_call` explicitamente relacionado ao agente solicitado, com destinatário `receiver_thread_ids` identificável, início + conclusão correlacionados e estado de término do receptor; somente a presença de `wait` não prova criação.
- **RUNTIME/modelo/esforço:** somente a partir de valores efetivos explicitamente emitidos. Modelos do TOML e catálogo são intenções, não observações.
- **BLOCKED:** falta de evidências suficientes, sem inferir falha de execução a partir da ausência de telemetria.
- **NOT_RUN:** demais agentes, especialmente `masp-especialista-critico`, que **não devem** ser chamados nesta etapa.

O parser do PR #4 aceita um formato *sintético* com destinatários e estado de conclusão e preserva o parser legado. Os testes de CI **não comprovam** compatibilidade com `spawn_agent` emitido realmente pelo Codex, pois o JSONL histórico do repositório só contém chamadas `wait`.

## Entregáveis para revisão futura

Preserve `.tmp/masp-pr4-runtime/codex-smoke.json` e `codex-smoke.md`, o commit do checkout, versão CLI, status Git antes/depois e trechos relevantes de JSONL com cuidado para não divulgar dados sensíveis.

Se uma delegação verificável ocorrer, avalie o parser e o modelo efetivo antes de considerar testes de outros papéis. Qualquer ampliação deve ser autorizada separadamente.
