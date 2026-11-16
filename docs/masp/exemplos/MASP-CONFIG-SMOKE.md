# Exemplo: ler a evidência de configuração e smoke

Este exemplo resume [`../evidencias/codex-smoke.md`](../evidencias/codex-smoke.md) e seu registro detalhado [`../evidencias/codex-smoke.json`](../evidencias/codex-smoke.json). Os arquivos de evidência são a fonte dos resultados abaixo; este texto não é uma nova execução.

## Execução registrada

- CLI: `codex-cli 0.169.0`.
- Classificação global: `RUNTIME`, pois foram executados comandos reais do CLI.
- PASS: versão, help, catálogo, parse estático da configuração local e compatibilidade de catálogo para os modelos/esforços configurados.
- BLOCKED: evento estruturado de carregamento da skill MASP; delegação correlacionada e modelo/esforço efetivo para cada um dos oito papéis filhos; descoberta local completa.

Os campos da matriz indicam configuração esperada. A compatibilidade de catálogo mostra que os valores aparecem entre as opções aceitas pelo catálogo consultado. Como o processo não gerou os eventos estruturados requeridos, os valores efetivos por agente permanecem desconhecidos. O texto devolvido pelo processo não foi aceito como substituto de evento de carregamento/delegação.

## Como reproduzir

No PowerShell, a partir da raiz do repositório:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_codex_smoke.ps1
```

O runner grava evidência JSON e Markdown sob `docs/masp/evidencias/`. Confira comando, stdout, stderr, exit code, versão e estado individual de cada check. Uma execução nova pode produzir resultados diferentes; substitua este resumo somente depois de conferir os novos artefatos.

Para validações locais separadas do smoke:

```powershell
python -m masp_skill.cli validate-routing --routing docs/masp/masp-routing.toml --classification STATIC
python -m masp_skill.cli validate-case --case tests/fixtures/cases/valid-case.json --root .
python -m pytest -q
```

As duas chamadas da CLI são `STATIC`; a criação e transições pelo motor local são `SIMULATED`; Pytest é verificação local de código. Nenhuma delas muda os checks de runtime para PASS. No registro atual, o estado geral correto de descoberta/carregamento/delegação é `BLOCKED`.
