---
name: workflow-docs-sync
description: 从用户显式指定的本地 Git 路径、GitHub repository URL 或当前工作目录所属 Git 根重建项目事实，按请求语言默认选择 zh/en，最小必要改写 wlvh/coding-workflow 的九份核心工作流文档并运行真实测试；只有用户明确要求 PR 时，才从固定的 exact commit 在仓库外真实 Git checkout 创建 draft PR。用户要求同步、补齐或核对 architecture、capability、interact、business guide、testing 或 governance 文档时使用。
---

# Workflow Docs Sync

一次调用完成事实重建、必要文档改写、真实测试、复核、机械检查和明确授权的 Draft PR。
现有文档与模板都是待验证声明；主 Agent 是候选 checkout 的唯一写入者。

## 调用、身份与 checkout

### 安装后同轮继续

同一指令先用 `$skill-installer` 安装再立即同步时：运行安装器 helper；若仅因默认目标已存在而
失败，用 `--dest <unique-install-root>` 在目标与执行 checkout 外重试，不覆盖旧目录。只消费
本次成功输出 `Installed workflow-docs-sync to <installed-skill-root>` 并按安装 cwd 解析绝对
路径。会话已注册该目录时显式调用 Skill；否则完整读取其中的 `SKILL.md`，从同一目录解析
`scripts/sync_docs.py` 并在本轮继续。不猜安装路径，不要求重启或下一轮；仍无法验证才
`BLOCKER`。

### 默认解析

目标来源优先级是：用户显式本地路径、用户显式 GitHub repository URL、当前 cwd 所属 Git 根。
本地路径用 `git -C <path> rev-parse --show-toplevel` 归一化。Skill 安装、canonical Skill 或
模板 URL 不是目标，除非用户另行明确指定；三项都无法解析时才询问。

GitHub 来源只接受能确定 `owner/repository` 的 repository URL，或 ref 可无歧义解析的
repository tree URL；不接受 blob、单文件或无法区分 ref 与子路径的 URL。无 ref 时解析 default
branch，有 ref 时解析该 ref。先取得远端 commit 并将其作为 `target_head`，再用当前已有、已
认证的通用 Git/GitHub 能力在目标与 Skill checkout 外真实 clone/fetch；必要时获取额外历史。
从 `target_head` 创建并记录唯一 local branch，编辑前断言 branch HEAD 与
`git rev-parse 'HEAD^{commit}'` 均等于 `target_head`。不得逐文件 REST 下载或用
`git init`、现场 commit 拼装 checkout；无法物化 Git object、mode、symlink、HEAD 与 branch
identity 时 `BLOCKER`。成功后仍走一条流程，不建立本地/remote/hosted Skill mode；该来源报告
`Original worktree protection: NOT_APPLICABLE`。

语言以显式 `zh/en` 为先，否则中文请求用 zh，其他语言用 en，并显式传给
`sync_docs.py --language`。明确拒绝 PR 时 PR 意图为 false；否则提到提/创建/提交 PR 或
open/create pull request 时为 true；未提及时为 false。true 只创建 Draft，不标 Ready、不合并。
除不可恢复的 `BLOCKER` 外，不向用户索要内部路径、branch、SHA、命令、Agent 数量或顺序。

PR 意图 true 时还必须在编辑前得到可发布的远端 `base_ref`：无 ref 的 GitHub URL 使用已解析的
default branch；显式 tree ref 只在它是该仓库 branch 时使用同一 branch；tag、裸 commit 或其他
detached ref 没有可发布 base，远端写入前 `Publication: PR_BLOCKED`。本地来源优先使用
HEAD 所属且远端同 SHA 的 branch；只有 `target_head` 精确等于远端 default branch SHA 时才可
回退 default。该 `base_ref` 只是本轮事实，不写状态文件。

### 本地原工作树保护

本地来源先固定调用时 `HEAD^{commit}`；无 commit 时 `BLOCKER`，不要求用户 commit/stash。
PR 意图 true 时，无论原工作树是否 clean，都在仓库外保存以下 NUL 原始输出：

```bash
GIT_OPTIONAL_LOCKS=0 git -C <original-root> status \
  --porcelain=v1 -z --untracked-files=all
GIT_OPTIONAL_LOCKS=0 git -C <original-root> ls-files --stage -z
```

从 status 提取 dirty tracked、untracked、rename/copy source 与 destination。只对该集合逐项做
不跟随 symlink 的 `lstat`，记录相对路径、类型、mode、普通文件 SHA-256、symlink target 或
missing sentinel。随后从调用时 HEAD 在仓库外创建唯一 branch 和 clean linked worktree；全部
调查、编辑、测试、stage、commit、发布只在其中进行。原工作树不 stash/clean/reset/commit/
覆盖/运行 prepare，dirty bytes 不作项目事实。

在任何远端写入前和最终报告前，都用同一算法复核 status-path，并逐 byte 重比两份原始输出。
status 捕获 clean tracked/untracked 变化，定向 SHA 捕获 dirty tracked 内容被覆写但 XY 不变，
stage 输出捕获 index 变化。任一差异只证明并发变化：逐项标 `DISCLOSED`，停止之后的远端写入，
并保留外部 checkout；若远端写入已完成，也保留 checkout 与远端对象并报告发生时点，不自动
归因或回滚。差异始终禁止 cleanup。

不枚举、读取或哈希 ignored path，不比较 raw index-file bytes，不做 whole-tree/O(N) 哈希。
已存在的 `.env`、venv、`node_modules`、cache 等 ignored 内容变化不在机械检测范围；风险由
路径隔离承担。本地最终报告包含“本次同步与 PR 基于调用时的 committed HEAD；原工作树中的
未提交修改未进入调查或 PR。”

PR 意图 false 时，仅当当前工作树满足 prepare dirty allowlist、editable path 的真实 index 与
`target_head` 一致、且 canonical gate 不依赖或改写真实 index，才可直接执行。直跑前在仓库外
保存 `git ls-files --stage -z` 原始输出；prepare 后创建仓库外临时 `GIT_INDEX_FILE`，以
`git read-tree "$target_head"` 初始化。Candidate seal 的 `git add`、cached diff、
`write-tree`、tree 断言和 final check 全部继承该 alternate index，绝不写用户真实 index。
每条测试前后也用 alternate index 断言 candidate；若测试本身需要真实 index 语义，则改用外部
clean checkout。最终删除临时 index 并逐 byte 重比真实 staged entries；差异时停止并报告并发
变化。其他情况从同一调用时 HEAD 建外部 clean worktree 完整重跑，不要求用户清理。

### 固定上游并 prepare

Skill 位于 canonical `wlvh/coding-workflow` Git 根时复用其 object store；否则在目标与执行
checkout 外临时 shallow clone canonical 仓库，网络失败就停止，不回退缓存。调用：

```bash
python3 <skill-root>/scripts/sync_docs.py prepare \
  --target-repo <target> \
  --upstream-dir <upstream> \
  --language <zh|en>
```

只消费单行 JSON，整轮固定返回的 `target_head`、`upstream_sha` 和 language。临时 upstream
必须在最终回复前由当前 Agent 删除并验证不存在；失败则停止完成报告。prepare 从固定 object
验证九份 UTF-8 source 和八份非 PR active marker，只创建缺失文档，不覆盖已有 bytes。执行过程
与证据不持久化为仓库状态、Skill 副本、模板镜像或仓库内 PR body。

## Facts、改写与测试

### Findings 驱动的最小改写

写入前运行 `git -C <target> ls-files -z` 建范围，从当前代码、配置、测试、committed artifacts、
可重复结果和必要历史重建事实；旧文档和近期 diff 都不能自证。

- 描述性事实须有项目证据；规范性政策可由 scoped instruction、accepted decision、团队配置或
  持久化 owner decision 支持。混合语句拆分核验，禁止把事实改写成政策或把政策伪装成实现事实。
  配置只证明 enforcement，不自动 supersede 政策；同类政策按显式 supersession 与既有
  authority/scope 裁决。冲突登记 finding/open decision；权威仍不明时保留原文和已检查来源。
  个人偏好未被持久化时不进入项目。
- 任何语义编辑前登记 finding：唯一 ID、`BLOCKER/WARN/NOTE`、证据、风险、最小修复边界。
  同根因合并，多文档共同虚构能力必须是 BLOCKER，不得事后倒填。
- BLOCKER 表示候选会错误、虚构、越权、不可复现或遗漏关键风险，必须修复；WARN 表示实质性
  质量/维护风险，除非需要 owner 决策否则修复；NOTE 是不改变可交付性的非阻断观察。
- 从 finding 提取具体路径、命令、能力、字段、政策名与 superseded 术语，做定向 `git grep`
  或等价 tracked-file 搜索。完整核对九份核心文档，但不无条件审计全仓 Markdown/配置；范围外
  漂移只记录 exact path、snippet、风险和建议，由 owner 决定扩 PR、拆 PR 或开 Issue。
- 只改失真内容。不得因关键词、旧路径、命令或术语命中就删除父 heading/section；整节删除须由
  finding 证明全部语义失效。整段、整节删除或大范围替换后，重读完整 section 与相邻 section，
  确认有证据的政策、命令、能力和责任未被误删。
- 保持 `capability_contract.json → interact.md → docs/business_user_guide.md` 权威方向并清除
  active marker。Architecture 查入口/调用链/边界/数据流/错误/副作用；Capability 查 UI/API/
  tests/限制/anchor；Testing 查真实 gate；Governance 最后查 AGENTS、Checklist、SOP、PR
  template。四项是覆盖维度，不是固定 Agent 拓扑；通用模板不写 docs-sync 的 pin、seal、review
  隔离或发布实现。

新增 marker、alias、机器状态、parser、兼容入口或控制机制前，finding 必须证明独立风险、真实
消费者、可复现失败和现有机制不足；能扩展现有机制时不另造同义入口。

### 测试合同

从 `target_head` 的 TESTING、CI、构建配置和 accepted policy 取得 canonical gate，只运行项目
已定义的必要 gate。local/container/CI/remote 只是每次测试证据的 environment 属性，不是 Skill
mode。分别记录 exact command、scope、result、not-run reason、environment、side effects、
cleanup；一个解释器/环境的 PASS 不覆盖另一个尝试的 `BLOCKED` 或失败。

不得临时加入 workflow/runner、创建 validation-only ref、发明 docs-sync backend，或缺依赖时
静默改跑弱测试并称 PASS。当前环境无法运行必要 gate 时，只按项目既有政策使用受信任的
repository-owned gate；不存在时 `Tests: BLOCKED`。普通交付 head 不为临时测试环境提前 push；
项目政策已定义正式远端 gate 时才照其执行并披露副作用。

多解释器各自运行或记录原因。bug-first 与 no-test-diff 独立；无 test diff 时指出具体既有覆盖并
重跑。Unit/contract/scenario/golden/report build/repair/light/full/live 只按实际范围命名。正式
tests 在 seal 后执行。

## Seal、review 与 check

### Candidate tree

最终语义编辑后，逐一比较九个已知核心路径与 `target_head` tree 的存在性、类型、mode 和
bytes；不能只依赖 status/diff，因为 untracked ignored path 不可见。由此得到唯一 changed subset。
每个 changed path 必须是最终普通文件，并能用普通 `git add -- <explicit-paths>` 进入 index；
被 ignore 或需 force-add 时以 exact path `Candidate: REJECTED`，不运行 gates，也不修改 ignore
policy。

`.gitignore` 不属于发布 subset，但 final check 会读取它。seal 前必须证明它要么在 index 与
worktree 都不存在，要么已由 `target_head` 跟踪且 target/index/worktree 的 type、mode、bytes
完全一致；untracked、ignored、dirty、staged、symlink 或其他差异均 REJECTED。该发布约束比
unchanged sync checker 的 dirty allowlist 更窄，防止 check 消费 tree 外 bytes。

显式 stage 后，用 `git diff --cached --name-only -z` NUL-safe 确认 staged paths 精确等于
changed subset，运行 `git diff --cached --check` 与 `git diff --exit-code`，并从 NUL status
确认无 unexpected untracked/范围外 dirty。记录固定身份事实：target head、upstream SHA、
language、changed paths、`candidate_tree="$(git write-tree)"`，以及 PR 意图 true 时的
`base_ref`。

不创建 candidate JSON、patch SHA contract、evidence manifest、receipt 或 repository-local
candidate file。tests、review、final check 都绑定该 tree；每个 gate 前后执行
`test "$(git write-tree)" = "$candidate_tree"` 与 `git diff --exit-code`。修改使旧 tree 失效：
重新 stage/seal，重跑受影响测试并 review 新 tree，不保留生命周期状态。九文档零 diff 时以
target head tree 为 candidate；仍可 check，但不建空 commit/PR。

### Fresh-context review

Independent 与 self-review 都绑定 `(target_head, candidate_tree)`。优先 fresh-context
independent reviewer：完整仓库只读，blind-first 先从代码/配置/tests/committed artifacts 形成
高风险 findings，再读候选与原始 diff；不编辑、stage、commit、push 或写仓库。

记录 mode、可用的 reviewer/session/thread identity、reviewed head/tree、blind-first boundary
和 result。head/tree 任一变化即失效；仅 commit metadata 变化不重做语义 review。无认知隔离时
完整 self-review 并写 `Review: SELF_REVIEW`；用户明确要求 independent 而平台不可用时停止。
Review finding 复用前述 ID/severity/证据/风险/边界；修复全部 BLOCKER 与无需 owner 决策的 WARN
后 reseal、重跑受影响测试并 review 新 tree。

### Final check

在 sealed tree、commit 前运行：

```bash
python3 <skill-root>/scripts/sync_docs.py check \
  --target-repo <target> \
  --upstream-dir <upstream> \
  --upstream-sha <prepare 返回值> \
  --expected-target-head <prepare 返回值> \
  --language <zh|en>
```

它从固定 object 重验 source，再机械检查 target HEAD、dirty allowlist、index/worktree 分叉、九份
普通 UTF-8 非空文件、JSON、active marker、gitignore 和固定 whitespace；不证明文案语义、调查、
tests 或 review，不得用 commit 后 HEAD 绕过固定身份。

## 五条事实与 Draft 发布

### 独立状态

最终摘要固定为：

```text
Candidate: NOT_GENERATED | GENERATED | CHECKED | REJECTED
Tests: PASS | FAIL | BLOCKED | NOT_RUN
Review: INDEPENDENT_PASS | SELF_REVIEW | CHANGES_REQUESTED | NOT_RUN
Process deviations: NONE | <逐条自然语言说明>
Publication: NOT_REQUESTED | NO_CHANGES | DRAFT_VERIFIED | PR_BLOCKED
```

NOT_GENERATED：尚无 tree。GENERATED：tree 已形成，final check 尚未执行。CHECKED：同一 tree
通过 final check。REJECTED：identity/范围/check 已失败或候选被明确放弃；Tests FAIL 与 Review
CHANGES_REQUESTED 不自动推导 REJECTED。Tests、Review、Publication 不互推。无偏差写 NONE；
否则每条事实只标 DISCLOSED 或 OWNER_ACCEPTED，不另建 schema。不输出 Overall、Merge readiness、
Orchestrator result 或聚合 PASS/PARTIAL/FAIL。

状态轴独立只限制报告推导，不豁免动作前置条件。PR 意图 true 且 Candidate 不是 CHECKED 时，
不得 commit、push 或创建 PR，Publication 必须 PR_BLOCKED。若偏差已产生远端对象，仍按读回事实
报告 Publication，并在 Process deviations 明确写出越过的 gate；后续成功不能追溯抹掉违规。

Publication 优先级唯一：PR 意图 false 始终 NOT_REQUESTED；PR 意图 true 且九文档零 diff 才
NO_CHANGES；其余请求按远端事实为 DRAFT_VERIFIED 或 PR_BLOCKED。随后报告固定身份、证据、每次
test attempt、review finding/关闭证据、check 边界与原工作树复核。

### Commit、readback 与恢复

PR 意图 true 且有 diff 时，只有 Candidate CHECKED、必要 tests、所需 review、cleanup 和发布前
原工作树复核都通过后才：

1. 用 sealed index commit；断言 parent 等于 target head，`HEAD^{tree}` 等于 reviewed candidate。
2. 任何远端写入前重新解析 `base_ref`，要求其 SHA 仍等于 `target_head`，并 NUL-safe 证明
   candidate 相对该 base 的 changed files 精确等于 sealed subset；不一致即 PR_BLOCKED。
3. push 唯一 head branch，并以 `base_ref` 创建 Draft PR；不得静默改用 default base。
4. 读回 PR number、base、head、head SHA、能取得时的 head tree、Draft 状态、changed files；
   全部一致才 DRAFT_VERIFIED。

仓库外 PR body 记录 target head、base ref、candidate tree、changed files、findings、exact
tests、review、check、五条状态、known limits、rollback 和本地原工作树边界；sync checker
不参与 Git/GitHub 发布。

- **Readback unavailable**：403、GitHub 5xx、read permission 不足或 metadata 暂不可读。保留
  CHECKED candidate、commit、branch 和可能存在的 Draft；不回滚、不称 verified，PR_BLOCKED，
  给 exact recovery command 或权限事实。
- **Readback mismatch**：base/head/commit/tree/Draft/changed files 已确认不一致。保留本地
  candidate，尝试修正 branch/PR 后重读；无法安全修正时撤回或隔离错误远端对象，未闭合仍
  PR_BLOCKED。

无 remote/auth/push/PR 权限时也保留 checkout、branch、commit、仓库外 body，输出已解析身份的
recovery command，不猜未知值。只有 DRAFT_VERIFIED、原工作树两次复核无差异时才可移除外部
checkout；任何原工作树差异或 PR_BLOCKED 都保留。
