# adr-generator — 架构决策记录生成器

创建、管理和索引 Architecture Decision Records (ADR)。支持 MADR 和 Y-Statement 两种模板，状态流转，自动编号。

## 安装

### Claude Code

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/adr-generator/claude-code-plugin
```

### Nexgent

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/adr-generator/nexgent-plugin
```

## 使用

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

## 两种模板

### MADR (Markdown Any Decision Record)
最全面的模板，适合重要决策：
- 上下文 → 决策 → 替代方案（含优缺点） → 后果（正面/负面/风险）

### Y-Statement
最简洁的模板，适合快速记录：
> 在 {上下文} 的背景下，面对 {问题}，我们决定 {决策}，以实现 {期望后果}，接受 {负面后果}。

## 状态流转

```
Proposed → Accepted → Deprecated
         → Superseded by ADR-XXXX
```

## 存储结构

```
docs/adr/
├── index.md                    # ADR 索引
├── 0001-use-postgresql.md
├── 0002-rest-api-design.md
└── templates/
```

## team-coord 集成

Worker 可创建 ADR 草稿，Lead 审批状态变更。参见 `references/team-coord-guide.md`。

## License

MIT
