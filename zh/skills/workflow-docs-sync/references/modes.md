# 安装与 mode 人工调用

每个 mode 必须在独立新会话使用。先把 Skill 根路径、目标路径和 SHA 替换为真实值。
`<workflow-docs-sync-root>` 必须解析为当前 canonical / installed `SKILL.md` 所在目录的
绝对路径；命令从目标仓库 cwd 执行时也不得把它缩写成目标仓库内的 `scripts/`。

## 使用模型

- Studio / 自动编排：直接把 pinned upstream 的 `zh/skills/` 作为 canonical
  skill source，不运行目标仓库安装器。
- 个人使用：运行 `python3 zh/scripts/install_skills.py --upstream-dir <checkout> --upstream-sha <完整SHA>`；
  默认写入用户级 `~/.agents/skills/` 与 `~/.claude/skills/`。
- 团队仓库安装：显式增加 `--scope repo --target-repo <仓库>`，并先通过独立安装 PR
  提交 `.agents/` 与 `.claude/`。
- 每个安装副本只携带 `.source.json`，记录 upstream SHA、canonical 相对路径和平台。
  切换 pinned SHA 前重新安装即可。

## Codex

```text
使用 $workflow-docs-sync。Mode: <PREPARE|PASS_1|PASS_2|PASS_3|PASS_4|SUBMIT>。
目标仓库：`<目标仓库绝对路径>`。Upstream SHA：`<完整 SHA>`。
```

## Claude Code

```text
/workflow-docs-sync Mode: <PREPARE|PASS_1|PASS_2|PASS_3|PASS_4|SUBMIT>。
目标仓库：`<目标仓库绝对路径>`。Upstream SHA：`<完整 SHA>`。
```

两个平台都必须由用户显式调用。Codex 安装产物设置
`allow_implicit_invocation: false`；Claude 安装产物由安装器加入
`disable-model-invocation: true`。

## Harness 命令

以下参数在每次调用中都显式提供：

```bash
python3 "<workflow-docs-sync-root>/scripts/harness.py" prepare \
  --target-repo <仓库> --upstream-dir <checkout> --upstream-sha <SHA>

python3 "<workflow-docs-sync-root>/scripts/harness.py" start-pass --mode PASS_1 \
  --target-repo <仓库> --upstream-dir <checkout> --upstream-sha <SHA>

python3 "<workflow-docs-sync-root>/scripts/harness.py" finish-pass --mode PASS_1 \
  --target-repo <仓库> --upstream-dir <checkout> --upstream-sha <SHA>

python3 "<workflow-docs-sync-root>/scripts/harness.py" prepare-submit \
  --target-repo <仓库> --upstream-dir <checkout> --upstream-sha <SHA>

python3 "<workflow-docs-sync-root>/scripts/harness.py" seal-submit \
  --target-repo <仓库> --upstream-dir <checkout> --upstream-sha <SHA>

python3 "<workflow-docs-sync-root>/scripts/harness.py" finish-submit --pr-number <编号> \
  --base <base> --head <head> \
  --target-repo <仓库> --upstream-dir <checkout> --upstream-sha <SHA>

python3 "<workflow-docs-sync-root>/scripts/harness.py" status \
  --target-repo <仓库>
```

`prepare-submit` 只进入 active、unsealed 状态。测试和 `PR Test Evidence` 完成后才运行
`seal-submit`；只有 seal 成功才可以 commit / push / 更新远端 PR。普通证据错误直接
修正后重试 seal，不删除 runtime。`finish-submit` 要求从 SUBMIT `start_head` 到远端
head 恰好新增一个 commit，并绑定 sealed 路径、内容、executable bit 与 PR body。

若 seal 暴露 PASS-owned 问题，不修改或删除失败 runtime，也不把当前 worktree
rebaseline。从失败仓库本地 clone（不依赖已发布 remote branch），把原 head 分支指向
SUBMIT baseline 的 `start_head`，并恢复真实 GitHub `origin`，再从 `prepare`、
PASS_1–4、`prepare-submit` 完整重跑。旧 run 只保留为失败证据；整个重启过程在最终
SUBMIT 前不创建 commit。开始前必须从失败仓库记录真实发布 URL；缺失时 fail-fast，
不得把指向失败 worktree 的 clone source remote 当成发布 remote。

```bash
git -C <failed-repo> remote get-url origin  # 记录为 <publish-url>
git clone --no-local --no-checkout --origin failed-source \
  <failed-repo> <restart-dir>
git -C <restart-dir> switch -C <head> "<SUBMIT start_head>"
git -C <restart-dir> remote add origin <publish-url>
test "$(git -C <restart-dir> rev-parse HEAD)" = "<SUBMIT start_head>"
test "$(git -C <restart-dir> branch --show-current)" = "<head>"
test "$(git -C <restart-dir> remote get-url origin)" = "<publish-url>"
```
