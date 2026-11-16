# Auditoria e correções do PR #1

**Base auditada:** `origin/main` em `0a53205` (merge do PR #1).  
**Branch de correção:** `fix/masp-pr1-review-findings`.  
**Escopo:** comentários automáticos ainda não resolvidos do PR #1 e requisitos adicionais da solicitação de auditoria.  
**Resultado local:** `rtk pytest -q` — 82 passed no Windows; validações da matriz e do fixture passaram como `STATIC`.

## Parecer

As correções locais cobrem os três comentários pendentes: disponibilidade de modelo no histórico, exceções causadas por evidências malformadas e testes acoplados ao cache Superpowers do computador original. A matriz continua com oito fases e dez papéis. O smoke registrado não prova descoberta, carregamento da skill nem delegação real; o multi-agent runtime remains BLOCKED até obter eventos estruturados suficientes.

O sistema não autentica rótulos de ator, aprovação ou modelo efetivo. SHA-256 detecta divergência de conteúdo, mas não prova autoria nem impede que alguém com acesso reescreva e recalcule todo o ledger.

## Requisitos e estado

| Requisito | Estado | Evidência ou pendência |
|---|---|---|
| Disponibilidade histórica separada da disponibilidade atual | PASS — testes locais | Snapshots de modelo/disponibilidade são registrados nos eventos; a consulta atual é separada para novas decisões. Regressões cobrem indisponibilidade posterior, inclusive Astra. |
| Evidência malformada retorna erros sem exceções não controladas | PASS — testes locais | Validadores protegem tipos/caminhos; gates não consomem evidência inválida. Cobertura inclui objetos nulos e metadados Astra inválidos no replay. |
| `PASS` rejeita testes malsucedidos | PASS — testes locais | Verificação exige execuções relevantes com código zero; falhas mistas continuam bloqueando `PASS`, mesmo com outra execução ou parecer Astra bem-sucedido. |
| Testes portáveis sem caminhos absolutos do autor | PASS — teste local | Descoberta Superpowers usa configuração/caches disponíveis e marca dependências externas ausentes como skip. |
| Hashes de conteúdo das evidências | PASS — testes locais | Novas evidências registram SHA-256; validação recalcula o hash e rejeita divergência ou formato inválido. Ledger legado com eventos schema 1 requer migração explícita. |
| Configuração de agentes aplicada nos pontos de decisão | PASS — testes locais | `new-case`, `transition` e `validate-case` validam matriz, `.codex/config.toml` e contratos dos agentes; ausência da configuração local ou papel malformado retorna erro sem traceback. |
| Política de concorrência aplicada | PASS — validação local | `--parallel-tasks` valida caminhos/propriedade e aplica o menor limite configurado/efetivo. O smoke usa `max_threads` configurado; não há prova de execução paralela real no runtime. |
| `runtime-smoke --strict` falha com `FAIL`/`BLOCKED` | PASS — teste local | CLI retorna código não zero se qualquer verificação terminar em `FAIL` ou `BLOCKED`; não foi executada inferência nova apenas para repetir essa prova. |
| GitHub Actions Windows e Linux | PASS — configuração; NOT_RUN — remoto | `.github/workflows/ci.yml` define `windows-latest` e `ubuntu-latest`, instala pacote e dependências, executa Pytest e validações estáticas. O workflow ainda precisa ser executado no GitHub após abrir o PR. |
| Skill descoberta em `.agents/skills/masp/` | PASS — estático; BLOCKED — runtime | O arquivo existe no diretório reconhecido pelo Codex; o smoke disponível não emitiu evento estruturado de carregamento. A existência do arquivo não prova descoberta efetiva. |
| Modelos/esforços configurados compatíveis com catálogo | PASS — estático/runtime parcial | Configuração local e matriz passam a validação cruzada. O catálogo do smoke verificou nove papéis; o especialista crítico Astra não apareceu no objeto de verificação por papel. Nenhum modelo/esforço efetivo de subagente foi comprovado. |
| Descoberta dos dez agentes e delegação independente | BLOCKED | O JSONL capturado não contém eventos estruturados correlacionados de spawn, identidade do agente e conclusão. Alegações textuais do assistente não são aceitas como evidência. |
| Validação Linux local | NOT_RUN | Ambiente disponível nesta execução é Windows; a matriz CI inclui Linux, mas o workflow remoto ainda não rodou. |
| Migração de casos schema 1 com eventos | BLOCKED até migração explícita | Casos schema 1 sem eventos podem ser promovidos a schema 2 na primeira transição. Ledgers schema 1 não contêm snapshots/hash novos requeridos e são rejeitados com instrução para migrar/recriar eventos com evidência original. |

## Testes e comandos executados

- Baseline na branch atual antes das correções: `rtk pytest -q` — 57 passaram.
- Suite após integração final local: `rtk pytest -q` — **82 passaram**.
- `python -m masp_skill.cli validate-routing --routing docs/masp/masp-routing.toml --classification STATIC` (com `PYTHONPATH=src`) — oito fases, dez papéis, zero erros.
- `python -m masp_skill.cli validate-case --case tests/fixtures/cases/valid-case.json --routing docs/masp/masp-routing.toml --root .` — fixture e ledger válidos (`STATIC`).
- `rtk git diff --check origin/main...HEAD` — sem erros de whitespace.
- Testes específicos exercitam `runtime-smoke --strict` com resultado `BLOCKED`; não foi feita nova inferência Codex para evitar custo duplicado.

Os resultados são locais ao Windows. A configuração GitHub Actions Linux/Windows ainda não foi executada remotamente. `STATIC`, `SIMULATED` e `RUNTIME` mantêm significados distintos; Pytest local não é classificado como evidência de execução MASP.

## Arquivos alterados

- `.github/workflows/ci.yml` — CI Ubuntu e Windows.
- `.agents/skills/masp/SKILL.md` — localização de skill no projeto reconhecível pelo Codex.
- `src/masp_skill/case.py`, `evidence.py`, `routing.py`, `cli.py` — snapshots históricos, validação segura, hashes, gates e políticas aplicadas nos comandos.
- `tests/test_skill_contract.py`, `test_case_transitions.py`, `test_routing.py`, `tests/runtime/test_codex_smoke.py` — portabilidade e regressões.
- `docs/masp/modelos/CASO-MASP.md` — schema v2, snapshots e limites de integridade.
- `docs/masp/RELATORIO-AUDITORIA-PR1.md` — este parecer.

## Riscos e pendências

1. Carregamento real de `.agents/skills/masp/` e descoberta/delegação dos agentes permanecem `BLOCKED`; exige evento estruturado emitido pelo Codex.
2. O workflow Linux/Windows precisa executar após a publicação do novo PR; no momento, somente testes Windows locais foram executados.
3. Ledgers antigos schema 1 com eventos precisam de migração explícita; a CLI não os eleva silenciosamente ao schema 2.
4. SHA-256 protege contra alteração acidental detectável, mas não é assinatura/autenticação.
5. A validação do paralelismo aplica limites e conflitos declarados antes da transição; não demonstra paralelismo efetivamente executado em runtime.

## Parecer final

**PASS** para correções locais verificadas por testes no Windows, critérios de gate, validação de evidências, portabilidade do teste de skill e configuração de CI. **BLOCKED** para integração multiagente operacional, carregamento/runtime da skill e modelos/esforços efetivos de subagentes, pois a captura não contém provas estruturadas. **NOT_RUN** para execução local Linux e execução remota do GitHub Actions. A merge deve aguardar os resultados do novo PR e a evidência runtime que falta; esta branch não altera `main` diretamente.
