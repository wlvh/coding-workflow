# Coding Workflow Operations

[中文](zh/README.md) | English

This repository publishes bilingual downstream workflow-document templates, the canonical
`workflow-docs-sync` Skill, and its installer. Chinese under `zh/` is the semantic source; `en/` is derived.

Invoke the Skill once with only the target Git repository, `zh` or `en`, and whether a draft PR should be
created after success:

```text
Use $workflow-docs-sync for /absolute/path/to/repository in English.
Do not create a draft PR.
```

The repository root contains CI and GitHub infrastructure. Downstream `.github/` templates live under the
language directories and are installed without that leading language prefix.

For source ownership, edit locations, and validation commands, use the
[Chinese maintainer map](zh/README.md#维护者地图). English template and directory guidance is available in
[en/README.md](en/README.md).
