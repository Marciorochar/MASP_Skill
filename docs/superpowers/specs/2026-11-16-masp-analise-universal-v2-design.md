# Desenho técnico — MASP Análise Universal v2 (16/11/2026)

## Intenção e escopo aprovado

Implementar o Módulo 03 para comparar hipóteses concorrentes e avaliar evidências **favoráveis, contrárias e ausentes** sobre problemas de qualquer domínio, inclusive fenômenos históricos, sociais e qualitativos. O pedido "aplicar" acompanha a especificação detalhada enviada na conversa; é autorização para preparar esta evolução numa branch e abrir PR, **não** para alterar diretamente a `main`, fazer experimentos perigosos ou integrar sem revisão.

**Não objetivos:** comprovação matemática automática de causa, inferência estatística sem dados, mudança dos módulos 01/02 ou 04–08, execução de ações corretivas, autenticação de registros, migração do ledger, execução de todos os papéis Codex.

## Alternativas e trade-offs

| Alternativa | Vantagem | Risco |
| --- | --- | --- |
| Apenas Markdown/TOML | Muito simples, compatível | Critérios de referências de evidência sem validação automatizada |
| Alterar o schema do ledger | Gate mais estruturado e obrigatório | Migração e regressão transversal; custos altos |
| **Contrato universal + ficha humana + sidecar JSON opcional (selecionada)** | Verifica consistência estrutural de hipóteses e vínculos de evidências sem mudar o motor MASP | Não confirma veracidade ou causalidade; requer revisão humana |

## Arquitetura

1. `docs/masp/analise/ESPECIFICACAO-V2.md`: fluxo de raciocínio causal, métodos opcionais, fronteiras, estados de hipótese e gate.
2. `docs/masp/analise/MATRIZ-HIPOTESES-EVIDENCIAS.md`: worksheet para hipóteses, contraevidências, alternativas, testes e conclusão delimitada.
3. `docs/masp/analise/REFERENCIAS-METODOLOGICAS.md`: ASQ (RCA, 8D D4, 5 Porquês), CDC (confusão/viés/associação), AHRQ (limites sistêmicos), Superpowers, licenças.
4. Contratos `docs/masp/agentes/03-analise.md`, `.codex/agents/masp-analista.toml`, `.agents/skills/masp/SKILL.md`, bloco M03 da matriz `docs/masp/masp-routing.toml`, ficha humana `CASO-MASP.md`.
5. `src/masp_skill/analysis.py`: `validate_analysis_record(record) -> list[str]`; validará **estrutura declarada**, IDs de fontes/hipóteses, estados, resultados executados versus não executados, coerência declarativa da conclusão e vínculo de causa sustentada a hipótese corroborada. Não validará o raciocínio, autoria nem o Gate 03.
6. `src/masp_skill/cli.py`: comando `validate-analysis --record ... --root ...` classificado **STATIC** e isolado do ledger.

## Compatibilidade e segurança

Manter exatamente três IDs de `GATE_REQUIREMENTS["analise"]`: `hypotheses`, `evidence_for_and_against`, `root_cause_or_explicit_inconclusive`. Nenhum ajuste em `case.py`, `schema_version`, estados do motor, modelos, modelos de effort ou fases 01/02/04–08.

A existência de `CORROBORADA` no sidecar representa **declaração humana não autenticada**. Mesmo um sidecar válido NÃO concede `PASS` ao gate. O coordenador deve avaliar suficiência causal contextual, método, fontes, limitações e riscos. Risco iminente segue procedimentos competentes, nunca experimentos perigosos. Não exportar dados pessoais ou evidências sensíveis para o repositório público.

## Validação

- Primeiro: testes RED reproduzíveis em `tests/test_analysis_v2.py` antes do código.
- Testes funcionais: identificadores duplicados, fontes ausentes, prova contra ignorada, estado `CORROBORADA` sem avaliação executada, conclusão suportada sem hipótese corroborada, prova exclusivamente correlacional, `NOT_RUN`, análise retrospectiva inconclusiva, caso multi-causa; limites de workspace na CLI.
- Fixtures: 9 domínios + 20 entradas adversariais. São apenas **SIMULATED**.
- CI Python 3.11 Windows/Ubuntu, `validate-routing`, `validate-case`, revisão do diff antes de abrir PR.
- Sem `spawn_agent` do runtime Codex disponibilizado nesta sessão: delegação `masp-analista` e revisão `masp-testador` ficam `NOT_RUN`; não inferir dados de modelo/effort nem declarar validação comportamental.
