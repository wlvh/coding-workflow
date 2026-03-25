# Issue Closure FSD Acceptance Prompt

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
