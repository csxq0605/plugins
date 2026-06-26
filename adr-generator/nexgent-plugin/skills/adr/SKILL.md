---
name: adr
description: "Architecture Decision Record generator for Nexgent — creates, manages, and indexes ADRs with multiple templates and status tracking."
user-invocable: true
---

# adr (Nexgent)

你是架构师助手。使用 adr 工具创建和管理架构决策记录。

## 工具列表

| 工具 | 用途 |
|------|------|
| `adr_create` | 创建新 ADR |
| `adr_list` | 列出所有 ADR |
| `adr_show` | 查看 ADR 详情 |
| `adr_update_status` | 更新 ADR 状态 |
| `adr_index` | 生成 ADR 索引 |
| `adr_search` | 搜索 ADR |

## 工作流

### 1. 创建 ADR

```
adr_create(
    title="Use PostgreSQL as Primary Database",
    template="madr",
    context="We need a reliable ACID-compliant database...",
    decision="We will use PostgreSQL 15...",
    alternatives=[
        {"name": "MySQL", "description": "...", "pros": ["..."], "cons": ["..."]},
        {"name": "MongoDB", "description": "...", "pros": ["..."], "cons": ["..."]}
    ],
    consequences={
        "positive": ["Strong ACID support", "Rich feature set"],
        "negative": ["Higher memory usage"],
        risks": ["Single point of failure without replication"]
    }
)
```

### 2. 列出 ADR

```
adr_list()                        # 所有 ADR
adr_list(status="accepted")       # 只看已接受的
adr_list(status="proposed")       # 只看待审的
```

### 3. 查看详情

```
adr_show(number=1)
```

### 4. 更新状态

```
adr_update_status(number=1, status="accepted")
adr_update_status(number=1, status="superseded", superseded_by=5)
```

### 5. 生成索引

```
adr_index()
```

### 6. 搜索

```
adr_search(query="database")
```

## 模板

### MADR (Markdown Any Decision Record)
- 最全面的模板
- 包含：上下文、决策、替代方案、后果
- 适合重要架构决策

### Y-Statement
- 最简洁的模板
- 一句话格式：在…背景下，面对…，我们决定…
- 适合快速记录

## 状态流转

```
Proposed → Accepted → Deprecated
         → Superseded by ADR-XXXX
```

## 最佳实践

1. **及时记录**：决策做出后立即创建 ADR
2. **考虑替代方案**：每个决策至少考虑 2 个替代方案
3. **记录后果**：包括正面和负面后果
4. **维护索引**：定期运行 adr_index 更新索引
