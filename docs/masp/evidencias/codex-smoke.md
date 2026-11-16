# Codex smoke evidence

Classification: **RUNTIME**

CLI version: `codex-cli 0.169.0`

## Checks

- version (RUNTIME): **PASS**
- CLI help (RUNTIME): **PASS**
- model catalog (RUNTIME): **PASS**
- local agent config parse (STATIC): **PASS**
- role model/effort catalog compatibility (RUNTIME): **PASS**
- MASP skill load (RUNTIME): **FAIL**
- delegation masp-identificador (RUNTIME): **BLOCKED** — no explicit subagent tool call for this role was observed in JSONL
- effective model/effort masp-identificador (RUNTIME): **BLOCKED** — no verifiable effective model/effort was emitted by a completed subagent event
- delegation masp-observador (RUNTIME): **BLOCKED** — no explicit subagent tool call for this role was observed in JSONL
- effective model/effort masp-observador (RUNTIME): **BLOCKED** — no verifiable effective model/effort was emitted by a completed subagent event
- delegation masp-analista (RUNTIME): **BLOCKED** — no explicit subagent tool call for this role was observed in JSONL
- effective model/effort masp-analista (RUNTIME): **BLOCKED** — no verifiable effective model/effort was emitted by a completed subagent event
- delegation masp-planejador (RUNTIME): **BLOCKED** — no explicit subagent tool call for this role was observed in JSONL
- effective model/effort masp-planejador (RUNTIME): **BLOCKED** — no verifiable effective model/effort was emitted by a completed subagent event
- delegation masp-executor (RUNTIME): **BLOCKED** — no explicit subagent tool call for this role was observed in JSONL
- effective model/effort masp-executor (RUNTIME): **BLOCKED** — no verifiable effective model/effort was emitted by a completed subagent event
- delegation masp-testador (RUNTIME): **BLOCKED** — no explicit subagent tool call for this role was observed in JSONL
- effective model/effort masp-testador (RUNTIME): **BLOCKED** — no verifiable effective model/effort was emitted by a completed subagent event
- delegation masp-padronizador (RUNTIME): **BLOCKED** — no explicit subagent tool call for this role was observed in JSONL
- effective model/effort masp-padronizador (RUNTIME): **BLOCKED** — no verifiable effective model/effort was emitted by a completed subagent event
- delegation masp-relator (RUNTIME): **BLOCKED** — no explicit subagent tool call for this role was observed in JSONL
- effective model/effort masp-relator (RUNTIME): **BLOCKED** — no verifiable effective model/effort was emitted by a completed subagent event
- local agent discovery (RUNTIME): **BLOCKED** — not all configured subagents produced explicit tool-call events
- local config file (STATIC): **PASS**
- local skill file (STATIC): **PASS**

## Limitations

- Runtime delegation status requires explicit tool-call and completion events; an assistant claim alone is not accepted
