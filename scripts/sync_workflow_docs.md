# Sync Workflow Docs Prompt

## 你要做什么

你要执行一次 `full_reconcile`：把当前项目事实和最新 `wlvh/coding-workflow` upstream 规则放在一起，全量检查 9 个核心文档是否仍然可信。

本流程不做增量 baseline，不读取或写入 `.coding_workflow/source.json`。

---

## 第一步：运行 sync

```bash
curl -fsSL https://raw.githubusercontent.com/wlvh/coding-workflow/main/scripts/sync.sh | bash
```

它会：

- clone 最新 `wlvh/coding-workflow` 到临时目录；
- 检查当前目录是 git worktree；
- 拒绝未提交的项目代码 / 配置 / 测试变更；
- 安装缺失的 9 个核心文档模板；
- 写入 `.coding_workflow/diffs/` 作为本次运行证据；
- 自动确保 `.gitignore` 忽略 `PR_BODY.md` 和 `.coding_workflow/diffs/`；
- 打印 PR body 需要复制的 sync summary、后续指引 raw URL 和 upstream raw URL。
- 打印 working tree evidence 状态，说明 `project_head_commit` 是 sync 运行时 base commit，证据内容来自工作区。

允许 dirty 的文件：

- 9 个核心文档；
- `.gitignore`；
- `PR_BODY.md`；
- `.coding_workflow/diffs/`。

其他 dirty 文件必须先 commit / stash / discard。

---

## 第二步：读取 sync 证据

按顺序读取：

1. `.coding_workflow/diffs/full_reconcile_report.md`
2. `.coding_workflow/diffs/installation_status.md`
3. `.coding_workflow/diffs/upstream_vs_local/`

状态含义：

- `installed_template`：文件缺失，sync 刚安装模板，必须项目化。
- `template_copy_requires_specialization`：文件和 upstream 完全一致，除 PR template 外必须解释或项目化。
- `partially_specialized`：仍含模板占位符，必须修。
- `inherited_upstream_allowed`：只允许 PR template 使用。
- `specialized`：看起来已项目化，但仍需 reviewer 对照 upstream 检查。

---

## 第三步：写 Repo Facts Map

在动核心文档前，先在 PR body 写完整 10 项 Map。每项必须有证据指针；没有证据时写“待人工确认”，不能编。

```markdown
## Repo Facts Map

### 1. 项目类型
证据:

### 2. 系统输入
证据:

### 3. 系统输出
证据:

### 4. 用户身份
证据:

### 5. 核心模块清单
证据:

### 6. 主要数据流
证据:

### 7. 关键不变量
证据:

### 8. 当前能力清单
证据:

### 9. 测试现状
证据:

### 10. 不确定项
```

原因：full reconcile 的目标不是把 upstream 文本搬进项目，而是用当前项目事实重新判断 9 个核心文档是否可信。

---

## 第四步：全量检查 9 个核心文档

对每个核心文件都做三步：

1. 读最新 upstream raw URL。
2. 读本地文件。
3. 判断本地是否已经把 upstream 规则项目化，且是否符合 Repo Facts Map。

9 个核心文件：

- `AGENTS.md`
- `architecture.md`
- `capability_contract.json`
- `interact.md`
- `docs/business_user_guide.md`
- `TESTING.md`
- `PR_Checklist.md`
- `SOP.md`
- `.github/pull_request_template.md`

注意：

- 本地文件可以因为项目特化而不同于 upstream。
- upstream 新增原则时，要检查它应该投影到哪些本地文档，而不是只改 diff hunk。
- 如果用户明确说明某些模板文件不应项目化，PR body 必须记录这个决策和理由。

---

## 第五步：刷新证据

文档修改完成后，重新运行 sync：

```bash
curl -fsSL https://raw.githubusercontent.com/wlvh/coding-workflow/main/scripts/sync.sh | bash
```

然后用最新输出覆盖 PR body 中这些段：

- `Sync Summary`
- `Working Tree State at Sync Time`
- `Upstream Templates at Sync Time`
- `Installation Status`
- `Full Document Reconcile`
- `Remaining Human Decisions`

保留人工写的 `Repo Facts Map`，但如果文档修改改变了事实判断，也要同步更新 Map。

---

## 第六步：PR body 必填格式

```markdown
## Repo Facts Map
(完整 10 项)

## Sync Summary
- sync mode: full_reconcile
- upstream_resolved_commit:
- project_head_commit:
- evidence_source: working_tree
- core files checked: 9

## Working Tree State at Sync Time
(复制 full_reconcile_report.md 中的工作区状态；最终 review 以 PR head 上的核心文档为准)

## Upstream Templates at Sync Time
(9 个 raw URL)

## Installation Status
| File | Action | Note |
|---|---|---|

## Full Document Reconcile
| 文件 | 当前判断 | 是否需要更新 | 证据 |
|---|---|---|---|

## Remaining Human Decisions
none / 待人工确认项
```

---

## 禁止事项

- 禁止跳过 Repo Facts Map 直接改文档。
- 禁止提交 `.coding_workflow/diffs/`。
- 禁止把 `installed_template`、`template_copy_requires_specialization`、`partially_specialized` 状态静默带进 PR。
- 禁止把 `<项目名>`、`<对象>`、`sample_*`、`<!-- capability-anchor: TODO -->` 等模板残留作为正式文档。
- 禁止把 PR body 写成“已全量检查”，但不给每个核心文档的证据。
- 禁止引用不存在的 `prompts/sync_*.md`；sync 文件位于 `scripts/`。
