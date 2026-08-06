# Standard Operating Procedures

## Purpose and Authority

`SOP.md` keeps stable process entrypoints and does not copy volatile commands, test lists, or publishing
details. When sources conflict, current code, configuration, tests, contracts, and focused authorities such
as `TESTING.md` and `PR_Checklist.md` take precedence. Follow this project's actual audit, recoverability,
and delivery policy for how execution records are stored and retained.

## Available SOPs

<!-- project-fill: List real project SOP names and authoritative entrypoints. If none exist, replace this with None and the scope checked, then remove this marker. -->

## SOP Entry Structure

Every SOP step contains only:

1. Action: the stable action to perform.
2. Authority / Source: the authoritative entrypoint to read without copying volatile details.
3. Acceptance: how current tests, artifacts, or observable results prove completion.

## Failure, Rollback, and Escalation

On failure, stop at a safe boundary and preserve the exact error and current repository state. Rollback
must match real persistence and side effects. Escalate missing authority, product decisions, or external
coordination to the responsible person instead of guessing or bypassing the boundary.

<!-- project-fill: Add verified stop conditions, recoverable rollback entrypoints, and escalation ownership. If no project-specific rules exist, write None with a verified reason, then remove this marker. -->

Use LF line endings and UTF-8 for text files unless repository configuration explicitly requires another
format.
