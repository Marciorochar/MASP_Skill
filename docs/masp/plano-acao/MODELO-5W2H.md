# Modelo 5W2H — Plano de Ação Universal v2

**Ficha complementar ao caso, sem autorização automática.** Preencher com dados verificáveis; campos desconhecidos devem permanecer explicitamente pendentes, não simulados.

## 1. Vínculo com o MASP

- ID do caso, versão do plano, autor e data conhecida:
- Problema e impacto (M01):
- Baseline quantitativo/qualitativo/indisponível (M02):
- Conclusão da Análise (M03): causa(s) sustentada(s) / `INCONCLUSIVA`:
- Escopo e exclusões:
- Modo `rápido` / `aprofundado`, justificativa e restrições:
- Autorizações, profissionais competentes e premissas:

## 2. Alternativas avaliadas

| ID | Alternativa | Relação com causa/risco | Evidência | Viabilidade e recursos | Riscos | Reversibilidade | Decisão e justificativa |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | A definir | Fonte M03 | ID de evidência | Disponível/pendente | ID R1 | Reversível/parcial/irreversível | Selecionada/não selecionada |

**Mudança mínima adequada:** declarar por que a solução cobre o risco ou causa delimitada sem efeitos desproporcionais; menor preço ou menor esforço não é suficiente por si só.

Se M03 for inconclusivo, ações permanentes `corrective` não podem ser tratadas como solução definitiva. Considerar `investigative`, `containment`, `protective` ou `monitoring` devidamente justificadas.

## 3. Plano 5W2H

| ID | What (O quê) | Why (Por quê) | Where (Onde) | When (Quando) | Who (Quem) | How (Como) | How much (Custo/recursos) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T1 | A definir | Referência M03 | Processo/unidade | Prazo conhecido ou dependência | Responsável por função | Procedimento proposto | Valor com fonte ou `unknown` fundamentado |

Campos complementares por tarefa:

- Alternativa vinculada (A1...), responsável e responsável pela verificação:
- Dependências, pré-requisitos, acesso e autorizações:
- Entregável e resultado esperado:
- Controle preventivo e mitigador, ID do risco:
- Gatilho de interrupção (stop):
- Reversão/contingência e ID:
- Plano de teste, baseline, critério de aceitação e falha:
- Evidência a produzir **depois** da execução:

## 4. Aprovação humana real

- Plano/versão/escopo apresentado a:
- Pessoa/função autorizada (não inventar):
- Decisão: `pending` / `approved` / `rejected`:
- Evidência real de aprovação (localização e controles de acesso):
- Data, condições, recursos, limites e riscos aceitos:
- Pendências que impedem Gate 04 `PASS`:
- Confirmação de que nada foi executado na elaboração:

`approved` declarado no sidecar opcional continua **sem autenticação**. Gate 04 e início da Ação dependem de verificação externa competente.

## 5. Exemplo JSON estritamente sintético

```json
{
  "case_id": "MASP-EXEMPLO",
  "problem_reference": "M01-EXEMPLO",
  "analysis_reference": "M03-EXEMPLO",
  "analysis_status": "inconclusive",
  "plan_objective": "Planejar coleta adicional antes de ação corretiva",
  "alternatives": [{
    "id": "A1", "description": "Solicitar dados históricos autorizados",
    "rationale": "Necessários para diferenciar hipóteses",
    "evidence_reference": "M03-LACUNA-1", "intervention_type": "investigative",
    "feasibility": "Depende de autorização", "selection_rationale": "Intervenção limitada"
  }],
  "selected_actions": ["A1"],
  "tasks": [{
    "id": "T1", "alternative_id": "A1", "what": "Preparar solicitação",
    "why": "Atribuir fonte da lacuna", "where": "Unidade ilustrativa",
    "when": "Após aprovação", "who": "P1", "how": "Coleta documental",
    "how_much": {"status": "unknown", "reason": "Custo ainda não estimado"},
    "dependencies": [], "expected_result": "Dados disponíveis para nova análise"
  }],
  "owners": [{"id": "P1", "role": "Responsável de coleta"},
             {"id": "P2", "role": "Responsável de verificação"}],
  "scope": {"included": "Consulta documental", "excluded": "Intervenção operacional"},
  "risks": [{
    "id": "R1", "task_id": "T1", "description": "Acesso indevido",
    "preventive_control": "Validar autorização", "mitigation": "Suspender acesso",
    "stop_condition": "Autorização ausente",
    "residual_risk": "A definir em avaliação competente"
  }],
  "rollback": [{
    "task_id": "T1", "type": "reversible", "owner_id": "P1",
    "trigger": "Acesso não autorizado", "procedure": "Suspender solicitação",
    "verification": "Conferir encerramento da solicitação"
  }],
  "tests": [{
    "id": "V1", "task_id": "T1",
    "baseline": {"type": "unavailable", "reason": "Dados ainda não obtidos",
                 "collection_needed": "Consultar registros autorizados"},
    "indicator": "Disponibilidade das fontes", "method": "Conferência documental",
    "expected_result": "Fontes disponíveis", "acceptance": "Fonte identificada e acessível",
    "failure": "Fonte não disponível", "stop_condition": "Risco de sigilo",
    "verification_owner_id": "P2"
  }],
  "human_approval": {"status": "pending", "reason": "Aguardar autorização real"}
}
```

A execução de `python -m masp_skill.cli validate-action-plan --record .tmp/plano.json --root .` é **STATIC** e não aprova plano, causa, recursos ou autorização.
