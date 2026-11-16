# Desenho técnico — MASP Módulo 06: Verificação Universal v2

**Data:** 16/11/2026  
**Estado:** PROPOSTA DE DESENHO — aprovação humana pendente; **não implementar antes da aprovação**  
**Branch:** `feat/masp-verificacao-universal-v2`  
**Base examinada:** `main` `c6ca23226f61bd74f400f181aa1da27f9103ec9a`  
**Escopo:** exclusivamente a fase 06, respeitando os contratos anteriores e posteriores

## 1. Objetivo e critério de sucesso

Desenvolver uma verificação de **resultado, eficácia e regressões**, não apenas da execução de comandos. Aplicável a indústria, logística, saúde, administração, meio ambiente, educação, serviços, tecnologia e problemas cotidianos, com medidas quantitativas, condições qualitativas e dados incompletos.

**Ação bem executada ≠ problema resolvido.** A verificação só poderá declarar o que for sustentado por evidências atribuídas, critérios prévios e avaliação independente de alcance adequado. Um arquivo válido, um teste isolado, uma correlação ou um parecer do executor não demonstram eficácia por si sós.

O produto do M06 separará: conformidade da execução, funcionamento imediato, resultados observados, eficácia no escopo avaliado, sustentabilidade no horizonte verificado, regressões/efeitos indesejados e evidências pendentes.

## 2. Auditoria da situação atual

O documento `docs/masp/agentes/06-verificacao.md` contém 29 linhas, centradas em diff, logs, testes reproduzíveis e revisão do executor, incluindo restrições OTServer como persistentes. `.codex/agents/masp-testador.toml` define um agente de verificação independente, mas sua configuração não prova que foi instanciado.

`docs/masp/masp-routing.toml` fornece o papel `masp-testador`, acessos `read-only` / `execute-approved` e retornos diretos **somente para Ação ou Análise**. A CLI e `src/masp_skill/case.py` operam com casos `SIMULATED`, sem autenticação de identidades ou execução real.

O Gate 06 tem exatamente quatro requisitos:
- `baseline_comparison`
- `runtime_tests`
- `relevant_regressions`
- `independent_review`

**Dependência real:** PR #11 foi mesclado, mas incluiu **apenas a proposta e o plano do Módulo 05**; a `main` ainda apresenta o antigo `05-acao.md`, sem `docs/masp/acao/ESPECIFICACAO-V2.md` ou validador de execução universal. Isso impede declarar integração funcional fim a fim com a Ação Universal v2. O M06 pode ser especificado e, após aprovação, testado com registros sintéticos, mas o handoff operacional real ficará `BLOCKED` até existir evidência do M05.

| Aspecto | Situação atual | Gap | Direção v2 |
| --- | --- | --- | --- |
| Entrada | Diff, plano, logs, meta | Software como padrão | Registros antes/depois, procedimentos ou comandos e critérios de qualquer domínio |
| Baseline | Comparação mencionada | Sem equivalência explícita de métodos/unidades/períodos | Verificar compatibilidade; aceitar base qualitativa ou indisponível com limites |
| Eficácia | Não separada de sucesso do teste | Risco de falso PASS | Distinguir implementação, funcionamento, resultado, eficácia e sustentabilidade |
| Regressões | Pergunta genérica | Sem checagem de métricas de proteção | Avaliar efeitos colaterais, deslocamento do problema e riscos novos |
| Independência | Exigência textual | Sem autenticação de revisor ou proveniência | Segregação de função e evidência real de revisão, fora da simples estrutura |
| Retornos | Ação e Análise | Observação não é retorno direto | Manter os retornos existentes; propor alteração só com revisão separada |
| Segurança | Condições OTServer globais | Não universal | Restrições condicionais ao domínio e avaliações autorizadas |
| Evidências | Comandos/logs | Pode faltar ensaio físico ou qualitativo | Registrar método, origem, resultado observado, status e limitações |

## 3. Alternativas de arquitetura

**A. Apenas documentação Markdown/TOML:** custo baixo, mudanças mínimas; não garante consistência de referências/medidas.

**B. Ampliar `case.py`/ledger para calcular eficácia e liberar gates:** maior automação aparente; cria risco de falso PASS, extrapolação causal, alterações transversais e falsa autenticação. **Rejeitada.**

**C. Contrato metodológico + ficha humana + JSON sidecar opcional e validador puramente estrutural (recomendada):** continuidade com M01–M04, sem migração de schema; pode detectar unidades incompatíveis, denominador zero, referências inválidas, revisão declarada pelo executor e testes `NOT_RUN` falsamente aprovados. Não identifica se a evidência existiu ou se a intervenção causou os resultados.

**Critério de decisão:** compatibilidade, simplicidade, risco de falso PASS, neutralidade de domínio e possibilidade de teste real no futuro.

## 4. Modelo de entradas e fronteiras

Receber do M01: problema, impacto, meta e escopo; M02: baseline quantitativo/qualitativo/indisponível, fontes/períodos/métodos; M03: hipóteses e limitações causais; M04: plano/versão aprovada, testes, aceitação, falha e critérios de stop; M05: **evidência de intervenção realmente executada** e alterações reais, ambiente, escopo, desvios e resultados.

**Fronteira de confiança:** os sidecars do M04, rótulos de `approved`, hashes e eventos simulados do ledger não autenticam aprovação ou execução de intervenção. Sem execução real/autorizações suficientes, `NOT_RUN` ou `BLOCKED` para a verificação de eficácia real.

Não recalibrar metas depois de conhecer o resultado. Preservar critérios e versões originais.

## 5. Fluxo de verificação proposto

1. **Inspecionar pré-requisitos:** comprovar que M05 realizou alguma ação no ambiente pertinente, com evidências próprias. O verificador não executa nem corrige a ação.
2. **Confirmar comparabilidade:** mesmo objeto, indicador, unidade, período/denominador, condições operacionais e método; verificar amostra, representatividade e fontes. Se incomparável, não afirmar melhoria.
3. **Aplicar baseline:** `quantitative` com diferença absoluta e, quando matematicamente aplicável, percentual; `qualitative` com critérios observáveis pré-definidos e registros atribuídos; `unavailable` como limitação que pode impedir conclusão.
4. **Verificar critérios planejados:** status `performed` (com evidência) ou `not_run` (motivo), nunca `PASS` para teste não executado. Não exigir comandos de terminal em avaliações não digitais.
5. **Examinar explicações rivais:** sazonalidade, mudanças simultâneas, seleção da amostra, confiabilidade, observador, regressão à média, causalidade versus simples coincidência temporal. Não criar estatística não calculada.
6. **Verificar regressões:** métricas de proteção, efeitos colaterais, deslocamento de problema, custo/qualidade/segurança/acesso e riscos residuais.
7. **Revisão independente:** responsável por verificação distinto de quem executou, segundo o processo competente, com prova de consulta das fontes e parecer próprio; rótulos em JSON são somente declarações.
8. **Concluir de forma delimitada:** conformidade da execução, resultados, eficácia demonstrada ou não demonstrada, `INCONCLUSIVA`, condições de sustentabilidade e dados pendentes. Uma única observação inicial não sustenta efeito duradouro.
9. **Encaminhar:** avanço à Padronização apenas quando Gate 06 atender seus quatro critérios com prova relevante. Retorno válido à Ação (execução não conforme) ou à Análise (causa não tratada); Observação só mediante caminhos válidos ou mudança específica aprovada.

### Cálculos sob condições apropriadas

`delta_abs = after - before`; `delta_pct = ((after - before) / before) * 100` apenas com denominador **diferente de zero** e escala adequada. Sinal do benefício depende do sentido desejado da métrica (`higher_is_better`/`lower_is_better`), não da positividade matemática de `delta`.

Nenhum cálculo por si mesmo demonstra eficácia causal; não apresentar p-valores, intervalos ou probabilidades sem dados e metodologia reprodutível.

## 6. Gate 06 e classificação de evidência

Preservar `baseline_comparison`, `runtime_tests`, `relevant_regressions`, `independent_review` exatamente.

- **PASS:** verificação efetivamente realizada, com critérios atendidos, comparação adequada, efeitos colaterais pertinentes examinados e revisão independente demonstrada. Não significa sustentabilidade futura automática.
- **FAIL:** procedimento/avaliação realizada com critério de aceitação não atendido, com resultados e fontes preservados.
- **BLOCKED:** faltam execução comprovada, baseline necessário, autorização, competência, dados ou independência para decidir com segurança.
- **NOT_RUN:** avaliação não realizada; **nunca** interpretar como PASS.
- **PENDING / IN_PROGRESS:** estados de trabalho já presentes no ledger, sem reinterpretação.

`STATIC` = inspeção documental ou sidecar; `SIMULATED` = testes/fixtures fictícios; `RUNTIME` = comando ou inspeção efetivamente observada (escopo específico). Um teste Python executado no GitHub Actions é RUNTIME da **suíte**, mas não prova eficácia de intervenções MASP em campo nem delegação de agentes.

## 7. Esboço do contrato universal e da API opcional

Ficha humana em `docs/masp/verificacao/MATRIZ-VERIFICACAO.md` e `MODELO-COMPARACAO-BASELINE.md`: cada item liga baseline, indicador, critério predefinido, período, fonte, resultado, estado, regressões, limitação, revisão independente e decisão sobre retorno.

Se aprovado, o JSON opcional pode fornecer:
- `case_id`, `action_reference`, `approved_plan_reference`, `verification_scope`;
- `baseline_comparison` (tipo, valor/condição, período, unidade, fonte, antes/depois, comparabilidade);
- `runtime_tests` (ID, método, `performed`/`not_run`, resultado e fonte);
- `relevant_regressions` (indicadores de proteção, resultado, efeito colateral, fontes/limites);
- `independent_review` (responsáveis por função, origem da evidência, parecer e limites; **declaração não autenticada**);
- `effectiveness_assessment`, `sustainability_assessment`, `limitations`, `pending_verifications`, `recommended_return_phase`.

**API possível após aprovação:** `src/masp_skill/verification.py` com `validate_verification_record(record: Any) -> list[str]`; opcional `compare_numeric_baseline(before: float, after: float, direction: str) -> dict` puramente aritmético e explícito sobre limitações. CLI `validate-verification --record ... --root ...`, **somente STATIC**, read-only e sem side effects.

Validação estrutural **não autentica** `independent_review`, resultado real, causa ou eficácia, **não muda Gate 06** e **não autoriza Padronização**.

## 8. Escopo de arquivos após aprovação

**Documentação proposta:**
- `docs/masp/verificacao/ESPECIFICACAO-V2.md`
- `docs/masp/verificacao/REFERENCIAS-METODOLOGICAS.md`
- `docs/masp/verificacao/MATRIZ-VERIFICACAO.md`
- `docs/masp/verificacao/MODELO-COMPARACAO-BASELINE.md`
- `docs/masp/verificacao/CONTROLE-REGRESSOES.md`
- `docs/masp/verificacao/RELATORIO-TESTES-V2.md`

**Contratos a modificar:** `docs/masp/agentes/06-verificacao.md`, `.codex/agents/masp-testador.toml`, apenas o bloco Verificação do `docs/masp/masp-routing.toml`, `.agents/skills/masp/SKILL.md`, ficha de caso e seção correspondente do `README.md`.

**Python opcional após RED:** `src/masp_skill/verification.py`, inclusão controlada em `src/masp_skill/cli.py` e `tests/test_verification_v2.py`. Não modificar `src/masp_skill/case.py` nem os contratos/gates de M01–05/M07–08.

**Fixtures:** 9 domínios e 30 casos adversariais, **sintéticos**. Não representar o corpus como 39 verificações reais de agente.

## 9. Fontes e cautela de aplicação

- [CDC — Program Evaluation Framework (2024)](https://www.cdc.gov/evaluation/php/evaluation-framework/index.html): avaliação adequada ao contexto, evidência crível, rigor, independência, transparência e ética.
- [CDC — Gather Credible Evidence](https://www.cdc.gov/evaluation/php/evaluation-framework-action-guide/step-4-gather-credible-evidence.html): selecionar indicadores, fontes e métodos quantitativos/qualitativos.
- [IHI — PDSA Worksheet](https://www.ihi.org/library/tools/plan-do-study-act-pdsa-worksheet): observar e aprender com resultados de mudanças.
- [NIST/SEMATECH — Engineering Statistics Handbook](https://www.itl.nist.gov/div898/handbook/): análise estatística contextual, medições e variação.
- [ASQ — Quality Resources](https://asq.org/quality-resources): métodos de controle e melhoria.

Adaptação autoral dos princípios; links não implicam adoção formal nem certificação. Verificar licenças antes de copiar imagens/textos/templates. Sem experimentos perigosos ou reprodução de acidente para "passar" num gate.

## 10. Plano de validação e bloqueios

1. Após aprovação, criar testes RED (função ausente/contrato ainda não satisfeito) antes do código.
2. Cobrir diferenças antes/depois válidas, baseline indisponível, unidade/período incompatíveis, divisão por zero, amostra insuficiente, efeitos colaterais, regressão grave, `not_run` alegando PASS, dados sem fonte, falseificação de revisão independente, `PASS` a partir de SIMULATED e retorno inválido.
3. Executar pytest e CLI de roteamento/caso no SHA final, Ubuntu+Windows, lendo logs. Não omitir testes ignorados.
4. Testar comportamento real `masp-testador` em sessão Codex com delegação e observabilidade **quando** runtime permitir; se não, `NOT_RUN`.
5. Integrar com M05 v2 **somente quando implementado**, sem inventar logs de ação ou autorização e sem bloquear o trabalho documental da Verificação.

**Limitações desta sessão:** conector GitHub e Browser em Chat permitem leitura/edição do repositório; nenhuma ferramenta de `spawn_agent` Codex foi encontrada. A delegação e auditoria independentes de agentes, assim como testes reais de eficácia, permanecem `NOT_RUN`.

**Aprovação necessária:** os documentos de desenho e plano são submetidos para revisão. **Nenhuma alteração funcional, teste RED, configuração TOML ou merge deve ser feita antes de aprovação explícita do desenho.**
