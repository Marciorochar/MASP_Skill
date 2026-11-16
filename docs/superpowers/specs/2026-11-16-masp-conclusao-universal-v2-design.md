# Desenho técnico — MASP Módulo 08: Conclusão Universal v2

**Data:** 2026-11-16  
**Situação:** PROPOSTA DE DESENHO — implementar somente após aprovação humana explícita  
**Branch:** `feat/masp-conclusao-universal-v2`  
**Base auditada:** `main` `953c53c870d786dcb84525bfe232f5cf4968990a`

## 1. Objetivo, alcance e não objetivos

Construir uma Conclusão MASP **universal**, adequada a problemas industriais, logísticos, ambientais, de saúde, administrativos, educacionais, tecnológicos, de serviços e cotidianos. O relator deve produzir **síntese auditável, avaliação dos objetivos, lições aprendidas, riscos residuais, pendências, responsáveis futuros e parecer proporcional às evidências**, sem converter documentação, integridade de hashes, registros simulados ou opiniões de agentes em comprovação operacional.

**Conclusão documental ≠ problema resolvido ≠ melhoria sustentável ≠ aprovação institucional ≠ implantação em produção.**

Não objetivos: executar ações reais, aprovar operação/promoção, encerrar administrativamente casos em nome de pessoas, alterar scores/gates históricos, mudar schema de ledger, acessar informações sensíveis ou executar modelos críticos indevidamente.

## 2. Auditoria do repositório — estado verificado

- `docs/masp/agentes/08-conclusao.md`: relator com orientação sucinta para relatório final, métricas antes/depois, integração e backlog. Restrições OTServer chamadas de persistentes, embora a skill busque uso universal.
- `.codex/agents/masp-relator.toml`: papel `masp-relator` com modelo **declarado** `gpt-6.1-sol`, `medium`; instrui preservar limites, bloqueios e resultados negativos. Arquivo TOML não comprova execução do agente.
- `docs/masp/masp-routing.toml`: retorno da Conclusão **somente para Verificação ou Padronização**; `read-only`; skill `superpowers:finishing-a-development-branch` opcional, pertinente apenas a software.
- `src/masp_skill/case.py`: ledger **SIMULATED**, sem autenticação de identidade/aprovação. Estados `PENDING`, `IN_PROGRESS`, `PASS`, `FAIL`, `BLOCKED`, `NOT_RUN`; seis IDs do Gate 08: `complete_ledger`, `results`, `limitations`, `residual_risks`, `pending_items`, `audit_opinion`. `ALLOWED_TRANSITIONS` existente não será alterado.
- `src/masp_skill/evidence.py` documenta hash de arquivos existentes com classificações `STATIC`, `SIMULATED`, `RUNTIME` e `NOT_RUN`. Hash comprova consistência de conteúdo, não veracidade, causalidade, autoria ou aprovação.
- `.agents/skills/masp/SKILL.md` resume conclusão em uma linha, com orquestração e limites de evidência definidos globalmente.
- `AGENTS.md` na raiz da `main` não foi encontrado via GitHub; não inventar regras locais ausentes. Verificar workspace Codex ao implementar.
- **Dependências reais:** M01–04 têm evoluções funcionais universais. PR #11 do M05 foi mesclado **apenas com desenho e plano**; `05-acao.md` ainda usa contrato anterior. PR #12 do M06 foi mesclado **apenas com desenho e plano**; `06-verificacao.md` permanece na versão anterior. PR #13 do M07 está **aberto em rascunho** e ainda não consta na `main`. Não declarar integração funcional M05–07 ou ciclo completo já validado.

| Aspecto auditado | Lacuna | Impacto | Medida proposta |
| --- | --- | --- | --- |
| Consolidação | relatório final centrado em software e promoção | pouca utilidade em outros domínios | síntese universal das 8 fases e dois formatos proporcionais |
| Gates | seis campos sem parecer universal detalhado | falso PASS a partir de presença textual | requisitos com proveniência e restrições explícitas |
| Objetivos | antes/depois sem matriz de critério e incerteza | vitória artificial | status de atingimento e fonte por objetivo |
| Integridade | risco de confundir SHA com verdade factual | conclusão indevida | separar integridade, evidência e validade inferencial |
| Riscos | riscos residuais sem relação com responsáveis | acompanhamento indefinido | matriz e proprietário por função, sem inventar nome/prazo |
| Pendências | backlog genérico | encerramento sem destino das ações | rastrear bloqueadores, ações, responsável, critério |
| Decisão | encerramento técnico pode parecer implantação | risco operacional | separar parecer, gate, arquivamento, merge e produção |
| Especificidade | restrições OTServer globais | baixa generalidade | condicionais ao domínio e políticas competentes |

## 3. Alternativas avaliadas

**A — Apenas contrato/relatório Markdown:** entrega mínima, sem código e sem migração. Limitação: nenhuma inspeção determinística de referências e inconsistências em sidecars.

**B — Integrar aprovação automática e fechamento de ledger em `case.py`:** automatiza mais, mas aumenta risco de autoaprovação, falsos resultados, quebra de versões e confusão de representação. **Rejeitar.**

**C — contrato humano universal + matriz auditável + sidecar JSON/CLI opcional e estritamente `STATIC` (recomendado):** preserve os seis IDs e o motor. Usar ferramenta estrutural apenas quando TDD demonstrar valor. Nunca efetuar encerramento, autorizar produção ou atestar eficácia via CLI.

## 4. Modelo do histórico e matriz dos oito módulos

Fonte por item: `case_id`, identificador da fase, versão do artefato, evidência, estado, origem/classificação, limitação, autor/competência se confirmado, prazo e status de acompanhamento quando existir. Preservar lacunas e divergências.

| Fase | Entrada/entrega a consolidar | Risco de extrapolação |
| --- | --- | --- |
| M01 Identificação | problema, impacto, escopo, objetivo/critério | reescrever meta a posteriori |
| M02 Observação | baseline quantitativo/qualitativo/indisponível e fontes | comparar condições incompatíveis |
| M03 Análise | hipóteses, evidências a favor/contra, causa ou inconclusão | tratar hipótese como causa comprovada |
| M04 Plano | alternativas, 5W2H, risco, rollback/contingência, aprovação | aceitar `approved` declarado como autorização |
| M05 Ação | mudança **realmente realizada** e resultados imediatos | equiparar teste de software a intervenção operacional |
| M06 Verificação | comparação com baseline, regressões, independência e alcance | transformar `NOT_RUN` em PASS/eficácia |
| M07 Padronização | controle preventivo, proprietário, gatilho e regressão | confundir plano de padrão com implantação |
| M08 Conclusão | riscos/pendências, lições, auditoria e decisão adequada | encerrar como resolução sem provas |

**Gate 08 não é recursivo:** `complete_ledger` confere histórico anterior e material exigido nesta fase, sem exigir um PASS do próprio Gate 08 antes de emitir parecer. Ainda assim, não preencher artificialmente gaps de outras fases para fechar o ciclo.

## 5. Comparação de objetivos e eficácia

Por critério aprovado anteriormente: condição inicial, meta e versão, método, indicador quantitativo ou condição qualitativa, dados observados (com fonte), comparabilidade, incerteza, status do objetivo e limites. Categorias técnicas (não estados do ledger): `achieved`, `partially_achieved`, `not_achieved`, `inconclusive`, `not_evaluated`.

Distinguir oito situações: planejado, aprovado, executado, funcionando, resultado observado, eficácia demonstrada no escopo, padrão aplicado, sustentabilidade comprovada **somente no horizonte efetivamente observado**. Não utilizar cálculo percentual com denominador inválido, nem relação temporal como causa comprovada.

Preservar `FAIL`, `BLOCKED`, `NOT_RUN`, regressões, fontes conflitantes, hipóteses refutadas, objetivos não atingidos e resultados negativos, sem retocá-los para parecer favorável.

## 6. Riscos residuais, pendências e retrospectiva

**Riscos residuais:** ID, fenômeno, fonte/evidência, consequência, controles restantes, condição de monitoramento, pessoa/função responsável quando formalmente definida, estado e lacunas. Separar risco eliminado demonstrado de risco apenas reduzido/monitorado/não avaliado; não inventar severidade/probabilidade.

**Pendências:** ID, origem, relevância, critério impeditivo ou transferível, responsável por função, passo seguinte autorizado, dependências, prazo real ou `pending`, condição de encerramento, referência e posição no fluxo. Pendências críticas não são automaticamente transferidas como solução.

**Lições aprendidas:** observação, evidência, interpretação restrita, recomendação, reutilização possível, alcance/limites. Nunca confundir sugestão com conhecimento validado. Reconhecimento de equipes apenas quando pertinente e atribuição sustentada por evidências.

## 7. Parecer, encerramento e estados

**Natureza do resultado** (classificação técnica): resolução demonstrada, parcial, inconclusiva, desfavorável; **encerramento administrativo com ressalvas** é decisão separada por autoridade competente. Mesmo com arquivamento administrativo válido, gates incompletos **não** passam.

- `PASS` no Gate 08: seis requisitos de documentação realmente satisfatórios, evidência suficiente para o parecer do escopo, decisões e pendências corretamente descritas. **Não** prova automaticamente resolução, eficácia ou autorização para produção.
- `FAIL`: verificação realizada de requisito obrigatório não atendido, com achado e fonte.
- `BLOCKED`: falta de evidências, competência, integridade ou autorização indispensáveis; não produzir PASS documental.
- `NOT_RUN`: auditoria/encerramento não executado. `PENDING`/`IN_PROGRESS` permanecem estados já existentes, não novas categorias.

Rótulos de relatório propostos: `closure_type` `technical`/`administrative_with_reservations` e `resolution_status` `demonstrated`/`partial`/`inconclusive`/`unfavorable`; isto é **proposta de ficha**, não novo schema do caso.

**Retornos declarados da Conclusão:** Verificação e Padronização. Se houver necessidade de análise, retornar por caminho permitido e registrar coordenação; não inserir novo retorno direto sem revisão/autorização separada.

## 8. Entregáveis propostos e controle de segurança

**Relatório humano (fonte canônica)** com duas granularidades: resumo executivo sintético e relatório técnico de auditoria. Campos: identificação, versão, contexto, objetivo, escopo, metodologia, matriz das 8 fases, causa/inconclusão, ações reais, before/after, eficácia e regressões, estado da Padronização, limitações, riscos, pendências/donos, lições, parecer e decisão de encerramento referenciada. Não incluir dados sensíveis em repositório público.

**Sidecar JSON opcional após aprovação/TDD:** `src/masp_skill/conclusion.py` com `validate_conclusion_record(record: Any) -> list[str]` e CLI `validate-conclusion --record FILE --root WORKSPACE`. Verificar somente estrutura e consistência de IDs/estados/links do relatório; o próprio registro não autentica aprovações, evidência externa, relação causal ou poderes institucionais. Não alterar `case.py`, ledger, permissões, gates ou autoexecutar comandos.

**Permissões:** relator `read-only`; produzir novo documento versionado com conector de edição do repositório pela equipe autorizada não concede escrita/execução a agentes do MASP em casos operacionais. Sem merge, deploy, VPS, máquina/serviço real, alterações em protocolos ou dados privados.

**Política crítica:** `high_risk_requires_astra=true` no roteamento da base auditada. Esta proposta não invoca Astra nem remove obrigação: um caso real de alto risco sem auditoria exigida é `BLOCKED`. Não substituir modelo sem aprovação competente.

**Skills:** `superpowers:finishing-a-development-branch` opcional apenas em casos de desenvolvimento de software. `verification-before-completion` e `writing-plans` são referenciais de implementação, não evidência de execução de agentes Codex.

## 9. Escopo de modificações **após aprovação**

**Arquivos novos esperados:**
- `docs/masp/conclusao/ESPECIFICACAO-V2.md`
- `docs/masp/conclusao/REFERENCIAS-METODOLOGICAS.md`
- `docs/masp/conclusao/MODELO-RELATORIO-FINAL.md`
- `docs/masp/conclusao/MATRIZ-RASTREABILIDADE.md`
- `docs/masp/conclusao/MATRIZ-RISCOS-PENDENCIAS.md`
- `docs/masp/conclusao/LICOES-APRENDIDAS.md`
- `docs/masp/conclusao/CRITERIOS-ENCERRAMENTO.md`
- `docs/masp/conclusao/RELATORIO-TESTES-V2.md`

**Arquivos a alterar minimamente:** `docs/masp/agentes/08-conclusao.md`, `.codex/agents/masp-relator.toml`, apenas o bloco M08 em `docs/masp/masp-routing.toml`, item M08 em `.agents/skills/masp/SKILL.md`, ficha M08 em `docs/masp/modelos/CASO-MASP.md`, seção M08 de `README.md`. Não alterar modelo/effort sem justificativa e autorização separada.

**Código opcional:** `src/masp_skill/conclusion.py`, `src/masp_skill/cli.py`, `tests/test_conclusion_v2.py` e `tests/fixtures/conclusao-v2/casos.json`, se aprovados. Corpus projetado de **9 domínios + 32 situações adversariais, todos sintéticos**; não são 41 auditorias humanas ou 41 execuções do LLM.

## 10. Testes e critérios de aceitação **futuros**

TDD RED antes de funcionalidade, GREEN e refactor. Conjunto mínimo: ledger incompleto ou bloqueado, evento/hash inconsistente, `SIMULATED` como `RUNTIME`, evidência sem origem, objetivo apagado, revisão independente não realizada, baseline/resultado incompatíveis, risco/pendência omitidos, conclusão contraditória ao ledger, decisão administrativa tratada como resolução, sustentabilidade sem acompanhamento, caso de alto risco sem auditoria requerida, retorno inexistente e tipo JSON inválido. Preservar material negativo.

Comandos previstos após aprovação:
```powershell
python -m pytest -q
python -m masp_skill.cli validate-routing --routing docs/masp/masp-routing.toml --classification STATIC
python -m masp_skill.cli validate-case --case tests/fixtures/cases/valid-case.json --root .
```
Conferir CI Ubuntu e Windows, saídas/códigos e SHA final, não apenas badge. `STATIC` denota validação documental/estrutura; `SIMULATED` casos fictícios; `RUNTIME` comandos observados sob escopo explícito; `NOT_RUN` ausência de ação.

**Sem `spawn_agent` nesta sessão Chat:** delegação ao `masp-relator`, `masp-testador` real e avaliação comportamental Codex **NOT_RUN**. Validação de caso simulado não valida identidade, autorização, operação ou resultado real.

## 11. Referências metodológicas e condição de parada

Referências para futura consulta/verificação (princípios adaptados, sem reprodução integral):
- [ASQ 8D, etapa D8](https://asq.org/quality-resources/eight-disciplines-8d): fechamento e reconhecimento pertinente;
- [IHI PDSA](https://www.ihi.org/library/tools/plan-do-study-act-pdsa-worksheet): aprendizagem e decisões baseadas na observação;
- [CDC — Program Evaluation Framework](https://www.cdc.gov/evaluation/php/evaluation-framework/index.html): comunicação de resultados e limitações;
- [NIST/SEMATECH Statistics Handbook](https://www.itl.nist.gov/div898/handbook/): limitações dos indicadores/medição;
- [MASP_Skill](https://github.com/Marciorochar/MASP_Skill): contratos e histórico em análise.

**Parada:** esta branch pode conter somente desenho e plano de implementação para revisão. **Nenhuma alteração funcional, teste RED, gate, TOML, ledger, merge ou execução de intervenção até aprovação explícita do desenho.** A decisão de implementar seguirá a especificação do usuário e o processo competente.
