---
description: Implement a GitHub issue end to end. Branch, code with TDD, run lint/type/test, open a PR with the right labels and assignee, and link the issue.
---

# /implement-issue

You implement one GitHub issue and open a pull request. Be interactive: confirm direction at the major forks, then act.

## Arguments

The user passes an issue number, e.g. `/implement-issue 42`.

## Procedure

### 1. Read the issue

```bash
gh issue view <N> --json title,body,labels,assignees
```

If the issue is broad or exploratory, offer to run `/research-agents` first and wait for the user's decision. Do not start coding before that decision.

### 2. Pick branch and PR

Ask via `AskUserQuestion`:

- New branch from `main`, or continue on an existing branch?
- New PR, or add to an existing draft PR?

Branch name convention: `<area>/<issue-slug>` (e.g. `tools/add-power`, `tracing/langfuse-only`). Always start from up-to-date `main`:

```bash
git fetch origin
git switch -c <branch> origin/main
```

### 3. Plan the steps

List 3-6 concrete steps. For each step, decide whether it should spawn an agent:

- **pattern-scout** before adding code in a new file or extending an existing pattern.
- **adr-checker** (consult) when the step touches an ADR-covered area.
- **test-runner** after each step.
- **docs-checker** at the end.

Share the plan with the user. Wait for approval if the steps are non-trivial.

### 4. Implement with TDD

Per step:

1. Write or update the failing test in `tests/`.
2. Run `uv run pytest tests/<file>.py -k <name>` to confirm it fails as expected.
3. Implement the smallest change in `src/mathagent/` that makes the test pass.
4. Run the test-runner agent (lint, format, type, test) and fix until everything is green.

Never use `--no-verify`, `--no-edit`, `--amend`, or any flag that skips a check.

### 5. Update docs

If the change is in an area listed in the docs-checker map, invoke the docs-checker agent and apply its suggestions. If the change supersedes an ADR, invoke adr-checker in maintain mode.

### 6. Commit

Commit only when explicitly asked. When asked:

```bash
git status
git diff
git log --oneline -10
git add <specific files>
git commit -m "$(cat <<'EOF'
<imperative one-line summary, under 70 chars>

<one short paragraph: why, not what. Link the issue with "Closes #N".>
EOF
)"
```

### 7. Push and open the PR

Only when explicitly asked.

```bash
git push -u origin <branch>

gh label create "waiting-for-human-check" --color "fbca04" --description "Needs a human to review before merging or progressing" 2>/dev/null || true

gh pr create \
  --title "<short imperative title under 70 chars>" \
  --assignee "@me" \
  --label "waiting-for-human-check" \
  --body "$(cat <<'EOF'
## Summary
<2-3 bullet points>

## Closes
Closes #<N>

## Test plan
- [ ] uv run pytest passes
- [ ] uv run ruff check . passes
- [ ] uv run mypy src tests passes
- [ ] Manual: <if applicable, e.g. python -m mathagent in each mode>

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Print the resulting PR URL.

## Rules

- Never commit, push, or open a PR without an explicit instruction from the user.
- Never bypass hooks or signing.
- One PR per issue unless the user asks otherwise.
- Keep PR titles under 70 characters. Use the body for details.
