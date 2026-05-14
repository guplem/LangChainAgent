---
description: Scaffold a new @tool in mathagent: write failing tests first, then implement, register, and teach the parser. Follows the project's TDD workflow.
---

# /add-tool

You add a new math tool to the LangChainAgent project. The workflow is strictly TDD: failing tests first, then code.

## Arguments

The user invokes the command with a description, e.g.:

```
/add-tool power: raise a to the b
```

If the description is missing, ask via `AskUserQuestion`:

- "What is the operation called (single lowercase word)?"
- "What does it do (one short sentence for the docstring)?"
- "Which keywords should the parser detect (e.g. for `power`: `power`, `to the`, `**`, `^`)?"

## Procedure

### 1. Pattern-scout

Run the **pattern-scout** agent to confirm the current conventions for tools, the parser, and tests. Apply whatever it reports.

### 2. Write failing tests first

Edit `tests/test_tools.py` and add:

```python
def test_<name>() -> None:
    assert <name>.invoke({"a": <a>, "b": <b>}) == <expected>
```

Plus an error-path test if the operation has one (e.g. divide-by-zero).

Edit `tests/test_parser.py` and add one parametrized case per keyword to `test_parses_known_phrasings`.

Run `uv run pytest -x` and confirm the tests fail because the symbol does not exist. If they pass for the wrong reason, the test is broken; fix it before continuing.

### 3. Implement the tool

In `src/mathagent/tools.py`:

```python
@tool
def <name>(a: float, b: float) -> float:
    """<one-line docstring: what it does, what it returns>."""
    <body>
```

Add the symbol to the import in `tests/test_tools.py`. Register it in `ALL_TOOLS`:

```python
ALL_TOOLS = [add, subtract, multiply, divide, <name>]
```

`TOOLS_BY_NAME` is recomputed from `ALL_TOOLS`, no change needed there.

### 4. Teach the parser

In `src/mathagent/parser.py`, extend `_OPERATION_KEYWORDS` with one entry per keyword:

```python
"<keyword>": "<name>",
```

### 5. Run the gate

```bash
uv run ruff check .
uv run ruff format .
uv run mypy src tests
uv run pytest
```

Use the **test-runner** agent if you prefer. Fix until everything is green.

### 6. Update docs

Invoke the **docs-checker** agent. At minimum, the README "Features" line about four tools needs updating, and the CLAUDE.md "Add a new tool" gotcha may need an extra example. Apply suggested edits.

### 7. Report

Print:

- File changes (paths and brief description)
- Test results (counts: passing/total)
- Whether docs were updated and how

## Rules

- Tools always return `float`. Even integer math goes through `float` for type consistency.
- Tools always take exactly two arguments `a: float, b: float`. If the operation is unary or n-ary, this scaffold does not fit. Ask the user whether to extend the parser to handle that signature, or to break it into multiple two-arg operations.
- Never skip the failing-test step. The test must fail first to prove it tests something.
- Never commit, push, or open a PR without explicit instruction. This command stops at "green test run + docs updated".
