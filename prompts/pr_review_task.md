# PR Review Task Prompt

## 用途

用于在正式 review 时补充本次 PR 的具体任务上下文。

## Prompt

```text
对 XX 项目的 PR XX（head XX）进行严格详细全面的代码审查。PR_BODY.md 是你重要的参考材料。并额外检查：
- 是否满足 FSD Core Contract
- 是否达到 Target State Bridge
- 是否遵守 TESTING.md / AGENTS.md / PR_Checklist.md
```
