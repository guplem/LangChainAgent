---
description: Multi-agent research orchestrator. Splits a broad question into focused angles, spawns research-agent workers in parallel, then runs research-synthesizer to combine outputs into one recommendation.
---

# /research-agents

You orchestrate parallel research on a broad or exploratory question for the LangChainAgent project.

## When to use

- The user asks a question that needs 4+ files read and synthesized.
- The user is choosing between multiple approaches with non-obvious trade-offs.
- The user wants a structured second opinion on a design.

Do not use this command for narrow questions that can be answered with one `Read` or one `Grep`.

## Procedure

### 1. Restate the question

Write the umbrella question in one sentence. Share with the user and ask if it captures the intent. If not, refine before continuing.

### 2. Split into angles

Identify 3-5 focused angles. Each angle should be answerable by one research-agent in 5-10 minutes. Examples for a routing-related question:

- Angle A: how `langchain.agents.create_agent` works internally
- Angle B: how the explicit graph compares to `create_agent`
- Angle C: tracing differences across the three paths
- Angle D: cost/performance implications

Avoid overlap. If two angles touch the same file, narrow the angles so each owns a different question.

### 3. Spawn research-agents in parallel

One Agent tool call per angle, all in the same message so they run concurrently. Each prompt must include:

- The umbrella question
- The specific angle this worker owns
- What the siblings are investigating (so this worker does not duplicate)
- The expected output format (see `.claude/agents/research-agent.md`)

### 4. Synthesize

Once all research-agent runs return, invoke the `research-synthesizer` agent with the full set of outputs. Its job is to produce one consolidated recommendation, not a menu of options.

### 5. Present

Print the synthesizer's recommendation, plus a one-line summary of each worker's contribution. End with the Follow-ups list and ask the user how to proceed.

## Rules

- Always run angles in parallel. Sequential research-agent calls defeat the purpose.
- The synthesizer is single-threaded. Do not split it.
- Do not write or edit code from this command. Output is research and recommendations only. To act on a recommendation, use `/create-issue` or `/implement-issue`.
- If the user wants only a partial run (e.g. just spawn the workers and stop before synthesis), respect that and skip step 4.
