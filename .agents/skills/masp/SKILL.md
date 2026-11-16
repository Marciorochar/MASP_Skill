---
name: masp
description: Use the MASP workflow for staged problem solving, corrective action, evidence gates, and traceable decisions.
---

# MASP

Follow the eight phases in `docs/masp/masp-routing.toml` in order: Identificação, Observação, Análise, Plano de ação, Ação, Verificação, Padronização, Conclusão. Advance a gate only with its required evidence. Preserve `BLOCKED` and `NOT_RUN` as distinct from success.

Before work, inspect the repository `AGENTS.md`, define scope and exclusions, and record a baseline. During analysis, compare hypotheses with evidence and state uncertainty. Plan owners, risks, rollback, tests, and human approval. Implement only the authorized files. Verify against baseline and obtain independent review. Conclude with outcomes, limitations, residual risks, and pending work.

Use `masp_skill` CLI only for simulated workflow records. Role, actor, approval, and model labels are not authenticated. Missing prerequisites block dependent gates; do not claim runtime behavior from static inspection or text assertions.
