# MASP Skill: fluxo MASP local para Codex

Este repositório reúne uma matriz de roteamento, contratos para dez papéis, uma skill local e uma CLI Python para validar a configuração e registrar transições simuladas de casos MASP. A validação local não comprova que Codex carregou a skill ou descobriu os agentes. O smoke registrado em [`docs/masp/evidencias/codex-smoke.md`](docs/masp/evidencias/codex-smoke.md) confirma o catálogo consultado, mas deixa carregamento da skill e descoberta dos agentes como `BLOCKED`.

## Começar um caso

No diretório raiz deste repositório, valide a matriz e crie um manifesto em local novo dentro do workspace:

Prepare o pacote antes do primeiro comando da CLI:

```powershell
python -m pip install -e .
```

```powershell
python -m masp_skill.cli validate-routing --routing docs/masp/masp-routing.toml --classification STATIC
python -m masp_skill.cli new-case --id MASP-002 --output .tmp/MASP-002.json --root .
python -m masp_skill.cli validate-case --case .tmp/MASP-002.json --root .
python -m masp_skill.cli case-revision --case .tmp/MASP-002.json
```

`new-case` recusa sobrescrever arquivo existente. O manifesto é `SIMULATED`: rótulos de ator, modelo, aprovação e papel não são autenticados. Guarde evidências em arquivos dentro do mesmo workspace. Uma transição requer um JSON de evidências e a revisão SHA-256 atual; veja a sintaxe completa com `python -m masp_skill.cli transition --help`. Não use uma transição simulada como prova de execução operacional.

## Classificações e estados

- `STATIC`: inspeção de arquivos/configuração ou validação estrutural pela CLI.
- `SIMULATED`: exercício do motor de caso, transições e gates com rótulos fornecidos pelo chamador.
- `RUNTIME`: comando ou comportamento executado no runtime, com comando, saída e código de saída registrados. `RUNTIME` sozinho não quer dizer sucesso: cada verificação também tem estado.
- `BLOCKED`: havia uma verificação pretendida, mas uma condição impediu sua conclusão. `NOT_RUN`: a verificação não foi executada.

Os estados do caso são `PENDING`, `IN_PROGRESS`, `PASS`, `FAIL`, `BLOCKED` e `NOT_RUN`. Somente o coordenador solicita transições; aprovação humana e identidade de modelo continuam sendo rótulos, não assinaturas verificadas.

## Estrutura

- [`docs/masp/masp-routing.toml`](docs/masp/masp-routing.toml): oito fases, dez papéis e políticas transversais.
- [`.codex/`](.codex/): registro de configuração local e dez contratos de agentes.
- [`.agents/skills/masp/SKILL.md`](.agents/skills/masp/SKILL.md): instruções da skill local.
- [`src/masp_skill/`](src/masp_skill/): validação, ledger, evidências e CLI.
- [`docs/masp/RELATORIO-IMPLEMENTACAO.md`](docs/masp/RELATORIO-IMPLEMENTACAO.md): inventário, decisões, testes, riscos e limites observados.
- [`docs/masp/exemplos/MASP-CONFIG-SMOKE.md`](docs/masp/exemplos/MASP-CONFIG-SMOKE.md): leitura guiada da evidência atual do smoke.

## Testes

Instale o extra de desenvolvimento (`python -m pip install -e ".[test]"`) e rode `python -m pytest -q`. Isso testa código Python local; não reproduz descoberta de agentes nem carregamento da skill no Codex. O smoke runtime é separado e pode ser solicitado por `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_codex_smoke.ps1`; ele executa sondagens reais do CLI e produz evidência sob `docs/masp/evidencias/`.

O piloto [`MASP-001`](docs/masp/exemplos/MASP-001-falha-gcc-c.md) é ilustrativo. Este repositório não reproduz a falha do OTServer, não altera seu código e não autoriza execução no servidor, banco ou binários.


## PR #3 — Validação de robustez e smoke mínimo

A skill descoberta pelo Codex tem fonte canônica em `.agents/skills/masp/SKILL.md`; `skills/masp/SKILL.md` é apenas um ponteiro de compatibilidade. Os testes adversariais verificam rejeição controlada de entradas JSON/TOML malformadas e o piloto de oito fases é um caso **SIMULATED** sem agentes reais.

O smoke runtime é **opcional e manual**: por padrão tenta apenas um subagente em sandbox `read-only`, evitando sondar os oito papéis sem necessidade. Para uma execução autorizada, com o Codex instalado, use:

```powershell
python -m masp_skill.cli runtime-smoke --root . --output-dir docs/masp/evidencias --strict
```

`--all-roles` amplia explicitamente a tentativa a todos os papéis e pode consumir muitos tokens. `--strict` retorna código diferente de zero quando existem checagens `FAIL` ou `BLOCKED`. Papéis não sondados são `NOT_RUN`; descoberta completa continua `BLOCKED`. O GitHub Actions não chama esse smoke e não executa inferência paga. Relatórios históricos de smoke não comprovam funcionamento das novas configurações.
