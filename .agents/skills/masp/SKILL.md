---
name: masp
description: Use when coordinating a MASP problem investigation or corrective action that needs staged evidence, explicit gates, independent work, or traceable decisions.
---

# MASP

## Overview

Use the eight MASP phases to move from a defined problem to a documented conclusion. Gates advance only on recorded evidence; a skill name or agent report does not prove that a tool ran.

## When to use

The coordinator uses `superpowers:dispatching-parallel-agents` for independent read-only investigation and `superpowers:subagent-driven-development` only for approved implementation plans. Confirm that each skill is available before attempting to invoke it.


- A defect, operational problem, or recurring failure needs baseline, causal analysis, corrective action, and verification.
- Multiple roles, independent investigations, approvals, or evidence records must be coordinated.
- A project already defines another incident or quality process: follow its `AGENTS.md` and use MASP only where compatible.

## Core pattern

1. **Identificação**: follow [the universal v2 specification](../../../docs/masp/identificacao/ESPECIFICACAO-V2.md): describe observed versus expected conditions, impact, scope, exclusions, and a verifiable numeric or qualitative success criterion. Classify uncertainty, record missing baseline as PENDENTE_DE_OBSERVACAO without automatic blocking, and hand off gaps to Observação. Do not conclude cause or prescribe a solution. Address immediate safety first using applicable procedures; MASP does not replace them.
2. **Observação**: follow [the universal v2 specification](../../../docs/masp/observacao/ESPECIFICACAO-V2.md): characterize the current condition in any domain using attributed sources and appropriate quantitative, qualitative, or unavailable baseline. Record environment, collection method, quality, and safely reproducible result or limitation. Keep causality and corrective action for later phases; structural validation does not approve the gate.
3. **Análise**: follow [the universal v2 specification](../../../docs/masp/analise/ESPECIFICACAO-V2.md). Compare rival hypotheses, sources, evidence for and against, potential disconfirmations and alternative explanations. Distinguish association from causality; report supported causes only with evaluated evidence, or an explicit qualified inconclusion. Do not invent tests or begin corrective action.
4. **Plano de ação**: follow [the universal v2 specification](../../../docs/masp/plano-acao/ESPECIFICACAO-V2.md). Compare viable interventions, justify the minimum adequate change, plan 5W2H, owners, scope, risks, rollback or contingency for irreversible actions, test criteria and external human approval. An inconclusive cause does not justify definitive corrective action; no task is executed in this phase. JSON STATIC checks cannot authenticate approval or pass Gate 04.
5. **Ação**: follow [the universal v2 specification](../../../docs/masp/acao/ESPECIFICACAO-V2.md). Require externally verified authorization, approved plan revision, scope and safety before action; document genuine before/after, performed/NOT_RUN steps, procedures or commands, deviations, stop and contingency. The executor cannot self-approve or claim efficacy. JSON validation is STATIC and never grants Gate 05 PASS.
6. **Verificação**: follow [the universal v2 specification](../../../docs/masp/verificacao/ESPECIFICACAO-V2.md). Compare quantitative or qualitative baseline with observed result and acceptance criteria, seek independent review, detect regressions and do not equate command success to efficacy. Non-digital observations require attributed performed method, source, result and independent reviewer. Gate 06 preserves command-failure rejection; sidecar validation remains STATIC.
7. **Padronização**: follow [the universal v2 specification](../../../docs/masp/padronizacao/ESPECIFICACAO-V2.md). Adopt only adequately verified improvements; define proportionate preventive control, owner, observable trigger/reaction, regression checking, monitoring, document version, and training where needed. A written or STATIC-valid pattern does not prove approval, actual adoption, or sustainability. Return to Verification if efficacy is not established.
8. **Conclusão**: consolidate the ledger, outcomes, limitations, residual risks, pending work, and audit opinion.

Keep phases sequential at their gates. Only independent read-only investigation may run in parallel. The coordinator may use `dispatching-parallel-agents` to identify and assign those independent reads, with distinct contracts and no overlapping write ownership. This is fan-out planning; it does not execute a phase plan.

For an approved implementation plan, the coordinator may use `subagent-driven-development` to assign its tasks to implementers and review each result, only when the active runtime supports that workflow. It governs plan execution; it does not authorize concurrent writes to the same file or let child agents spawn further agents. If that workflow is unavailable, the coordinator records the limitation and proceeds serially or marks the task `BLOCKED` when delegation is essential.

## Status and evidence

Use only `PENDING`, `IN_PROGRESS`, `PASS`, `FAIL`, `BLOCKED`, and `NOT_RUN`. `PASS` requires the phase gate's evidence; `NOT_RUN` is not success. Label evidence `STATIC`, `SIMULATED`, or `RUNTIME`: file inspection and dry-run scenarios do not establish runtime behavior. Record commands, exit codes, outputs, paths, and limitations. A missing tool, model, approval, or prerequisite blocks the dependent gate; do not substitute silently.

## Quick reference: local CLI

Run from the repository root with Python 3.11+ and the project installed or importable:

```powershell
python -m masp_skill.cli validate-routing --routing docs/masp/masp-routing.toml --classification STATIC
python -m masp_skill.cli new-case --id MASP-001 --output .cases/MASP-001.json --root .
python -m masp_skill.cli case-revision --case .cases/MASP-001.json
python -m masp_skill.cli transition --case .cases/MASP-001.json --state IN_PROGRESS --actor masp-coordenador --evidence .cases/evidence.json --expected-revision <SHA256> --root .
python -m masp_skill.cli validate-case --case .cases/MASP-001.json --root .
```

`new-case` and `transition` create `SIMULATED` records. Replace paths and evidence with files inside the chosen workspace. They do not authenticate people, approvals, or model identities. See [the routing guide](../../../skills/masp/references/routing-guide.md) for gates, returns, and evidence details.

## Common mistakes

- Treating phase gates as permission to skip earlier phases: retain the declared order and use only documented returns.
- Treating parallel agent replies as verification: inspect artifacts and run the required checks independently.
- Treating simulated labels, empty output, or missing evidence as `PASS`: record the true classification and leave the gate open.
- Treating the unavailable REA tool as a prerequisite for every case: REA is not required by default; if a specific analysis depends on it, mark that analysis `BLOCKED` and state what would unblock it.
- Treating local documents as installed runtime agents or claiming unobserved discovery: confirm capabilities in the active session.

