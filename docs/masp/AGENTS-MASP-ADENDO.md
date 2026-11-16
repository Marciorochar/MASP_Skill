# ADENDO SUGERIDO PARA AGENTS.md — não substituir o original

> Cole somente após revisar compatibilidade com as regras existentes do seu repositório.

## Método MASP

O coordenador orquestra oito fases com os perfis presentes em `docs/masp/agentes/`. Para cada problema, crie um caso usando `docs/masp/modelos/CASO-MASP.md`, com ID, baseline, logs, métricas, decisões, rastreabilidade e responsáveis.

### Prioridade de instruções

Preserve `AGENTS.md`, políticas de segurança do repositório e restrições explícitas do usuário. Skills Superpowers orientam processo, mas não anulam essas regras. Se a delegação de subagentes não estiver disponível, informe a limitação e execute os mesmos papéis em etapas identificadas, sem alegar multiagentes reais.

### Controle de gates

A sequência é 01 Identificação → 02 Observação → 03 Análise → 04 Plano de ação → 05 Ação → 06 Verificação → 07 Padronização → 08 Conclusão. Cada transição exige artefato e julgamento documentados. `BLOCKED`, `FAIL` e `NOT_RUN` não habilitam promoção. Investigações independentes podem ser delegadas em paralelo; implementação e revisões vinculadas são sequenciais.

### Segregação de funções

Um agente não aprova sozinho o próprio trabalho quando houver alteração de código. O Agente 05 executa; o Agente 06 verifica de forma independente e o coordenador integra a decisão. Um único responsável grava cada arquivo por vez. Os subagentes não criam outros agentes.

### Segurança

O checkout original do OTServer permanece somente leitura. Use workspace isolado para mudanças. Não execute servidores, bancos reais ou binários de proveniência desconhecida. Não sobrescreva snapshots Graphify. Não altere configuração global do Codex sem autorização. Mantenha o gate de promoção fechado até comprovação de build/testes adequados e isolamento.

### Evidências

`PASS` só é permitido após comando real, captura de saída e leitura do código de retorno. Diferencie fatos de hipóteses e recomendações. Relatórios passados não substituem validações frescas. Ao concluir, apresente o que foi executado, o que não foi, hashes relevantes, testes, riscos e decisão de integração.