# MASP-001 — Geração de objeto C++11 (`-c`) falha sem diagnóstico visível

**Status inicial do exemplo: OBSERVAÇÃO PENDENTE DE REPRODUÇÃO.** Este caso usa o **relatório trazido pelo usuário**; não foram inspecionados arquivos locais nem executados comandos aqui.

## 01 Identificação — registro preliminar

- Problema: `g++ -c` teria encerrado com código 1 sem diagnóstico capturado na cópia isolada, apesar de `-fsyntax-only` e `-S` terem sido reportados como PASS.
- Consequência: build/link e harness não executados; promoção bloqueada.
- Objetivo: reproduzir a falha com logs completos, identificar causa verificável e, se autorizado, obter objeto/link/harness executados em workspace isolado.
- Não confundir sucesso `-S` com criação de objeto; não inferir culpa do código.

## 02 Observação — próximo trabalho permitido

- Inventariar comando exato, shell, compilador, assembler, diretório de trabalho, opções `-o`, paths e permissões.
- Comparar `-fsyntax-only`, `-S` e `-c` com `-v`/`-###` e captura de stdout, stderr e exit code, quando suportados.
- Preservar artefatos temporários em diretório de testes dedicado, sem alterar o checkout original nem sobrescrever snapshots.
- Guardar identificador do toolchain e hash do arquivo de teste.

## 03 Análise — somente após evidências

- Hipóteses a investigar (não são diagnósticos): falha do assembler, problema no caminho/saída, permissão, ferramenta ausente, ambiente, flags, recursos, interrupção do processo.
- Testar uma hipótese por vez. Registrar negativa/positiva e causa confirmada quando possível.

## 04-08 — condicionadas aos gates

- Plano: 5W2H de mudança mínima + critérios de rollback.
- Ação: não alterar engine sem causa e plano aprovados; teste primeiro.
- Verificação: medir harness 3/3 executados (não só compilados), sem concluir validação de DB real a partir de stubs.
- Padronização: preservar comando de build reproduzível e cenário de regressão.
- Conclusão: promover apenas após decisão separada, evidências de isolamento, build e proveniência. Até lá: BLOQUEADO.
