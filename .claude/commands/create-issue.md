---
description: Create a GitHub issue interactively. Investigates the codebase, detects duplicates, drafts a tight issue body, and posts it with self-assign + waiting-for-human-check label.
---

# /create-issue

You create one GitHub issue for the LangChainAgent project. Be interactive: clarify, then act.

## Procedure

### 1. Clarify the request

If the user's message is short or ambiguous, ask one focused question via `AskUserQuestion`. Examples of good questions:

- "Is this a bug, a feature, or a refactor?"
- "Which routing path is affected: chain, agent, graph, or all three?"
- "Does this depend on adding a new tool, or only on changing existing code?"

Do not ask more than two questions total. Stop when you have enough to write a useful issue body.

### 2. Investigate the codebase

Use the **pattern-scout** agent to find existing code in the relevant area. For broad or exploratory requests ("rework the tracing", "redesign the parser"), offer to run `/research-agents` first and wait for the user's decision.

### 3. Detect duplicates

```bash
gh issue list --search "<keywords from the request>" --state all --limit 20
```

If a likely duplicate exists, surface its URL and title. Ask the user whether to comment on the existing issue or create a new one.

### 4. Draft the issue body

Strict template, no padding:

```
## Context
<2-3 sentences: what the project does, what the relevant area is. Link to the ADR if one applies.>

## Problem / Goal
<One paragraph. State what is wrong or what is missing.>

## Proposed approach
<Bulleted, concrete. Reference file paths.>

## Out of scope
<What this issue does NOT cover. Prevents scope creep.>

## Acceptance criteria
- [ ] <observable behavior 1>
- [ ] <observable behavior 2>
- [ ] Tests added or updated under tests/
- [ ] CLAUDE.md / README.md / ADR updated if affected
```

### 5. Pick labels

Auto-pick from this list based on the content:

- `bug` if the body describes broken behavior
- `enhancement` for new features
- `refactor` for restructuring with no behavior change
- `docs` for README / CLAUDE.md / ADR changes only
- `area:chain`, `area:agent`, `area:graph`, `area:tools`, `area:tracing`, `area:repl` for the affected module

Always add `waiting-for-human-check`.

### 6. Create the issue

```bash
gh label create "waiting-for-human-check" --color "fbca04" --description "Needs a human to review before merging or progressing" 2>/dev/null || true

gh issue create \
  --title "<short imperative title under 70 chars>" \
  --label "waiting-for-human-check,<other labels>" \
  --assignee "@me" \
  --body "$(cat <<'EOF'
<body from step 4>
EOF
)"
```

Print the resulting issue URL.

## Anti-redundancy rules

- One issue per problem. If you find two unrelated problems, ask the user whether to file two issues or pick one for now.
- Do not write the same content in multiple sections. Each section answers a different question.
- Do not duplicate ADR content into the issue body. Link to the ADR instead.
