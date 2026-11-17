# Validação integrada — MASP Universal v2, M05–M08

**Alcance:** ciclo sintético e verificação estrutural. Não autentica identidade, aprovação humana, autoria de evidência, execução real, eficácia em campo ou delegação Codex.

## Integração

Os PRs intermediários #17–#19 haviam sido mesclados entre branches, não na `main`. Corrigimos a integração em sequência pelos PRs [#20 (M06)](https://github.com/Marciorochar/MASP_Skill/pull/20), [#21 (M07)](https://github.com/Marciorochar/MASP_Skill/pull/21) e [#22 (M08)](https://github.com/Marciorochar/MASP_Skill/pull/22), com CI aprovada nos dois sistemas antes de cada merge.

## Interface de verificação

`masp_skill.universal_cycle.validate_universal_cycle(bundle, case=None)` confere os quatro sidecars e a consistência entre IDs de caso, ação, baseline, revisor, Verificação, Padronização, objetivos e conclusão. Caso um manifesto seja passado, compara os sete estados anteriores declarados com os eventos encontrados no ledger; não faz replay criptográfico nem prova observação real.

Exemplo de CLI para JSONs **previamente criados** no workspace:

```powershell
python -m masp_skill.cli validate-universal-cycle --root . `
  --action .tmp/acao.json `
  --verification .tmp/verificacao.json `
  --standardization .tmp/padronizacao.json `
  --conclusion .tmp/conclusao.json `
  --case .tmp/MASP-DEMO.json
```

Esses caminhos são exemplos e não arquivos incluídos automaticamente no projeto. O argumento `--case` é opcional. A CLI não modifica arquivos ou serviços. **Verifique também o ledger e seus hashes**:

```powershell
python -m masp_skill.cli validate-case --case .tmp/MASP-DEMO.json --root .
```

## Reprodução do teste sintético

```powershell
python -m pip install -e ".[test]"
python -m pytest -q tests/test_universal_cycle_v2.py
python -m pytest -q
python -m masp_skill.cli validate-routing --routing docs/masp/masp-routing.toml --classification STATIC
```

O teste cria um caso `SIMULATED` com oito fases, 16 transições e registros de M05 a M08, comparando os contratos individuais, referências entre fases e ledger. Casos adversariais mudam referências e estados para exigir erros. O Gate M06 recebe uma **declaração sintética** classificada como `RUNTIME` exclusivamente para testar a regra existente; não é um evento operacional.

## Evidências TDD

- [RED de vínculo entre módulos](https://github.com/Marciorochar/MASP_Skill/actions/runs/43995350741): 12 falhas esperadas do módulo inexistente; 310 testes anteriores permaneceram aprovados.
- [GREEN de vínculo entre módulos](https://github.com/Marciorochar/MASP_Skill/actions/runs/43995616741): 322 aprovados, 1 ignorado, Ubuntu e Windows.
- [RED da CLI](https://github.com/Marciorochar/MASP_Skill/actions/runs/43995842338): subcomando ausente, como esperado.
- [GREEN da CLI](https://github.com/Marciorochar/MASP_Skill/actions/runs/43995971370): 323 aprovados, 1 ignorado, Ubuntu e Windows.

## Próxima validação: Codex

Executar apenas em ambiente autorizado o procedimento de [VALidação de runtime](VALIDACAO-RUNTIME-PR4.md), começando por um agente não crítico e somente leitura. Não usar `--all-roles` nem invocar Astra no smoke inicial. Confirmar descoberta real da skill, delegação, correlação de eventos, isolamento e modelo/effort efetivos; sem observação, marcar `NOT_RUN`. 323 testes Python não provam agentes Codex operacionais.