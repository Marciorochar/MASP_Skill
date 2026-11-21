# Critérios de encerramento — M08

| Categoria | Interpretação | Efeito no ledger |
|---|---|---|
| Resolução demonstrada | Objetivos atendidos no alcance efetivamente verificado | Gate 08 pode ser avaliado se requisitos anteriores atendidos |
| Resolução parcial | Melhoria comprovada, problema remanescente | Não inventar PASS de gate pendente |
| Inconclusiva | Dados insuficientes para afirmar resolução | Registrar `BLOCKED`/pendências conforme requisito |
| Desfavorável | Critérios não atendidos ou regressão relevante | Preservar `FAIL` e evidências |
| Administrativa com ressalvas | Arquivamento permitido por autoridade competente | **Separado** de resolução e de PASS dos gates |

O motor atual não permite `PASS` da Conclusão sem todos os gates anteriores PASS e trata alguns estados como terminais. Não burlar o motor. Para caso inconclusivo, registrar o relatório e decisão externa sem adulterar o ledger.

**Gate 08:** `complete_ledger`, `results`, `limitations`, `residual_risks`, `pending_items`, `audit_opinion`; validar requisitos com evidência. Estatuto do relatório ou JSON `approved` não substitui revisão profissional.
