# 合并前端到端 Eval

以下 Case 是 Skill 的真实合并门，不是单元测试或注入已知缺陷的阳性对照。只在最终候选
`upstream_sha` 上运行；后续代码、模板或合同变化都会使记录过期。每次保存固定 target SHA、
language、exact prompt、执行者与 review mode、exact commands、files changed / digest、findings
和原始 final-check JSON；未实际运行不得写“已验证”。目标仓库内不得出现 run state、ledger、
receipt、scratch 或 PR body。

## Case G：Marker 必要性门

让 fresh-context 执行者只从仓库根开始，只提供以下 exact prompt，不提供路径、DEC、测试入口
或历史结论：

```text
请在这个仓库中增加一种新的 Markdown project-fill marker，并同步必要的中英文模板、测试和说明。先调查仓库，但不要 commit、push 或创建 PR。
```

执行者必须先调查现有两个 active marker、真实 consumer 与 DEC-006 的机制必要性合同，再判断
新 Markdown marker 是否承担独立状态、真实消费者和可复现失败路径。Case G 只有两种合法
PASS：

1. 证明新 marker 承担独立状态，并完成覆盖该状态的最小双语模板、测试与说明修改；
2. 证明现有两个 marker 已覆盖请求风险，有证据地拒绝新增同义 marker，并保持零 diff。

正式记录包含 target/candidate SHA、exact prompt 明文、files read、files changed、necessity
judgment、是否发现现有两个 marker 已足够、navigation mistakes 和 verdict。只报告链接或 anchor
数量的 navigation audit 可以保留为 smoke，但不是正式 Case G，也不是第三个正式 eval。

## Case A：SEC_metrics 真实端到端

从 SEC_metrics 当前真实 Git HEAD 建立隔离目标，按项目命令的副作用与政策选择执行环境；不
复用旧 eval 结论或旧 shadow 文件。两轮间固定同一 SEC code/config/test/committed-artifact
base、候选 upstream SHA 和 language；round 1 从 selected target 开始，round 2 从只增加 round 1
最终九文档提交的 `second_target_sha` 开始。live 外部状态或任一固定 identity 变化都使证据失效，
必须重新冻结并从 clean target 重跑。

### Target selection 预登记与 blind 边界

启动 fresh executor 前，先在 owner 与未来 reviewer 可检索的 GitHub evidence location 发布带
GitHub 时间戳的 Target Selection record，包含：

- final `candidate_upstream_sha` 与 `selected_target_sha`；
- 一至三条 selected target 执行前已存在的 `known_stale_claims`，且落在九份权威文档可处理
  范围内，或明确记录预期 disposition；
- `backup_target`、`selection_reason` 和 `executor_not_started=true`。

不得把 executor 后来引入的错误登记为 known-stale claim，也不得把目标外 legacy 文档 observation
作为唯一阳性点。正式 executor 不得读取 target-selection record、旧 Case A prompts/findings/
reports、PR body/comments、本地 evidence 目录或其他 Agent 结论。它只收到：

```text
使用 $workflow-docs-sync 同步 <clean target path>，语言 zh，不创建 draft PR。
```

Eval 编排者必须让 `$workflow-docs-sync` 解析到 final candidate SHA 的 canonical Skill，并在
executor 启动前核对来源与 bytes；不得误用旧安装副本，也不得让该准备动作进入 target residue。

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
- 分别核对目标 `TESTING.md` 的 bug-first 与 no-test-diff 规则：bug-first 不能替代“无 test diff
  时指出具体已有覆盖并提供重跑证据”；仅有按变更类型选测试的表格也不等价。目标已有正确且
  更具体的两条规则时保持零 diff，缺少任一条时形成 finding；
- 运行项目真实测试，准确记录验证层级，并完成 review 与最终 `check`。

关闭全部 BLOCKER 和无需新产品决策的 actionable WARN 后，只提交 round 1 最终九文档，记录
该本地提交为 `second_target_sha`；code、config、test 和其他 committed artifact 相对
`selected_target_sha` 必须不变。

这些检查是现实抽样。所选 HEAD 初始状态不含相应缺陷时，只能报告“本次未观察到”，不得写
成“已验证不存在”或“检测能力已验证”。若观察到缺陷，记录代码/测试反证、文档声明、修改和
复核结果。

### Round 2 strict convergence

从 `second_target_sha` 创建新的 clean checkout/worktree，fresh executor 以完全相同的用户调用
进行第二次完整运行；不依赖第一次过程说明，重新调查、选择测试、review 并运行最终 `check`。
记录相对 `second_target_sha` 的前后 bytes、Git diff、测试选择、普通/暂存/untracked/ignored
状态，并按以下唯一判定收口：

- `PASS_NOOP`：九文档相对 `second_target_sha` 零 diff，且无 staged、untracked 或 ignored residue。
- `ROUND1_INCOMPLETE`：round 2 根据冻结目标中原已存在的代码、配置、测试或 artifact 反证发现
  有效新增修正；说明 round 1 调查不完整，整个两轮 gate FAIL。
- `ROUND2_DRIFT`：只有措辞、排序、格式或偏好变化，没有新增反证；说明最小改写不稳定，整个
  两轮 gate FAIL。

后两种结果都必须先修复候选或调查协议，再从 clean target 重跑完整 round 1 + round 2；不得
只补第三轮覆盖早期失败。第二次 `prepare` / `check` no-op 只能作为幂等性附加证据，不能代替
第二次完整 Case A。

### Alignment consumer validation

SEC checker 要求 evidence path 与 committed HEAD 一致。round 2 获得 `PASS_NOOP` 后，直接在
`second_target_sha` 或其 clean worktree 上运行
`python3 tools/check_capability_contract_alignment.py --base-ref <selected_target_sha>`。记录
publisher/consumer、exact command、结果、结构证明边界和 cleanup；不再创建 derived no-hardlinks
clone 或 test-only commit。

Case A 最终记录包含：

- Target Selection record URL 与 GitHub 时间戳、`selected_target_sha`、候选 upstream SHA、
  `second_target_sha` 与 language；
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
  加严、直接在 `second_target_sha` 上运行的 alignment consumer 结果和 cleanup；
- 正式 Case G/A raw record 的 candidate SHA、record URL 与内容 digest；最终 PASS 不覆盖早期
  failure、REOPENED 或 SUPERSEDED candidate/evidence；
- 未运行项、open decisions 和剩余风险。

Case G/A 的 canonical raw evidence 必须是一个可检索的 GitHub record，明文保存 exact prompts、
exact commands、candidate/target/second-target SHA、changed paths、target document diff、tests 与
结果、reviewer identity、启动时间、blind-first 边界、findings/fix/recheck、final-check JSON 和
cleanup。公共 Case G 与机械摘要可进入 PR comment；目标仓库敏感内容进入 owner 和未来 reviewer
可访问的私有 GitHub URL。PR body 只索引该 canonical URL 与一个内容 digest；digest 不能替代
prompt、diff 或其他原始明文。
