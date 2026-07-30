# Agent Working Guide

## Authority Map

- 当前代码、配置、测试、committed artifacts 和可重复运行结果是项目事实来源。
- `architecture.md` 定义系统结构与边界；`TESTING.md` 定义测试入口与证据层级；
  `PR_Checklist.md` 定义交付核对；`SOP.md` 只保存稳定流程入口。
- `capability_contract.json` 定义能力边界，`interact.md` 定义用户可观察行为与验收，
  `docs/business_user_guide.md` 只派生解释前两者。
- 现有文档是需要与实现核对的声明，不能单独证明自身正确。

<!-- project-fill: 补充本项目的其他权威来源及冲突优先级；完成后删除此 marker -->

## Repository Overview

文件简介只记录稳定模块、入口和职责，不永久镜像 `git ls-files`。

### Core Configuration

<!-- project-fill: 列出真实配置入口及其职责；如不适用，写 Not applicable — 已验证原因；完成后删除此 marker -->

### Runtime Entrypoints

<!-- project-fill: 列出用户、服务、作业或 CLI 的真实运行入口；完成后删除此 marker -->

### Core Modules

<!-- project-fill: 按稳定模块边界概述核心实现，不逐文件抄目录；完成后删除此 marker -->

### Domain Logic

<!-- project-fill: 说明领域规则所在模块及其权威测试或契约；完成后删除此 marker -->

### Generated Artifacts and External State

<!-- project-fill: 列出 committed/generated artifacts、持久化状态和外部系统；无此类状态时写 Not applicable — 已验证原因；完成后删除此 marker -->

## Change Impact Rules

- 模块边界、运行时调用链、数据流、状态、错误模型、外部依赖或扩展点变化时，更新或确认
  `architecture.md`。
- 能力边界变化时，先更新或确认 `capability_contract.json`，再检查 `interact.md` 和 business
  guide；用户可观察行为变化时，先更新或确认 `interact.md`。
- 测试仍是事实证据；具体命令、fixture、层级和隔离要求只在 `TESTING.md` 维护。
- 不要求每次修改全部文档。未更新受影响候选文档时，在交付说明中给出基于当前事实的
  no-update reason。
- 编码、lint、formatter、build 和类型规则必须从仓库真实配置提取，不从本模板推断。

## Collaboration

- 主执行者对最终判断、最终产物和最终写入结果负责；受委派结果必须经过审阅与合成。
- 并行写入时必须先明确不重叠的路径所有权；具体隔离方式遵循目标项目政策。
- 可按模块、调用链、风险或证据类型动态分工，不强制 Agent 数量或固定调度顺序。
- 协作者结论、投票或共识不等于证据；重要判断必须回到仓库事实和可重复验证。
- 调查与审查任务默认只读；需要修改时应显式移交给具有写入所有权的执行者。

<!-- project-fill: 补充本项目确有需要的协作或所有权规则；没有时删除此 marker -->

## Architecture

以 `architecture.md` 为架构权威。修改前从真实入口重建受影响调用链，修改后核对不变量、
模块职责、数据契约、状态、副作用和失败路径是否闭合。

## Testing

测试前完整读取 `TESTING.md`，从仓库配置确认 exact command。不得用 light、mock、golden
或局部 repair 成功冒充更高验证层级。测试环境由命令副作用、CI 能力和项目政策决定，并在
执行前确认隔离与清理边界。

## SOP

执行标准流程时读取 `SOP.md` 的对应入口。执行 checklist 保留在当前会话，不创建仓库内
运行状态、receipt 或临时流程文档。

## PR Delivery

- 遵循 `PR_Checklist.md` 和 `.github/pull_request_template.md`，以真实 Git diff、测试结果和
  最终仓库状态编写说明。
- 默认分支从仓库解析，不硬编码分支名。PR body 草稿位置与发布方式遵循目标项目政策；
  临时草稿不得被误提交，且 body 必须与真实 diff 和测试证据一致。
- 未经用户明确要求，不 commit、push 或创建 PR。

## Project-specific Conventions

<!-- project-fill: 从 lint、formatter、compiler、build 或团队配置提取项目专属约定；没有可验证约定时写 None — 已检查的配置范围；完成后删除此 marker -->
