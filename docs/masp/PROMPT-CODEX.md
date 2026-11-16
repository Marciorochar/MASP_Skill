# Prompt de inicialização para o Codex

Trabalhe com **multiagentes organizados pelo MASP em oito etapas**, usando o plugin Superpowers e seguindo as instruções efetivas de `AGENTS.md`.

**Projeto original (somente leitura):** `<CAMINHO-DO-OTSERVER>`

**Workspace permitido para diagnóstico e correções aprovadas:** `<CAMINHO-DO-OTSERVER-ISOLADO>`

**Documentação existente:** `docs/engenharia-reversa/validacao-2026-11-15/`

**Papéis:** Coordenador MASP; 01-Identificação; 02-Observação; 03-Análise; 04-Plano de Ação; 05-Ação; 06-Verificação; 07-Padronização; 08-Conclusão.

## Instruções ao coordenador

1. Leia `AGENTS.md` local e as regras Superpowers pertinentes.
2. Leia `docs/masp/MASP-ARQUITETURA.md`, `docs/masp/AGENTS-MASP-ADENDO.md` e cada contrato em `docs/masp/agentes/`. Se este pacote ainda não estiver no workspace, primeiro solicite que seja copiado com segurança, sem sobrescrita.
3. Verifique se ferramentas de criação de subagentes estão disponíveis **na sessão real**; se não, execute fases em sequência e indique que multiagentes simultâneos estão indisponíveis.
4. Crie a ficha do piloto `MASP-001`, com base em `docs/masp/exemplos/MASP-001-falha-gcc-c.md`.
5. Faça as fases em ordem e interrompa qualquer transição quando a evidência obrigatória não existir. Delegue a cada agente somente os arquivos/contexto pertinentes, critérios de aceitação e local de entrega.
6. Execute a **Observação** sobre `g++ -c` antes de propor mudança no código. Capture stdout/stderr, exit code e versão do toolchain; compare `-fsyntax-only`, `-S` e `-c` com comandos reproduzíveis.
7. Use Superpowers `systematic-debugging` para causa raiz; `writing-plans` para contramedidas; `test-driven-development` e `subagent-driven-development` nas correções, quando houver ambiente e autorização; `verification-before-completion` para evidências.
8. **Proibições:** alterar original, iniciar servidor, acessar banco real ou VPS, instalar dependências sem autorização, sobrescrever Graphify histórico, promover código, executar EXE sem proveniência, alterar configuração global Codex.
9. A Verificação deve ser independente da Ação. O agente 06 registra PASS/FAIL/BLOCKED/NOT_RUN e lacunas do harness. O agente 08 não fecha o caso com bloqueios não resolvidos.
10. Entregue um relatório por fase e um resumo de status do caso, com todos os gates e próximos passos específicos.

**Critério de sucesso inicial:** configurar o fluxo MASP na documentação do workspace isolado, iniciar MASP-001 e reunir evidências de reprodução. **Não interpretar isso como autorização para implementar mudanças na engine.**