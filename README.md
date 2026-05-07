# Coding Workflow Operations

[中文](zh/README.md) | English

This repository root is the English public entrypoint for workflow templates,
user-facing docs, and operations runbooks. After choosing English, stay inside
the `en/` tree except for the shared implementation at
`scripts/sync_coding_workflow.py` and repository-level tests.

## Quick Start

Run English workflow docs sync from the target repository root:

```bash
curl -fsSL https://raw.githubusercontent.com/wlvh/coding-workflow/main/en/scripts/sync.sh | bash
```

Then follow PASS 1 through PASS 4 in
[en/scripts/OPERATIONS.md](en/scripts/OPERATIONS.md). English sync uses source
templates under `en/`, but installs them into the target repository's canonical
root paths.

## Directory Map

- [en/AGENTS.md](en/AGENTS.md): agent entrypoint, file map, coding rules, and document relationships.
- [en/architecture.md](en/architecture.md): architecture, module boundaries, data flow, and invariants.
- [en/capability_contract.json](en/capability_contract.json): machine-readable capability and behavior contract.
- [en/interact.md](en/interact.md): user-visible behavior and acceptance invariants.
- [en/TESTING.md](en/TESTING.md): testing strategy and evidence rules.
- [en/PR_Checklist.md](en/PR_Checklist.md): PR submission, commit, push, and PR body rules.
- [en/SOP.md](en/SOP.md): standard process entrypoints.
- [en/.github/pull_request_template.md](en/.github/pull_request_template.md): English downstream PR body template.
- [en/docs/business_user_guide.md](en/docs/business_user_guide.md): business-user guide.
- [en/docs/development_workflow/README.md](en/docs/development_workflow/README.md): English workflow overview.
- [en/prompts/](en/prompts/): English prompt catalog status.
- [en/scripts/OPERATIONS.md](en/scripts/OPERATIONS.md): English workflow docs sync runbook.
- [en/scripts/sync.sh](en/scripts/sync.sh): English template sync launcher.
- [en/scripts/sync_pr_review_system.md](en/scripts/sync_pr_review_system.md): English independent reviewer prompt.

## Install Path Rule

`en/` is an upstream source prefix; it is not installed into the target project.
Sync strips only the leading `en/` and writes the remaining path as-is:

- `en/AGENTS.md` -> `<target>/AGENTS.md`
- `en/docs/business_user_guide.md` -> `<target>/docs/business_user_guide.md`
- `en/.github/pull_request_template.md` -> `<target>/.github/pull_request_template.md`

The inner `.github` layout is preserved. The rule is prefix stripping only, not
special-case path rewriting.

## Language Policy

Chinese remains the source of truth. English is derived from the Chinese
workflow. When English coverage is pending, mark `en-pending` in the PR body and
avoid exposing untranslated flows as English-ready.

Root `README.md` intentionally mirrors the English entrypoint with
root-relative links, so the repository homepage stays useful without depending
on symlink rendering behavior.
