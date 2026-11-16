# MASP_Skill — investigação e solução de problemas com evidências

**Um fluxo estruturado de melhoria e resolução de problemas técnicos, preparado para uso com o Codex.**

O **MASP_Skill** ajuda a transformar um problema mal definido — como uma falha de compilação, um teste que começou a falhar ou um defeito recorrente — em um processo rastreável: **descrever o problema → coletar evidências → analisar causas → planejar uma correção → executar com aprovação → verificar → prevenir recorrência → concluir**.

O projeto aplica as **oito etapas do MASP (Método de Análise e Solução de Problemas)**. Combina uma **skill local para Codex**, **contratos de dez papéis especializados** e uma **CLI Python** para validar configurações e registrar casos, decisões, evidências e critérios de passagem (*gates*).

> **Em resumo:** este repositório fornece o **método e os mecanismos de registro e validação**. Ele **não é um agente autônomo** que encontra e corrige erros sozinho. O motor de casos simulados está coberto por testes; a execução real dos subagentes no Codex ainda requer comprovação no ambiente em que será utilizada.

## Para que serve?

O MASP_Skill é útil quando não basta “pedir para a IA corrigir um erro” e é necessário demonstrar **o que aconteceu, por que aconteceu, o que mudou e se a solução funcionou**.

| Necessidade | Como o repositório ajuda |
| --- | --- |
| Investigar um erro sem tirar conclusões precipitadas | Orienta a coleta de baseline, logs, hipóteses e evidências |
| Planejar uma correção com controle | Exige escopo, responsáveis, riscos, rollback, testes e registro de aprovação antes da ação |
| Evitar que uma correção aparente seja considerada sucesso | Define gates e estados que distinguem `PASS`, `FAIL`, `BLOCKED` e `NOT_RUN` |
| Organizar trabalho especializado | Declara um coordenador, oito papéis ligados às fases e um especialista crítico |
| Documentar o histórico de um problema | Registra transições e referências a evidências em um *ledger* JSON com hashes SHA-256 |
| Repetir um processo de análise | Oferece matriz TOML, modelo de caso, CLI e testes de regressão |

**Público:** pessoas desenvolvedoras, equipes de qualidade, manutenção de software e responsáveis por investigações técnicas. O método pode ser adaptado a outros projetos; os caminhos e as configurações do Codex devem ser revistos em cada ambiente.

### Exemplo prático: uma compilação falha

Imagine que `g++ -c` encerre com código 1, mas o diagnóstico não tenha sido capturado.

1. **Identificação:** registrar o erro, o impacto e o resultado esperado.
2. **Observação:** coletar comando exato, ambiente, stdout, stderr e código de saída.
3. **Análise:** comparar hipóteses, sem atribuir a causa ao código antes de verificar.
4. **Plano de ação:** definir mudança mínima, riscos, rollback e critérios de teste.
5. **Ação:** executar apenas a mudança aprovada, em ambiente isolado.
6. **Verificação:** repetir o teste e comparar com a situação inicial.
7. **Padronização:** registrar uma verificação de regressão para evitar recorrência.
8. **Conclusão:** consolidar resultado, limitações e pendências.

Há um [exemplo documentado de falha de compilação](docs/masp/exemplos/MASP-001-falha-gcc-c.md). Ele é **ilustrativo e ainda depende de reprodução**; o repositório não executou essa compilação nem alterou um OTServer.

## Como funciona

O processo segue **oito fases em sequência**. Cada fase possui entradas, entregas e requisitos de evidência para avançar.

| Fase MASP | Entrega principal |
| --- | --- |
| 1. Identificação | Problema, impacto, escopo e métrica de sucesso |
| 2. Observação | Baseline, ambiente e coleta reproduzível |
| 3. Análise | Hipóteses avaliadas e causa sustentada ou inconclusão |
| 4. Plano de ação | Tarefas, riscos, rollback, testes e registro de aprovação humana |
| 5. Ação | Mudanças aprovadas, diff e comandos/resultados |
| 6. Verificação | Comparação com baseline, testes e revisão independente |
| 7. Padronização | Controle preventivo, responsável e regressão |
| 8. Conclusão | Histórico consolidado, resultados e riscos residuais |

A configuração declara **dez papéis**: um coordenador, oito especialistas das fases e um especialista crítico (Astra). A coordenação e os contratos estão documentados, mas **arquivos TOML não comprovam que o Codex criou ou executou esses agentes**. Gates e transições de caso são validados pela CLI; ações reais e autorizações dependem do ambiente e do processo de aprovação utilizado.

## Comece pelo motor local (sem delegação de agentes)

**Requisitos:** Python **3.11 ou superior** e Git. Execute os comandos a partir da raiz do repositório:

```powershell
git clone https://github.com/Marciorochar/MASP_Skill.git
cd MASP_Skill
python -m pip install -e ".[test]"
```

**1. Verifique a matriz** de fases, papéis e regras:

```powershell
python -m masp_skill.cli validate-routing --routing docs/masp/masp-routing.toml --classification STATIC
```

**2. Crie um caso de demonstração**, em um caminho novo dentro do workspace:

```powershell
python -m masp_skill.cli new-case --id MASP-DEMO --output .tmp/MASP-DEMO.json --root .
```

**3. Valide o registro e consulte a revisão SHA-256:**

```powershell
python -m masp_skill.cli validate-case --case .tmp/MASP-DEMO.json --root .
python -m masp_skill.cli case-revision --case .tmp/MASP-DEMO.json
```

O caso começa em `PENDING` (ou `BLOCKED` se a configuração declarar um modelo indisponível). Ele **não é concluído automaticamente**. Para registrar transições, prepare um JSON de evidências com arquivos dentro do workspace, obtenha a revisão atual e consulte:

```powershell
python -m masp_skill.cli transition --help
```

O comando `new-case` não sobrescreve arquivos existentes. As transições exigem evidências e verificação da revisão do manifesto para evitar atualizações sobre dados desatualizados. Os registros criados pela CLI são classificados como **`SIMULATED`**.

Para testar a implementação Python:

```powershell
python -m pytest -q
```

A [CI do GitHub Actions](.github/workflows/ci.yml) executa testes em Windows e Ubuntu, além da validação estrutural da matriz e do caso de referência. **Esses testes não executam inferência de agentes Codex.**

## Como utilizar com o Codex

A entrada principal da skill está em [`.agents/skills/masp/SKILL.md`](.agents/skills/masp/SKILL.md). A [matriz TOML](docs/masp/masp-routing.toml) declara o roteamento das fases e [`.codex/config.toml`](.codex/config.toml) aponta para os contratos de papéis.

Para experimentar a integração:

1. Abra o checkout do projeto no Codex e confirme que a skill `masp` é descoberta e que o ambiente suporta os agentes configurados.
2. Leia as instruções da skill e o [guia de integração](docs/masp/LEIA-ME.md). Se estiver adaptando o MASP a outro projeto, respeite o `AGENTS.md` já existente nesse projeto.
3. Comece com **um único papel não crítico**, em sandbox somente leitura, antes de considerar outras delegações.

O teste manual opcional é:

```powershell
python -m masp_skill.cli runtime-smoke --root . --output-dir .tmp/masp-runtime --strict
```

**Atenção:** esse comando pode invocar o Codex e consumir tokens. Execute somente em um ambiente autorizado. Por padrão, tenta no máximo **um subagente não crítico**; os demais permanecem `NOT_RUN`, incluindo o especialista Astra. O `--strict` retorna código diferente de zero quando há verificações `FAIL` ou `BLOCKED`. **Não use `--all-roles` no teste inicial.** Consulte o [procedimento de validação runtime](docs/masp/VALIDACAO-RUNTIME-PR4.md) antes de executar.

Os caminhos de skills externas na matriz incluem referências locais da instalação original; adapte-os às dependências realmente disponíveis em seu computador, sem presumir que os plugins estão instalados.

## O que significam os resultados?

| Classificação | Significado |
| --- | --- |
| `STATIC` | Inspeção e validação estrutural de arquivos/configurações |
| `SIMULATED` | Exercício do motor MASP, com eventos e identidades declarados pelo chamador |
| `RUNTIME` | Evidência de comando/comportamento executado, que ainda precisa ser verificada quanto ao resultado |

Os estados usados pelo motor são `PENDING`, `IN_PROGRESS`, `PASS`, `FAIL`, `BLOCKED` e `NOT_RUN`. **`PASS` exige o gate atendido; `BLOCKED` e `NOT_RUN` nunca significam sucesso.**

### Limites atuais

- O **motor Python e o fluxo MASP simulado** têm cobertura automatizada; o **carregamento real da skill, a delegação e o modelo/esforço efetivos dos agentes** ainda não foram comprovados em uma sessão runtime.
- Hashes de eventos e evidências ajudam a verificar **integridade de conteúdo**, mas não autenticam a identidade de pessoas, aprovações ou agentes.
- O controle de conflitos de escrita verifica **tarefas declaradas**; não substitui isolamento efetivo de permissões e sistema de arquivos.
- O repositório **não realiza automaticamente alterações de produção**, nem autoriza acesso a serviços, servidores ou bancos de dados.

## Onde encontrar cada parte

| Recurso | Finalidade |
| --- | --- |
| [`.agents/skills/masp/SKILL.md`](.agents/skills/masp/SKILL.md) | Instruções do método para Codex |
| [`docs/masp/masp-routing.toml`](docs/masp/masp-routing.toml) | Oito fases, papéis e políticas |
| [`.codex/`](.codex/) | Configuração e dez contratos de agentes |
| [`src/masp_skill/`](src/masp_skill/) | Motor de casos, validações, evidências e CLI Python |
| [`docs/masp/modelos/CASO-MASP.md`](docs/masp/modelos/CASO-MASP.md) | Modelo de documentação de um problema |
| [`docs/masp/LEIA-ME.md`](docs/masp/LEIA-ME.md) | Orientações de adaptação e uso com Codex/Superpowers |
| [`docs/masp/VALIDACAO-RUNTIME-PR4.md`](docs/masp/VALIDACAO-RUNTIME-PR4.md) | Procedimento seguro para verificar um agente |
| [`docs/masp/RELATORIO-AUDITORIA-PR4.md`](docs/masp/RELATORIO-AUDITORIA-PR4.md) | Correções, testes e bloqueios conhecidos |

Relatórios anteriores dos PRs #1–#3 permanecem em `docs/masp/` como **histórico de implementação**, não como comprovação atual de execução dos agentes.

---

**Finalidade do projeto:** dar **método, rastreabilidade e critérios de verificação** à investigação de problemas técnicos. A automação por agentes é uma camada adicional que só deve ser considerada operacional quando houver evidência real da execução.
