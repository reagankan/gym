# Agent Orchestration System — Claude Code Runtime

This directory configures a multi-agent orchestration system running in Claude Code. It mirrors the Kiro runtime configuration in `../kiro/` but uses Claude Code's native mechanisms (CLAUDE.md, Agent tool, hooks).

## Architecture

Two loops are available:

### Dev Loop
```
ORCHESTRATOR (you, reading this file)
    ├── RETRIEVER (Agent tool — research/context gathering)
    ├── CODER (Agent tool — production code)
    ├── REVIEWER (Agent tool — code review, read-only)
    ├── TESTER (Agent tool — write and run tests)
    ├── DOC-WRITER (Agent tool — documentation)
    └── KIRO-BRIDGE (Agent tool → kiro-cli — strict-isolation delegate)
            └── Kiro orchestrator (runtime-enforced tool boundaries)
```

### Ideation (standalone)
```
IDEATION (Agent tool — analyzes repo, generates sized prompts)
    └── RETRIEVER (nested Agent — external research for sizing)
```
Use ideation to generate new `.agents/prompts/` files with effort estimates. It does NOT execute prompts.

### Research Loop
```
RESEARCH-ORCHESTRATOR (you, with research-orchestrator.md loaded)
    ├── RESEARCHER (Agent tool — hypothesis generation + falsification)
    │       └── RETRIEVER (nested Agent — evidence gathering)
    ├── REVIEWER (Agent tool — independent hypothesis evaluation)
    └── COMPLETE (report.md deliverable)
```

## How to Use

### Dev Loop
When given a development task, follow the dev loop:
1. Read `.claude/agents/orchestrator.md` for the full orchestration protocol
2. Spawn sub-agents using the Agent tool with prompts from `.claude/agents/<role>.md`
3. Maintain checkpoints in `.agents/checkpoints/<task>/plan.md` and `log.md`
4. For tasks requiring strict isolation, delegate to Kiro via `kiro-bridge.md`

### Research Loop
When given a research/investigation task:
1. Read `.claude/agents/research-orchestrator.md` for the research protocol
2. Follow the hypothesis-driven investigation loop
3. Produce `report.md` as the final deliverable

## Principles

All agents follow `context/principles.md`:
1. Think Before Coding — state assumptions, surface tradeoffs
2. Simplicity First — minimum that solves the problem
3. Surgical Changes — touch only what you must
4. Goal-Driven Execution — define success criteria, loop until verified
5. Explicit Subagent Naming — always specify agent type
6. Parallelize Independent Work — batch independent Agent calls

**Exception:** The researcher agent does NOT follow principles 2-3 (research requires deep investigation and speculative hypotheses).

## Sub-Agent Dispatch Pattern

When spawning a sub-agent, load its prompt from `.claude/agents/<role>.md` and include it in the Agent tool's `prompt` parameter. Example:

```
Agent({
  description: "Retrieve context on authentication patterns",
  prompt: "<contents of .claude/agents/retriever.md>\n\n---\nTASK: Find how OAuth is implemented in this codebase"
})
```

## Checkpoint Discipline

After every sub-agent return, update:
- `plan.md` — current state, what's done, what's next
- `log.md` — append-only record of delegations and results

### Hybrid Nesting

When Kiro is used as a delegate, checkpoints nest:
```
.agents/checkpoints/<task>/
├── plan.md       ← Claude owns
├── log.md        ← Claude owns
└── kiro/
    ├── plan.md   ← Kiro owns (read-only to Claude)
    └── log.md    ← Kiro owns (read-only to Claude)
```
Claude references Kiro's logs but never modifies them.

## Audit Logging

Hooks in `hooks/settings.json` log Bash, Agent, Write, and Edit tool calls to `/tmp/claude_agent_log.txt`.

## Permission Model

Claude Code uses a single global `settings.json` — there is no per-agent tool restriction. Instead:
- **Structural safety**: deny list blocks only truly destructive ops (force-push, hard-reset, rm -rf /, sudo)
- **Prompt-level constraints**: retriever and reviewer are told "NEVER write files" in their prompts
- **Human gate**: `git push` is not in the allow list, so it always prompts the user

This is less strict than Kiro (which enforces per-agent tool access at runtime). The trade-off: the loop closes autonomously for coding/testing, but a misbehaving sub-agent *could* write files if it ignores its prompt. In practice, Claude models respect explicit NEVER constraints reliably.

**Hybrid approach:** When you need runtime-enforced isolation (not just prompt-level), delegate to Kiro via `kiro-bridge.md`. Claude handles orchestration and flexible tasks; Kiro handles tasks where structural guardrails are mandatory.

## Safety

- Never commit code that breaks tests
- Never push without explicit user permission
- Never skip the REVIEW phase after code changes
- Incomplete work goes behind feature flags
