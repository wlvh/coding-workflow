# PR Submission Checklist

本文件本身就是提交前 todo。只勾选已经由当前 diff、测试输出或仓库状态证明的项目；不适用
时记录原因。除非用户明确要求，不执行 commit、push 或 PR 创建。

<!-- project-fill: 补充本项目特有的审批、提交、base/head 或发布 gate；没有项目专属要求时删除此 marker -->

## Scope and Git State

- [ ] 从 repository default branch 解析 `<base>`，确认当前工作分支和目标分支正确。
- [ ] 检查 `git status`、工作树 diff、暂存区 diff 和 `git diff --name-only <base>...HEAD`。
- [ ] 实际变更范围与交付说明一致，不包含本地草稿、秘密、生成垃圾或未落地计划。
- [ ] 团队若采用单 commit，将其视为可替换的团队默认；否则遵循仓库现有提交策略。重写远端
  历史前必须有明确授权，并使用安全的 lease 保护。

## Tests and Evidence

- [ ] 按 `TESTING.md` 和当前仓库配置选择真实命令，没有从模板猜测 runner 或服务。
- [ ] 每条测试记录 exact command、scope、result、not-run reason、实际环境和隔离方式。
- [ ] 环境选择与命令副作用、CI 能力和项目政策一致；写入、外部状态、残留和清理结果均有
  可核对记录。
- [ ] 失败、跳过和验证层级被准确描述；light、golden 或 repair 未冒充 full validation。

## Documentation and Contracts

- [ ] 已按真实影响检查 `AGENTS.md`、`architecture.md`、`capability_contract.json`、
  `interact.md`、business guide、`TESTING.md` 和 `SOP.md`；无需更新的候选项有真实
  no-update reason，不要求为了齐全而修改所有文档。
- [ ] 能力变化遵循 `capability_contract.json → interact.md → business_user_guide.md` 的权威
  方向；用户可见声明有当前实现或测试证据和稳定 anchor。
- [ ] 架构影响已核对入口、模块边界、数据流、状态、错误模型、外部依赖、artifact 和副作用。
- [ ] 所有 active project-fill marker 已替换或删除，Markdown 与 JSON 仍可被严格解析。

## Review Closure

- [ ] 已完成本项目测试与交付政策要求的 review gate，并准确记录 reviewer 身份、范围和限制。
- [ ] 所有 BLOCKER 和不需要新产品决策的 actionable WARN 已修复并复核；其余问题进入 open
  decisions，包含证据与影响。
- [ ] 修复后重跑受影响测试和机械检查，最终 diff 与 Git 状态已再次检查。

## PR Delivery

- [ ] PR body 只写当前已完成事实，并使用 `.github/pull_request_template.md` 的结构。
- [ ] PR body 的草稿位置、发布工具和提交方式遵循目标项目政策；临时草稿不得被误提交，且
  body 必须与真实 diff 和测试证据一致。
- [ ] base 使用 `<base>` 或 repository default branch，不硬编码某个分支名。
- [ ] 只有用户要求时才创建 draft PR；发布前再次确认 title、base、head、body 和实际 diff。
