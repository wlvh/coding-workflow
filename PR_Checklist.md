# PR提交检查清单
## Commit / Push 策略

本项目默认采用“单 PR 单 commit + PR body 记录修复轮次”的策略。

目标：
- 保持 PR 对外 commit history 简洁。
- 避免 reviewer / LLM 被 commit timeline 分散注意力。
- 用 PR body 的“Review / 修复记录”保存每轮 review 与修复历史。

规则：
1. 一个 PR 默认保持 1 个 commit。
2. 每轮 review / 修复后，必须先更新 PR body 的“Review / 修复记录”。
3. 修复代码、测试、文档后，使用 `git commit --amend` 合入当前 commit。
4. 推送重写后的 PR 分支时，必须使用 `git push --force-with-lease`，禁止裸 `git push --force`。
5. PR_body模板参照.github/pull_request_template.md

## PR提交检查清单
注意：你必须一一完成check清单（等价于todo list）并最终提交pr，任何偷懒和跳过都会让用户暴跳如雷。
使用 gh pr create --title（修改主题+MMDD日期） --body-file（.github/pull_request_template.md作为模板） --head <feature-branch> --base master 来创建PR，固定指令避免遗漏参数。始终牢记你可以使用gh工具。

在提交 PR 前的确认清单，你需要将其转为todo list进行step by step的完成：
- [ ] 撰写结构化的工作总结，至少包含以下小节，确保下一个开发人员能顺利接手继续开发：
  - 背景 & 目标（Why）：本次改动解决了什么问题？关联哪些 Issue / 需求？
  - 实现方案（How）：核心思路、关键设计决策、有无其他候选方案。
  - 变更范围（What）：主要修改了哪些模块/文件（可按目录分组列出）；文件清单必须来自 `git diff --name-only <base>...HEAD` 的实际输出，禁止写未出现在当前 patch 中的文件。
- [ ] 确认当前分支不是主干，并调用 git diff 工具仔细分析本地修改，确认无遗漏
- [ ] 已用 `git diff --name-only <base>...HEAD` 反向核对 `PR_BODY.md` 的“变更范围/测试文件”清单：diff 中有但 PR_BODY 未列的已补齐，PR_BODY 中列了但 diff 中不存在的已删除
- [ ] 测试策略以 `TESTING.md` 为唯一权威：已按 `TESTING.md` 判断本 PR 是否需要新增/修改测试、需要运行哪些测试、以及测试证据如何记录。
- [ ] 如果本 PR 新增/修改测试文件，已按 `TESTING.md` 更新测试文件简介或相关测试说明。
- [ ] 当有文件新增和修改后，确认对应的文档已更新。例如新增了测试文件，就需要更新在`TESTING.md`，有代码脚本的功能被修改，更新在`AGENTS.md`的## 文件简介。
- [ ] 任何用户可见的行为变化（入口/输出结构/默认行为/错误提示/排序稳定性）都必须同步更新`interact.md`，并确保浏览器验收覆盖了对应断言
- [ ] 最终提交前，已重新对照 `git diff --name-only <base>...HEAD`、`git status` 与 `PR_BODY.md`，确认 PR 描述不包含历史草稿、本地未提交改动或“计划做但未落地”的内容
