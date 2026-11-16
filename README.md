# Coding Workflow Operations

[中文](zh/README.md) | English

Copy this exact instruction into Codex while it is open in the target project:

```text
Use $skill-installer to install https://github.com/wlvh/coding-workflow/tree/main/zh/skills/workflow-docs-sync, then immediately use $workflow-docs-sync to synchronize the current project's documentation and create a draft pull request. If the newly installed Skill is not registered in the current session, read SKILL.md from the installation directory returned by the installer and continue in the same turn; do not stop to request a restart.
```

It uses an explicitly supplied local target path or GitHub repository URL, otherwise infers the current Git
root, and infers the request language. Local targets use an external clean worktree to protect an unclean
original worktree; publication creates only a draft PR. A newly installed Skill is read from the installer’s
actual returned directory when the current session has not registered it yet.

This repository publishes bilingual downstream workflow-document templates, the canonical
`workflow-docs-sync` Skill, and its installer. Chinese under `zh/` is the semantic source; `en/` is derived.
The templates provide task routing, change propagation, combined behavior and open questions, and
user/interface navigation. Mature projects can keep a short guide that links to their existing documentation.

## Issue-driven coding loop

The [coding-loop v2 specification](en/docs/development_workflow/README.md) defines Issue-first development,
two-company Issue and PR review, continuous engineering responsibility, candidate-bound evidence, and
outcome acceptance. The [Chinese prompt sources](zh/prompts/README.md) and their
[source index](zh/prompts/coding_workflow.json) are canonical; executable English prompts remain
[en-pending](en/prompts/README.md).

Tongxu and other consumers pin an exact upstream commit. A user-requested upgrade compares the workflow
and prompts, adapts the execution controls, and validates them before enabling the version for new work.
See [version adoption](en/docs/development_workflow/version_adoption.md). Publishing this specification
does not claim the consumer's runtime capabilities are implemented. The documentation-sync Skill below
keeps its existing independent scope and behavior.

Detailed behavior and optional repository installation are in the [中文指南](zh/README.md#一句话开始) and
[English guide](en/README.md#one-line-start).

For source ownership, edit locations, and validation commands, use the
[Chinese maintainer map](zh/README.md#维护者地图).

## Related work

This repository maintains the coding-loop policy and project-document synchronization tools.
[Tongxu](https://github.com/wlvh/tongxu) is a consumer responsible for controlled execution,
coordination, progress, and the actual validation of its adopted workflow version.

[acceptance-agent](https://github.com/wlvh/acceptance-agent) covers the **acceptor** side: how a
separate verifier decides `accept` / `reject` / `request_evidence` from the spec, the final artifact,
and the test evidence — while being deliberately denied the builder's implementation conversation,
so it cannot inherit the builder's framing. It is a related project, not a mandatory third full review
after the coding loop's two-company review.

Author: [github.com/wlvh](https://github.com/wlvh) · [huaweidata.com](https://huaweidata.com)
