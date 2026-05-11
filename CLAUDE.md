# CLAUDE.md — Project Working Rules

These rules apply to every task in this repository unless the user explicitly overrides them.
Bias toward caution on non-trivial work; use judgment and move quickly on trivial, reversible tasks.

## Project Snapshot

This is a Python MCP server for sequential thinking tools.

Common commands:

- Run tests: `uv run --extra dev pytest`
- Run a focused test: `uv run --extra dev pytest tests/test_models.py -q`
- Format Python: `uv run --extra dev ruff format .`
- Lint/fix Python: `uv run --extra dev ruff check --fix .`
- Type check: `uv run --extra dev basedpyright`

If a command is unavailable in the current environment, say so and choose the closest useful verification.

## Rule 1 — Think Before Coding

State assumptions when they affect the solution.
If the request is ambiguous, present the plausible interpretations and ask before making high-impact changes.
Push back when a simpler approach would solve the problem.
If confused, stop and name what is unclear.

## Rule 2 — Simplicity First

Write the minimum code that solves the stated problem.
Do not add speculative features, broad abstractions, or one-off frameworks.
Prefer boring, explicit code over clever code.
Test: would a senior maintainer call this overbuilt? If yes, simplify.

## Rule 3 — Surgical Changes

Touch only the files needed for the task.
Do not refactor, reformat, rename, or "clean up" adjacent code unless required.
Preserve existing style, public APIs, and behavior unless changing them is the point of the task.
Clean up only the mess introduced by this change.

## Rule 4 — Goal-Driven Execution

Define the success criteria before implementing.
Do not blindly follow a checklist; use the checklist to reach verified success.
Keep iterating until the success criteria are met or a blocker is surfaced.

## Rule 5 — Use Tools for Deterministic Work

Use the language model for judgment: design tradeoffs, classification, drafting, summarization, and explanation.
Use code, tests, search, and scripts for deterministic work: routing, counting, parsing, retries, formatting, and verification.
If code can answer a factual question reliably, let code answer it.

## Rule 6 — Manage Context and Token Budget

Keep each task focused.
If the work is becoming large, summarize the current state, decisions, and remaining work before continuing.
Do not silently exceed the scope implied by the request.
Surface when a task needs a fresh session, a separate plan, or user prioritization.

## Rule 7 — Surface Conflicts, Don't Average Them

If two patterns, requirements, or sources disagree, choose one intentionally.
Prefer the more local, recent, tested, or user-provided source.
Explain the choice briefly and flag the conflicting pattern for follow-up if needed.
Do not blend incompatible conventions.

## Rule 8 — Read Before Writing

Before changing code, inspect the relevant exports, immediate callers, tests, and shared utilities.
Do not assume a file is isolated just because it looks small.
If the structure seems odd, look for the reason before changing it.

## Rule 9 — Tests Verify Intent

Tests should encode why the behavior matters, not just what happens today.
Add or update tests when behavior changes or when fixing a bug.
A test that would still pass after breaking the intended behavior is not good enough.

## Rule 10 — Checkpoint on Significant Work

After each significant step, be able to state:

- What changed
- What was verified
- What remains
- Any uncertainty or blocker

For trivial edits, keep the checkpoint brief.

## Rule 11 — Match Repository Conventions

Conformance beats personal taste inside this codebase.
Follow existing naming, layout, dependency, typing, testing, and error-handling patterns.
If a convention appears harmful, surface it instead of silently forking the style.

## Rule 12 — Fail Loud

Do not claim completion if anything important was skipped.
Do not claim tests pass if tests were not run, failed, or were only partially run.
Report skipped verification, environmental limits, assumptions, and risks plainly.
