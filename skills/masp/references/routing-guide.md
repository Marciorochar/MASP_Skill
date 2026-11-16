# MASP routing and evidence guide

This reference follows `docs/masp/masp-routing.toml`, `src/masp_skill/cli.py`, and the case transition rules. The matrix is the declared source for roles, phase order, gates, skills, and returns; run the CLI to check the local copy.

## Phase gates

| Phase | Minimum gate evidence | Declared return |
|---|---|---|
| Identificação | Problem, impact, scope, exclusions, success metric | Conclusão |
| Observação | Baseline, environment, collection method, reproducible result or limitation | Identificação |
| Análise | Hypotheses, evidence for and against, supported cause or explicit inconclusive result | Observação |
| Plano de ação | Tasks, owners, scope, risks, rollback, tests, human approval record | Análise |
| Ação | Changes, diff, commands, results, no self-approval | Plano de ação |
| Verificação | Baseline comparison, runtime tests, relevant regressions, independent review | Ação; Análise |
| Padronização | Preventive control, owner, trigger, regression | Verificação |
| Conclusão | Complete ledger, results, limitations, residual risks, pending items, audit opinion | Verificação; Padronização |

Only the next phase may start after a `PASS`. A `FAIL` may return only along the matrix's declared edge. `BLOCKED` and `NOT_RUN` do not advance. Record a new decision and its evidence; do not edit a manifest to simulate a transition.

## Evidence classes

- `STATIC`: source, config, or document inspection; no behavior execution is implied.
- `SIMULATED`: controlled scenario or ledger operation explicitly labeled simulated.
- `RUNTIME`: an actual command or experiment with command, integer exit code, and captured stdout or stderr. A `RUNTIME` label alone is insufficient.

Evidence files must exist under the selected case root. Do not describe a simulation or static check as a real integration, build, or runtime result. The case engine records simulated approval and role labels; it does not authenticate them.

## Skill routing and coordination

Use the declared phase skills when they are present in the active environment. Superpowers 7.0.1 skill paths recorded in the routing matrix were confirmed as files when this package was assembled; current session availability must still be checked. ECC repo-scan is optional. REA is unavailable and is not a general MASP prerequisite.

| Phase | Superpowers skills declared by the matrix |
|---|---|
| Identificação | `superpowers:brainstorming` |
| Observação | `superpowers:systematic-debugging` |
| Análise | `superpowers:systematic-debugging` |
| Plano de ação | `superpowers:writing-plans` |
| Ação | `superpowers:using-git-worktrees`, `superpowers:test-driven-development`, `superpowers:subagent-driven-development` (optional) |
| Verificação | `superpowers:verification-before-completion`, `superpowers:requesting-code-review` |
| Padronização | `superpowers:writing-skills` (optional) |
| Conclusão | `superpowers:finishing-a-development-branch` (optional) |

`superpowers:dispatching-parallel-agents` is a coordinator skill for choosing independent tasks to fan out. Use it for independent investigation, with explicit inputs, outputs, read/write scope, and distinct file ownership. It does not run the implementation plan.

`superpowers:subagent-driven-development` is the implementation workflow for an approved plan. Under the coordinator, it assigns plan tasks and reviews completions. It does not replace independent-work selection, override sequential MASP gates, or allow child agents to create subagents. When the workflow or runtime capability is unavailable, proceed serially if safe and feasible; otherwise report `BLOCKED` and the missing prerequisite.

## CLI commands

From the repository root:

```powershell
python -m masp_skill.cli validate-routing --routing docs/masp/masp-routing.toml --classification STATIC
python -m masp_skill.cli new-case --id MASP-001 --output .cases/MASP-001.json --root .
python -m masp_skill.cli case-revision --case .cases/MASP-001.json
python -m masp_skill.cli transition --case .cases/MASP-001.json --state IN_PROGRESS --actor masp-coordenador --evidence .cases/evidence.json --expected-revision <SHA256> --root .
python -m masp_skill.cli validate-case --case .cases/MASP-001.json --root .
```

The `transition` evidence argument is a JSON file containing an evidence array. Get the current revision immediately before a transition and pass it as `--expected-revision`; stale revisions fail. Paths for cases and evidence must remain inside `--root`. `new-case` refuses to overwrite. State-changing CLI operations are reported `SIMULATED`; none authenticates the named actor or a human approval.

The official command-line interface does not provide a `resolve-blocked` command. Do not infer a resolution or edit the ledger manually. Resolve the prerequisite through an explicitly reviewed change to the case contract/tooling or keep the case blocked and record the missing capability.

