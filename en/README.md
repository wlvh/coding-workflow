# Coding Workflow Operations

[中文](../zh/README.md) | English

This directory provides English templates derived from the Chinese semantic source. The templates are
language-, framework-, and project-neutral. The canonical `workflow-docs-sync` Skill remains under
`zh/skills/workflow-docs-sync/` and reads English templates from the pinned upstream commit.

## One-line start

Copy this exact instruction into Codex while it is open in the target project:

```text
Use $skill-installer to install https://github.com/wlvh/coding-workflow/tree/main/zh/skills/workflow-docs-sync, then immediately use $workflow-docs-sync to synchronize the current project's documentation and create a draft pull request. If the newly installed Skill is not registered in the current session, read SKILL.md from the installation directory returned by the installer and continue in the same turn; do not stop to request a restart.
```

The instruction above is for first-time installation; once the Skill is installed, in another project directly ask `$workflow-docs-sync` to synchronize the current project's documentation and create a draft pull request.

The user does not provide an absolute target path, `zh` / `en`, a branch name, upstream SHA, or installation
path, and does not need to clean the target worktree first. A successful system `$skill-installer` run prints
`Installed workflow-docs-sync to <installed-skill-root>`. If the current session has not registered the
Skill, use that actual directory from this successful run, read its complete `SKILL.md`, resolve scripts from
the same directory, and continue in the current turn. Do not guess an installation path or wait for another
turn.

## Defaults

- Target: prefer an explicit local path, then an explicit GitHub repository URL; otherwise use the Git root
  containing Codex's current working directory. A Skill installation source URL is not treated as the target.
- Language: an explicit `zh` / `en` wins; otherwise a Chinese request selects `zh` and any other language
  selects `en`.
- PR: an explicit request not to create a PR selects false. Mentioning PR, opening, creating, or submitting a
  pull request selects true. No mention selects false. The Skill never marks a PR Ready or merges it.
- Worktree: for a local target and requested PR, create an external clean worktree and unique branch from the
  committed HEAD captured at invocation. Before the final report, byte-compare the captured NUL-delimited
  status and staged entries, then recheck type, mode, regular-file SHA-256, or symlink target only for paths in
  the invocation-time status. This still detects a dirty tracked file overwritten without changing its status
  code. The Skill does not enumerate, read, or hash ignored paths. Concurrent changes to pre-existing ignored
  content such as `.env`, virtual environments, `node_modules`, and caches are an accepted residual risk
  carried by running all work only in the external worktree. A GitHub URL is materialized as a real clone/fetch
  checkout and reports original-worktree protection as `NOT_APPLICABLE`.

For a local target, the final report states that the sync and PR use the invocation-time committed HEAD and
exclude uncommitted changes from the original worktree.

A repository with no commit is a `BLOCKER`. The final summary reports only five independent facts:
Candidate, Tests, Review, Process deviations, and Publication; it has no Overall or aggregate
PASS/PARTIAL/FAIL. Both unavailable readback and confirmed remote mismatch preserve the correct local
candidate and report `Publication: PR_BLOCKED`, with distinct recovery handling.

## Repository installer (optional)

This path is for maintainers or for installing both Codex and Claude copies; it is not the one-line entrypoint
above. Clone the canonical repository and verify that this upstream checkout is clean. That clean requirement
does not apply to the target project being synchronized:

```bash
git clone --depth 1 https://github.com/wlvh/coding-workflow.git
cd coding-workflow

git status --porcelain=v1 --untracked-files=all
python3 zh/scripts/install_skills.py --upstream-dir "$PWD"
```

`git status` should print nothing. If it prints an entry, stop and inspect the canonical checkout. A
successful JSON result lists actions for both `~/.agents/skills/workflow-docs-sync/` and
`~/.claude/skills/workflow-docs-sync/`.

To review and share the Skill as part of a target project, run this from the canonical checkout root:

```bash
python3 zh/scripts/install_skills.py \
  --scope repo \
  --target-repo "/absolute/path/to/target-repository" \
  --upstream-dir "$PWD"
```

The repo-scope target must be exactly a clean Git repository root. Review the resulting Git diff, then commit
it according to the target project's policy. Both scopes replace an existing Skill with the same name,
remove only the obsolete `workflow-docs-sync-review`, store no source state, and do not update automatically.
Studio can also load the canonical `zh/skills/workflow-docs-sync/` directly.

## Synchronization boundary

The Skill pins target HEAD and upstream SHA, reconstructs facts from current code, configuration, tests,
committed artifacts, reproducible results, and necessary Git history, then makes only the document changes
those facts require. Existing documents and upstream templates are hypotheses, not evidence.

Architecture, Capability / User Behavior, Testing, and Governance are coverage dimensions, not a fixed
agent topology. The main agent is the only execution-worktree writer. Test environments follow actual
commands, side effects, CI capabilities, and project policy.

Review prefers a fresh-context, blind-first independent reviewer. When cognitive isolation is unavailable,
the result is reported honestly as self-review. The deterministic checker proves final repository state
only, not investigation, test, or review history.

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

## Related Work

This repository covers the **producer** side: how an agent reconstructs repository facts from committed
code, config, tests, and artifacts, keeps changes to the minimum necessary, and delivers a reviewable
draft PR from an isolated clean worktree.

[acceptance-agent](https://github.com/wlvh/acceptance-agent) covers the **acceptor** side: how an
independent verifier decides `accept` / `reject` / `request_evidence` from the specification, the final
artifact, and the test evidence — while being deliberately denied the builder's implementation
conversation, so it cannot inherit the builder's framing.

Author: [github.com/wlvh](https://github.com/wlvh) · [huaweidata.com](https://huaweidata.com)
