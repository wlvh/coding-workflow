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
  用户只提供目标仓库、必选的 `zh` / `en`，以及成功后是否创建 draft PR。
- 机械边界：`prepare` 只解析 Git 根目录与 SHA、在任何写入前检查 dirty allowlist，
  并补齐缺失模板；`check` 只读验证最终仓库状态。检查器不证明 Agent、审计或测试曾经
  执行，测试由主 Agent 实际运行并在最终报告记录。
- 发布边界：PR body、commit、push、远端绑定和 draft PR 创建不属于同步器。用户要求
  draft PR 时，由通用 GitHub 发布能力使用仓库外临时 Markdown body 完成。
- 替代关系：本决策在 `workflow-docs-sync` 范围内 supersede DEC-003 和 DEC-004 的旧
  实现；不保留旧 launcher、mode、harness、缓存模板或控制面兼容 fallback，Git 历史
  承担回滚。无 subagent 时的顺序执行是当前正式路径，不是旧实现 fallback。仍保留
  DEC-003 的原则：AI 负责项目语义与文档改写，机械层只判断可确定事实。
- 后续：DEC-006 partial supersede 本决策中的固定四个领域 Agent、固定内部对抗性审计 Agent，
  以及无 subagent 时固定四章节执行顺序；其余边界继续有效。
- 英文状态：`en-pending`。

## DEC-006：Workflow Docs Sync 以直接风险覆盖取代代理约束

- 状态：accepted
- 日期：2026-08-01 UTC
- 原则：更少不是目标；只有在风险已由更直接机制覆盖，或被明确接受时，才删除原机制。
  行数下降、测试变少或文件减少都不能单独构成删除理由。
- 机制必要性：恢复或新增 marker、alias、机器状态、parser、兼容入口或其他控制机制前，必须
  先登记 finding，证明独立风险、真实消费者与可复现失败路径，并说明现有场景、review 或真实
  eval 为何不足。能最小扩展现有机制时不另造同义入口；缺少具体缺口时保持零 diff。
- 产品边界：保留 one-call UX、固定目标 HEAD 与上游 SHA、从固定 Git object 分发模板、dirty
  allowlist、写入前完整预检、只创建缺失文件、single writer、全量事实重建、最小必要改写、
  fresh-context review、最终 `check` 和显式授权发布。Architecture、Capability / User Behavior、
  Testing、Governance 是覆盖维度，不是固定 Agent 拓扑、写入顺序或完成进度协议。
- 与 DEC-005 的关系：本决策 partial supersede 其中的固定四个领域 Agent、固定内部对抗性审计
  Agent，以及无 subagent 时固定四章节执行顺序。DEC-005 的 one-call、single writer、不写
  repository run state / receipt、`prepare` / `check` 机械责任边界，以及发布必须显式授权且不由
  `sync_docs.py` 执行继续有效。

### 删除的机械机制与风险转移

- 删除 Markdown heading / fence parser。它只能证明有限语法形状，不能证明章节语义、文案
  质量或项目事实；模板语义完整性改由四维 review 和 SEC_metrics Case A 真实 eval
  发现。接受的剩余风险是：纯机械 `check` 不再单独发现空标题或 fence 失配。
- 删除模板 equality，包括 CRLF 归一化和 PR template 特例。每份非 PR 上游模板必须至少含
  一个 active project-fill marker；逐字复制模板必然保留 marker，最终 `check` 因 marker 失败，
  因此 equality 不再提供独立保护。`prepare` 与 `check` 共用 source-template validator，从调用方
  指定 object 与 language 读取全部九份 UTF-8 模板，并对八份非 PR source fail closed；若未来
  放宽 active-marker source contract，必须重新评估是否恢复 equality。
- 合并 tracked working-tree、index 与 final-file whitespace 分支，只以一条路径扫描九份最终
  文件及存在的 `.gitignore`。无损性首先依赖 dirty allowlist：同步范围外改动始终被拒绝时，
  允许范围内的 untracked、staged、tracked 或 committed 文件都由同一 working-tree final bytes
  覆盖；若未来放宽 allowlist，必须重新评估 whitespace 覆盖。editable path 的 index/worktree
  分叉仍 fail closed，因为它代表两个发布候选，而不是第二套 whitespace 检查。Git CLI 在临时
  非 Git 目录固定 `core.whitespace=blank-at-eol,blank-at-eof,space-before-tab`，不继承目标
  repository attributes、用户 global attributes 或 system attributes；存在的 `.gitignore` 仍须
  为普通 UTF-8 文件。dirty status 按 editable path 聚合 index 与 worktree 两侧；index 删除或
  rename source 后同路径以 untracked 或 ignored 文件重建也属于两个候选，必须 fail closed。
  任一前提不满足时 `check` fail closed。
- 删除旧版 22 项 `TEMPLATE_TOKENS` 和独立的 broad“待补充”扫描，并新引入两个 active
  project-fill marker 作为唯一机器未完成状态。历史 upstream 模板确实包含旧 token；2026-08-06
  对九份核心文档重新核对 SEC_metrics
  `a77b9055a53de5e5808649551f03fe567cb2de0a`、trading
  `cb1fe04071ed516abd57b7999072cba5b11f85e3` 与 nl2dax-eval
  `5c850f4fa78fd87e34d5039459f1d4e7400ace22`；三仓均未命中旧 22 token、active marker 或
  broad“待补充”，因此不逐项保留 target-side legacy blacklist。历史 upstream
  `f669ee40b1fbfe91baee097fd26ad975d7783aea` 可在 `zh/capability_contract.json` 与
  `zh/docs/business_user_guide.md` 重演旧 token，证明迁移风险曾真实存在；旧 upstream 由 source
  active-marker invariant fail closed。“待补充”仍可表达人工明确暂缓。未来只有具体下游仓库
  与文件的真实命中证据才能恢复最小 compatibility。
- 删除 `references/sections.md` 和 `references/audit.md`。旧 `SKILL.md` 强制完整读取两者，实际
  没有渐进式披露收益；四维覆盖、独立复核、严重度和 finding 收口规则合并到 `SKILL.md`，
  由单一权威避免重复漂移。
- 删除 Working Brief 产品机制及其生命周期。Reviewer 的自足规则是：blind-first 初始阶段
  不得读取主 Agent 的任何中间产物。
- 跨项目模板撤回 Workflow Docs Sync 特有的 clone / pin、reviewer isolation 和 publishing
  实现，以及 run-state / receipt、documentation-sync checker 和内部 finding/candidate 状态词；
  同时保留并通用化主执行者负责、委派结果需审阅、共识不等于证据、审查默认只读和不固定
  Agent 数量或顺序等协作原则。主防线是 `SKILL.md` 的语义检查；分发合同只扫描本次真实误植
  过的五个精确语境 token，作为已知回归兜底，不扩展成自然语言黑名单。
- 安装器继续直接复制 canonical Skill，但把“clean source”补全为可复制 entry 合同：普通
  tracked/untracked 状态之外，任何会进入安装结果的 ignored path 也必须在所有删除和复制前
  fail closed；仅明确不会复制的 Python cache 与 `.DS_Store` 豁免。该边界直接防止本地 PR body
  或私有 residue 污染 user/repo × Codex/Claude 安装，不增加来源 receipt 或 migration registry。

### 删除的代理测试与新信任基础

- 删除全部函数级单元测试、parser 分支测试、实现细节 status-code 测试、模板 equality / CRLF
  测试、标题/fence 测试、广泛自然语言 residue 扫描，以及行数、行宽、测试数量预算。
- 这些 proxy invariant 已产生真实问题：普通散文中的 `baseline` 被误伤；为守行数预算产生
  难审查的超长行；equality 与 active marker 同时保护模板项目化，形成重叠并在合法 PR
  template 上需要特例。
- 新信任基础是少量公共 CLI 场景、真实模板分发合同、fresh-context review，以及在同一最终
  SHA 上连续两轮完整 SEC_metrics Case A。第二轮必须重新调查、选择测试、review 并运行最终
  `check`；连续 prepare/check no-op 只证明机械幂等，不能替代第二轮 eval。场景覆盖成功主路径、
  prepare 原子前置失败、check 无效终态、user/repo 与 Codex/Claude 完整安装、以及仓库分发
  结构；测试不 import `sync_docs.py` helper。
- 旧 eval 风险并未静默删除：部分过时旧文档、共同虚构能力和验证层级膨胀成为 Case A 的
  强制检查项；机械 no-op 与第二轮完整 Case A 分别承担不同风险；review-mode 身份风险由公共
  场景和 `SKILL.md` 规则承担。

Case A 对“部分过时旧文档、共同虚构能力、验证层级膨胀”的检查是现实抽样，不是注入已知
缺陷的阳性对照；若所选目标初始状态不含相应缺陷，只能报告“本次未观察到”，不得写成
“已验证不存在”或“检测能力已验证”。

- 英文状态：本决策对应的对外说明已同步到英文 README 与 development workflow。

## DEC-007：政策证据、Anchor 协议与两轮严格收敛

- 状态：accepted
- 日期：2026-08-03 UTC
- 知识分类：描述性事实必须由当前代码、配置、测试、committed artifacts 或可重复运行结果
  支持；规范性政策可由 scoped repository instruction、accepted decision、团队/项目配置或已
  持久化的 owner decision 支持；个人/会话偏好默认不进入下游项目。混合语句拆分核验，禁止
  把事实改写成政策或把政策伪装成实现事实。
- 政策权威：机器配置证明 enforcement，不自动 supersede 规范意图。配置与政策冲突是治理
  漂移，必须形成 finding/open decision；同类政策按显式 supersession 和既有 authority/scope
  规则裁决。权威仍不明确时保留原文和已检查来源，不静默删除或永久神圣化。
- 持久化边界：当前 task instruction 只授权当前任务；只有 owner 明确采纳为长期项目政策并在
  同一变更中写入 repository authority 或 accepted decision 后，才可跨轮保留。
- Anchor 协议：canonical authoring form、大小写、ID grammar 和 whitespace tolerance 只在
  `capability_contract.json.rules` 定义。其他形式不受支持，但当前 SEC consumer/checker 不承诺
  穷举拒绝未知 alias；结构引用不单独证明句子级绑定或业务语义。显式 `test_anchor: null` 同时
  要求非空、具体的 `untested_reason` 和非空 `pending_since`，只表示覆盖缺口已登记。
- 版本语义：`schema_version` 继续为 `0.1.0`，只表示 JSON shape 和机器必需字段；纯 authoring
  prose 规则变化不升级该字段，未来 shape 或机器必需字段变化再按版本策略处理。
- 测试决策：跨项目模板保留 escaped-bug、无法先红测、公开契约、无 test diff、纯重构和
  documentation-only gate 的最低证据规则，并由 PR checklist 执行。bug-first 与 no-test-diff
  是两条独立责任；新增测试判据或按变更类型选测试不能替代具体已有覆盖与重跑证据。一个协议
  只有一个定义点。
- Finding 闭环：上述 stable ID、severity、first-seen、REOPENED 和 candidate/evidence 状态只
  属于本仓库维护与 canonical Skill / eval 的内部证据合同。下游模板只要求按目标项目政策记录
  review、可执行反馈、复核和开放决策，不固化本 Skill 的 round、状态词或 raw-record 拓扑。
- Case A：先预登记 `candidate_upstream_sha`、`selected_target_sha`、known-stale claims、backup 和
  selection reason，再启动 blind executor。两轮间 target code/config/test/committed-artifact base、
  upstream candidate 与 language 不变；round 1 关闭 review finding 后只提交最终九文档，round 2
  从该 `second_target_sha` 的新 clean checkout 开始。相对 `second_target_sha` 九文档零 diff 且无
  staged/untracked/ignored residue 才是 `PASS_NOOP`；冻结事实支持的新增修正为
  `ROUND1_INCOMPLETE`，无新增反证的表达漂移为 `ROUND2_DRIFT`。两种失败都要求从 clean target
  重跑完整两轮；alignment consumer 直接在 `second_target_sha` 或其 clean worktree 上运行，
  不创建 derived test-only identity。外部状态或固定 identity 变化使证据失效，不构成 PASS 例外。
- 与 DEC-006 的关系：本决策 refine 其 Case A 两轮收敛语义，并补充政策证据、Anchor publisher
  和测试/finding 合同；不恢复 template equality、旧 token blacklist、固定 Agent 拓扑或代理
  parser。
- 实现边界：不修改 `sync_docs.py`、installer 或 CLI schema，不新增 anchor/policy/Markdown
  parser、repository ledger、receipt、run state 或 claim-level binding。
- 英文状态：双语下游模板已等价同步；canonical Skill、eval 与决策继续以中文路径为权威。

## DEC-008：开发工作流采用复杂度守恒与可退役实验机制

- 状态：accepted；其中条件性 Issue Readback 和 Owner Decision 机制为 `experimental`。
- 日期：2026-08-24 UTC
- 适用范围：`zh/docs/development_workflow/README.md` 及其引用的 prompts、双语模板与开发审核
  规则；不改变 `workflow-docs-sync` 的运行时、CLI 或发布边界。
- 复杂度守恒：新增或扩展工作流机制时，必须说明它改变谁的下一步动作、承担什么独立风险、
  现有机制为何不足，以及它替代、合并、缩小或删除什么；能扩展现有机制时不建立平行机制。
- 诚实记账：本次改造是经 owner 接受的净复杂度增加。它保留双模型协作并改变分工，恢复正式
  详细 PR 审核、合并后实现解读、文档检查、FSD 完备性验收和用户视角验收，同时增加条件性
  Issue Readback、显式 Owner Decisions 和测试复用规则。
- 双模型边界：Issue 阶段使用需求完成 / 验收与工程量 / 最小充分两个镜头，由 Issue Agent
  统一执笔；正式 PR 审核仍是独立的详细步骤。Finding 阶段由 Codex 重点核实事实与复现，
  Claude Code 重点判断影响面、同类入口和最小充分修复。模型身份不是争议裁决依据。
- 审核出口：最终只使用 `PASS`、`REWORK_REQUIRED` 和 `OWNER_DECISION_REQUIRED`。证据不足但
  可能改变结论时归入 `REWORK_REQUIRED` 并说明待补证据；不再增加平行的规格或证据状态词。
- Owner Decision 单一权威：`OWNER_DECISION_REQUIRED` 的适用条件、`OD-xxx` 记录格式和生命周期
  只在 `zh/prompts/issue_agent.md` 的“Owner Decisions：唯一规范”中定义。README、Target State
  Bridge、PR review prompt 和本决策只引用该规范并说明各自下一步动作，不建立平行定义。
- Issue Readback：用于编码前理解高风险 Issue，不形成第二套权威，也不设置额外批准状态。
  它不替代合并后基于最终代码的 Tech Lead 机制解读、用户可感知变化与文档检查、FSD 完备性
  验收、用户视角验收计划及必要时的实际执行。
- 测试复杂度：优先复用、参数化和扩展 scenario；只有复现已确认缺陷、保护已登记不变量或
  覆盖现有测试无法到达的真实边界时，才把对抗探针晋升为长期测试。

### 实验机制重审与退役

每项实验机制累计 3 个适用 PR 后单独复盘：

- Issue Readback 的适用 PR：实际执行了编码前 Readback；
- Owner Decision 机制的适用 PR：实际出现需要 owner 作出的选择。

复盘判断机制是否改变下一步动作、是否降低错误实施或无效等待，以及额外成本是否高于收益。
结论只能为 `PROMOTE`、`MODIFY` 或 `RETIRE`。从未触发或触发后未改变下一步动作的机制默认
退役；继续保留必须有新的具体风险证据。

- 与 DEC-006 / DEC-007 的关系：把直接风险覆盖和可退役知识原则应用到开发工作流自身；不改变
  两项决策对 `workflow-docs-sync` 与下游模板的既有语义。
- 实现边界：本轮只修改现有文档和 prompt，不新增 prompt 文件、ledger、run state、自动化
  workflow 或机器 parser。
- 英文状态：对外语义摘要同步到英文 development workflow；中文决策文件继续是权威。
