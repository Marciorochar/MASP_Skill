# MASP Skill — Multiagentes + Superpowers

Modelo documental de coordenação de **oito agentes MASP** (Identificação, Observação, Análise, Plano de ação, Ação, Verificação, Padronização e Conclusão), com um coordenador transversal e gates entre as fases.

Integra o método MASP às skills do [Superpowers](https://github.com/obra/superpowers), com foco em evidências, segurança de execução, revisão independente e melhoria contínua.

> **Estado:** documentação e contratos de agentes. A publicação desses arquivos **não instala nem cria automaticamente subagentes** em Codex, e não executa alterações em projetos-alvo.

## Comece aqui

- [Guia de instalação e uso](docs/masp/LEIA-ME.md)
- [Arquitetura e gates](docs/masp/MASP-ARQUITETURA.md)
- [Adendo sugerido ao AGENTS.md](docs/masp/AGENTS-MASP-ADENDO.md)
- [Prompt de início para Codex](docs/masp/PROMPT-CODEX.md)
- [Contratos dos oito agentes](docs/masp/agentes/)
- [Ficha de caso MASP](docs/masp/modelos/CASO-MASP.md)
- [Exemplo MASP-001 (compilação C++11)](docs/masp/exemplos/MASP-001-falha-gcc-c.md)

## Como usar

Abra o repositório-alvo em um workspace isolado e leia seu `AGENTS.md`. Copie o conteúdo de `docs/masp/` para o mesmo caminho no projeto-alvo, sem sobrescrever regras existentes. Revise o adendo do AGENTS.md antes de incorporar suas recomendações e adapte os caminhos exemplificados no prompt. Confirme se a sessão de Codex realmente suporta multiagentes e as skills Superpowers.

Os gates MASP são sequenciais; somente tarefas independentes de investigação podem ser paralelizadas. Ação requer plano aprovado; Verificação exige resultados reais, não apenas declarações de um agente. A promoção para produção é uma decisão separada.

## Escopo do exemplo

O MASP-001 demonstra um caso de falha em `g++ -c` relatada num OTServer. É material ilustrativo: compilação, harness, build integral e integração **não foram executados por este repositório**.
