# Regressões e revisão independente

| ID | Requisito ou risco | Método de verificação | Resultado | Evidência/condições | Revisor independente | Critério de parada | Providência |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

Uma regressão `fail` não pode ser ocultada por uma melhora em outro indicador. Se um comando verificado falha (`exit_code != 0`), o Gate 06 não poderá passar simplesmente porque outra verificação observacional passou. Revisão feita pelo próprio executor não é independente. Sem revisão/execução, registrar `NOT_RUN` ou `BLOCKED`, sem alegar eficácia.
