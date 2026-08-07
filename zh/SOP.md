# Standard Operating Procedures

## Purpose and Authority

`SOP.md` 只保存稳定流程入口，不复制易漂移的命令、测试清单或发布细节。发生冲突时，以
当前代码、配置、测试、契约以及 `TESTING.md`、`PR_Checklist.md` 等专项权威为准。执行记录的
保存方式与保留期限遵循本项目真实的审计、可恢复性和交付政策。

## Available SOPs

<!-- project-fill: 列出本项目真实存在的 SOP 名称和权威入口；没有时替换为 None — 已检查的范围与原因；完成后删除此 marker -->

## SOP Entry Structure

每个 SOP step 只包含：

1. Action：要执行的稳定动作。
2. Authority / Source：应读取的权威入口，不复制其易漂移内容。
3. Acceptance：如何用当前测试、artifact 或可观察结果判断完成。

## Failure, Rollback, and Escalation

失败时停止在安全边界，保留精确错误和当前仓库状态；回滚方式必须与真实持久化及副作用
模型一致。需要权限、产品判断或外部协调时，明确升级给责任人，不猜测或绕过。

<!-- project-fill: 写入本项目已验证的停止条件、可恢复回滚入口和升级责任；没有专属规则时写 None — 已验证原因；完成后删除此 marker -->

所有文本文件使用 LF 换行与 UTF-8 编码，除非仓库配置明确规定其他格式。
