# Coding Workflow Operations

[中文](zh/README.md) | English

Copy this exact instruction into Codex while it is open in the target project:

```text
Use $skill-installer to install https://github.com/wlvh/coding-workflow/tree/main/zh/skills/workflow-docs-sync, then immediately use $workflow-docs-sync to synchronize the current project's documentation and create a draft pull request. If the newly installed Skill is not registered in the current session, read SKILL.md from the installation directory returned by the installer and continue in the same turn; do not stop to request a restart.
```

It infers the current Git root and request language, preserves an unclean original worktree through an
external clean worktree, and creates only a draft PR. A newly installed Skill is read from the installer’s
actual returned directory when the current session has not registered it yet.

This repository publishes bilingual downstream workflow-document templates, the canonical
`workflow-docs-sync` Skill, and its installer. Chinese under `zh/` is the semantic source; `en/` is derived.

Detailed behavior and optional repository installation are in the [中文指南](zh/README.md#一句话开始) and
[English guide](en/README.md#one-line-start).

For source ownership, edit locations, and validation commands, use the
[Chinese maintainer map](zh/README.md#维护者地图).
