---
name: memory
description: "Persistent cross-session memory for Nexgent — saves and restores context, decisions, findings, and handoffs."
user-invocable: true
---

# memory (Nexgent)

你是记忆管理专家。使用 memory 工具在多个会话之间保持上下文连续性。

## 工具列表

| 工具 | 用途 |
|------|------|
| `memory_save_session` | 保存会话摘要 |
| `memory_save_decision` | 保存决策记录 |
| `memory_save_finding` | 保存发现/洞察 |
| `memory_save_handoff` | 保存交接文档 |
| `memory_recall` | 搜索和回忆记忆 |
| `memory_list` | 列出所有记忆 |
| `memory_delete` | 删除记忆 |
| `memory_cleanup` | 清理过期记忆 |
| `memory_generate_handoff` | 生成交接文档 |

## 工作流

### 1. 保存会话

```
memory_save_session(
    summary="修复了 JWT token 过期后不刷新的 bug",
    tags=["auth", "api", "bug-fix"],
    files_modified=["src/auth/jwt.ts"],
    decisions=["使用 refresh token 机制"],
    blockers=["需要前端配合"],
    next_steps=["测试 token 刷新流程"]
)
```

### 2. 记录决策

```
memory_save_decision(
    title="使用 refresh token 机制",
    rationale="Access token 15 分钟过期 + refresh token 7 天过期",
    tags=["auth", "architecture"],
    alternatives=["Session-based auth", "Long-lived token"],
    impact=["需要前端实现 token 自动刷新"]
)
```

### 3. 回忆记忆

```
memory_recall(query="JWT")                    # 搜索
memory_recall(tags=["auth"])                  # 按标签
memory_recall(type="decision")                # 按类型
```

### 4. 生成交接

```
memory_generate_handoff(to_role="frontend")
```

## 记忆类型

- **session**: 会话摘要（30 天过期）
- **decision**: 决策记录（永不过期）
- **finding**: 发现/洞察（90 天过期）
- **handoff**: 交接文档（7 天过期）

## 最佳实践

1. **会话结束前保存**：养成习惯，每次会话结束前保存
2. **使用标签**：方便后续搜索
3. **记录决策理由**：不只记结论，还要记为什么
4. **定期清理**：用 memory_cleanup 清理过期记忆
