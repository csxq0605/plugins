# plugins

Claude Code & Nexgent 插件集合。

## 插件列表

| 插件 | Claude Code | Nexgent | 说明 |
|------|-------------|---------|------|
| [team-coord](./multi-agent/) | [claude-code-plugin](./multi-agent/claude-code-plugin/) | [nexgent-plugin](./multi-agent/nexgent-plugin/) | 多 agent 团队协调 |
| [adversarial-review](./adversarial-review/) | [claude-code-plugin](./adversarial-review/claude-code-plugin/) | [nexgent-plugin](./adversarial-review/nexgent-plugin/) | 多视角代码审查 |
| [lit-review](./lit-review/) | [claude-code-plugin](./lit-review/claude-code-plugin/) | [nexgent-plugin](./lit-review/nexgent-plugin/) | 科研文献调研 |

## 目录结构

每个插件遵循统一结构：

```
plugins/
├── multi-agent/
│   ├── claude-code-plugin/    ← Claude Code 版本（纯 SKILL.md）
│   └── nexgent-plugin/        ← Nexgent 版本（Python 工具 + SKILL.md）
├── adversarial-review/
│   ├── claude-code-plugin/    ← Claude Code 版本
│   └── nexgent-plugin/        ← Nexgent 版本
└── lit-review/
    ├── claude-code-plugin/    ← Claude Code 版本
    └── nexgent-plugin/        ← Nexgent 版本
```

## 安装

### Claude Code

```bash
# 添加 marketplace（一次性）
/plugin marketplace add csxq0605/plugins

# 安装插件
/plugin install team-coord@plugins
/plugin install adversarial-review@plugins
/plugin install lit-review@plugins
```

### Nexgent

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/multi-agent/nexgent-plugin
/plugin install https://github.com/csxq0605/plugins/tree/master/adversarial-review/nexgent-plugin
/plugin install https://github.com/csxq0605/plugins/tree/master/lit-review/nexgent-plugin
```

## 插件详情

### team-coord — 多 Agent 团队协调

- **Lead**：纯协调者，spawn worker、分配任务、综合结果
- **Teammate**：执行者，inbox sync 协议避免竞态条件
- **适配 superpowers**：完整的开发工作流

### adversarial-review — 多视角代码审查

6 个审查视角：Security / Performance / Architecture / Code Quality / Test Quality / API Design

- 健康评分 0-100
- 统一发现格式（JSON）
- 支持 SARIF 导出（GitHub Code Scanning）
- Nexgent 版本：6 个工具

### lit-review — 科研文献调研

3 个子技能：search / analyze / synthesize

- arXiv API + Semantic Scholar API 真实接入
- 引用网络分析（citations / references / recommendations）
- 本地论文工作区管理
- Nexgent 版本：14 个工具

## License

MIT
