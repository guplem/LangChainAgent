---
description: Walk through review comments on a PR, decide Apply / Reject / Ambiguous for each with evidence, and post replies on GitHub.
---

# /review-pr-comments

You triage review comments on a pull request and respond to each with a clear decision and evidence.

## Arguments

The user passes a PR number, e.g. `/review-pr-comments 42`.

## Procedure

### 1. Read the PR and the comments

```bash
gh pr view <N> --json title,body,headRefName,baseRefName,url
gh pr diff <N>
gh api repos/:owner/:repo/pulls/<N>/comments
```

For each comment, capture: path, line, body, the original commenter, the thread id.

### 2. For each comment, decide

Three possible decisions:

- **Apply**: the comment is correct and you can make the change now. State the change you will make.
- **Reject**: the comment is wrong, off-scope, or contradicts an ADR. State the reason with evidence (link to ADR, cite file:line, point to a test).
- **Ambiguous**: the comment is unclear or depends on a tradeoff only the human can decide. State the question you would ask back.

Use the **pattern-scout** agent if a comment hinges on convention. Use the **adr-checker** agent if a comment touches an ADR-covered area.

### 3. Apply the Apply ones

Make the code changes, run the test-runner agent, and commit only if the user asks.

### 4. Post replies

For each comment, post a reply on GitHub with the decision and evidence:

```bash
gh api -X POST repos/:owner/:repo/pulls/<N>/comments \
  -f in_reply_to=<thread_id> \
  -f body="<reply>"
```

Reply format:

- **Apply**: "Applied in <commit-sha>. <one-line summary of the change>."
- **Reject**: "Will not apply. <reason with citation>."
- **Ambiguous**: "<the question back to the reviewer>."

### 5. Summarize

Print a table:

| Comment | Decision | Action |
|---|---|---|
| <path:line> | Apply | <commit> |
| <path:line> | Reject | <reason> |
| <path:line> | Ambiguous | <pending answer> |

## Rules

- Be evidence-based. Every Reject must cite a file, an ADR, or a test.
- Never push commits or merge the PR without explicit instruction.
- Never resolve a thread on the user's behalf. Only reply.
