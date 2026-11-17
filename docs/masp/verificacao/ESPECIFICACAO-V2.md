# MASP — Verificação Universal v2 (M06)

**Missão:** confrontar resultados observados com objetivo e baseline, identificar regressões e produzir parecer independente proporcional às evidências. Funciona em tecnologia, indústria, logística, saúde, ambiente, educação, serviços, administração e cotidiano.

## Contrato

Entradas: objetivo/critério M01 e M04, baseline qualitativo/quantitativo/indisponível e limitações M02, causas M03, intervenções M05 e evidências. Não antecipar métrica nem inventar medições. Saída: comparação antes/depois, critérios de aceitação, resultado, riscos, regressões, revisão independente e limites para M07.

**Conformidade de execução ≠ funcionamento ≠ resultado ≠ eficácia ≠ sustentabilidade**. Mudança temporal isolada não prova causalidade. Compare unidade, método, população e período quando relevantes. Referências atribuídas, observações históricas não reproduzíveis e critérios qualitativos são admissíveis com limites explícitos. Percentual com baseline zero é indefinido; o validador estrutural não autentica a fonte.

## Gate 06

Preservar exatamente `baseline_comparison`, `runtime_tests`, `relevant_regressions`, `independent_review`. A verificação pode consistir em **comando realmente executado** com `exit_code=0` e saída, ou **procedimento observacional** registrado como realizado com método, fonte, resultado, observador, revisor independente e referência de revisão. Nunca inventar comando shell para inspeção física; nunca esconder um comando com exit_code diferente de zero usando uma inspeção favorável. Rótulos `RUNTIME` do ledger continuam não autenticados.

- `PASS`: critérios suficientemente verificados no escopo e revisão competente, sem regressão impeditiva.
- `FAIL`: avaliação realizada demonstra critério não atendido.
- `BLOCKED`: evidência, segurança, autorização, competência ou revisão indispensável ausente.
- `NOT_RUN`: verificação não realizada; não emitir conclusão de eficácia.

## Sidecar

`validate-verification --record .tmp/verificacao.json --root .` chama `validate_verification_record` e compara estrutura/consistência quantitativa ou qualitativa apenas, com classificação **STATIC**. Uma ficha com `effectiveness_claim=demonstrated` e dados preenchidos não autentica observação, causalidade, independência ou Gate 06.

**Astra:** política existente de revisão em alto risco permanece obrigatória; ausência => BLOCKED. Restrições específicas OTServer somente em caso OTServer; não reproduzir acidentes ou experiências perigosas para testar.
