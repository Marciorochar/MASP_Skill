# Desenho técnico — MASP Módulo 07: Padronização Universal v2

**Data:** 2026-11-16  
**Situação:** PROPOSTA PARA REVISÃO — implementação funcional condicionada à aprovação explícita do desenho  
**Branch:** `feat/masp-padronizacao-universal-v2`  
**Base auditada:** `main` `c6ca23226f61bd74f400f181aa1da27f9103ec9a`

## 1. Objetivo e fronteira

Evoluir somente o Módulo 07 para transformar **resultados suficientemente verificados** em controles de prevenção de recorrência proporcionais ao risco, com proprietário, gatilho, verificação de regressão, gestão de versões, responsabilidades, treinamento quando necessário, monitoramento e plano de reação.

O objetivo é servir a problemas **industriais, logísticos, de saúde, administrativos, ambientais, educacionais, de serviços, tecnológicos e cotidianos**, sem impor a todos uma skill de IA, código, POP, FMEA ou carta de controle.

**Princípio:** documentar um padrão não comprova que ele foi autorizado, implantado, seguido ou eficaz ao longo do tempo. O Módulo 07 deve registrar esses estados separadamente. Não introduzir operações reais ou ações automatizadas em processos externos ao repositório.

## 2. Diagnóstico verificável da versão atual

- `docs/masp/agentes/07-padronizacao.md`: missão de evitar recorrência, saídas de testes, instruções e controles. Gate descrito como padrão versionado e testado. Restrições OTServer presentes como **persistentes**, embora se pretenda uso universal.
- `.codex/agents/masp-padronizador.toml`: modelo **declarado** `gpt-6.1-terra`, esforço `medium`, sem prova de execução. Instrução breve para controle, proprietário, gatilho e regressão.
- `docs/masp/masp-routing.toml`: papel `masp-padronizador`; ferramentas `filesystem`, `version_control`, `test_runner`; acessos `read-only`, `write-approved`, `execute-approved`; retorno **somente à Verificação**.
- `src/masp_skill/case.py`: gate 07 com os quatro IDs **`preventive_control`, `owner`, `trigger`, `regression`**. O motor é `SIMULATED`; não autentica identidade, assinatura, aprovação, implantação ou sustentabilidade.
- `.agents/skills/masp/SKILL.md`: etapa 07 descrita em uma linha. O restante da orquestração distingue `STATIC`, `SIMULATED`, `RUNTIME` e `NOT_RUN`.
- `docs/masp/modelos/CASO-MASP.md`: ficha geral e ledger; faltam modelo de padrão, reação, responsabilidade e monitoramento universal.
- **Dependências:** PR #11 (M05) foi mesclado somente com desenho e plano; `docs/masp/agentes/05-acao.md` ainda tem contrato anterior. PR #12 (M06) está **aberto em rascunho**, com desenho e plano, e `docs/masp/agentes/06-verificacao.md` na `main` permanece na versão anterior. Não afirmar integração funcional M05→M06→M07.
- `AGENTS.md` na raiz não foi encontrado pela busca de arquivo; caso a árvore de trabalho contenha instruções locais, respeitá-las.

| Critério | Lacuna existente | Consequência potencial | Tratamento no M07 v2 |
| --- | --- | --- | --- |
| Pré-requisito | `Verificação aprovada` sem prova de eficácia real | Padronizar solução sem validação | Handoff documentado, evidência e escopo; `BLOCKED` se essencial faltar |
| Documentação | Não diferencia proposta/implantação | Falso resultado operacional | Ciclo de vida documental separado do ledger |
| Controle | Tipos de controles não diferenciados | Plano genérico e reativo | Preventivo/detectivo/mitigador/monitoramento, com evidência |
| Responsáveis | Sem mapa de manutenção/revisão | Padrão sem dono | Proprietário e funções de aplicação, revisão e reação |
| Gatilhos | Sem reação operacional explícita | Regressão detectada sem resposta | Gatilho, forma de detecção, autoridade, reação e stop |
| Monitoramento | Teste de regressão sem horizonte | Sustentabilidade alegada prematuramente | Indicadores, fonte, período, acompanhamento realizado/pendente |
| Segurança | OTServer tratado como restrição permanente | Exclui outros domínios | Restrições condicionais, competências e autorizações por contexto |

## 3. Alternativas de arquitetura

| Alternativa | Benefício | Limite/risco |
| --- | --- | --- |
| **A. Contratos e modelos Markdown** | Menor mudança, sem código | Não detecta automaticamente IDs cruzados ou estados contraditórios |
| **B. Alterar `case.py`/schema/gates para aprovar padrão automaticamente** | Maior centralização | Migrações, regressões, risco grave de falsas aprovações e confusão entre fatos e rótulos |
| **C. Contrato humano + modelos de padrão/controle + sidecar JSON opcional de validação STATIC (recomendada)** | Continuidade com módulos 01–04, integridade estrutural sem alterar ledger | Não autentica aplicação, competência ou durabilidade; exige avaliação externa |

**Escolha proposta:** C, com especificação e fichas humanas como referência principal. Implementar JSON/CLI somente se testes justificarem utilidade sem ampliar capacidade de execução. A alternativa A continua válida se não houver necessidade de sidecar; B não recomendada.

## 4. Política de entrada: resultados da Verificação

Exigir, conforme criticidade, registro do problema M01, baseline M02, causa/limitações M03, contramedidas M04, execução M05, parecer de eficácia e regressões M06, aprovação aplicável e riscos residuais.

Distinguir:
- **Eficácia demonstrada no escopo:** permite propor adoção proporcional, sem afirmar sustentabilidade futura.
- **Eficácia parcialmente demonstrada:** considerar padrão provisório **somente** se processo competente autorizar, com restrições, revisão e sem alegação de eficácia plena.
- **M06 inconclusivo, FAIL, NOT_RUN ou ausente:** não consolidar solução definitiva como eficaz; registrar `BLOCKED` quando requisito essencial.
- **Gate 06 PASS simulado:** não autentica eficácia real, revisão independente ou autorização de padronização operacional.
- **M05/M06 sem implementação funcional:** padrões/fixtures podem ser elaborados para testes da skill, mas **não** suportam alegações de padronização operacional.

## 5. Seleção e desenho do padrão

Escolher o menor conjunto de controles **adequado e sustentável** ao mecanismo demonstrado, incluindo efeitos sistêmicos em processos relacionados apenas quando evidências/autorizações permitirem.

**Estrutura proposta de padrão humano:**
- `standard_id`, `standard_version`, descrição, problema/objetivo, `verification_reference`, `effectiveness_evidence`, condição de validade e limitações;
- `applicability` e `exclusions` explícitos, responsável `owner` e funções de aplicar/monitorar/revisar/aprovar;
- `preventive_control` (tipo, procedimento, causa/risco, prova esperada, controles/limitações);
- `trigger` com evento verificável, método de detecção, responsável, severidade sem números inventados, `reaction_plan`, critérios de parada;
- `regression` com indicador/teste, baseline/fonte, frequência condicionada, aceitação/falha, monitoramento e evidências;
- competência/treinamento proporcional, riscos residuais, critérios de revisão, retirada e responsabilidades;
- controle documental e aprovação institucional externa quando exigida.

**Tipos de controles:**
- `preventive`: reduz possibilidade de recorrência;
- `detective`: identifica desvio;
- `mitigating`: reduz efeito de desvio;
- `monitoring`: acompanha manutenção de resultados.

São categorias de controle, **não** estados MASP. Preferir linguagem do domínio quando adequada; não exigir método quantitativo para avaliação qualitativa.

## 6. Governança, gatilhos e monitoramento

**Proprietário:** papel identificado com responsabilidade de manter padrão. Outros papéis: executor, monitor, revisor, aprovador e responsável pela reação. Segregação quando exigida por risco/autoridade; não inventar nomes ou designar agente como aprovador humano.

**Gatilho de resposta:** evento verificável, fonte, método de detecção, responsável, comunicação, ação inicial segura e limites de autorização; reação que requeira mudança não prevista deve retornar ao processo competente, **não** executar automaticamente.

**Monitoramento:** nome do indicador, definição/unidade ou critério qualitativo, fonte, baseline/limitação, método, janela de coleta, cadência fundamentada, limiar predefinido (ou pendente), responsável e verificação de regressão. Não inventar metas, limites de controle, datas ou tendências.

**Treinamento:** separar exigência/planejamento, material disponível, treinamento realizado, presença verificada, competência observada e aplicação no trabalho. Campo preenchido não prova formação.

**Ciclo documental** proposto `DRAFT`, `UNDER_REVIEW`, `APPROVED`, `ACTIVE`, `SUSPENDED`, `OBSOLETE` — **distinto** de `PENDING`, `IN_PROGRESS`, `PASS`, `FAIL`, `BLOCKED`, `NOT_RUN` do ledger. `APPROVED` textual não autentica aprovação; `ACTIVE` não significa que implantação e aderência foram verificadas. Exigir versionamento e preservação de históricos, revisão e critérios de obsolescência.

## 7. Gate 07 e passagem à Conclusão

Preservar **exatamente** `preventive_control`, `owner`, `trigger`, `regression`. Os requisitos ampliados nas fichas são **recomendações**, não novas chaves obrigatórias do ledger.

- `PASS`: com evidências pertinentes de verificação, controle preventivo bem definido, proprietário/autoridade, gatilho verificável, teste/monitoramento de regressão, limites e documentação necessária. Declarar exatamente se o produto é um **padrão preparado e revisado**, **aprovado**, **implantado** ou **em acompanhamento**; PASS da elaboração não prova os estados subsequentes.
- `FAIL`: requisito efetivamente avaliado e não atendido, com registro de divergência.
- `BLOCKED`: eficácia/independência necessária não comprovada, aprovação indispensável ausente, risco/competência insuficiente, dono não definido ou condição de adoção insegura.
- `NOT_RUN`: avaliação ou atividade não executada. Não classificar como sucesso.

**Retorno existente:** Padronização → **Verificação**. Não propor transição direta para outras fases sem mudança separada e aprovada no roteamento. Conclusão recebe riscos residuais, status documental real, pendências, evidências e limites; não inventa sustentabilidade.

## 8. Sidecar opcional, interfaces e segurança

Se aprovado e justificado por TDD, propor `src/masp_skill/standardization.py` com `validate_standardization_record(record: Any) -> list[str]` e CLI `validate-standardization --record PATH --root ROOT`. A CLI apenas valida **estrutura declarada** e referências (IDs, owners, fontes, status, vínculo de regressão, versão, revisão e autorização textual). Não lê dados fora do workspace e não executa controles, treinamento, auditoria, configurações, notificações ou operações em máquinas/ambientes.

A existência de `APPROVED`, `ACTIVE` ou `effectiveness_evidence` no JSON **não autentica aprovação, implantação nem eficácia**. O sidecar não concede Gate 07 PASS.

**Segurança:** não criar/alterar POP de segurança, protocolo clínico, controle ambiental, configuração industrial, VPS, sistemas de produção ou dados privados por iniciativa do agente; especialistas autorizados e processos institucionais decidem. Restrição OTServer apenas se caso OTServer. Em emergência, usar procedimentos competentes, não a skill para testar perigo.

## 9. Escopo de arquivos após aprovação

**Documentação nova proposta:**
- `docs/masp/padronizacao/ESPECIFICACAO-V2.md`
- `docs/masp/padronizacao/REFERENCIAS-METODOLOGICAS.md`
- `docs/masp/padronizacao/MODELO-PADRAO.md`
- `docs/masp/padronizacao/PLANO-CONTROLE.md`
- `docs/masp/padronizacao/MATRIZ-GATILHOS-REGRESSOES.md`
- `docs/masp/padronizacao/CONTROLE-DOCUMENTAL.md`
- `docs/masp/padronizacao/RELATORIO-TESTES-V2.md`

**Ajustes controlados:** `docs/masp/agentes/07-padronizacao.md`, `.codex/agents/masp-padronizador.toml`, bloco Padronização em `docs/masp/masp-routing.toml`, item M07 em `.agents/skills/masp/SKILL.md`, ficha M07 em `docs/masp/modelos/CASO-MASP.md`, referência do README. Não alterar modelo/effort, `src/masp_skill/case.py`, ledger ou contratos de outros módulos.

**Python opcional** somente após aprovação/TDD: `src/masp_skill/standardization.py`, `src/masp_skill/cli.py`, `tests/test_standardization_v2.py`. Fixtures: `tests/fixtures/padronizacao-v2/casos.json` com **9 domínios + 30 cenários adversariais sintéticos**. Corpus não equivale a 39 respostas de agentes.

## 10. Critérios de aceitação e verificação

Após aprovação, RED antes de implementação. Casos: fonte de verificação inexistente ou SIMULATED apresentada como eficácia real, padrão sem dono, gatilho não mensurável/observável, regressão sem teste, responsabilidade conflitante, limite inventado, treino planejado tratado como realizado, obsolescência ignorada, alteração sem versão, plano de reação fora da autorização, evidência sobrescrita, e sustentabilidade alegada sem monitoramento.

Comandos futuros:
```powershell
python -m pytest -q
python -m masp_skill.cli validate-routing --routing docs/masp/masp-routing.toml --classification STATIC
python -m masp_skill.cli validate-case --case tests/fixtures/cases/valid-case.json --root .
```
Confirmar saída e CI Ubuntu/Windows para o SHA final, não apenas badge de sucesso. Separar `STATIC` (contratos), `SIMULATED` (fixtures), `RUNTIME` (comandos realmente executados) e `NOT_RUN` (ausência de execução). Só comparar comportamento real dos agentes em runtime Codex com telemetria. Nesta sessão **não foi disponibilizada ferramenta `spawn_agent`**, portanto delegação e revisão independente multiagente permanecem `NOT_RUN`.

**Referências metodológicas:** [ASQ 8D — D7](https://asq.org/quality-resources/eight-disciplines-8d), [Minitab 8D — D7](https://support.minitab.com/en-us/engage/help-and-how-to/tools/forms/types-of-forms/process-improvement/8d-methodology/), [IHI PDSA](https://www.ihi.org/library/tools/plan-do-study-act-pdsa-worksheet), [ISO 9001](https://www.iso.org/iso-9001-quality-management.html) e [ISO 31000](https://www.iso.org/iso-31000-risk-management.html). São princípios adaptados com redação autoral; verificar licenças para eventual reprodução de material.

## 11. Aprovação e parada

**Este documento não autoriza implementação funcional.** Até aprovação explícita do desenho: somente proposta, plano de trabalho, checagem do diff e PR em rascunho. Nada de mudança direta na `main`, merge, emissão de aprovação de padrão, intervenção real, execução de Astra ou desligamento de políticas de risco.
