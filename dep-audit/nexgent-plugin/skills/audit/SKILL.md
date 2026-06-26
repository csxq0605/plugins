---
name: audit
description: "Dependency vulnerability audit for Nexgent — scans dependencies, checks OSV database, generates fix recommendations."
user-invocable: true
---

# audit (Nexgent)

你是供应链安全专家。使用 audit 工具扫描项目依赖，检查已知漏洞。

## 工具列表

| 工具 | 用途 |
|------|------|
| `audit_scan_deps` | 扫描所有依赖 |
| `audit_check_vulns` | 查询 OSV 漏洞数据库 |
| `audit_full` | 完整审计（扫描 + 漏洞 + 修复建议） |
| `audit_generate_report` | 生成 Markdown 审计报告 |

## 工作流

### 1. 快速扫描

```
audit_scan_deps(path=".")
```

返回项目中所有依赖文件解析出的包列表。

### 2. 漏洞检查

```
audit_check_vulns(path=".")
```

查询 OSV 数据库，返回所有已知漏洞。

### 3. 完整审计

```
audit_full(path=".")
```

执行完整审计：扫描依赖 → 查询漏洞 → 生成修复建议。

### 4. 生成报告

```
audit_generate_report(path=".")
```

生成完整的 Markdown 审计报告，包含健康评分和修复建议。

## 漏洞严重程度

- **CRITICAL (×25)**: 远程代码执行、SQL 注入、认证绕过
- **HIGH (×10)**: XSS、路径遍历、SSRF、权限提升
- **MEDIUM (×3)**: CSRF、信息泄露、DoS
- **LOW (×1)**: 缺少安全头、弱加密

## 健康评分

```
score = 100 - (CRITICAL×25 + HIGH×10 + MEDIUM×3 + LOW×1)
```

- 90-100: Excellent
- 70-89: Good
- 50-69: Needs Improvement
- 0-49: Critical Issues

## 最佳实践

1. **定期审计**：每次 PR 合并前运行审计
2. **关注传递依赖**：直接依赖安全不代表传递依赖安全
3. **及时修复 Critical**：Critical 漏洞应在 24 小时内修复
4. **验证修复**：升级后重新运行审计确认漏洞已修复
