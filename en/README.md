# Coding Workflow Operations

[中文](../zh/README.md) | English

This directory contains the English workflow-document templates. The canonical
single-session Skill is shared from `zh/skills/workflow-docs-sync/` and reads the
selected English templates from the pinned upstream commit.

## Quick Start

Invoke the Skill once and provide only the target repository, optional language,
and optional draft-PR intent:

```text
Use $workflow-docs-sync for `/absolute/path/to/repository` in English.
Do not create a draft PR.
```

The main agent is the only target-workspace writer. Architecture, capability and
user behavior, testing, governance, and adversarial audit analysis are read-only.

## Directory Map

- [AGENTS.md](AGENTS.md): agent entrypoint, rules, and document relationships.
- [architecture.md](architecture.md): architecture and system-boundary template.
- [capability_contract.json](capability_contract.json): machine-readable capability contract.
- [interact.md](interact.md): user-visible behavior and acceptance template.
- [TESTING.md](TESTING.md): testing strategy and evidence template.
- [PR_Checklist.md](PR_Checklist.md): general PR submission template.
- [SOP.md](SOP.md): standard-process entrypoint template.
- [.github/pull_request_template.md](.github/pull_request_template.md): downstream PR body template.
- [docs/business_user_guide.md](docs/business_user_guide.md): business-user teaching template.
- [docs/development_workflow/README.md](docs/development_workflow/README.md): English workflow overview.
- [../zh/skills/workflow-docs-sync/](../zh/skills/workflow-docs-sync/): canonical Skill implementation.

## Install Path Rule

`en/` is an upstream source prefix, not a target directory. Sync strips only the
leading `en/` and preserves the rest of each path:

- `en/AGENTS.md` -> `<target>/AGENTS.md`
- `en/docs/business_user_guide.md` -> `<target>/docs/business_user_guide.md`
- `en/.github/pull_request_template.md` -> `<target>/.github/pull_request_template.md`

Chinese remains the workflow source of truth. English is derived; unfinished
coverage must be marked `en-pending` instead of being presented as ready.
