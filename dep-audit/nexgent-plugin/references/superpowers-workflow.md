# Superpowers Workflow — dep-audit 集成

当用户要求使用 superpowers 工作流时，dep-audit 在以下阶段被调用：

## Step 0: 项目文档布局 阶段

在开始开发前，扫描现有依赖的安全状态，识别需要先修复的漏洞。

## Step 8: Review 阶段

在代码审查时，检查新增依赖是否引入漏洞。

### 调用方式

```
# 完整审计
audit_full(path=".")

# 生成报告
audit_generate_report(path=".")

# 只检查新增依赖
audit_check_vulns(path=".")
```

### 与 team-coord 集成

Lead 可分配 worker 按生态系统并行审计：
- Worker A → npm 依赖
- Worker B → Python 依赖
- Worker C → 其他生态系统

Lead 合并结果，按严重程度排序，生成修复计划。

### 审计结果用途

- **Step 0** — 识别需要先修复的漏洞，作为开发前置条件
- **Step 8** — 检查 PR 是否引入新的漏洞
- **Step 10** — 合并前的最终安全检查
