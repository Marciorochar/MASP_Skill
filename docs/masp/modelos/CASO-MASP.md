# Caso MASP — manifesto JSON e ledger

O caso executável é um arquivo JSON criado por `python -m masp_skill.cli new-case`. O manifesto registra o identificador, a fase e o estado atuais, a classificação, o nível de risco e aprovações humanas. O histórico fica em `ledger`; cada transição contém sequência, fase, estado anterior e novo, ator, timestamp, referências de evidência, classificação e hash encadeado.

## Campos do manifesto

| Campo | Uso |
|---|---|
| `case_id` | Identificador seguro e estável do caso. |
| `current_phase` | Uma das oito fases da matriz, na ordem declarada. |
| `state` | `PENDING`, `IN_PROGRESS`, `PASS`, `FAIL`, `BLOCKED` ou `NOT_RUN`. |
| `classification` | `STATIC`, `SIMULATED` ou `RUNTIME`; casos novos começam como `SIMULATED`. |
| `high_risk` | Indica se um `PASS` requer parecer independente de Astra. |
| `approvals` | Aprovações humanas registradas, inclusive aprovação do plano antes da Ação. |
| `ledger` | Eventos imutáveis em sequência, ligados por hashes SHA-256. |

Cada objeto de evidência tem `id`, `path`, `classification` e `description`; metadados como `command`, `exit_code`, `role` e `opinion` podem complementar o registro. O caminho deve referenciar um arquivo existente. `NOT_RUN` nunca satisfaz um gate; quando o gate exige execução real, a evidência deve ser `RUNTIME`.

## Transições e autoridade

Use `transition` para gravar qualquer mudança. O comando valida o ator coordenador, a fase e o estado permitidos, as evidências e as regras especiais antes de gravar o arquivo por substituição atômica. Só o coordenador autoriza transições. O executor não aprova a própria ação; a fase Ação também exige aprovação humana registrada para o plano. Um caso de alto risco não pode receber `PASS` sem parecer `PASS` ou `APPROVED` do papel `masp-especialista-critico`.

`BLOCKED` impede avanço até resolução explícita fora do motor. `FAIL` só permite retorno a uma fase listada em `returns` para a fase que falhou. Modelo indisponível bloqueia o caso sem fallback automático. Trabalho paralelo com o mesmo caminho de escrita deve ser rejeitado pelo validador de tarefas.

Edição manual do manifesto ou do ledger não autoriza transições. `validate-case` recalcula a cadeia de hashes e verifica referências, estados e consistência do resumo com o último evento. Qualquer alteração manual em evento existente invalida seu hash e/ou a cadeia.

## Uso

```powershell
python -m masp_skill.cli new-case --id MASP-001 --output casos/MASP-001.json
python -m masp_skill.cli transition --case casos/MASP-001.json --state IN_PROGRESS --actor masp-coordenador --evidence evidencias/abertura.json
python -m masp_skill.cli validate-case --case casos/MASP-001.json --root .
```

O arquivo passado a `--evidence` é um JSON contendo uma lista de referências de evidência. A classificação `SIMULATED` é explícita e não equivale a resultado de runtime.

## Ficha humana de acompanhamento

Esta ficha complementa o manifesto JSON para planejamento e leitura humana. Seu preenchimento manual não altera o estado executável do caso.

- Título do problema:
- Criado em:
- Coordenador:
- Workspace:
- Fonte do relato (arquivo/caminho e data):
- Objetivo quantitativo:
- Fora do escopo:

### Ledger resumido dos gates

| Fase | Estado | Evidência/IDs | Revisão independente | Próxima decisão |
|---|---|---|---|---|
| 01 Identificação | PENDING | | | |
| 02 Observação | PENDING | | | |
| 03 Análise | PENDING | | | |
| 04 Plano de ação | PENDING | | | |
| 05 Ação | PENDING | | | |
| 06 Verificação | NOT_RUN | | | |
| 07 Padronização | PENDING | | | |
| 08 Conclusão | PENDING | | | |

### Critério de sucesso

[Condição verificável, baseline, resultado esperado e método de medição.]

### Registro humano de evidências

Para cada evidência, registrar data/hora, responsável, arquivo alvo, comando completo, diretório, toolchain, stdout/stderr, código de saída, hash/commit quando relevante, classificação do fato (`FATO | HIPÓTESE | INFERÊNCIA`) e ID correspondente no manifesto.

### Plano 5W2H

| O quê | Por quê | Onde | Quando/ordem | Quem | Como | Quanto/custo/risco |
|---|---|---|---|---|---|---|
| | | | | | | |

### Decisões e exceções

- [data] [decisão; justificativa; risco; autorização humana se aplicável]

### Auditoria e encerramento

- Resultado dos testes:
- Limitações:
- Retorno a uma fase anterior:
- Mudanças realizadas:
- Riscos residuais e pendências:
- Gate de promoção: BLOQUEADO até aprovação separada.
