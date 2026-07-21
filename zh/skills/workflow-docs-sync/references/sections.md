# 四领域只读分析

四个领域分析都以目标仓库当前代码、测试、九份现有文档和固定上游模板为证据。只读执行，
不编辑文件、不暂存改动、不运行会写项目 artifact 的命令，也不把发现写入磁盘。

每个分析返回同一结构：`Findings`（BLOCKER / WARN / NOTE）、`Evidence`（路径与符号或
行号）、`Proposed updates`（建议由主 Agent 落盘的文件和内容边界）、`Open decisions`。
事实不足时明确写未知；不得用上游模板替代项目事实。

## 1. Architecture

负责 `architecture.md`。

- 读取真实入口、核心模块、调用链、数据流、状态与错误模型、外部依赖、配置和扩展点。
- 核对架构不变量是否能由代码、配置或测试证伪；移除只描述愿景而无当前证据的断言。
- 区分三类问题：仍是模板或缺段；固定上游新增的通用写作要求未吸收；代码已经变化而
  文档未跟上。
- 只提出架构文档修改。能力、测试或治理影响作为下游建议交回主 Agent，不越界改写。

## 2. Capability / User Behavior

负责 `capability_contract.json`、`interact.md`、`docs/business_user_guide.md`。

- 从真实入口、响应、错误、测试和可见限制提取已实现能力、拒绝、追问、降级与责任边界。
- 以 `capability_contract.json` 为能力边界真相源，以 `interact.md` 为用户可观察行为和
  验收不变量真相源；business guide 只能教学性解释前两者已确认的内容。
- 递归核对稳定 `anchor_id`、Markdown 引用和测试证据；不依赖 JSON 数组位置或固定桶路径。
- 禁止把内部日志、仅代码可见状态、推测能力或未来计划写成用户已可用功能。
- 对模板残留、上游语义变化、代码或测试行为漂移分别给出证据和建议。

## 3. Testing

负责 `TESTING.md`。

- 盘点真实测试入口、层级、fixture、外部依赖、生成 artifact 的副作用和推荐执行顺序。
- 区分 unit、contract、scenario、golden、report build、repair/validation gate 与 live test；
  不用其中一层的成功替代另一层。
- 验证文档中的命令、环境前提、失败条件和产物与当前代码一致；标出重型或污染性命令，
  供主 Agent 在隔离 checkout 中运行。
- 判断已有覆盖、冗余测试、真实高价值缺口、mock-only 风险和不值得新增的测试。
- light review 只能按代码实际覆盖范围描述，不能写成 full validation。

## 4. Governance

负责 `PR_Checklist.md`、`SOP.md`、`AGENTS.md`、`.github/pull_request_template.md`。

- 从前三个领域的下游影响反向检查规则入口、文档关系、测试证据和文件地图是否闭合。
- 保持权威边界：`AGENTS.md` 做入口与规则，`SOP.md` 做流程骨架，`PR_Checklist.md`
  做提交核对，PR template 做长期通用 body 结构；避免四处复制易漂移细节。
- 核对所有命令、路径、分支和发布声明是否仍真实；没有当前代码或配置证据时，不得声称
  已完成生产部署、调度或自动化。
- PR template 可以直接继承固定上游内容；其他八份核心文档必须体现目标项目事实。
