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
- 后续：`workflow-docs-sync` 范围内的上述实现已由 DEC-005 替代；语义与
  机械事实的责任边界仍保留。
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
- 后续：`workflow-docs-sync` 范围内的三阶段实现已由 DEC-005 替代。
- 英文状态：`en-pending`。

## DEC-005：Workflow Docs Sync 采用单会话内建编排

- 状态：accepted
- 日期：2026-07-20 UTC
- 决策：用户每轮只调用一次 `$workflow-docs-sync`。主 Agent 是目标工作区的唯一
  写入者；Architecture、Capability / User Behavior、Testing、Governance 四个领域
  Agent 只读分析，内部对抗性审计 Agent 也只读。平台不支持 subagent 时，由主 Agent
  在同一会话按四个隔离章节顺序完成同样的语义检查。
- 数据边界：子 Agent 发现只通过当前会话返回，不写运行状态、result receipt、工单、
  模板镜像或 PR body。上游 checkout 和 SHA 由 Skill 内部解析并在同一轮固定复用；
  用户只提供目标仓库、可选语言和可选 draft PR 意图。
- 机械边界：`prepare` 只解析 Git 根目录与 SHA、在任何写入前检查 dirty allowlist，
  并补齐缺失模板；`check` 只读验证最终仓库状态。检查器不证明 Agent、审计或测试曾经
  执行，测试由主 Agent 实际运行并在最终报告记录。
- 发布边界：PR body、commit、push、远端绑定和 draft PR 创建不属于同步器。用户要求
  draft PR 时，由通用 GitHub 发布能力使用仓库外临时 Markdown body 完成。
- 替代关系：本决策在 `workflow-docs-sync` 范围内 supersede DEC-003 和 DEC-004 的旧
  实现；不保留旧 launcher、mode、harness、缓存模板或控制面兼容 fallback，Git 历史
  承担回滚。无 subagent 时的顺序执行是当前正式路径，不是旧实现 fallback。仍保留
  DEC-003 的原则：AI 负责项目语义与文档改写，机械层只判断可确定事实。
- 英文状态：`en-pending`。
