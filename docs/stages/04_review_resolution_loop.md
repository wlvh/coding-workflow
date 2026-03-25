# 阶段 4：Review 争议处理与补丁回合

## 目标

当 GPT 5.4 Pro 提出问题后，不直接盲修，而是先验证问题是否存在，再决定是否值得引入额外复杂度。

## 输入

- GPT 5.4 Pro 的 review findings
- 本地完整代码
- 同一个 PR 的最新状态

## 输出

- 对 review finding 的证据分析
- 综合后的修复方案
- 更新后的既有 PR

## 执行顺序

1. 先不要动代码，使用 [prompts/review_recheck_local.md](../../prompts/review_recheck_local.md) 让 Codex GPT 5.4 thinking 和 Opus 分别验证问题是否存在。
2. 如果 Codex 和 Opus 意见不同，把 Opus 的意见再发回给 Codex，要求给出综合分析版本。
3. 如果双方分歧仍然很大，再把 GPT 5.4 对 Opus 的反驳发给 Opus，由 Opus 重新分析并按自己的方案执行。
4. 修复完成后，复用 [prompts/submit_existing_pr.md](../../prompts/submit_existing_pr.md) 更新既有 PR。

## 关键原则

- 先验真，再决定是否修。
- 修复建议要同时评估复杂度成本和收益。
- 同一个 PR 的 patch 可以在原对话里覆盖，以减少上下文过时问题。

## 下一步入口

修复并更新 PR 后，回到 [docs/stages/03_coding_to_pr.md](03_coding_to_pr.md) 的审核环节，或直接进入 [docs/stages/05_merge_post_merge_acceptance.md](05_merge_post_merge_acceptance.md)。
