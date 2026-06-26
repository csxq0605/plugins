---
name: adr
description: "Architecture Decision Record generator — creates, manages, and indexes ADRs with multiple templates (MADR, Y-Statement), status tracking, and cross-referencing. Trigger on: 'create ADR', 'architecture decision', 'record decision', 'ADR list', 'design decision', 'technical decision'."
user-invocable: true
---

# adr — 架构决策记录

你是架构师助手。帮助团队记录、管理和查询架构决策。

## 铁律

1. **决策必须有上下文。** 不记录没有背景的结论。
2. **考虑替代方案。** 每个决策至少考虑 2 个替代方案。
3. **记录后果。** 包括正面和负面后果。
4. **状态必须准确。** 及时更新决策状态。

## 调用方式

```
/adr new                                 # 交互式创建 ADR
/adr new --template madr                 # 使用 MADR 模板
/adr new --template y-statement          # 使用 Y-Statement 模板
/adr new --title "Use PostgreSQL"        # 直接指定标题
/adr list                                # 列出所有 ADR
/adr list --status accepted              # 按状态过滤
/adr show 0001                           # 查看 ADR 详情
/adr supersede 0001 --by 0005            # 标记被替代
/adr index                               # 生成 ADR 索引
/adr search "database"                   # 搜索 ADR
```

## ADR 目录结构

```
docs/adr/
├── index.md                    # ADR 索引
├── 0001-use-postgresql.md      # 第一个决策
├── 0002-rest-api-design.md     # 第二个决策
└── templates/
    ├── madr.md                 # MADR 模板
    └── y-statement.md          # Y-Statement 模板
```

## 模板 1: MADR (Markdown Any Decision Record)

```markdown
# {NNNN}. {标题}

日期: {YYYY-MM-DD}

## 状态

{Proposed | Accepted | Deprecated | Superseded by [ADR-XXXX](XXXX-标题.md)}

## 上下文

{描述促使决策的问题或机会。包括技术、业务、组织等方面的背景。}

## 决策

{清晰地陈述做出的决策。使用主动语态，如"我们决定……"}

## 考虑的替代方案

### 方案 A: {名称}

{描述}

- 优点: {列表}
- 缺点: {列表}

### 方案 B: {名称}

{描述}

- 优点: {列表}
- 缺点: {列表}

## 后果

### 正面

- {列表}

### 负面

- {列表}

### 风险

- {列表}

## 相关决策

- [ADR-XXXX](XXXX-标题.md) — {关系说明}

## 参考

- {链接或文档}
```

## 模板 2: Y-Statement

```markdown
# {NNNN}. {标题}

日期: {YYYY-MM-DD}

## 状态

{Proposed | Accepted | Deprecated | Superseded by [ADR-XXXX](XXXX-标题.md)}

## Y-Statement

在 {上下文} 的背景下，
面对 {问题}，
我们决定 {决策}，
并且 {补充说明}，
以实现 {期望后果}，
接受 {负面后果}。

## 详细说明

{扩展说明，包含技术细节}

## 考虑的替代方案

- {替代方案 1}: {一句话说明为什么不选}
- {替代方案 2}: {一句话说明为什么不选}

## 参考

- {链接}
```

## 创建流程

### 1. 收集信息

在创建 ADR 前，确认以下信息：

- **决策标题**: 简短描述决策
- **上下文**: 为什么需要这个决策？
- **决策内容**: 具体决定什么？
- **替代方案**: 考虑过哪些其他方案？
- **后果**: 这个决策会带来什么影响？

### 2. 选择模板

- **MADR**: 最全面，适合重要决策
- **Y-Statement**: 最简洁，适合快速记录

### 3. 生成 ADR

```bash
# 确定下一个编号
ls docs/adr/*.md 2>/dev/null | sort -V | tail -1
# 输出: docs/adr/0003-previous-decision.md
# 下一个编号: 0004

# 创建 ADR
cat > docs/adr/0004-use-postgresql.md << 'EOF'
# 0004. Use PostgreSQL as Primary Database

Date: 2024-01-15

## Status

Accepted

## Context

Our application needs a reliable, ACID-compliant relational database...
EOF
```

### 4. 更新索引

```bash
# 生成索引
echo "# Architecture Decision Records\n" > docs/adr/index.md
echo "| # | Title | Date | Status |" >> docs/adr/index.md
echo "|---|-------|------|--------|" >> docs/adr/index.md
for f in docs/adr/[0-9]*.md; do
  num=$(basename "$f" | cut -d'-' -f1)
  title=$(head -1 "$f" | sed 's/^# [0-9]*\. //')
  date=$(grep "^Date:" "$f" | cut -d' ' -f2)
  status=$(grep -A1 "^## Status" "$f" | tail -1)
  echo "| $num | [$title]($f) | $date | $status |" >> docs/adr/index.md
done
```

## 状态管理

### 状态流转

```
Proposed → Accepted → Deprecated
                   → Superseded by ADR-XXXX
```

### 标记为 Superseded

```bash
# 在旧 ADR 中添加
## Status

Superseded by [ADR-0005](0005-new-approach.md)

# 在新 ADR 中添加引用
## Related Decisions

- [ADR-0004](0004-old-approach.md) — Superseded by this decision
```

## team-coord 集成

当检测到 team-coord 环境时：

```
# Worker 可以创建 ADR
/adr new --title "Use Event Sourcing"

# Lead 汇总所有 ADR
/adr index

# Lead 审查决策状态
/adr list --status proposed
```

## 参考文件

- `references/adr-principles.md` — ADR 最佳实践
- `references/team-coord-guide.md` — team-coord 集成指南
