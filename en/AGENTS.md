## File Overview

### Core Config

- `AGENTS.md`: Agent entrypoint, file overview, coding rules, and user-facing document relationships.
- `capability_contract.json`: Cross-project sample registry for capability boundaries, responsibility boundaries, and agent behavior commitments.
- `.github/pull_request_template.md`: Long-term PR body template used to draft local `PR_BODY.md`.

### Core Modules

### Business Logic

### Notes

- When files are added or changed, update this file overview where relevant. Test files are governed by `TESTING.md`.
- All repository files use UTF-8. Command-line reads and edits must explicitly use UTF-8.
- One-off artifact folders are exempt from this overview when explicitly approved.

## Architecture

The authoritative architecture document is `architecture.md`. If a change affects module boundaries, runtime call flow, data flow, state model, error model, external dependencies, or extension points, update `architecture.md`; otherwise explain the no-update reason in the PR body.

## Business Knowledge

## Review Checklist

When the user asks you to submit a PR, fully follow `PR_Checklist.md`; any exemption must be explained in the PR description.

## Testing Flow

Before fixing bugs, starting tests, or submitting a PR, read and follow `TESTING.md`. Main branch changes must go through PR merge only.

## SOP

When you execute a standard process, read and follow `SOP.md`; when SOP entries are added or changed, update this list with the SOP name.

## User-Facing Document Relationships

This project distinguishes three user-facing sources of truth:

1. `capability_contract.json`
   - Machine-readable source for capability boundaries.
   - Answers what the system can do, cannot do, must ask about, or must refuse.

2. `interact.md`
   - Source for user-visible behavior and acceptance invariants.
   - Answers how the system must behave and what acceptance means.

3. `docs/business_user_guide.md`
   - Derived teaching document for first-time business users.
   - Answers what business users can ask, how to ask, how to read results, and when to ask a human.
   - It must not declare independent capabilities; it only explains capabilities and behavior already declared in `capability_contract.json` and `interact.md`.

Update rules:

- If capability boundaries change, update or confirm `capability_contract.json` first, then check `interact.md` and `docs/business_user_guide.md`.
- If user-visible behavior changes, update or confirm `interact.md` first, then check `docs/business_user_guide.md`.
- If business-user questions, prompts, result interpretation, or escalation guidance change, check `docs/business_user_guide.md`.
- Any "can do / cannot do / must ask / must refuse" statement in `docs/business_user_guide.md` must anchor to `capability_contract.json`, `interact.md`, or tests.

## Coding Rules

1. What I cannot create, I do not understand.
2. Use the project's selected working language; answer in English unless user or project instructions require otherwise. Code volume is a liability after functionality is met; keep code as small as possible, then optimize for maintainability.
3. Follow PEP 8 for Python. Use UTC time. Use UTF-8 text.
4. Manage parameters centrally. Always call functions with explicit parameter names instead of relying on positional defaults. Do not use `get` for expected parameters; fail fast when a required parameter is missing.
5. Every class and function needs a docstring. Each functional block inside a function needs comments explaining why, expected output, and parameter meaning, range, and format. Script-level docstrings must explain purpose and call relationships.
6. Do not let `try/except` or `if/else` blocks run naked. Use explicit exception types and enough print/log information in `except` and `else` branches. Unexpected errors should fail inside the current function.
7. Data in, data out: scripts, functions, and modules interact only through explicit data inputs and outputs, not hidden external state.
8. Reused code blocks should be wrapped into functions or modules to keep code DRY.
9. Use language features to reduce code and performance cost while keeping readability.
10. Do everything necessary to help the user reach the goal.
