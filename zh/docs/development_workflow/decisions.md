# 工作流实现决策

## DEC-002：Workflow Skill 威胁模型采用 A 档

- 状态：accepted
- 日期：2026-07-16 UTC
- 决策：MVP 防善意执行者漏步骤、顺手越权和机械事实错误，不防与 harness 同权限、
  可修改 shell、Git、脚本和工作区的主动恶意执行者。
- 结果：删除 receipt chain、repository fingerprint、whole-tree installation
  identity、跨 Skill trust bootstrap 和 Git index 对抗型防御。
- 未来边界：对抗级防御属于 Coding Workflow Studio 的进程外 harness、OS sandbox
  和权限分离。
- 重审条件：进入无人值守分发，或 Studio M6 开始实现安全边界。
- 英文状态：`en-pending`。

## DEC-003：AI 与机械事实的信任边界

- 状态：accepted
- 日期：2026-07-16 UTC
- 决策：相信 AI 对项目语义、证据和文档改写的解释；不相信执行者自行证明 mode
  顺序、文件范围、upstream SHA、final gate、提交范围和远端 PR identity。
- 实现：调用方在 mode 边界运行薄 harness，直接检查普通 Git diff、pinned sync、
  pinned final gate 和真实 GitHub PR；不使用执行过程中的链式自证。
- 独立 reviewer：在执行 Skill 之外复核语义，并由 validator 派生 verdict。
- 用户边界：Gate W0 始终由用户负责，不移入 Skill。
- 英文状态：`en-pending`。

## DEC-004：SUBMIT 使用 evidence / seal / publish 三阶段

- 状态：accepted
- 日期：2026-07-17 UTC
- 决策：`prepare-submit` 只建立 active、unsealed baseline；提交 agent 先运行测试并
  填写 submission-owned evidence；`seal-submit` 在 commit 前运行 pinned final gate，
  封存 workflow snapshot、PR body 和精确 allowed paths；发布后由 `finish-submit`
  绑定 sealed 内容、实际 commit 与远端 PR。
- 失败恢复：普通 evidence 错误保留同一 active runtime 并重试 seal。PASS-owned 问题
  保留失败 runtime，从同一未变化 HEAD 的 fresh clone 新建 run，并完整重跑 PREPARE
  与四个 PASS；不要求中间 commit，也不把当前 worktree rebaseline。
- 排除项：不增加 receipt、hash chain、generic rebaseline、rollback framework 或
  Threat Model B 的 index / whole-tree 对抗机制。
- 英文状态：`en-pending`。
