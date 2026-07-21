# Coding Workflow Operations

[中文](zh/README.md) | English

This repository publishes bilingual workflow-document templates and the
`workflow-docs-sync` Skill that specializes them against a real target repository.

## Quick Start

Invoke the Skill once. Provide only the target repository, optional language
(`zh` or `en`), and whether to create a draft PR after successful validation.

```text
Use $workflow-docs-sync for /absolute/path/to/repository in English.
Do not create a draft PR.
```

The main agent is the only workspace writer. Four domain analyses and the
adversarial audit are read-only; the final checker validates repository state,
not execution history. Upstream checkout and commit resolution are internal.

## Directory Map

- [en/](en/): English templates and workflow documentation.
- [zh/](zh/): Chinese source templates, prompts, decisions, and Skill implementation.
- [zh/skills/workflow-docs-sync/](zh/skills/workflow-docs-sync/): single-session orchestration, read-only analysis references, and the deterministic checker.
- [tests/test_workflow_docs_sync.py](tests/test_workflow_docs_sync.py): sync and installer regression tests.

## Install Path Rule

The `zh/` and `en/` directories are upstream source prefixes. The Skill strips
only the selected leading language directory and installs the remaining paths at
the target repository root. Inner paths such as `.github/` remain unchanged.

Chinese remains the source-of-truth workflow. English is its derived language
path; unfinished English coverage must be identified explicitly as `en-pending`.
