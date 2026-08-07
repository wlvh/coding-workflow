---
name: workflow-docs-sync
description: 从当前或用户显式指定的 Git 根重建项目事实，按请求语言默认选择 zh/en，最小必要改写 wlvh/coding-workflow 的九份核心工作流文档并运行真实测试；只有用户明确要求 PR 时，才基于调用时 committed HEAD 在仓库外 clean worktree 创建 draft PR。用户要求同步、补齐或核对 architecture、capability、interact、business guide、testing 或 governance 文档时使用。
---

# Workflow Docs Sync

一次调用完成事实重建、必要文档改写、真实测试、复核和机械检查。现有文档与上游模板都是
待验证声明，不是项目事实来源。主 Agent 是目标工作区唯一写入者。

## 安装后同轮继续

当用户在同一条指令中先用 `$skill-installer` 安装本 Skill，再要求立即同步时：

1. 运行安装器 helper。如果它只因默认目标已存在而失败，不覆盖或删除旧目录；用 `--dest
   <unique-install-root>` 在原 Git 根和任何执行 worktree 外的唯一新目录重试。
2. 只消费 helper 本次成功输出。对本 Skill，固定前缀是 `Installed workflow-docs-sync to `；
   其后整段文本是安装根。相对路径按安装命令的工作目录立即解析为绝对路径。
3. 当前会话若已经注册这次返回目录对应的 `$workflow-docs-sync`，显式调用它；否则完整读取安装根中的
   `SKILL.md`，把该文件所在目录作为 `<skill-root>`，从该目录解析 `scripts/sync_docs.py`，并在
   当前轮继续执行本文件全部流程。
4. 不得猜测 `~/.codex`、`$CODEX_HOME` 或其他固定安装路径，也不得要求重启、打开新会话或等待
   下一轮。只有重试后仍得不到本次成功输出及其可验证 Skill 根时才报告 `BLOCKER`；不得把
   错误中的候选路径冒充本次成功安装结果。

## 默认推断，不追问

### 目标仓库

按以下优先级解析：

1. 用户显式给出的目标路径；用 `git -C <path> rev-parse --show-toplevel` 归一化为 Git 根。
2. 否则在当前工作目录执行 `git rev-parse --show-toplevel`，使用其所属 Git 根。

只有当前工作目录不在 Git 仓库中，且用户也未提供可解析路径时，才允许询问目标路径。

### 语言

按以下优先级解析：

1. 用户显式指定的 `zh` 或 `en`。
2. 否则由 Agent 按当前请求的自然语言判断：中文请求使用 `zh`，其他语言请求使用 `en`。

不得新增语言探测脚本、配置、marker 或状态文件。`sync_docs.py --language` 仍是必填参数，由
Agent 将上述结果显式传入。

### PR 意图

按以下优先级解析：

1. 用户明确说不创建 PR，结果为 `false`。
2. 否则用户提到 PR、提 PR、创建 PR、提交 PR、`open pull request` 或
   `create pull request`，结果为 `true`。
3. 未提及，结果为 `false`。

`true` 只允许在全部 gate 成功后创建 draft PR；不得自动标记 Ready 或合并。除真正不可恢复的
`BLOCKER` 外，不得要求用户补充目标绝对路径、语言、分支名、上游 SHA、安装路径、内部命令、
Agent 数量或执行顺序。

## 选择执行工作树

先固定解析后的原 Git 根和调用时提交：

```bash
git -C <original-root> rev-parse --verify 'HEAD^{commit}'
```

仓库没有任何 commit 时报告 `BLOCKER`，不得要求用户先 commit 或 stash。

### PR 意图为 true

无论原工作树是否 clean，都必须：

1. 在仓库外建立原工作树调用前快照。对原工作树的 Git 读取设置
   `GIT_OPTIONAL_LOCKS=0`，避免只读检查刷新 index。快照必须同时包含：

   - 以下两条命令的 NUL 分隔原始输出：

     ```bash
     git -C <original-root> status --porcelain=v1 -z --untracked-files=all --ignored
     git -C <original-root> ls-files --stage -z
     ```

   - `git -C <original-root> rev-parse --git-path index` 解析路径的原始 index bytes；
     index 不存在时记录明确的 missing sentinel。
   - 原 Git 根下除顶层 `.git` 管理入口外每个文件系统 entry 的 NUL-safe manifest：
     记录相对路径、类型、权限/可执行位，对普通文件记录原始 bytes 的 SHA-256，对
     symlink 记录 link target。不跟随 symlink，不保存文件内容副本。

2. 在原仓库之外创建临时根，从调用时 `HEAD` 创建唯一、有意义的新分支和 clean linked
   worktree。不得从之后变化的分支 tip、`main` 或 `origin/main` 重建起点。
3. 只在外部 worktree 中调查、编辑、测试、stage、commit 和发布。除上述不可逆内容摘要用于
   隔离证明外，不得读取或复制原工作树的 dirty bytes；摘要和 metadata 不得作为项目事实
   证据或进入 PR。不得在原工作树 stash、clean、reset、commit、覆盖或运行 `prepare`。
4. 任何最终报告前（包括发布失败时）用同一算法重建全部快照，分别比较 status、
   staged entries、index bytes 和文件系统 manifest。任一差异都登记 `BLOCKER`；不得仅用
   porcelain 路径和状态码宣称原工作树未变。

最终报告必须原样包含：

```text
本次同步与 PR 基于调用时的 committed HEAD；原工作树中的未提交修改未进入调查或 PR。
```

### PR 意图为 false

当前工作树满足 `prepare` 的 dirty allowlist，且后续编辑不会制造 editable path 的
index/worktree 分叉时，可以直接运行。若 `prepare` 因同步范围外 dirty path 或 editable path
分叉拒绝，或预期编辑会制造分叉，则不追问用户清理；从同一调用时 committed HEAD 在仓库外
创建 clean worktree 并完整重跑。`prepare` 的此类前置失败不得改变原工作树；其他失败按实际
证据登记 `BLOCKER`，不得一概用 worktree 掩盖。

只要使用外部 worktree，事实调查就只能消费其中的 committed HEAD，不得混入原工作树的未提交
内容。

## 固定上游并准备

选定 `<target>` 后，按以下方式准备：

1. 如果当前 Skill 位于 canonical `wlvh/coding-workflow` Git 根目录，复用该 checkout。
2. 否则在目标仓库和外部执行 worktree 之外临时 shallow clone
   `https://github.com/wlvh/coding-workflow.git`；网络失败
   时停止，不回退到缓存模板。
3. 调用：

   ```bash
   python3 <skill-root>/scripts/sync_docs.py prepare \
     --target-repo <target> \
     --upstream-dir <upstream> \
     --language <zh|en>
   ```

4. 只消费单行 JSON，固定返回的 `target_head` 和 `upstream_sha`，整轮复用同一对 SHA。
5. 创建临时 upstream 时立即记录临时根目录。当前 Agent 必须在任何成功、失败或提前停止的
   最终回复前删除它并运行 `test ! -e <temporary-root>`。未通过时登记
   `WDS-UPSTREAM-CLEANUP / BLOCKER`，不得报告完成；Controller 后置清理不能改判本轮成功。
   canonical checkout 不清理。

`prepare` 从固定 Git object 读取模板，并在任何目标写入前确认九份 source path 都存在且为
UTF-8、八份非 PR source 至少含一个 active marker；随后只创建缺失文件，不覆盖已有文档。
上游 dirty worktree 不影响模板 bytes。不得创建 run state、receipt、ledger、Skill 副本、模板
镜像或仓库内 PR body。

## 重建事实并最小改写

写入前至少运行 `git -C <target> ls-files -z` 建立范围。完整调查当前代码、配置、测试、
committed artifacts、可重复运行结果和必要 Git 历史；不得用旧文档证明旧文档正确，也不得
因为内容未出现在近期 diff 中而跳过。

按语义而非句式分类待核对声明：

- 描述性事实说明当前状态、能力、命令、职责、行为、副作用、交付状态或证据强度，必须由
  当前代码、配置、测试、committed artifacts 或可重复运行结果支持。
- 规范性政策规定开发者或 Agent 应如何工作，可由当前 scoped repository instruction、accepted
  decision、团队/项目配置，或已明确采纳并持久化的 owner decision 支持。
- 个人或当前会话偏好默认不属于目标项目；只有 owner 明确采纳为长期政策并在同一变更中写入
  repository authority 或 accepted decision 后才可持久化。
- 混合语句拆分规范意图与现状断言，事实部分仍按描述性事实核验。不得把事实改写成政策来
  规避证据，也不得把政策写成实现事实。

当前 tracked、scoped 治理入口可推定为 active policy authority；明显模板残留、个人偏好、历史
说明、失效状态或冲突仍须形成 finding。机器配置证明 enforcement，不自动 supersede 规范意图；
两者冲突时登记 finding/open decision，既不破坏硬 gate，也不静默选边。同类政策先按显式
supersession 和现有 authority/scope 规则裁决；仍有歧义时保留原文并记录已检查来源。对 material
policy 的保留、修改或 no-update reason 必须记录 authority source、scope 和冲突检查结果。

确认文档问题后、任何语义编辑前，先在会话中登记 finding：唯一 ID、`BLOCKER` / `WARN` /
`NOTE`、代码/配置/测试或 artifact 证据、风险和最小修复边界。不得在编辑完成后根据最终 diff
或 reviewer 结论倒填为“写入前 finding”。同一根因、同一证据链和同一修复边界影响多份文档
时合并为一个 finding，不按文件或行机械拆分。多份文档共同声明但代码和测试不存在的能力，
必须在编辑前登记 `BLOCKER`。

- 全量质疑九份文档，只改错误、缺失、失真或失效内容；正确内容保持零 diff。
- 删除、收窄或降级没有当前证据的描述性强声明；规范性政策按政策权威、作用域和冲突处理。
  不得把事实改写为政策以规避证据，也不得把政策伪装成实现事实。需要产品判断时记录 open
  decision，不编造结论。
- 保持 `capability_contract.json → interact.md → docs/business_user_guide.md` 的权威方向。
- 清除所有 active project-fill marker；不要使用固定写入顺序、完成百分比、KEEP ledger 或
  过程状态。
- Architecture、Capability / User Behavior、Testing、Governance 是覆盖维度，不是固定四
  Agent 拓扑。可自行调查，也可按模块、调用链、风险或证据类型委派只读工作；所有结论都
  必须回到项目证据。

## 四个覆盖维度

### Architecture

从真实入口向下重建核心调用链，核对系统目的、模块职责、依赖方向、数据流、状态、错误
模型、配置、认证、外部依赖、artifact、副作用、扩展点和架构债务。主动证伪架构不变量，
不得把未来设想写成 active 现状。

### Capability / User Behavior

从入口、UI 或 API 响应、错误、测试和用户可见限制提取已实现能力、拒绝、追问、降级和责任
边界。递归核对稳定 `anchor_id` 与 Markdown 引用。主动寻找多份文档彼此一致、但代码和测试
不存在的共同虚构能力；文档共识不是实现证据。Business guide 只能教学性解释 contract 与
`interact.md` 已确认的内容。

### Testing

盘点真实 runner、命令、fixture、层级、外部依赖、副作用和必要顺序。测试环境由真实命令、
副作用、CI 能力和项目政策决定，可以是 CI、container、独立 checkout、远端环境或其他已
验证环境；记录 exact command、scope、result、not-run reason、环境、隔离和清理结果。

目标 `TESTING.md` 要求多个解释器时，分别运行并记录每个解释器的命令和结果；不能运行时分别
记录 not-run reason。一个解释器的结果不能替代另一个解释器。

分别核对 bug-first 与 no-test-diff：前者要求可复现行为缺陷先建立失败证据；后者要求没有
test diff 时指出具体已有测试如何覆盖本次新风险并提供重跑证据。新增测试的判据、按变更类型
选测试或泛称“已有高层测试”都不能代替 no-test-diff 责任；目标缺少等价规则时登记 finding。

验证层级不得膨胀。Unit、contract、scenario、golden、report build、repair validation、light
review、full validation 和 live test 只能按实际覆盖范围表述；未运行不得报告为通过。

### Governance

在前三维事实稳定后核对 `AGENTS.md`、`PR_Checklist.md`、`SOP.md` 与 PR template。命令、路径、
默认分支、发布和部署声明必须有当前证据。跨项目模板不得混入仅属于 Workflow Docs Sync 的
内部执行语境、pin、reviewer 拓扑或隔离实现。PR body 只能位于目标仓库外。

## Fresh-context review

优先使用 `independent` reviewer：提供 fresh context、完整仓库只读访问和同一 `target_head`。
Reviewer 在 blind-first 初始阶段不得读取主 Agent 的任何中间产物；必须先从代码、配置、
测试和 committed artifacts 独立重建高风险事实并形成 findings。初始 findings 形成后，才可
读取最终候选文档和原始 Git diff，检查遗漏、最小改写与跨文档影响。

Reviewer 不编辑、stage、commit、push，也不把复核过程写入目标仓库。无法提供认知隔离时，
执行完整 self-review，并在最终报告原样写：

```text
Review mode: self-review; independent review was not available
```

不得把 self-review 称为 independent。用户明确要求 independent review 而平台无法提供时，
停止在发布前。

review mode 为 `independent` 时，最终报告必须记录 reviewer 会话或线程标识、启动时间和认知
隔离边界；缺少这些证据时，不得仅凭主 Agent 声明认定 independent。

Reviewer 使用同一受控 severity。每个 finding 包含唯一 ID、severity、证据、风险和预期修复
边界：

- `BLOCKER`：当前候选会产生错误、虚构、越权、不可复现交付或关键风险遗漏，必须修复后才能
  收口。
- `WARN`：存在实质性质量或维护风险；除非需要新的产品决策，否则必须修复。
- `NOTE`：不改变可交付性的观察或后续建议，不作为 gate。

主 Agent 修复全部 BLOCKER 和无需新产品决策的 actionable WARN，请 reviewer 复核 finding
对应修改及直接跨文档影响，并重跑受影响测试。不得用新增状态文件、额外 Agent、词表或代理
指标代替本应覆盖该风险的场景、review 或真实 eval。恢复或新增 marker、alias、机器状态、
parser、兼容入口或其他控制机制前，finding 必须证明它承担独立风险，存在真实消费者与可复现
失败路径，并说明现有高层机制为何不足；能最小扩展现有机制时不得另造同义入口。

## 最终检查与报告

运行固定 SHA 的最终检查：

```bash
python3 <skill-root>/scripts/sync_docs.py check \
  --target-repo <target> \
  --upstream-dir <upstream> \
  --upstream-sha <prepare 返回的 upstream_sha> \
  --expected-target-head <prepare 返回的 target_head> \
  --language <zh|en>
```

`check` 从 `upstream_dir` 的 object store 按 `upstream_sha` 与 language 重读并验证同一 source
contract，再验证目标 HEAD、dirty allowlist、editable path 无 index/worktree 分叉、九份普通
文件、UTF-8、非空、JSON object、active marker，以及存在时为 UTF-8 的 `.gitignore`。唯一
final bytes 的 whitespace 检查在临时非 Git 目录以固定 Git 规则运行，不继承目标仓库
attributes、用户 global attributes 或 system attributes。它不解析 Markdown 标题或 fence，
不判断文案质量、capability 真实性、测试层级或业务指南可读性，也不证明调查、测试或 review
曾执行。该单一路径的覆盖依赖同步范围外 dirty path 始终被拒绝；若未来放宽 dirty allowlist，
必须重新评估 whitespace 覆盖。index/worktree 分叉拒绝只消除两个发布候选，不执行第二套
whitespace 检查。

最终报告必须包含：

- `target_head`、`upstream_sha`、language 和真实 review mode；
- 修改文档及代码、配置、测试或 artifact 证据；
- 每条测试的 exact command、scope、result、not-run reason、环境与隔离方式；
- review finding、修复、复核结果和 open decisions；
- mechanical check 结果，并明确它只证明最终状态；
- 使用外部 worktree 时的调用时 committed HEAD 和原工作树快照比较结果。

`check` 必须在 commit 前通过；不得用 commit 后的新 HEAD 绕过固定的 `expected_target_head`。

## Draft PR 发布

PR 意图为 `false` 时不 commit、push 或创建 PR，最终把 publication 标记为 `NOT_REQUESTED`。

PR 意图为 `true` 时，只有调查、测试、review、原工作树状态边界和上述 `check` 全部通过后，
才按顺序执行：

1. 从最终 diff 得到本轮实际修改的九份核心文档子集，用显式路径逐个 stage；不得使用
   `git add -A`，不得包含代码、配置、测试残留、PR body 或其他非权威路径。
2. 用 `git diff --cached --name-only` 读回 staged 路径，确认精确等于预期子集，再运行：

   ```bash
   git diff --cached --check
   ```

3. 创建一个有意义的 commit；没有文档 diff 时不得制造空 commit 或虚假 PR。
4. 解析真实 remote、远端默认 base 和唯一 head branch，push 该新分支。
5. 只创建 draft PR，不标记 Ready、不合并。创建后从远端读回 PR number、base、head、head SHA、
   Draft 状态和 changed files；任一不一致都登记 `BLOCKER`。

PR body 必须是仓库外的临时 Markdown 文件，并准确记录：

- base/head 与调用时 committed HEAD；
- changed files；
- findings、修复与 open decisions；
- exact tests 及 PASS、FAIL、`NOT_RUN` 或 `BLOCKED`；
- 真实 review mode 和 reviewer 证据；
- final `check` 结果及其机械证明边界；
- 以下原工作树边界原句：

  ```text
  本次同步与 PR 基于调用时的 committed HEAD；原工作树中的未提交修改未进入调查或 PR。
  ```

commit、push 和 draft PR 创建交给通用 GitHub 发布能力，`sync_docs.py` 不参与发布。

若无 remote、无认证、无 push 权限或 PR 创建失败，保留外部 worktree、branch、commit 和仓库外
PR body，不反问用户，不删除可恢复现场。最终状态必须原样写：

```text
Documentation sync: PASS
Publication: PR_BLOCKED
Overall: PARTIAL
```

同时输出基于已解析 worktree、remote、repo、base、head 和 body 路径的可直接执行 push 与
draft PR 创建命令。无法解析的外部身份必须在命令中明确标为 required blocker，不得猜测 URL、
repo 或权限，也不得声称 PR 已创建。只有 PR 创建成功、远端读回一致且原工作树快照逐 byte
不变后，才可以移除外部 worktree；publication blocked 时必须保留。
