# Development Workflow

This document is the English overview for the repository's human-in-the-loop
coding workflow. The Chinese workflow remains the source of truth; this file
only exposes the English path and the current English coverage boundary.

## Main Flow

1. Define the requirement.
2. Draft the `FSD Core Contract` with the Pro web model when local repository
   exploration is not available.
3. Use a Target State Bridge agent to compare the FSD, current repository code,
   and authoritative docs, then produce the `Repo Impact Forecast` and
   `Target State Bridge`.
4. Use an Issue agent to turn the FSD, forecast, and bridge into an executable
   issue contract.
5. Let the coding agent implement the issue after reading `AGENTS.md`,
   `SOP.md`, `TESTING.md`, `PR_Checklist.md`, `interact.md`, and any project
   capability or business-user docs.
6. Review the PR with business context first, then implementation quality,
   test realism, and maintainability.
7. When reviewer findings appear, do not change code first. Verify each finding
   through code reading, a minimal reproduction, targeted tests, or a path close
   to real use. If a finding is real, report the analysis before fixing it:
   check the PR description for similar prior fixes and, if any exist, define
   an end-to-end acceptance plan that prevents repeated rework; assess affected
   upstream inputs, the current module, downstream callers, equivalent entry
   points, and adjacent scenarios; and determine whether test notes, user docs,
   architecture or workflow docs, the PR description, or the Review / Fix
   Record must be updated, stating why if no update is needed.
8. Keep PRs as one external commit when updating an existing PR, and keep
   `PR_BODY.md` as local PR-body scratch unless the target project explicitly
   tracks it.
9. After merge, summarize the PR from a tech-lead perspective and run
   user-view acceptance when useful.

## Core Artifacts

- `FSD Core Contract`: requirement contract that can be implemented, tested,
  and reviewed.
- `Repo Impact Forecast`: predicted repository touch points, risks, docs, and
  test impact.
- `Target State Bridge`: target user or caller-visible state and validation
  method.
- `Issue`: executable development contract.
- `PR_BODY.md`: local PR body draft generated from `.github/pull_request_template.md`.
- `Workflow Docs Sync`: one invocation that maps current code, performs four
  read-only domain analyses, lets the main agent update documents, runs a
  read-only adversarial audit, executes tests, and checks final repository state.

## English Coverage Boundary

English workflow docs are intentionally exposed only when the English path is
ready. The long prompt pack is not yet published as English-ready; see
[en/prompts/README.md](../../prompts/README.md). If a PR changes Chinese prompt
semantics without updating English, mark `en-pending` in the PR body.

## Workflow Docs Sync

Invoke `$workflow-docs-sync` once with the target repository, optional `en`
language, and optional draft-PR intent. Upstream checkout and commit resolution
are internal. The main agent is the only workspace writer; domain agents and
the adversarial auditor return read-only findings in the current session.

The deterministic script has only two internal commands: `prepare` installs
missing templates without replacing existing documents, and `check` validates
the final repository state. The entire sync flow neither creates, reads, rewrites,
nor deletes repository-local `PR_BODY.md`. It creates no run records, runs no
target test command, and performs no commit, push, or GitHub operation. If the
user asks for a draft PR, the post-check publishing step uses a temporary
Markdown body outside the repository and the general GitHub publishing ability.

Key implementation files:

- `../../../zh/skills/workflow-docs-sync/SKILL.md`: orchestration contract.
- `../../../zh/skills/workflow-docs-sync/references/sections.md`: four domain analyses.
- `../../../zh/skills/workflow-docs-sync/references/audit.md`: adversarial audit.
- `../../../zh/skills/workflow-docs-sync/scripts/sync_docs.py`: mechanical preparation and check.
- `../../../tests/test_workflow_docs_sync.py`: regression tests.
