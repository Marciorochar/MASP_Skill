# Relatório de testes — Verificação Universal v2

## RED / GREEN
- [RED — Actions 43988113806](https://github.com/Marciorochar/MASP_Skill/actions/runs/43988113806): **13 falhas** em Ubuntu, relacionadas ao validador/CLI inexistentes e ao Gate 06 que ainda rejeitava observação sem comando.
- [GREEN preliminar — Actions 43988595613](https://github.com/Marciorochar/MASP_Skill/actions/runs/43988595613): Ubuntu **281 passed, 1 skipped**, validação de routing/ledger; conferir Windows e novo HEAD documental antes de atestar a versão final.

## Verificações
`tests/test_verification_v2.py`: unidade/método comparável, denominador zero, inconsistências de referência, revisão independente, `NOT_RUN`, regressões, procedimento observacional, falha de comando que não pode ser ocultada e CLI STATIC. `tests/fixtures/verificacao-v2/casos.json`: 9 domínios e 30 situações adversariais **SIMULATED**, não 39 avaliações de agentes.

**Limites:** o motor conserva eventos e papéis autodeclarados SIMULATED; `RUNTIME` dentro de uma ficha não autentica observação, resultado ou independência. Nenhuma intervenção de campo ou caso real. Delegação Codex `masp-testador`: **NOT_RUN**. Modelo Astra não invocado; política de alto risco preservada. Os resultados são de testes Python, não de eficácia real ou segurança profissional.
