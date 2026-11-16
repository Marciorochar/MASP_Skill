# MASP Multiagentes + Superpowers — modelo para Codex / OTServer

Este repositório contém os contratos documentais, a skill local MASP e uma CLI Python para validar roteamento e simular transições de caso. Isso não comprova descoberta da skill nem dos agentes no runtime do Codex e não modifica o OTServer, checkout original, serviços, banco, configuração global ou binários.

## Organização

- `MASP-ARQUITETURA.md`: fluxo, estados e critérios de passagem.
- `../../.agents/skills/masp/SKILL.md`: skill local com fluxo MASP, limites de evidência e uso da CLI.
- `../../skills/masp/references/routing-guide.md`: fases, gates, evidências e comandos oficiais.
- `masp-routing.toml`: matriz declarativa consumida pela CLI.
- `AGENTS-MASP-ADENDO.md`: regras para incorporar ao AGENTS.md existente, sem substituí-lo.
- `PROMPT-CODEX.md`: ordem de início para o coordenador no Codex.
- `agentes/`: oito contratos de trabalho especializados.
- `modelos/CASO-MASP.md`: ficha para cada problema.
- `exemplos/MASP-001-falha-gcc-c.md`: piloto baseado na falha relatada do OTServer.

## Como usar

1. Abra o projeto **isolado** no Codex e leia seu `AGENTS.md` atual.
2. Copie o conteúdo deste pacote, de preferência, para `docs/masp/` ou outro diretório documental novo. Não sobrescreva instruções existentes.
3. Analise o `AGENTS-MASP-ADENDO.md` e incorpore somente o que não conflitar com o `AGENTS.md` original.
4. Confira se o Codex realmente oferece delegação de subagentes. Em ambientes compatíveis, a skill do Superpowers para Codex descreve `[features] multi_agent = true` no `~/.codex/config.toml`; configurar isso é uma ação separada, com autorização do usuário, e a disponibilidade real deve ser conferida na sessão.
5. Use `PROMPT-CODEX.md` para começar o piloto `MASP-001` em modo diagnóstico. Não execute ação sobre servidor, DB ou binários desconhecidos.
6. Não considere documentos de papel uma criação real de agentes. O coordenador deve verificar as ferramentas disponíveis e, somente então, criar/dispatchar os agentes nos mecanismos suportados.
7. Neste repositório, consulte `.agents/skills/masp/SKILL.md` para a integração local e execute `python -m masp_skill.cli validate-routing --routing docs/masp/masp-routing.toml --classification STATIC` para validar estaticamente a matriz. `STATIC` não confirma descoberta, delegação ou comportamento em runtime.

## Princípios

- Oito fases são **sequenciais em seus gates**; tarefas de investigação independentes podem ser paralelas.
- Cada agente recebe somente o contexto necessário, evidências e contrato de saída.
- O coordenador controla estados `PENDING`, `IN_PROGRESS`, `PASS`, `FAIL`, `BLOCKED` e `NOT_RUN`.
- Os agentes não criam subagentes e não escrevem simultaneamente no mesmo arquivo.
- `PASS` exige evidência executada; saída textual de agente isoladamente não prova sucesso.
- A promoção do OTServer é um gate separado, que permanece bloqueado até haver testes, build, isolamento e proveniência suficientes.

## Mapeamento das skills Superpowers

Identificação → brainstorming; Observação → systematic-debugging; Análise → systematic-debugging; Plano → writing-plans; Ação → using-git-worktrees, test-driven-development, subagent-driven-development; Verificação → verification-before-completion, requesting-code-review; Padronização → writing-skills (se criar uma skill reutilizável); Conclusão → finishing-a-development-branch (somente com verificações completas).

`dispatching-parallel-agents` é responsabilidade do coordenador para escolher leituras independentes e fazer fan-out. `subagent-driven-development` governa a execução de um plano aprovado. Uma skill não substitui a outra; ambas dependem de estarem disponíveis na sessão. São orientações de fluxo obtidas das skills do plugin Superpowers, não garantias de que todas as ferramentas estão operacionais na sua instalação de Codex.
