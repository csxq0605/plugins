# Superpowers 开发工作流

本文档是 `team-coord:lead` 的完整开发 lifecycle 参考。当用户要求使用 superpowers 工作流时，按本文档执行。

---

## 总览

```
Step  0   项目文档布局
Step  1   Brainstorming — 需求讨论、设计空间探索
Step  2   Writing-plans — 编写实现计划
Step  3   Worktree 创建 + spawn implementer teammates
Step 4-7  Implementer 执行（由 teammate 自行处理）
Step  8   Spawn reviewer teammates（每个 PR 一个 reviewer）
Step  9   Fix loop — lead 判定 findings、路由给 implementer
Step 10   Merge + cleanup — ExitWorktree、TeamDelete
```

---

## 核心原则

### WHAT vs HOW

Lead 只负责 WHAT，不干涉 HOW。

| Lead 负责（WHAT）         | Lead 不碰（HOW）             |
|---------------------------|------------------------------|
| 任务目标、scope、成功标准  | 具体实现方式、代码细节        |
| 哪个 finding 值得修       | 用什么 pattern、架构决策      |
| 优先级排序、任务路由       | teammate 的内部工作流         |
| 整体进度、用户沟通         | inbox sync、工具调用细节      |

### Worktree 隔离

每个 implementer 获得独立的 git worktree。好处：
- 并行开发不冲突
- 出问题可以直接丢弃 worktree
- main branch 保持干净

### Reviewer 一次性

每轮 review spawn 新的 reviewer teammate。好处：
- 每次都是 fresh eyes
- 避免 reviewer 对自己的 review 产生疲劳
- 完成后直接关闭，不需要用户批准

### Lead 全局视角

Lead 拥有全局视图，用于：
- 判定哪些 findings 真正重要（vs nitpick）
- 决定修复优先级
- 协调多个 implementer 之间的边界
- 防止 scope creep

---

## Step 0: 项目文档布局

在开始任何开发前，确保项目有以下文档结构：

```
docs/
├── vision.md              # 项目愿景、核心价值主张
├── overview.md            # 系统架构概览、技术栈
├── specs/
│   └── A-<name>.md        # 功能规格（每个 feature 一个文件）
├── plans/
│   └── PlanN-<name>.md    # 实现计划（Step 2 产出）
└── progress/
    └── PlanN-<name>.md    # 进度跟踪（implementer 更新）
```

### 各文件职责

**vision.md**
- 项目为什么存在？解决什么问题？
- 目标用户是谁？
- 核心差异化是什么？
- Lead 与用户在 Step 1 中共同确定

**overview.md**
- 系统整体架构图（ASCII 或 Mermaid）
- 技术栈选择及理由
- 关键模块及其职责
- 数据流、依赖关系
- Lead 在 Step 1 结束时整理

**specs/A-\<name\>.md**
- 每个 feature 的详细规格
- 包含：用户故事、验收标准、边界条件、out of scope
- Lead 在 Step 2 中为每个 feature 创建

**plans/PlanN-\<name\>.md**
- 实现计划：任务分解、依赖关系、预估工作量
- 每个 task 的 success criteria
- Lead 在 Step 2 中编写

**progress/PlanN-\<name\>.md**
- Implementer 负责更新
- 记录完成的 task、遇到的 blocker、实际工作量
- Lead 在 Step 9 中审阅

---

## Step 1: Brainstorming

**目标**：与用户充分讨论需求，探索设计空间，达成共识。

### 1.1 引导讨论

- 询问用户想解决什么问题、期望的用户体验
- 探索多个可能的方案（不要过早收敛）
- 讨论 trade-off：复杂度 vs 灵活性、速度 vs 质量
- 识别技术风险和不确定性

### 1.2 产出

讨论结束后，产出以下文档：

1. **vision.md** — 与用户确认后写入
2. **overview.md** — 系统架构初稿（后续可迭代）
3. **specs/A-\<name\>.md** — 每个已确认 feature 的规格

### 1.3 用户确认

在进入 Step 2 前，向用户展示：
- 识别了哪些 features？
- 每个 feature 的 scope 是否清晰？
- 有没有遗漏的需求或风险？

等待用户确认后再继续。

---

## Step 2: Writing-plans

**目标**：为每个 feature 编写可执行的实现计划。

### 2.1 任务分解

对每个 spec 文件：

1. 将 feature 分解为独立的、可测试的 tasks
2. 确定 task 之间的依赖关系
3. 为每个 task 定义 success criteria
4. 估计工作量（简单 / 中等 / 复杂）

### 2.2 产出 Plan 文件

每个 plan 写入 `plans/PlanN-<name>.md`，格式：

```markdown
# Plan N: <feature name>

## 目标
<一句话描述这个 plan 要实现什么>

## 前置条件
- <依赖的其他 plan 或外部条件>

## Tasks

### Task 1: <task name>
- 描述：...
- 范围：涉及哪些文件/模块
- 成功标准：怎样算完成
- 依赖：无 / 依赖 Task X

### Task 2: <task name>
...

## Out of Scope
- <明确不做的事情>

## 风险
- <潜在风险及应对>
```

### 2.3 用户确认

向用户展示所有 plans，确认：
- 任务分解是否合理？
- 优先级是否正确？
- 有没有遗漏的 task？

---

## Step 3: Worktree 创建 + Spawn Implementers

**目标**：为每个 plan 创建独立 worktree，spawn implementer teammates 执行。

### 3.1 创建 Worktrees

对每个 plan，使用 `EnterWorktree` 创建隔离的开发环境：

```
EnterWorktree(name="plan-<N>-<name>")
```

命名规范：`plan-<plan编号>-<简短名称>`，如 `plan-1-auth`、`plan-2-dashboard`。

### 3.2 Spawn Implementer Teammates

在一条消息中 spawn 所有 implementer，确保并行执行。

Spawn prompt 模板：

```
你是 implementer-plan<N>，负责实现 Plan N: <name>。

范围：plans/PlanN-<name>.md 中定义的所有 tasks
成功标准：每个 task 的 success criteria 都满足

工作流参考：Read 'skills/teammate/references/superpowers-implementer.md'
进度记录：更新 progress/PlanN-<name>.md

你的第一个动作：Skill('team-coord:teammate')
```

### 3.3 关键约束

- **一个 plan 一个 implementer**：不要让一个 implementer 跨多个 plan
- **只传 WHAT**：不描述具体实现方式
- **不传 HOW**：不重述 teammate skill 的执行步骤
- **批量 spawn**：所有 implementer 在一条消息中 spawn

### 3.4 Implementer 执行期间

Lead 在此阶段的职责：
- 监控 teammates 的状态报告
- 回答 teammates 的澄清问题
- 不要主动干预 implementer 的实现细节
- 如果 teammate 报告 blocker，判断是否需要调整 scope

---

## Step 4-7: Implementer 执行

这些步骤由 implementer teammates 自行处理，lead 不直接参与。

Implementer 的工作流参见 `skills/teammate/references/superpowers-implementer.md`，大致包括：

- Step 4: 阅读 plan，理解 task
- Step 5: 实现代码
- Step 6: 运行测试，修复问题
- Step 7: 创建 PR，报告完成

Lead 等待所有 implementer 报告完成后再进入 Step 8。

---

## Step 8: Spawn Reviewers

**目标**：为每个 PR spawn 一个独立的 reviewer，获取 fresh eyes 的代码审查。

### 8.1 确认 PR 就绪

在 spawn reviewer 前，确认：
- 所有 implementer 都已创建 PR
- PR 的 CI 检查已通过（如果有）
- 没有 merge conflict

### 8.2 Spawn Reviewer Teammates

每个 PR 一个 reviewer。在一条消息中 spawn 所有 reviewer。

Spawn prompt 模板：

```
你是 reviewer-pr-<N>，负责审查 PR #<N>。

范围：PR #<N> 的所有变更
成功标准：
- 代码质量达标
- 没有明显的 bug 或安全问题
- 符合 specs/A-<name>.md 中的规格

审查参考：Read 'skills/teammate/references/code-review.md'

你的第一个动作：Skill('team-coord:teammate')
```

### 8.3 Reviewer 特殊规则

- **一次性**：reviewer 完成审查后直接关闭，不需要用户批准
- **独立性**：每个 reviewer 只看一个 PR，不看其他 reviewer 的意见
- **输出格式**：reviewer 将 findings 按严重程度分类（critical / important / nitpick）

---

## Step 9: Fix Loop

**目标**：Lead 审阅所有 review findings，判定哪些值得修复，路由给 implementer。

### 9.1 收集 Findings

等待所有 reviewer 完成后，收集每个 PR 的 findings。

### 9.2 判定优先级

Lead 拥有全局视角，对每个 finding 做出判定：

| 判定       | 行动                                  |
|------------|---------------------------------------|
| Critical   | 必须修复，立即路由给 implementer      |
| Important  | 应该修复，路由给 implementer          |
| Nitpick    | 可以跳过，记录但不路由                |
| Won't fix  | 明确不修，说明理由                    |

判定标准：
- 是否影响核心功能？
- 是否引入安全风险？
- 是否影响可维护性？（但 nitpick 级别的 style 问题通常跳过）
- 修复成本 vs 收益

### 9.3 路由给 Implementers

对需要修复的 findings，通过 `SendMessage` 路由给对应的 implementer：

```
SendMessage(name="implementer-plan<N>", message="请修复以下 findings：
1. [finding 描述] — [为什么值得修]
2. [finding 描述] — [为什么值得修]
完成后更新 PR。")
```

### 9.4 循环

如果 implementer 修复后需要再次 review：
1. 再次 spawn 新的 reviewer（fresh eyes）
2. 重复 Step 8-9
3. 通常 1-2 轮即可收敛

设定最大轮次（建议 3 轮），超过后向用户报告剩余 findings，由用户决定。

---

## Step 10: Merge + Cleanup

**目标**：合并所有 PR，清理 worktrees，关闭 teammates。

### 10.1 确认合并就绪

在合并前确认：
- 所有 critical/important findings 已修复
- CI 通过（如果有）
- 用户已确认可以合并

### 10.2 合并 PRs

按依赖顺序合并：
- 无依赖的 PRs 可以并行合并
- 有依赖的 PRs 按依赖顺序合并
- 合并后确认 main branch 状态正常

### 10.3 清理 Worktrees

对每个 worktree，使用 `ExitWorktree(action="remove")` 清理：

```
ExitWorktree(action="remove", path="plan-<N>-<name>")
```

**注意**：只在合并成功且确认无误后才 remove worktree。

### 10.4 关闭 Teammates

**Implementer 关闭**：
- 需要用户批准
- 向用户报告每个 implementer 的完成状态
- 等待用户确认后发送 shutdown

**Reviewer 关闭**：
- 不需要用户批准（一次性角色）
- 直接关闭

### 10.5 TeamDelete

所有 teammates 关闭后，使用 `TeamDelete` 清理 team：

```
TeamDelete()
```

**前提条件**：
- 所有 teammates 已 idle 或已关闭
- 没有未读消息

### 10.6 最终报告

向用户报告：
- 完成了哪些 features？
- 合并了哪些 PRs？
- 有哪些 known limitations 或 technical debt？
- 后续建议（如果有的话）

---

## 常见场景处理

### Implementer 报告 Blocker

1. 了解 blocker 的性质（技术问题？scope 不清？依赖缺失？）
2. 如果是 scope 问题：澄清或调整 scope
3. 如果是技术问题：建议方案，但不强制 HOW
4. 如果是依赖问题：调整 task 顺序或创建新 task

### Reviewer 发现设计问题

1. 判断是实现问题还是 spec 问题
2. 如果是 spec 问题：回到 Step 1/2 更新 spec
3. 如果是实现问题：路由给 implementer

### 用户要求中途改需求

1. 评估影响范围
2. 更新相关 specs 和 plans
3. 通知受影响的 implementers
4. 如果影响重大，建议重新进入 Step 1

### Worktree 冲突

理论上每个 worktree 独立，但如果涉及共享文件（如 package.json）：
1. Lead 协调合并顺序
2. 先合并的 implementer 更新共享文件
3. 后合并的 implementer rebase 并解决冲突

---

## 时序图

```
User        Lead           Implementer-1    Implementer-2    Reviewer-1    Reviewer-2
 │           │                  │                │               │             │
 │──需求───▶│                  │                │               │             │
 │           │──Step 0-2──▶    │                │               │             │
 │◀─确认────│                  │                │               │             │
 │           │──Step 3: spawn─▶│                │               │             │
 │           │──────────────spawn──────────────▶│               │             │
 │           │                  │──Step 4-7──▶  │               │             │
 │           │                  │               │──Step 4-7──▶  │             │
 │           │◀──PR #1────────│                │               │             │
 │           │◀──────────────PR #2─────────────│               │             │
 │           │──Step 8: spawn────────────────────────────────▶│             │
 │           │──Step 8: spawn──────────────────────────────────────────────▶│
 │           │                  │                │               │──Review──▶│
 │           │◀────────────────────────────────────────────Findings────────│
 │           │◀──────────────────────────────────────────────────────Findings│
 │           │──Step 9: judge + route──▶       │               │             │
 │           │──────────────────────route─────▶│               │             │
 │           │                  │               │──Fix──▶       │             │
 │           │◀─Step 10: report────────────────────────────────────────────│
 │◀─报告────│                  │                │               │             │
 │──批准───▶│                  │                │               │             │
 │           │──merge + cleanup─▶               │               │             │
```

---

## Checklist

Lead 在每个阶段的检查点：

### Step 0-2 结束时
- [ ] vision.md 已与用户确认
- [ ] overview.md 覆盖系统架构
- [ ] 每个 feature 有对应的 spec
- [ ] 每个 spec 有对应的 plan
- [ ] 用户已确认 plans

### Step 3 结束时
- [ ] 每个 plan 有独立的 worktree
- [ ] 每个 implementer 已 spawn 并命名
- [ ] spawn prompt 只包含 WHAT

### Step 8 结束时
- [ ] 每个 PR 有独立的 reviewer
- [ ] reviewer 已 spawn 并命名

### Step 9 结束时
- [ ] 所有 findings 已判定
- [ ] critical/important findings 已路由
- [ ] 修复已验证（如有 fix loop）

### Step 10 结束时
- [ ] 所有 PRs 已合并
- [ ] 所有 worktrees 已清理
- [ ] 所有 teammates 已关闭
- [ ] TeamDelete 已执行
- [ ] 最终报告已发送给用户
