---
name: masp
description: Use when coordinating a MASP problem investigation or corrective action that needs staged evidence, explicit gates, independent work, or traceable decisions.
---

# MASP

## Overview

Use the eight MASP phases to move from a defined problem to a documented conclusion. Gates advance only on recorded evidence; a skill name or agent report does not prove that a tool ran.

## When to use

- A defect, operational problem, or recurring failure needs baseline, causal analysis, corrective action, and verification.
- Multiple roles, independent investigations, approvals, or evidence records must be coordinated.
- A project already defines another incident or quality process: follow its `AGENTS.md` and use MASP only where compatible.

## Core pattern

1. **Identificação**: define the problem, impact, scope, exclusions, and success measure.
2. **Observação**: capture baseline, environment, collection method, reproducible result, and limitations.
3. **Análise**: compare hypotheses against evidence; state the supported cause or the unresolved question.
4. **Plano de ação**: list tasks, owners, scope, risks, rollback, tests, and recorded human approval.
5. **Ação**: make only approved changes in the assigned workspace; record diff, commands, results, and limits. The executor never approves its own work.
6. **Verificação**: compare against baseline, run relevant tests, and obtain independent review.
7. **Padronização**: define a preventive control, owner, trigger, and regression check.
8. **Conclusão**: consolidate the ledger, outcomes, limitations, residual risks, pending work, and audit opinion.

Keep phases sequential at their gates. Only independent read-only investigation may run in parallel. The coordinator may use `dispatching-parallel-agents` to identify and assign those independent reads, with distinct contracts and no overlapping write ownership. This is fan-out planning; it does not execute a phase plan.

For an approved implementation plan, the coordinator may use `subagent-driven-development` to assign its tasks to implementers and review each result, only when the active runtime supports that workflow. It governs plan execution; it does not authorize concurrent writes to the same file or let child agents spawn further agents. If that workflow is unavailable, the coordinator records the limitation and proceeds serially or marks the task `BLOCKED` when delegation is essential.

## Status and evidence

Use only `PENDING`, `IN_PROGRESS`, `PASS`, `FAIL`, `BLOCKED`, and `NOT_RUN`. `PASS` requires the phase gate's evidence; `NOT_RUN` is not success. Label evidence `STATIC`, `SIMULATED`, or `RUNTIME`: file inspection and dry-run scenarios do not establish runtime behavior. Record commands, exit codes, outputs, paths, and limitations. A missing tool, model, approval, or prerequisite blocks the dependent gate; do not substitute silently.

## Quick reference: local CLI

Run from the repository root with Python 3.14 and the project installed or importable:

```powershell
python -m masp_skill.cli validate-routing --routing docs/masp/masp-routing.toml --classification STATIC
python -m masp_skill.cli new-case --id MASP-001 --output .cases/MASP-001.json --root .
python -m masp_skill.cli case-revision --case .cases/MASP-001.json
python -m masp_skill.cli transition --case .cases/MASP-001.json --state IN_PROGRESS --actor masp-coordenador --evidence .cases/evidence.json --expected-revision <SHA256> --root .
python -m masp_skill.cli validate-case --case .cases/MASP-001.json --root .
```

`new-case` and `transition` create `SIMULATED` records. Replace paths and evidence with files inside the chosen workspace. They do not authenticate people, approvals, or model identities. See [the routing guide](references/routing-guide.md) for gates, returns, and evidence details.

## Common mistakes

- Treating phase gates as permission to skip earlier phases: retain the declared order and use only documented returns.
- Treating parallel agent replies as verification: inspect artifacts and run the required checks independently.
- Treating simulated labels, empty output, or missing evidence as `PASS`: record the true classification and leave the gate open.
- Treating the unavailable REA tool as a prerequisite for every case: REA is not required by default; if a specific analysis depends on it, mark that analysis `BLOCKED` and state what would unblock it.
- Treating local documents as installed runtime agents or claiming unobserved discovery: confirm capabilities in the active session.

