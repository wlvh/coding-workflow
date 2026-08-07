# Coding Workflow Operations

[中文](zh/README.md) | English

Copy this exact instruction into Codex while it is open in the target project:

```text
用 $skill-installer 安装 https://github.com/wlvh/coding-workflow/tree/main/zh/skills/workflow-docs-sync，然后立即用 $workflow-docs-sync 同步当前项目文档并创建 draft PR；如果当前会话尚未注册新 Skill，直接读取安装器返回目录中的 SKILL.md 继续执行，不要停下来要求重启。
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
