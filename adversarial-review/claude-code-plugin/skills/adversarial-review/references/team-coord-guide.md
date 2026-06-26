# adversarial-review × team-coord 集成指南

当 adversarial-review 与 team-coord 共存时，lead 可以 spawn 多个 reviewer worker 并行审查。

## 何时使用 team-coord 模式

- 代码变更 > 10 个文件
- 需要深度审查（每个视角需要仔细分析）
- 时间紧迫，需要并行加速

小规模审查（< 5 个文件）用单 agent 快速模式即可。

## Lead 工作流

### Step 1: 分析变更范围

```
git diff --stat HEAD~1
```

确定需要审查的文件列表。

### Step 2: Spawn 6 个 Reviewer Worker

在一条消息中 spawn 所有 worker：

```
你是 reviewer-security，负责安全审查。

你的第一个动作：Skill('team-coord:teammate')

任务：从安全视角审查以下文件，检查 OWASP Top 10、密钥泄露、注入漏洞、认证缺陷。
文件列表：[文件列表]
成功标准：每个发现必须有代码证据，使用统一格式
依赖：无

⚠️ 硬规则：
- 用 Read、Grep 等工具分析代码
- 完成后用 SendMessage 把原始发现发给我
- 我负责综合所有 worker 的结果输出统一报告
```

类似地 spawn：reviewer-performance、reviewer-architecture、reviewer-quality、reviewer-test、reviewer-api。

### Step 3: 等待汇报

用 `team_check_inbox` 轮询收件箱，收集所有 reviewer 的原始发现。

### Step 4: 综合输出

1. 去重：不同 reviewer 可能发现同一问题
2. 冲突解决：安全说"加验证" vs 性能说"验证是热路径"
3. 统一格式
4. 计算健康评分
5. 输出统一报告

## Worker Spawn Brief 模板

### Security Reviewer
```
任务：从安全视角审查代码。检查：密钥泄露、注入漏洞、认证缺陷、配置问题、AI 特定风险。
参考：Read 'skills/adversarial-review/references/patterns.md' 中的安全模式。
```

### Performance Reviewer
```
任务：从性能视角审查代码。检查：算法复杂度、内存分配、热路径、N+1 查询、缓存缺失。
```

### Architecture Reviewer
```
任务：从架构视角审查代码。检查：变更传播、知识重复、依赖混乱、领域模型失真。
参考：Read 'skills/adversarial-review/references/risk-dimensions.md' 中的 6 个风险维度。
```

### Code Quality Reviewer
```
任务：从代码质量视角审查代码。检查：命名、可读性、错误处理、静默失败、代码风格。
```

### Test Quality Reviewer
```
任务：从测试质量视角审查代码。检查：覆盖率、测试质量、Mock 滥用、测试脆弱性。
```

### API Design Reviewer
```
任务：从 API 设计视角审查代码。检查：向后兼容、类型安全、一致性、不变量表达。
```

## 与 Superpowers 对接

在 superpowers 工作流的 Step 8（Spawn Reviewers）中，可以使用 adversarial-review 替代默认的 code-review：

```
你是 reviewer-pr-1，负责审查 PR #1。

范围：PR #1 的所有变更
成功标准：
- 6 个视角全部审查完成
- 使用统一发现格式
- 健康评分 >= 70

审查参考：Read 'skills/adversarial-review/SKILL.md'
```
