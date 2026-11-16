# MASP Identificação Universal v2 Implementation Plan

> **For agentic workers:** execute each task in order with the configured MASP roles. Work only in the feature worktree; preserve pending changes in the original checkout.

**Goal:** Make Módulo 01 a domain-independent characterization method that records known conditions, impacts, boundaries, criteria, uncertainty, and observation gaps without asserting root cause or prescribing a solution.

**Architecture:** Keep the existing Python case ledger and its schema unchanged. Put semantic guidance in the Identificação contract and human-readable worksheet; refine only the M01 routing declaration. Use static contract tests and a synthetic fixture corpus, then separately evaluate the configured M01 agent and request independent testador review.

**Tech Stack:** Markdown, TOML, Python 3.11+, pytest; Codex collaboration runtime for the separately classified agent evaluation.

**Spec:** Approved design in the conversation and docs/masp/identificacao/ESPECIFICACAO-V2.md (created in Task 2).

## Global Constraints

- Preserve the exact gate criteria: problem, impact, scope, exclusions, success_metric.
- Do not change the case ledger schema or implementation of MASP modules 02–08.
- Do not claim tests of documents or fixtures prove LLM behavior at runtime.
- Do not invent numbers, baselines, causes, targets, impact severity, or solutions.
- Missing baseline alone is not a blocker; mark it PENDENTE_DE_OBSERVACAO.
- Classify information as FATO_VERIFICADO, RELATO_NAO_VERIFICADO, HIPOTESE, or DESCONHECIDO; record source/date/limitations when known.
- Prioritize immediate safety guidance within competence and applicable emergency procedures.
- Use no more than two child agents simultaneously; do not invoke Astra.
- Work on feat/masp-identificacao-universal-v2. Keep the original checkout pending changes untouched.

## Review Focus

- Vague input must not produce fabricated specificity; fixtures require unknowns to remain explicit.
- A supplied cause or solution must not become an established fact or the problem statement.
- Contradictory details remain attributed and unresolved when material.
- Missing baseline must not cause an automatic block.
- Qualitative problems may use verifiable qualitative success criteria without invented numeric KPIs.
- Safety hazards require safety-first guidance without implying MASP replaces emergency response.

---

### Task 1: Add synthetic scenarios and failing contract tests

**Files:**
- Create: tests/fixtures/identificacao-v2/casos.json
- Create: tests/test_identification_contract.py

**Interfaces:**
- Eight domain scenarios: industry, logistics, health services, administration, environment, technology, education, and household.
- Eight adversarial scenarios: vague report, embedded solution, presumed cause, absent quantitative data, contradictory information, undefined scope, qualitative success criterion, and possible immediate safety risk.
- Each case contains synthetic input and expected invariants/labels, not purported observed outcomes.

- [ ] Write tests for required corpus inventory, uncertainty labels and fields, preservation of the five gate IDs, and separation of static assertions from runtime claims.
- [ ] Run the focused test and capture expected RED failures against the not-yet-created v2 contract.
- [ ] Confirm the original checkout pending changes are absent from this worktree and remain untouched.

### Task 2: Write specification, worksheet, references, and role contract

**Files:**
- Create: docs/masp/identificacao/ESPECIFICACAO-V2.md
- Create: docs/masp/identificacao/REFERENCIAS-METODOLOGICAS.md
- Create: docs/masp/identificacao/RELATORIO-TESTES-V2.md
- Modify: docs/masp/agentes/01-identificacao.md
- Modify: .codex/agents/masp-identificador.toml
- Modify: .agents/skills/masp/SKILL.md
- Modify: docs/masp/modelos/CASO-MASP.md
- Modify only the Identificação phase block in docs/masp/masp-routing.toml

**Interfaces:**
- Specification defines quick/deep modes, adaptive question triggers, the universal worksheet, uncertainty classes, safety boundary, observation handoff, and objective PASS/BLOCKED criteria.
- The worksheet complements the current case template. It is not a JSON schema or a ledger field.
- The role contract points to the canonical specification and applies domain-specific safety constraints conditionally.

- [ ] Write methodology references with links, adaptations, provenance/license notes, and explicit non-reuse where licensing is unclear or restrictive.
- [ ] Update role and skill instructions: describe the deviation; never conclude cause or prescribe solution in Identification.
- [ ] Add the worksheet while preserving all existing manual fields and five gate IDs.
- [ ] Refine only M01 routing gate/outputs; do not reorder phases or edit later phase blocks.
- [ ] Run focused contract tests and correct failures without changing the ledger schema.

### Task 3: Separate runtime evaluation and independent review

**Files:**
- Create: docs/masp/evidencias/identificacao-v2-runtime.md
- Update: docs/masp/identificacao/RELATORIO-TESTES-V2.md

**Interfaces:**
- The configured masp-identificador reads the new contract and produces outputs for the synthetic corpus.
- The configured masp-testador independently reviews outputs against fixture invariants without editing files.
- Runtime evidence records agent creation/completion, prompts, outputs, and paths. Claim effective model/effort only if runtime telemetry exposes it.

- [ ] Invoke only masp-identificador for the corpus; do not use --all-roles or Astra.
- [ ] Request independent testador review for domain transfer, non-invention, uncertainty, safety priority, and phase boundary.
- [ ] Record PASS, FAIL, BLOCKED, or NOT_RUN per check. Do not treat static tests as runtime evidence.

### Task 4: Verify and audit

**Files:**
- Update: docs/masp/identificacao/RELATORIO-TESTES-V2.md
- Review only: complete branch diff

- [ ] Run rtk pytest -q.
- [ ] Run rtk python -m masp_skill.cli validate-routing --routing docs/masp/masp-routing.toml --classification STATIC.
- [ ] Run rtk python -m masp_skill.cli validate-case --case tests/fixtures/cases/valid-case.json --root .
- [ ] Review GitHub Actions for the feature branch if checks are available; otherwise record NOT_RUN with the reason.
- [ ] Request independent masp-testador review of requirements, compatibility, coverage, and regressions; coordinator verifies its evidence.
- [ ] Route findings to the executor and revalidate corrected areas plus related regressions only.
- [ ] Record commands, exit codes, results, evidence paths, and limitations in the report.

### Task 5: Prepare a draft pull request

- [ ] Confirm only approved Módulo 01 scope is changed.
- [ ] If authenticated GitHub access is available, publish the branch and open a draft PR titled feat(masp): identificação universal v2 com validação multidomínio.
- [ ] Include motivation, references/licensing, compatibility, files, verified tests, delegation evidence, and limitations.
- [ ] Do not merge.

---

## Compatibility and rollback

The feature is isolated on feat/masp-identificacao-universal-v2; the original checkout remains unchanged. Reverting this feature branch or closing the draft PR rolls back the change. No migration is required because the ledger schema stays unchanged. The M01 routing block may change only its gate text and outputs; phase order and IDs remain fixed.

## Evidence boundary

- Pytest and CLI validators establish static contract, fixture inventory, routing, and existing case compatibility.
- Agent scenario outputs establish only what was observed in that runtime session; they do not establish universal future behavior.
- GitHub Actions establishes CI status only for a commit it actually checks.
- No effective model/effort claim is made without explicit runtime telemetry.
