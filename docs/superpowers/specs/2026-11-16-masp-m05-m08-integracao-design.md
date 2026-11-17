# Desenho integrado — MASP Universal v2, Módulos 05–08

**Estado:** proposta para aprovação humana, **não autoriza implementação**  
**Data:** 2026-11-16  
**Base auditada:** `main` @ `7e530d5bc3acf876f2d1cc0a34520ccd61fdba47`  
**Abordagem escolhida pelo usuário:** **A — quatro PRs funcionais sequenciais**, cada um revisado antes de integrar o próximo.

## 1. Intenção e resultado esperado

Completar os módulos universais de Ação, Verificação, Padronização e Conclusão sem reescrever os módulos 01–04, o modelo de oito fases nem o ledger. Cada módulo deverá produzir um artefato humano auditável, um registro opcional validável estaticamente e testes de domínio/limites. O ciclo de software deve ficar coberto por TDD e CI; comportamento efetivo de agentes Codex e resultados no mundo real devem ser comprovados separadamente.

**Critério transversal:** ação executada ≠ resultado eficaz ≠ padrão adotado ≠ conclusão administrativa. Nenhum módulo pode promover uma declaração SIMULATED/STATIC a eficácia RUNTIME ou a aprovação humana.

O sucesso deste projeto de desenvolvimento significa **contratos implementados, testes do software e integração simulada validados**, não que um sistema multiagente autônomo tenha sido validado em processos reais.

## 2. Abordagens consideradas

- **A — quatro PRs sequenciais (selecionada):** riscos delimitados, testes dedicados e revisão incremental, com dependências claras. Custo: quatro ciclos de CI/revisão.
- **B — PR único integrado:** evita quatro merges, mas mistura interfaces, eleva custo de isolamento de regressões e aumenta superfície de conflito. Não selecionada.
- **C — refazer o motor universal primeiro:** muda `case.py` e o ledger prematuramente. Não selecionada; só uma exceção extremamente limitada do Gate 06 poderá ser proposta à parte.
  
Os documentos de desenho e planos individuais dos Módulos 05–08 já existem na `main` e serão reutilizados, reconciliados com a auditoria atual e complementados pelo contrato integrado. Os PRs #11–#14 são **desenhos mesclados**, não implementações funcionais M05–08.

## 3. Componentes preservados

- Skill canônica: `.agents/skills/masp/SKILL.md`; `skills/masp/SKILL.md` é ponteiro de compatibilidade.
- Agentes: `.codex/agents/masp-executor.toml`, `masp-testador.toml`, `masp-padronizador.toml` e `masp-relator.toml`.
- Rotas: `docs/masp/masp-routing.toml`, oito fases e dez papéis, com limite de três agentes, coordenador único delegador e nenhum fallback automático de modelo.
- Motor: `src/masp_skill/case.py`, `src/masp_skill/evidence.py` e `src/masp_skill/cli.py`. Ledger e transições são **SIMULATED**, classificações de evidência declaradas por quem as envia; hash é integridade, não identidade ou veracidade.
- Estados do ledger: `PENDING`, `IN_PROGRESS`, `PASS`, `FAIL`, `BLOCKED`, `NOT_RUN`. Os rótulos de avaliação de eficácia ou ciclo documental são **categorias separadas**, nunca novos estados MASP.
- Módulos 01–04 permanecem como estão, exceto referências documentais estritamente necessárias. Não exigir que os sidecars existentes desses módulos sejam migrados.
- Alta criticidade mantém `high_risk_requires_astra=true`; se auditoria exigida estiver indisponível, `BLOCKED`. Não chamar Astra em sondagem inicial de baixa criticidade nem burlar a política.

## 4. Contrato de dados transversal proposto (sem migração de ledger)

A ficha Markdown é o documento interpretável por humanos. Para cada fase 05–08, um sidecar JSON **opcional** de diagnóstico estrutural, mantido fora do ledger e versionado, permite verificações determinísticas.

Campos comuns propostos para os sidecars da fase:
- `schema_version: "masp-phase-v2"` (versão **do sidecar**, sem mudar `case.schema_version=2`);
- `case_id` e `phase_id` (um dos IDs existentes);
- `record_id` e `record_revision` (referência imutável/versionada, quando aplicável);
- `input_references`: IDs do plano, baseline, evidências e/ou fase anterior, com versão conhecida;
- `assessment_status`: avaliação do **registro**, não estado do ledger, com valores descritos na especificação específica;
- `evidence_references`: fonte/caminho interno, data quando conhecida, método e classe declarada;
- `limitations` e `pending_items`: não omitir lacunas reais;
- `handoff`: destino e requisitos pendentes, sem criar novas rotas.

**Regra de compatibilidade:** os validadores `validate-*` somente verificam forma, coerência referencial e restrições documentais; não autenticam assinaturas, observações de campo, execução de agentes, causalidade ou decisão de gate. Não escrever `PASS` no manifesto por efeito de uma validação estrutural.

**Regra de provenance:** referências sem caminho/fonte não demonstram fato; `STATIC` = contrato/arquivo inspecionado; `SIMULATED` = caso fictício ou ledger simulado; `RUNTIME` = execução realmente observada, dentro do alcance documentado; `NOT_RUN` = avaliação não realizada. A palavra `RUNTIME` num JSON isolado continua sendo uma declaração não autenticada.

Os campos exatos dos sidecars serão congelados no plano de implementação de cada PR, **sem adicionar exigências ao schema de ledger**.

## 5. Módulo 05 — Ação Universal v2

**Entrada contratual:** M01 escopo/critério, M02 baseline e fontes, M03 causa/limitações, M04 plano 5W2H, versão aprovada, responsabilidade, restrições, risco, critério de testes, rollback/contingência e **autorização real verificada fora do sidecar**.

**Processo:** comparar plano versus condição real, verificar isolamento e limites de autoridade, avaliar pontos de parada, executar somente ação aprovada quando o domínio/ambiente autorizarem (esta implementação v2 por si só **não** executará intervenções externas). Para cada atividade registrar proposto/realizado/não realizado, responsável por função, data real ou ausente, contexto, resultado, evidência, desvio, contingência, risco emergente e rollback efetivamente realizado ou `NOT_RUN`.

**Saída para M06:** `action_record` + `plan_reference` + `baseline_reference` + matriz ação planejada/realizada + `before_after_changes` + resultados imediatos + testes/inspeções ocorridos + riscos e pendências + fontes. Em software, `diff` e comandos Git são válidos; em processo físico/administrativo, `diff` será representação estruturada de mudança de procedimento/condição e `commands` será transcrição fiel de passos executados ou **não aplicável fundamentado** no sidecar, sem inventar shell.

**Gate 05 — preservar exatamente:** `changes`, `diff`, `commands`, `results`, `no_self_approval`.

**Critérios de aceite do PR 05:**
- M05 aceita execução documentada de baixo risco em software **e** atividade não digital sem exigir Git.
- Rejeita sidecar com aprovação declarada mas não comprovada como requisito para ação real; não cria atuação automática.
- Rejeita `NOT_RUN` com resultados fabricados, divergência da versão do plano, atividade fora de escopo, rollback fictício de operação irreversível, autoaprovação e instrução perigosa.
- Mantém toda suíte anterior verde e cria RED→GREEN dos testes M05 com 9 domínios e 24 casos adversariais **sintéticos**.
- Entrega arquivo `src/masp_skill/action_execution.py` com `validate_action_execution_record(record: Any) -> list[str]` e comando `validate-action-execution`, se aprovado; documentação universal e sem mudança de `case.py`.
- Define handoff estável para M06 e registro das limitações.

## 6. Módulo 06 — Verificação Universal v2

**Entrada contratual:** M05 efetivamente executado, `action_record` e evidências, baseline do M02, metas e critérios congelados dos M01/M04, fontes, períodos, metodologia, riscos e registros de alteração.

**Processo:** comparar condições equivalentes em unidade, população, período, método e contexto; aceitar baseline quantitativo, qualitativo ou indisponível justificado; testar critérios observáveis; registrar evidências favoráveis/contrárias, regressões e efeitos indesejados; distinguir ação conforme, funcionamento, resultado, eficácia, sustentabilidade no horizonte de coleta e inconclusão; buscar revisão independente adequada. Não atribuir causalidade por mera sequência temporal. Se `before=0`, não calcular variação percentual; não inventar amostra, p-valores ou limites de controle.

**Saída para M07:** `verification_record` + `action_reference` + matriz baseline/depois, critérios e resultados + `effectiveness_assessment` qualificada + regressões/riscos + fontes + limitações + `independent_review` com proveniência conhecida. Parecer próprio do executor não satisfaz independência.

**Gate 06 — preservar exatamente:** `baseline_comparison`, `runtime_tests`, `relevant_regressions`, `independent_review`.

**Incompatibilidade material auditada:** `src/masp_skill/case.py::_gate_errors` exige atualmente `RUNTIME` contendo pelo menos um `command` com `exit_code=0` e `stdout`/`stderr` não vazio, excluindo apenas parecer Astra. Isso **não representa adequadamente** inspeção documental, medição física, auditoria qualitativa ou avaliação não digital. Simular um comando para conseguir `PASS` é proibido.

**Decisão proposta a aprovar separadamente dentro do PR 06:**
1. Preservar 4 IDs, ledger, estados, proteção de Astra e exigência de resultados verificáveis.
2. Permitir **alternativamente** um registro tipado de procedimento observacional executado com fonte, método, condições, resultados e qualificação/revisor, ao lado do caminho atual de comando verificável.
3. Preservar testes de regressão: comandos com saída não zero não podem ser mascarados por outra evidência favorável; `NOT_RUN` não permite PASS.
4. O sidecar e a transição do ledger continuam **SIMULATED/declared**, sem autenticar execução ou indivíduo. O ajuste melhora expressividade do gate, não garante veracidade.
5. Se o usuário não aprovar alterar pontualmente `case.py` neste PR, implementar apenas o validador v2 e a documentação, rotulando o gate de ciclo completo não digital **BLOCKED/pendente**. Não declarar universalidade integrada plena.

**Critérios de aceite do PR 06:**
- M06 distingue baseline incomparável, não disponível e evidência válida; não emite eficácia fictícia nem PASS por teste `NOT_RUN`.
- Calcula diferença absoluta e percentual somente quando apropriado, e explicita direção da métrica e limitações.
- Regressão crítica e revisão pelo próprio executor impedem parecer de aprovação indevida.
- Validador `src/masp_skill/verification.py`, `validate-verification` somente STATIC; 9 domínios + 30 casos adversariais sintéticos, RED→GREEN, testes do gate de compatibilidade se a exceção for aprovada.
- Mantém regressões existentes e handoff estável à M07.

## 7. Módulo 07 — Padronização Universal v2

**Entrada contratual:** `verification_record` e seu escopo demonstrado, resultados, riscos, indicadores, limites, revisão competente, identificação da causa/controle e responsável por função.

**Processo:** selecionar a menor padronização que preserve a melhoria demonstrada; controle preventivo/detectivo/mitigador/monitoramento, procedimento ou checklist proporcional; proprietário, gatilho observável, reação segura e autoridade, indicador de regressão, revisão documental, necessidade de treinamento e acompanhamento. Não inventar metas/datas nem declarar treinamento executado a partir do planejamento.

**Saída para M08:** `standardization_record` com `verification_reference`, controle, `owner`, `trigger`, `regression`, status do documento (`DRAFT/UNDER_REVIEW/APPROVED/ACTIVE/SUSPENDED/OBSOLETE` separado de estado MASP), autorização real quando aplicável, monitoramento e pendências. `ACTIVE` declarado não comprova implantação real nem sustentabilidade.

**Gate 07 — preservar exatamente:** `preventive_control`, `owner`, `trigger`, `regression`.

**Critérios de aceite do PR 07:**
- Não apresenta uma melhoria inconclusiva como padrão operacional eficaz.
- Detecta padrão sem dono, gatilho não observável, regressão sem verificação, versão obsoleta, treinamento planejado descrito como realizado, risco residual ignorado, reação fora de autoridade.
- Modelos simples e complexos sem impor POP a toda situação.
- Validador `src/masp_skill/standardization.py`, `validate-standardization` somente STATIC; 9 domínios + 30 adversariais sintéticos, RED→GREEN, CI, handoff para M08.
- Não cria novas transições: retorno válido M07 → M06.

## 8. Módulo 08 — Conclusão Universal v2

**Entrada contratual:** referência ao caso e ledger íntegro, objetivos originais M01, baseline M02, avaliação causal M03, plano M04, execução M05, verificação M06 e padronização M07; fontes, riscos residuais, pendências e decisões institucionais efetivamente verificadas.

**Processo:** consolidar a cadeia de evidências das oito fases sem substituir os registros anteriores; avaliar cada objetivo como atingido/parcial/não atingido/inconclusivo/não avaliado, preservar resultados negativos, riscos, pendências e responsáveis; sintetizar lições com fontes; redigir parecer proporcional às evidências; separar **resolução técnica** e **encerramento administrativo**.

**Saída:** `conclusion_record` + relatório técnico + resumo executivo + matriz oito fases + riscos e pendências + `audit_opinion` e limites + `resolution_status` (demonstrado/parcial/inconclusivo/desfavorável) separado de `closure_type` (técnico/administrativo com ressalvas, quando autorizado).

**Gate 08 — preservar exatamente:** `complete_ledger`, `results`, `limitations`, `residual_risks`, `pending_items`, `audit_opinion`.

**Limitação do ledger atual:** `case.py` exige PASS de todas as fases anteriores para PASS da Conclusão. Um encerramento administrativo de caso parcial ou desfavorável pode ser **descrito** num relatório, mas não transforma a sequência em PASS. O motor também considera `BLOCKED` terminal no fluxo simulado; não oferecer desbloqueio automático. Essas limitações não serão contornadas; mudança futura de ciclo de vida seria proposta separada.

**Critérios de aceite do PR 08:**
- Não omite objetivos fracassados, evidências contraditórias, riscos residuais e pendências impeditivas.
- Não aceita fechamento pleno com ledger inconsistente, gate pendente, `SIMULATED` promovido a fato ou falso parecer independente.
- Não interpreta SHA válido como verdade factual, nem arquivamento como solução, nem documento como autorização para produção.
- Validador `src/masp_skill/conclusion.py`, `validate-conclusion` somente STATIC; 9 domínios + 32 adversariais sintéticos, RED→GREEN, suíte integral, relatório e resumo.
- Retornos válidos M08 → M06 ou M07; outros retornos dependerão de mudança separada.

## 9. Mapa de handoff e invariantes entre fases

| Transição | Contrato mínimo | Rejeitar quando |
| --- | --- | --- |
| M04 → M05 | plano/versionamento + autorização real + riscos/testes + escopo | só houver `approved` textual ou plano incompleto |
| M05 → M06 | atividades realmente realizadas + referências + desvios + resultados imediatos + baseline | ação não realizada ser apresentada como executada |
| M06 → M07 | critérios congelados, comparação, avaliação de eficácia, regressões, parecer independente | baseline incomparável ou revisão não feita ser apresentado como eficaz |
| M07 → M08 | controle, dono, gatilho, regressão, situação documental real e riscos | padrão planejado ser apresentado como implantado |
| M08 → arquivo decisório | relatório, parecer, objetivos, riscos e pendências | encerramento administrativo ser chamado de problema resolvido |

**Sem acoplamento circular:** sidecar M05 usa registros e arquivos M01–04 existentes, não exige schema novo nas quatro fases. Cada PR pode verificar sua saída antes do próximo; o handoff entre módulos fica congelado na revisão daquele PR. A saída M08 permanece uma narrativa auditável, e não comando de execução.

## 10. Entregas, branches e revisão

Quatro PRs **funcionais** em série, cada um criado de `main` atualizada **depois** do merge do anterior (não implementar paralelamente sobre bases que divergem):

1. `feat/masp-acao-v2-implementation` → `src/masp_skill/action_execution.py`, CLI, testes, modelos/contratos M05.
2. `feat/masp-verificacao-v2-implementation` → `verification.py`, CLI, testes, modelos/contratos M06; decisão específica sobre `case.py`.
3. `feat/masp-padronizacao-v2-implementation` → `standardization.py`, CLI, testes, modelos/contratos M07.
4. `feat/masp-conclusao-v2-implementation` → `conclusion.py`, CLI, testes, modelos/contratos M08.

Evitar modificar `case.py` fora da exceção explícita de compatibilidade para Gate 06. Manter arquivos pequenos e independentes, `cli.py` como despachante, sem dependências externas novas se desnecessário. Não alterar modelos/effort no TOML sem justificativa.

Cada PR: plano técnico correspondente revisado, teste RED observado antes do código, GREEN e regressões, inspeção de diff, documentação atualizada, CI Ubuntu/Windows e revisão humana. Sem merge automático.

## 11. Aceitação integrada e experimento posterior

**Critérios técnicos mínimos da integração dos quatro PRs:**
1. Os 8 IDs de fase, 10 papéis, estados, chaves de gate e regras de segurança permanecem consistentes.
2. `validate-routing` e `validate-case` passam no SHA final; `python -m pytest -q` não apresenta falhas, com contagem/skip relatados sem inventar números futuros.
3. Uma fixture **SIMULATED** percorre as oito fases sem saltos nem falsificar identidade. Não interpretar `RUNTIME` declarado em fixture como execução real.
4. As quatro CLIs de sidecar são read-only, apresentam `STATIC` e código de saída coerente; rejeitam entradas malformadas, referências inválidas, tipos inesperados e caminhos fora do workspace.
5. O caso sintético de **melhoria de registro de ordens de serviço** (baixo risco) preserva baseline, escopo, autorização fictícia declarada, ação simulada, avaliação verificada apenas no escopo fictício, controle, gatilho, conclusão e pendências com referências coerentes.
6. Casos negativos devem produzir bloqueio/limitação corretos: `NOT_RUN`, autorização ausente, intervenção irreversível, revisão do próprio executor, baseline incomparável, regressão significativa, risco residual omitido, adoção não comprovada e conclusão precoce.
7. Cada PR contém revisão de segurança, CI Windows/Ubuntu e nenhuma quebra dos módulos 01–04.
8. A **delegação real Codex** é uma validação separada e posterior: confirmar descoberta da skill, ferramenta real, `spawn_agent` com evento de criação/conclusão correlacionado, papel/modelo/effort efetivamente observáveis quando telemetria permitir, política de no-spawn em filhos, isolamento, revisão independente. Se indisponível, `NOT_RUN/BLOCKED`, nunca declarar multiagentes operacionais.
9. Casos reais industriais, clínicos, ambientais e de produção continuam fora do escopo de implementação/teste até autorização e competência pertinentes. Não usar avaliação sintética como certificação de segurança em campo.

**Critério de parada:** uma fase cujo contrato falhe não avança. Cada PR permanece isolado até aprovação e testes. O ciclo universal v2 só será rotulado **implementado no escopo Python/documental** após os quatro PRs aprovados e integrados; não o chamar "autônomo e validado em campo" sem provas adicionais.

## 12. Riscos e questões que exigem decisão

- **Conflito de Gate 06 com universalidade:** aceitar uma modificação estreita e testada de `case.py::_gate_errors` que permita procedimento observacional realmente documentado **sem enfraquecer** os controles atuais para comandos de software. Sem essa aprovação, não afirmar Gate 06 apto a concluir casos não digitais no motor.
- **Autenticação:** o projeto ainda não possui sistema real de verificação de identidade/assinatura. Não desenvolver um sistema de aprovação/autenticação nesta etapa. Exigir processos externos competentes e registrar a limitação.
- **Runtime Codex:** execução de subagentes depende do ambiente do usuário; ferramentas de GitHub/Chat nesta sessão não incluem `spawn_agent` Codex. Uma avaliação simulada de parser não comprova agentes.
- **Fluxo de casos não resolvidos:** Gate 08 permanece dependente de todos os gates anteriores PASS; arquivamento administrativo com ressalvas será relatório fora do PASS do ledger. Alterar ciclo de vida seria outro design.
- **Configurações de plugins:** rotas contêm caminhos Windows locais de skills de instalação original. Validar descoberta real no ambiente, sem assumir caminho válido em qualquer máquina.

## 13. Condição de aprovação

**Neste momento, somente desenho.** Não iniciar implementações, testes RED, criação de CLIs ou alteração de gates até aprovação do presente documento, inclusive da exceção indicada para Gate 06. Após aprovação, usar `superpowers:writing-plans` para revisar os quatro planos individuais contra este contrato, então implementar o PR 05 primeiro.
