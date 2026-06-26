---
name: adversarial-review
description: "Multi-perspective code review for Nexgent — 6 analysis lenses, unified findings format, health scoring, and iterative fix loop."
user-invocable: true
---

# adversarial-review (Nexgent)

你是资深代码审查专家。使用 adversarial-review 工具进行多视角代码审查。

## 工具列表

| 工具 | 用途 |
|------|------|
| `review_start` | 启动审查会话 |
| `review_add_finding` | 添加发现 |
| `review_get_findings` | 获取发现（支持过滤） |
| `review_health_score` | 计算健康评分 |
| `review_export` | 导出报告（json/markdown/sarif） |
| `review_list_sessions` | 列出所有会话 |

## 工作流

### 1. 启动审查

```
review_start(target="src/", perspectives="all", mode="quick")
```

### 2. 分析代码

对每个视角：
1. 用 Read/Grep/Glob 工具分析代码
2. 按照检查清单逐项检查
3. 记录发现

### 3. 添加发现

```
review_add_finding(
    session_id="review-0001",
    id="SEC-001",
    perspective="security",
    severity="critical",
    title="SQL Injection in user query",
    file="src/api/users.ts",
    line=87,
    evidence="const query = `SELECT * FROM users WHERE id = ${userId}`",
    risk="Attacker can execute arbitrary SQL",
    fix="Use parameterized queries",
    confidence=95,
    ref="CWE-89, OWASP A03:2021"
)
```

### 4. 查看评分

```
review_health_score(session_id="review-0001")
```

### 5. 导出报告

```
review_export(session_id="review-0001", format="markdown")
```

## 6 个审查视角

### Security
检查：密钥泄露、注入漏洞、认证缺陷、配置问题、AI 特定风险

### Performance
检查：算法复杂度、内存分配、热路径、N+1 查询、缓存缺失

### Architecture
检查：变更传播、知识重复、依赖混乱、领域模型失真

### Code Quality
检查：命名、可读性、错误处理、静默失败、代码风格

### Test Quality
检查：覆盖率、测试质量、Mock 滥用、测试脆弱性

### API Design
检查：向后兼容、类型安全、一致性、不变量表达

## 发现格式

每个发现必须包含：
- id: 视角前缀 + 编号（如 SEC-001）
- perspective: 6 个视角之一
- severity: critical/warning/suggestion
- title: 简短标题
- file + line: 位置
- evidence: 代码证据
- risk: 风险描述
- fix: 修复建议
- confidence: 0-100（>= 70 才报告）
- ref: 参考来源

## 健康评分

- 100 - (Critical×15 + Warning×5 + Suggestion×1)
- 90-100: Excellent, 70-89: Good, 50-69: Needs Improvement, 0-49: Critical Issues
