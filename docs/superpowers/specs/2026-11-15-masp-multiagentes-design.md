# MASP Multiagentes — Desenho Arquitetural

## Intenção

Transformar o pacote documental MASP_Skill em uma configuração local, rastreável e testável para coordenar casos MASP com oito etapas obrigatórias, agentes especializados e roteamento explícito de modelos. A solução deve usar os recursos realmente disponíveis no Codex instalado, reutilizar Superpowers e permanecer integralmente dentro deste repositório.

## Objetivos

- Preservar Identificação, Observação, Análise, Plano de ação, Ação, Verificação, Padronização e Conclusão, nessa ordem.
- Criar um coordenador SOL que controle gates, delegação, custo, contexto, evidências e retornos de fase.
- Definir os oito papéis MASP e um especialista crítico transversal com modelos e esforços reais.
- Impedir avanço sem evidência, autoaprovação do executor e delegação por subagentes.
- Registrar decisões, comandos, resultados, limitações, bloqueios e auditorias.
- Validar separadamente configuração estática, descoberta no runtime e comportamento observado.

## Não objetivos

- Alterar `C:\Users\marci\.codex\config.toml` ou agentes globais.
- Publicar, fazer push, abrir PR ou mesclar alterações.
- Modificar OTServer ou qualquer projeto externo.
- Instalar versões concorrentes de Superpowers, ECC, Graphify ou outras skills.
- Tratar simulação ou inspeção estática como integração funcional.

## Antiobjetivos

- Inventar identificadores de modelo, skills, ferramentas ou resultados.
- Substituir silenciosamente um modelo indisponível.
- Permitir que uma falha simples de teste acione Astra automaticamente.
- Paralelizar tarefas dependentes ou permitir dois escritores no mesmo arquivo.
- Declarar `PASS` sem evidência verificável.

## Ambiente observado

- Codex CLI: `0.169.0-alpha.11.1`.
- Modelos-alvo presentes no catálogo de runtime: `gpt-6.1-sol`, `gpt-6-luna`, `gpt-6.1-terra` e `gpt-6-astra`.
- Esforços necessários aceitos: `low`, `medium` e `high`.
- O valor solicitado `llow` não é aceito e será corrigido explicitamente para `low`.
- Agentes globais estão habilitados, com limite observado de três threads concorrentes; não serão modificados.
- Superpowers 7.0.1 contém todas as skills solicitadas.
- ECC 2.2.3 e Graphify estão instalados e serão auxiliares opcionais.
- REA não foi identificada e permanecerá registrada como indisponível até que nome ou caminho sejam fornecidos.
- O repositório inicial contém somente Markdown e não possui testes nem configuração executável.

## Alternativas consideradas

### A. Agentes globais

Criar papéis em `~/.codex/agents` e editar o `config.toml` global facilitaria o uso fora do repositório, mas violaria o limite de implantação e poderia colidir com papéis existentes. Rejeitada.

### B. Configuração local ao repositório

Manter `.codex/config.toml`, camadas em `.codex/agents/`, roteamento declarativo, skill MASP e testes dentro do repositório. É versionável, auditável e preserva o ambiente global. Escolhida.

### C. Roteamento somente por prompts

Passar modelo e esforço em cada delegação, sem papéis locais persistentes. É compatível como fallback, porém mais sujeito a divergência e mais difícil de validar. Será usado apenas se o CLI atual não descobrir a configuração local; o fallback deverá ser explícito e testado.

## Componentes

### Configuração local Codex

`.codex/config.toml` registra os papéis locais e aponta cada um para um arquivo TOML dedicado. Cada camada declara instruções, modelo e esforço, sem alterar configurações globais.

### Papéis

| Papel | Modelo | Esforço padrão | Responsabilidade |
|---|---|---:|---|
| `masp-coordenador` | `gpt-6.1-sol` | medium | Controlar caso, gates, delegação, custo, contexto e consolidação |
| `masp-identificador` | `gpt-6-luna` | low | Delimitar problema, impacto, escopo e métrica |
| `masp-observador` | `gpt-6-luna` | medium | Coletar baseline, reprodução e evidências |
| `masp-analista` | `gpt-6.1-sol` | medium | Avaliar hipóteses e estabelecer causa raiz |
| `masp-planejador` | `gpt-6.1-sol` | medium | Produzir plano, riscos, rollback e critérios de teste |
| `masp-executor` | `gpt-6.1-terra` | medium | Implementar somente mudanças aprovadas e delimitadas |
| `masp-testador` | `gpt-6-luna` | low | Verificar mudanças independentemente do executor |
| `masp-padronizador` | `gpt-6.1-terra` | medium | Criar controles, regressões e documentação reutilizável |
| `masp-relator` | `gpt-6.1-sol` | medium | Consolidar resultados, limitações e pendências |
| `masp-especialista-critico` | `gpt-6-astra` | medium | Auditar problemas críticos sem implementar correções |

O coordenador pode elevar seu próprio esforço a `high` para decisões arquiteturais complexas. Astra pode usar `high` somente quando a justificativa de escalonamento também justificar esforço adicional.

### Matriz declarativa

`docs/masp/masp-routing.toml` será a fonte de verdade legível por máquina para:

- ordem e identificador das fases;
- papel, modelo e esforço;
- skills necessárias e opcionais;
- ferramentas e modos de acesso permitidos;
- entradas, saídas e critérios do gate;
- retornos permitidos;
- condições de Astra;
- política de modelo indisponível;
- paralelismo e auditoria.

O formato TOML é nativo tanto para a configuração Codex quanto para o `tomllib` do Python 3.14 observado, evitando dependência externa apenas para interpretar a matriz. Um schema local em Python validará sua forma e valores fechados.

### Motor de validação

Um validador local em Python 3.14, sem dependências de runtime externas, carregará TOML, verificará invariantes e avaliará transições. A interface de linha de comando deverá distinguir:

- validação estática;
- simulação de cenário;
- smoke test real do Codex;
- evidência não executada.

O formato concreto da implementação será escolhido a partir das ferramentas já presentes no ambiente e documentado no plano; nenhuma validação será chamada de runtime se apenas analisar arquivos.

Toda transição persistida deverá passar pelo comando central de transição. Edições manuais do ledger poderão ser detectadas pela validação, mas não constituirão uma transição autorizada. As instruções dos agentes reforçam a política; o validador é o controle técnico que a aplica.

### Registro de caso

Cada caso terá manifesto e ledger com:

- identificador do caso;
- fase e estado atuais;
- histórico de transições;
- responsável e modelo observado;
- referências de evidência;
- comandos e resultados;
- decisões e justificativas;
- bloqueios e limitações;
- acionamentos de Astra;
- pareceres de teste e auditoria.

Os estados válidos são `PENDING`, `IN_PROGRESS`, `PASS`, `FAIL`, `BLOCKED` e `NOT_RUN`.

## Fluxo e gates

O caminho normal é:

`Identificação → Observação → Análise → Plano de ação → Ação → Verificação → Padronização → Conclusão`.

Regras:

1. Somente o coordenador inicia uma fase ou delega uma tarefa.
2. Subagentes não criam subagentes.
3. Uma fase só entra em `PASS` quando as evidências exigidas forem referenciadas e validadas.
4. `FAIL` retorna à fase responsável indicada pela matriz.
5. `BLOCKED` impede avanço até resolução ou decisão explícita.
6. `NOT_RUN` nunca satisfaz gate.
7. Ação depende de plano aprovado.
8. O executor não aprova a própria ação.
9. Verificação é independente; alto risco exige auditoria independente adicional.
10. Conclusão consolida o caso, mas publicação e promoção permanecem decisões externas.

### Autoridade de aprovação

- O usuário aprova o plano de ação antes da Ação, qualquer substituição de modelo e a resolução de `BLOCKED` que mude escopo, risco, custo, modelo ou critério de aceitação.
- O coordenador pode resolver autonomamente bloqueios operacionais dentro do plano já aprovado, desde que registre a evidência e não amplie autoridade.
- O coordenador valida gates técnicos com base nos critérios declarados e nas evidências independentes; essa validação não substitui as aprovações humanas acima.

### Critérios mínimos por fase

| Fase | Evidência mínima para `PASS` |
|---|---|
| Identificação | problema observável, impacto, escopo, exclusões e métrica de sucesso |
| Observação | baseline, ambiente, método de coleta, resultado reproduzível ou limitação documentada |
| Análise | hipóteses avaliadas, evidências a favor/contra e causa raiz sustentada ou conclusão inconclusiva explícita |
| Plano de ação | tarefas, responsáveis, arquivos/escopo, riscos, rollback e testes; aprovação humana registrada |
| Ação | mudanças delimitadas, diff/artefatos, comandos executados e ausência de autoaprovação |
| Verificação | comparação com baseline, testes reais identificados, regressões pertinentes e parecer independente |
| Padronização | controle preventivo, proprietário, condição de acionamento e teste/regressão correspondente |
| Conclusão | ledger completo, resultados, limitações, riscos residuais, pendências e parecer de auditoria |

## Skills por fase

| Fase | Necessárias ou preferenciais |
|---|---|
| Identificação | `brainstorming` |
| Observação | `systematic-debugging`; Graphify/repo-scan quando pertinentes |
| Análise | `systematic-debugging` |
| Plano | `writing-plans` |
| Ação | `using-git-worktrees`, `test-driven-development`; `subagent-driven-development` sob coordenação |
| Verificação | `verification-before-completion`, `requesting-code-review` |
| Padronização | `writing-skills` somente quando houver conhecimento reutilizável |
| Conclusão | `finishing-a-development-branch` somente com pré-requisitos atendidos |

`dispatching-parallel-agents` pertence ao coordenador. Ela não substitui `subagent-driven-development`: a primeira decide fan-out independente; a segunda governa execução de um plano por agentes.

## Escalonamento crítico

Astra pode ser acionado por concorrência/deadlock, segurança, engenharia reversa complexa, decisão arquitetural crítica, evidências graves e contraditórias, alteração de alto risco ou problema persistente após diagnóstico sistemático.

Cada acionamento exige `astra_reason`, evidências relacionadas e decisão do coordenador. Primeira falha de teste, tarefa documental comum ou implementação delimitada sem alto risco não justificam Astra.

Alto risco significa pelo menos um dos seguintes: impacto em segurança ou credenciais; perda/corrupção de dados; indisponibilidade relevante; mudança irreversível ou de rollback não demonstrado; concorrência; alteração arquitetural transversal; ou efeito externo de alto impacto. Nesses casos, Astra é o auditor independente obrigatório. Se Astra estiver indisponível, o gate fica `BLOCKED`; outro modelo só poderá substituí-lo após aprovação humana explícita e registro de que não há equivalência presumida.

## Modelos indisponíveis

Falha de catálogo ou inicialização produz `BLOCKED`, com identificador solicitado e erro real. Nenhuma alternativa é automática. O sistema poderá sugerir `gpt-6-sol`/`gpt-5.6-sol`, `gpt-5.6-terra` ou `gpt-5.6-luna`, mas a substituição exige aprovação. Astra não será silenciosamente representado por outro modelo.

## Paralelismo

O limite inicial é três agentes concorrentes, sempre reduzido ao menor limite efetivo do ambiente. Só há paralelismo quando as tarefas são independentes, possuem propriedade de escrita exclusiva e não permitem avanço antecipado do gate.

## Estratégia de validação

1. Testes de schema e configuração para modelos, esforços, papéis, skills, ordem e gates.
2. Testes de transição para caminho feliz, retorno, bloqueio e ausência de evidência.
3. Testes da política Astra e de indisponibilidade de modelo.
4. Testes de paralelismo e propriedade exclusiva.
5. Smoke tests reais de descoberta, modelo/esforço, delegação e skills no CLI atual.
6. Auditoria independente do diff e das evidências.

Resultados serão classificados como `STATIC`, `SIMULATED` ou `RUNTIME`, evitando equivalência indevida.

## Riscos e decisões deixadas à implementação

- A descoberta de `.codex/config.toml` e dos agentes locais deve ser provada no CLI atual; falha ativa o fallback C como proposta, não como substituição silenciosa.
- O validador deve evitar dependência de rede e escolher a tecnologia já suportada no host.
- REA fica fora do caminho crítico até ser identificada.
- Graphify e ECC são opcionais e nunca condição para iniciar um caso comum.
- O conteúdo existente será preservado e reconciliado, não substituído indiscriminadamente.

