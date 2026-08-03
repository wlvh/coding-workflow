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
- canonical Skill、安装器、测试、README、development workflow、DEC-006 与 DEC-007；
- 根 `.github/` 与 `zh/.github/`、`en/.github/` 的不同职责；
- 最短测试入口、`py_compile`、Skill quick validation、`git diff --check` 和 CLI help。

记录 candidate upstream SHA、exact prompt、执行者上下文边界和实际命令，并报告每个入口的
实际路径、findings 和歧义。路径缺失、链接错误、把根 GitHub 基础设施当成下游模板，或需要
会话外隐含知识才能找到验证入口时，Case G 失败。

## Case A：SEC_metrics 真实端到端

从 SEC_metrics 当前真实 Git HEAD 建立隔离目标，按项目命令的副作用与政策选择执行环境；不
复用旧 eval 结论或旧 shadow 文件。两轮固定同一 SEC code/config/test/committed-artifact base、
候选 upstream SHA、language 和 round 1 最终九文档 bytes；live 外部状态或任一 identity 变化都
使证据失效，必须重新冻结并从 clean target 重跑。

### Round 1 mandatory checks

第一次运行 `$workflow-docs-sync` 时：

- 从当前代码、配置、测试和 committed artifacts 重建 pipeline，专门核对 stage 10、11、12
  的输入、写入副作用、容错参数和 hard failure；
- 编辑前从真实目标选择并记录三条当前 scoped normative policy（例如 fail-fast、具体异常、
  显式数据契约）和两条描述性强声明；逐条记录 classification、authority/evidence、scope、
  conflict check 和 expected disposition，不注入人工 fixture；
- 静默删除已分类政策，或把描述性事实改写成祈使句来逃避证据核验，均为 FAIL；修改、保留或
  不更新 material policy 都记录 authority source；
- 主动寻找部分过时旧文档；
- 主动寻找多份文档彼此一致、但代码和测试不存在的共同虚构能力；
- 主动检查 light、golden、repair validation 是否被写成 full validation；
- 没有当前部署配置和运行证据时，不得声称生产调度完成；
- 对照 contract publisher 的 canonical grammar 与 SEC checker 真实 regex，记录 consumer 只
  支持 canonical form、不穷举 alias；记录 SEC 的 `ENTRY_STATUSES={active, deprecated}` 是项目
  侧加严，不要求通用模板复制该词表；
- 核对目标 `TESTING.md` 的 bug-first 与 no-test-diff 规则，正确且更具体的内容保持零 diff；
- 运行项目真实测试，准确记录验证层级，并完成 review 与最终 `check`。

这些检查是现实抽样。所选 HEAD 初始状态不含相应缺陷时，只能报告“本次未观察到”，不得写
成“已验证不存在”或“检测能力已验证”。若观察到缺陷，记录代码/测试反证、文档声明、修改和
复核结果。

### Round 2 strict convergence

以 round 1 最终九文档 bytes 为输入立即进行第二次完整运行，不依赖第一次过程说明，重新调查、
选择测试、review 并运行最终 `check`。记录前后 bytes、Git diff、测试选择、普通/暂存/untracked/
ignored 状态，并按以下唯一判定收口：

- `PASS_NOOP`：九文档相对 round 1 最终候选零 diff，且无 staged、untracked 或 ignored residue。
- `ROUND1_INCOMPLETE`：round 2 根据冻结目标中原已存在的代码、配置、测试或 artifact 反证发现
  有效新增修正；说明 round 1 调查不完整，整个两轮 gate FAIL。
- `ROUND2_DRIFT`：只有措辞、排序、格式或偏好变化，没有新增反证；说明最小改写不稳定，整个
  两轮 gate FAIL。

后两种结果都必须先修复候选或调查协议，再从 clean target 重跑完整 round 1 + round 2；不得
只补第三轮覆盖早期失败。第二次 `prepare` / `check` no-op 只能作为幂等性附加证据，不能代替
第二次完整 Case A。

### Alignment consumer validation

SEC checker 要求 evidence path 与 committed HEAD 一致。为不改变 primary Case A target identity：

1. round 2 获得 `PASS_NOOP` 后冻结九文档 bytes 与 digest；
2. 从同一 SEC base 创建第二个 disposable validation checkout；
3. 应用完全相同的九文档候选并创建 test-only commit；
4. 运行 `python3 tools/check_capability_contract_alignment.py --base-ref <SEC_BASE_SHA>`；
5. 记录 derived validation commit、publisher/consumer、exact command、结果、结构证明边界和
   cleanup；不得把 derived commit 冒充 primary target identity 或发布 commit。

Case A 最终记录包含：

- SEC_metrics target SHA、候选 upstream SHA 与 language，且两轮固定为同一对身份；
- 每轮的 exact prompt、实际 review mode 和 exact commands；
- independent reviewer 的会话/线程身份、启动时间与认知隔离边界；不可用时明确记录
  self-review，不得冒充 independent；
- 第一次运行的 files changed / digest、完整文档 diff、测试选择与结果、review findings 和原始
  final-check JSON；
- 第二次完整重新调查后的 files changed / digest、完整 diff、重新选择的测试与结果、review
  findings 和原始 final-check JSON；
- 对“部分过时旧文档、共同虚构能力、验证层级膨胀”的逐项结果：已观察到并检出，或本次未
  观察到；
- policy classification table、Anchor publisher/consumer/grammar/alias limitation、项目侧 status
  加严、derived alignment commit 和 cleanup；
- 正式 Case G/A raw record 的 candidate SHA、record URL 与内容 digest；最终 PASS 不覆盖早期
  failure、REOPENED 或 SUPERSEDED candidate/evidence；
- 未运行项、open decisions 和剩余风险。
