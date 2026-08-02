# 合并前端到端 Eval

以下 Case 是 Skill 的真实合并门，不是单元测试或注入已知缺陷的阳性对照。只在最终候选
`upstream_sha` 上运行；后续代码、模板或合同变化都会使记录过期。每次保存固定 target SHA、
language、exact prompt、执行者与 review mode、exact commands、files changed / digest、findings
和原始 final-check JSON；未实际运行不得写“已验证”。目标仓库内不得出现 run state、ledger、
receipt、scratch 或 PR body。

## Case G：本仓库入口可导航性

让 fresh-context 执行者只从仓库根开始，不提供内部路径或维护说明。执行者必须能从根
`AGENTS.md` 与根 README 导航到中文 maintainer map，并准确找到：

- 双语下游模板源及中文语义源；
- canonical Skill、安装器、测试、README、development workflow 与 DEC-006；
- 根 `.github/` 与 `zh/.github/`、`en/.github/` 的不同职责；
- 最短测试入口、`py_compile`、Skill quick validation、`git diff --check` 和 CLI help。

记录 candidate upstream SHA、exact prompt、执行者上下文边界和实际命令，并报告每个入口的
实际路径、findings 和歧义。路径缺失、链接错误、把根 GitHub 基础设施当成下游模板，或需要
会话外隐含知识才能找到验证入口时，Case G 失败。

## Case A：SEC_metrics 真实端到端

从 SEC_metrics 当前真实 Git HEAD 建立隔离目标，按项目命令的副作用与政策选择执行环境；不
复用旧 eval 结论或旧 shadow 文件。第一次运行 `$workflow-docs-sync` 时：

- 从当前代码、配置、测试和 committed artifacts 重建 pipeline，专门核对 stage 10、11、12
  的输入、写入副作用、容错参数和 hard failure；
- 主动寻找部分过时旧文档；
- 主动寻找多份文档彼此一致、但代码和测试不存在的共同虚构能力；
- 主动检查 light、golden、repair validation 是否被写成 full validation；
- 没有当前部署配置和运行证据时，不得声称生产调度完成；
- 运行项目真实测试，准确记录验证层级，并完成 review 与最终 `check`。

这些检查是现实抽样。所选 HEAD 初始状态不含相应缺陷时，只能报告“本次未观察到”，不得写
成“已验证不存在”或“检测能力已验证”。若观察到缺陷，记录代码/测试反证、文档声明、修改和
复核结果。

在同一候选文档上立即进行第二次完整运行。重新调查和检查，但不得依赖第一次的过程说明；
记录前后九份文件 bytes、Git diff 与测试选择。预期是 no-op；只有新增项目事实要求的最小
改写才可接受，并必须说明触发证据。任何无事实依据的格式抖动、重复改写或新增过程状态均
失败。

Case A 最终记录包含：

- SEC_metrics target SHA、候选 upstream SHA 与 language，且两轮固定为同一对身份；
- 每轮的 exact prompt、实际 review mode 和 exact commands；
- 第一次运行的 files changed / digest、完整文档 diff、测试选择与结果、review findings 和原始
  final-check JSON；
- 第二次完整重新调查后的 files changed / digest、完整 diff、重新选择的测试与结果、review
  findings 和原始 final-check JSON；
- 对“部分过时旧文档、共同虚构能力、验证层级膨胀”的逐项结果：已观察到并检出，或本次未
  观察到；
- 未运行项、open decisions 和剩余风险。

第二次 `prepare` / `check` no-op 只能作为幂等性附加证据，不能代替第二次完整 Case A。
