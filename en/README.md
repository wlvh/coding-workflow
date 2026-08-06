# Coding Workflow Operations

[中文](../zh/README.md) | English

This directory provides English templates derived from the Chinese semantic source. The templates are
language-, framework-, and project-neutral. The canonical `workflow-docs-sync` Skill remains under
`zh/skills/workflow-docs-sync/` and reads English templates from the pinned upstream commit.

## Quick Start

Invoke the Skill once with the target Git repository, `zh` or `en`, and whether to create a draft PR after
success:

```text
Use $workflow-docs-sync for /absolute/path/to/repository in English.
Do not create a draft PR.
```

The Skill pins target HEAD and upstream SHA, reconstructs facts from current code, configuration, tests,
committed artifacts, reproducible results, and necessary Git history, then makes only the document changes
those facts require. Existing documents and upstream templates are hypotheses, not evidence.

Architecture, Capability / User Behavior, Testing, and Governance are coverage dimensions, not a fixed
agent topology. The main agent is the only target-workspace writer. Test environments follow actual
commands, side effects, CI capabilities, and project policy.

Review prefers a fresh-context, blind-first independent reviewer. When cognitive isolation is unavailable,
the result is reported honestly as self-review. The deterministic checker proves final repository state
only, not investigation, test, or review history.

The installer copies only the canonical Skill. Before any target mutation it rejects symlinks, invalid
frontmatter, and ignored source residue that would otherwise be copied; it stores no source receipt.

## Template Contract

Markdown project-fill slots use `<!-- project-fill: ... -->`; JSON uses strings prefixed with
`__PROJECT_FILL__:`. Target projects replace or delete every active marker before final `check`. Templates
at a pinned source object retain at least one active marker in every non-PR file; the PR template is exempt.
Templates do not assume a programming language, framework, test runner, service, or default branch.

## Maintainer Map

- Downstream templates: edit the nine core files under `zh/` as the Chinese semantic source, then derive the
  matching `en/` paths.
- Canonical Skill: `../zh/skills/workflow-docs-sync/`.
- Installer: `../zh/scripts/install_skills.py`.
- README entrypoints: the root README is a summary, `../zh/README.md` is the Chinese maintainer entry, and
  this file is derived from it.
- Development workflow and decisions: `../zh/docs/development_workflow/`; the English overview is under
  `docs/development_workflow/README.md`.
- Scenario tests: `../tests/test_workflow_docs_sync.py`; test code owns the detailed constraints.
- GitHub paths: root `.github/` serves this repository, while `.github/` here and under `zh/` are downstream
  template sources.

The residue-safe shortest entrypoint is
`PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider`. The full closure sequence is maintained
only in the [Chinese maintainer map](../zh/README.md#维护者地图).

## Directory Map

- [AGENTS.md](AGENTS.md): authority entrypoint, stable module map, and impact rules.
- [architecture.md](architecture.md): system purpose, call flows, boundaries, state, and side effects.
- [capability_contract.json](capability_contract.json): capability, boundary, responsibility, and behavior
  anchors.
- [interact.md](interact.md): user-visible behavior and acceptance.
- [docs/business_user_guide.md](docs/business_user_guide.md): first-use business guide.
- [TESTING.md](TESTING.md): test entrypoints, layers, isolation, and evidence.
- [PR_Checklist.md](PR_Checklist.md): general PR todo and target-project publishing-policy boundary.
- [SOP.md](SOP.md): stable standard-process entrypoints.
- [.github/pull_request_template.md](.github/pull_request_template.md): long-term PR body structure.
- [docs/development_workflow/README.md](docs/development_workflow/README.md): English workflow overview.
- [../zh/skills/workflow-docs-sync/](../zh/skills/workflow-docs-sync/): canonical Skill implementation.

## Install and Language Boundary

`en/` is an upstream source prefix, not a target directory. Sync removes only the leading `en/` and keeps
the remaining path, including `.github/`.

Chinese is the semantic source and English is derived. Bilingual content changed by a PR closes in that PR;
translation status in unchanged historical decisions remains a historical record.
