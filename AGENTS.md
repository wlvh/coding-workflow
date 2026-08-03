# 仓库维护入口

本仓库发布双语下游工作流模板、canonical `workflow-docs-sync` Skill 和安装器。

- `zh/` 是中文语义源；`en/` 是从中文派生的模板与说明。
- 根 `.github/` 是本仓库 CI 与 GitHub 基础设施；`zh/.github/`、`en/.github/` 是下游模板源。
- 修改模板：先改 `zh/` 对应九份核心文件，再同步 `en/`。
- 修改 Skill：进入 `zh/skills/workflow-docs-sync/`。
- 修改安装器：进入 `zh/scripts/install_skills.py`。
- 修改入口说明：更新根 README、`zh/README.md` 与 `en/README.md`；详细工作流在
  `zh/docs/development_workflow/`，实现决策在其 `decisions.md`。
- 修改测试：进入 `tests/test_workflow_docs_sync.py`；具体约束以测试代码为准，不在此复制。

新增 marker、alias、机器状态、parser、兼容入口或其他控制机制前，必须先证明它表达独立状态，
并存在真实消费者与可复现失败路径。若扩展现有机制可以覆盖：

- 先登记 finding；
- 说明最小扩展边界与新增成本；
- 不得改用同义 alias；
- 若与用户指定实现不同，先说明替代方案。

缺少真实缺口或消费者证据时保持零 diff，不因用户给出了具体实现方案就机械执行。

最短验证入口：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider
```

完整维护地图与补充验证见 [zh/README.md](zh/README.md#维护者地图)。
