# Issue Closure FSD Acceptance Prompt

> **历史提示，已退出默认索引。** coding-loop v2 使用 [用户路径验收](user_acceptance.md)：
> Issue 阶段定义验收，可运行候选在交付前实测，仅部署相关缺口留待补验。已有 FSD 可以作为
> 适用规格的证据；普通内部实现变化不自动要求用户批准或改写需求。下文保存旧回路的收口模板，
> 不能覆盖当前 [公共约定](coding_common.md) 或据此将验收推迟到合入主干后。

## 用途

用于在 issue 关闭前，基于主干代码核对 FSD 是否全部实现到位。

## Prompt

```text
当前 issue（贴上 head id，不然会搞混）的开发已经完成并合入主干，从主干代码仔细检查当前 issue 的 FSD 是否全部完成，如果与最初 FSD 有任何实现细节上的出入（即便是合理的工程优化），必须要求生成一个 Updates to FSD 的列表。

执行 FSD 完备性验收：

1. 读取当前 issue 描述中的 FSD 内容
2. 在代码库中找到每个 Spec Unit 的实现
3. 对比实现与 FSD 规格的一致性
4. 输出验收报告，格式如下：

## FSD 完备性验收报告

### Spec Unit 核对
| Spec Unit | 状态 | 实现位置 | 备注 |
|-----------|------|---------|------|

### Updates to FSD（如有偏差）
- 列出需要回写 FSD 的内容

### 验收结论
- [ ] 可关闭 Issue
- [ ] 需补充开发
- [ ] 需更新 FSD 后关闭
```
