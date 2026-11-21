# PR #3 — Robustez e integração MASP Multiagentes (design)

**Data:** 2026-11-16. **Base:** `eb23158b53bb9014445aed6105ea364722781e14`. **Fonte:** especificação fornecida pelo usuário na conversa.

## Objetivo
Fortalecer validação de entradas JSON/TOML, integridade do ledger, confiabilidade dos gates, descoberta da skill e observabilidade de delegação no Codex, preservando oito fases MASP, dez papéis, modelos/esforços configurados, limite de três agentes e classificação STATIC/SIMULATED/RUNTIME.

## Invariantes
- Apenas coordenador delega; filhos não delegam; executor não aprova sua própria ação.
- Plano de ação exige aprovação humana; auditor Astra em casos de alto risco; sem fallback automático.
- `PASS` somente com provas e gates adequados; `BLOCKED`/`NOT_RUN` não representam sucesso.
- História de eventos v2, hashes de evidência, compare-and-swap e lock preservados.
- Nunca alterar serviços reais, VPS, banco, OTServer nem `main`; PR sem merge automático.

## Abordagens consideradas
1. **Correções incrementais na arquitetura atual (adotada):** menor regressão; TDD e CI para cada grupo de mudanças.
2. Reescrever o motor de estados: rejeitada por risco e escopo desnecessários.
3. Declarar operação multiagente apenas via TOML: rejeitada por ausência de evidência runtime.

## Fronteiras e dependências
- `.agents/skills/masp/SKILL.md` deve ser referência local da descoberta; referências profundas continuam acessíveis por caminho explícito e verificado.
- Validadores devem rejeitar tipos inválidos sem exceções inesperadas; o piloto sintético e CI não equivalem à delegação real.
- Smoke real somente baixo custo, um agente inicialmente, read-only; evidência estruturada ou status BLOCKED.
- `C:\\Users\\marci\\Desktop\\Meu Site - M2R\\graphify-out` é diretório local externo ao repositório; não acessível neste ambiente. Não inventar conclusões do Graphify nem usá-lo como fonte até ser disponibilizado.

## Decisão de entrega
Entregar branch isolada, testes, documentação de evidências e PR em rascunho quando pendências runtime permanecerem. Evitar mudanças globais e inferências pagas no CI.
