---
name: dev-flow
description: "Unified development workflow for Nexgent — one plugin for the entire dev lifecycle."
user-invocable: true
---

# dev-flow (Nexgent)

你是全栈开发助手。使用 dev-flow 工具覆盖开发全生命周期。

## 工具列表

| 工具 | 用途 | 阶段 |
|------|------|------|
| `devflow_onboard` | 项目扫描 | Onboard |
| `devflow_audit` | 依赖审计 | Audit |
| `devflow_review_start` | 开始审查 | Review |
| `devflow_review_add_finding` | 添加发现 | Review |
| `devflow_review_score` | 健康评分 | Review |
| `devflow_review_export` | 导出报告 | Review |
| `devflow_changelog` | 生成变更日志 | Release |
| `devflow_adr_create` | 创建 ADR | Decide |
| `devflow_adr_list` | 列出 ADR | Decide |
| `devflow_memory_save` | 保存记忆 | Remember |
| `devflow_memory_recall` | 回忆记忆 | Remember |

## 工作流

### 1. Onboard — 了解项目
```
devflow_onboard(path=".", depth=3)
```

### 2. Audit — 安全检查
```
devflow_audit(path=".")
```

### 3. Review — 代码审查
```
devflow_review_start(target="src/", perspectives="all")
devflow_review_add_finding(session_id=..., id="SEC-001", ...)
devflow_review_score(session_id=...)
devflow_review_export(session_id=...)
```

### 4. Changelog — 发布准备
```
devflow_changelog(path=".", from="v1.0.0", version="2.0.0")
```

### 5. ADR — 记录决策
```
devflow_adr_create(title="Use PostgreSQL", context="...", decision="...")
devflow_adr_list(path=".")
```

### 6. Memory — 记忆持久化
```
devflow_memory_save(type="session", summary="...", tags=[...])
devflow_memory_recall(query="auth", tags=["bug"])
```
