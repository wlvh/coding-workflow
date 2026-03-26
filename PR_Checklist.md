# PR提交检查清单
注意：你必须一一完成check清单（等价于todo list）并最终提交pr，任何偷懒和跳过都会让用户暴跳如雷。
为了保持代码简洁，节约代码审核者的上下文窗口，如需在用户明确同意的前提下整理当前 HEAD 提交，可使用 git commit --amend（仅覆盖当前 HEAD 一条提交；如需合并多条提交，请先 git reset --soft <基准> 或 git rebase -i 做 squash 后再提交）。
使用 gh pr create --title（修改主题+MMDD日期） --body-file（建议使用 `PR_BODY.md`） --head <feature-branch> --base master 来创建PR，固定指令避免遗漏参数。始终牢记你可以使用gh工具。
在提交 PR 前的确认清单，你需要将其转为todo list进行step by step的完成：
- [ ] 撰写结构化的工作总结，至少包含以下小节，确保下一个开发人员能顺利接手继续开发：
  - 背景 & 目标（Why）：本次改动解决了什么问题？关联哪些 Issue / 需求？
  - 实现方案（How）：核心思路、关键设计决策、有无其他候选方案。
  - 变更范围（What）：主要修改了哪些模块/文件（可按目录分组列出）；文件清单必须来自 `git diff --name-only <base>...HEAD` 的实际输出，禁止写未出现在当前 patch 中的文件。
- [ ] 确认当前分支不是主干，并调用 git diff 工具仔细分析本地修改，确认无遗漏
- [ ] 已用 `git diff --name-only <base>...HEAD` 反向核对 `PR_BODY.md` 的“变更范围/测试文件”清单：diff 中有但 PR_BODY 未列的已补齐，PR_BODY 中列了但 diff 中不存在的已删除
- [ ] 测试策略以 `TESTING.md` 为准：按“变更类型决策表”选择并跑通必跑 Stage（优先使用 `.\run_tests.ps1`）；PR 描述必须分别提供：
  - 测试证据（Stage + 命令 + 关键输出摘要/日志/CI link；不适用的 Stage 标注 N/A 并写清原因）
  - 测试变更清单（实际新增/修改了哪些测试文件；若仅重跑 Stage 而未修改测试文件，必须明确写“未修改测试文件，仅重跑 <Stage> 作为 gate”）
- [ ] 检查所有本次新增/修改的测试文件是否遵循了 `TESTING.md` 中的测试原则
- [ ] 当有文件新增和修改后，确认对应的文档已更新。例如新增了测试文件，就需要更新在`TESTING.md`，有代码脚本的功能被修改，更新在`AGENTS.md`的## 文件简介。
- [ ] 任何用户可见的行为变化（入口/输出结构/默认行为/错误提示/排序稳定性）都必须同步更新`interact.md`，并确保浏览器验收覆盖了对应断言
- [ ] 最终提交前，已重新对照 `git diff --name-only <base>...HEAD`、`git status` 与 `PR_BODY.md`，确认 PR 描述不包含历史草稿、本地未提交改动或“计划做但未落地”的内容
