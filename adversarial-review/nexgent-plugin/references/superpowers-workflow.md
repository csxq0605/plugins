# Superpowers Workflow — adversarial-review 集成

当用户要求使用 superpowers 工作流时，adversarial-review 在以下阶段被调用：

## Step 8: Review 阶段

adversarial-review 替代默认的 reviewer teammate，提供 6 视角深度审查。

### 调用方式

```
# 启动审查会话
review_start(target="pr-branch-name", perspectives="all", mode="deep")

# 逐视角分析并添加发现
review_add_finding(session_id=..., id="SEC-001", perspective="security", ...)

# 计算健康评分
review_health_score(session_id=...)

# 导出报告
review_export(session_id=..., format="markdown")
```

### 与 team-coord 集成

Lead 可 spawn 6 个 reviewer worker，每个负责一个视角：
- Worker A → Security
- Worker B → Performance
- Worker C → Architecture
- Worker D → Code Quality
- Worker E → Test Quality
- Worker F → API Design

Lead 合并所有 worker 的发现，计算综合健康评分。

### Findings 判定

Lead 对每个 finding 做出判定：
- Critical → 必须修复，路由给 implementer
- Warning → 应该修复，路由给 implementer
- Suggestion → 可以跳过，记录但不路由

### 健康评分阈值

- 90+ → 可以合并
- 70-89 → 修复 Warning 后合并
- 50-69 → 修复 Critical + Warning 后合并
- < 50 → 不建议合并
