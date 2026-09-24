# Agent Working Guide

## Authority Map

- 描述性事实核对当前代码、配置、测试、committed artifacts 和可重复运行结果；规范性政策
  核对有效的项目授权与政策依据，混合语句拆开处理。文档不能单独证明自身的事实声明。
- 已有正式用户文档、接口规范和已接受政策继续在各自覆盖范围内有效；生成文档不因文件名
  自动覆盖既有权威。冲突按项目已有的适用范围和替代规则处理。
- `architecture.md` 定义系统结构与边界；`TESTING.md` 定义测试入口与证据层级；
  `PR_Checklist.md` 定义交付核对；`SOP.md` 只保存稳定流程入口。
- `capability_contract.json` 登记选定的公开承诺与边界；`interact.md` 展开交互语义；
  `docs/business_user_guide.md` 负责使用说明和正式接口导航，均须尊重上述权威范围。

<!-- project-fill: 列出本项目已有的正式文档、接口规范、政策依据及各自覆盖范围和既有冲突处理规则；完成后删除此 marker -->

## Task Routing

按当前任务选择入口，再沿相关证据继续调查，不要求每次完整读取九份文档。

| 任务 | 优先入口 | 随后核对 |
|---|---|---|
| 局部修复、内部实现 | `TESTING.md` | 相关实现和既有测试 |
| 用户可观察行为变化 | `interact.md`、`TESTING.md` | 正式接口、失败路径和行为测试 |
| 公共能力或数据约定变化 | `capability_contract.json`、`architecture.md`、`interact.md` | 对应实现、调用方和验证 |
| 共享组件变化 | `architecture.md`、`TESTING.md` | 使用该组件的入口与相关回归 |
| 项目使用或外部调用 | `docs/business_user_guide.md`、正式接口参考 | 实际 API、CLI 或协议 |
| 合并与发布 | `PR_Checklist.md`、PR template | 实际 diff、测试和文档 |
| 未决公共语义 | `interact.md` 的 Open questions、相关 Issue | 既有规则、当前授权和项目决定 |

- 事实不清楚：继续调查。
- 内部实现有多种方式，但外部行为等价：自行选择最简单、最符合项目风格的方式。
- 事实已查清，仍有超出当前授权的实质性公共语义分歧：提出具体问题，交给 maintainer/owner。

变更传播关系只在 [architecture.md 的 Change propagation](architecture.md#change-propagation)
维护；按相关关系调查，在 `TESTING.md` 查找对应验证。只更新受影响内容；确受影响但保持不变
的文档，在交付说明中写明事实或政策依据。编码、lint、formatter、build 和类型规则从仓库
真实配置提取，不从本模板推断。

`Not applicable` 表示经核对确实不适用；`Not configured` 表示适用的机制尚未配置；尚未确认
表示证据不足。三者不能互相替代，均须说明已检查范围与原因，不能把证据不足写成不适用。

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

## Collaboration

- 主执行者对最终判断、最终产物和最终写入结果负责；受委派结果必须经过审阅与合成。
- 并行写入前明确不重叠的路径所有权，共享状态的更新须统一协调；具体隔离方式遵循目标项目政策。
- 委派须有明确收益，如缩短整体完成时间、隔离大量原件读取、专业分工或独立审阅；不要求主动
  拆分，也不固定数量或顺序。case、公司、指标或文件不同本身不是拆分理由，不得为分工重复建立
  相同背景。
- 派发时简要交代已查明的结论、证据来源和剩余范围；上下文继承不一定包含工具输出，不能假定
  子代理看过主执行者读过的内容。
- 派发或复用结论前，核对当前可访问的任务记录与已有结果的对象版本、范围、判断标准和完成情况；
  结果路径存在不代表完成。只补做新增、未完成或失效的部分；同一执行任务不重复派发，增量优先
  交给原执行者。
- 独立审阅不得继承作者的工作对话；有的平台默认继承，新线程不等于隔离。可以提供审阅对象、
  需求、证据和待核主张，但作者说明和已有 finding 不作为证据。无法确认隔离的不算独立审阅，
  不能用于满足独立审阅要求。独立审阅与复核仍须覆盖要求的完整范围，必要的重复调查不受去重
  限制，批量分工不能冒充独立复核，用户安排的跨模型验证照常进行。
- 协作者结论、投票或共识不等于证据；重要判断必须回到对应的事实证据或有效政策依据。
- 调查与审查任务默认只读；需要修改时显式移交给具有写入所有权的执行者。子任务权限不超出当前
  有效授权和派发范围，继承的会话内容不增加权限。

<!-- project-fill: 补充本项目确有需要的协作或所有权规则；没有时删除此 marker -->

## Architecture

按 `architecture.md` 的覆盖范围读取架构说明及其引用的既有规范。修改前从真实入口重建
受影响调用链，修改后核对不变量、模块职责、数据契约、状态、副作用和失败路径是否闭合。

## Testing

测试前完整读取 `TESTING.md`，从仓库配置确认 exact command。不得用 light、mock、golden
或局部 repair 成功冒充更高验证层级。测试环境由命令副作用、CI 能力和项目政策决定，并在
执行前确认隔离与清理边界。修改现行规则时直接替换旧表述，并同步它的真实行为测试。

## SOP

执行标准流程时读取 `SOP.md` 的对应入口。执行记录是否保存、保存位置与保留期限遵循本项目
真实的审计、可恢复性和交付政策。

## PR Delivery

- 遵循 `PR_Checklist.md` 和 `.github/pull_request_template.md`，以真实 Git diff、测试结果和
  最终仓库状态编写说明。
- 默认分支从仓库解析，不硬编码分支名。PR body 草稿位置与发布方式遵循目标项目政策；
  临时草稿不得被误提交，且 body 必须与真实 diff 和测试证据一致。
- 未经用户明确要求，不 commit、push 或创建 PR。

## Project-specific Conventions

<!-- project-fill: 从 lint、formatter、compiler、build 等机器 enforcement，以及当前有效且适用于本范围的 repository/team instruction 或 accepted decision 提取项目专属约定；区分 machine-enforced 与 owner-declared，并标明权威来源、作用域和已检查冲突。个人/会话偏好仅在被明确采纳为项目政策并写入仓库权威后保留；没有可验证约定时写 None — 已检查的配置和治理范围；完成后删除此 marker -->
