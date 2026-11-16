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

## Coding workflow

The [development workflow](en/docs/development_workflow/README.md) starts with an Issue and acceptance
criteria. A coding agent investigates, implements, and tests. LLMs from two different LLM companies
independently review both Issues and PRs, then exchange conclusions.

[Prompt sources](zh/prompts/README.md) · [Source index](zh/prompts/coding_workflow.json) ·
[Version adoption for automation](en/docs/development_workflow/version_adoption.md) ·
[English prompt status](en/prompts/README.md)

Detailed behavior and optional repository installation are in the [中文指南](zh/README.md#一句话开始) and
[English guide](en/README.md#one-line-start).

For source ownership, edit locations, and validation commands, use the
[Chinese maintainer map](zh/README.md#维护者地图).

## Related work

- [Tongxu](https://github.com/wlvh/tongxu): AI project management and execution.
- [acceptance-agent](https://github.com/wlvh/acceptance-agent): independent acceptance from specifications,
  final artifacts, and test evidence.

Author: [github.com/wlvh](https://github.com/wlvh) · [huaweidata.com](https://huaweidata.com)
