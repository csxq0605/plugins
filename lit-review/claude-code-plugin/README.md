# lit-review (Claude Code Plugin)

系统性文献调研 — 3 个技能（search/analyze/synthesize）+ CLI 搜索工具。

## 安装

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/lit-review/claude-code-plugin
```

## 技能列表

| 技能 | 用途 |
|------|------|
| `/lit-review:search` | 搜索 arXiv + Semantic Scholar |
| `/lit-review:analyze` | 深度分析单篇论文 |
| `/lit-review:synthesize` | 生成文献综述 |

## Semantic Scholar API 配置

```bash
python bin/lit-search.py set-key YOUR_API_KEY
```

配置存储在 `~/.lit-review/config.json`，两个版本共享。

## 目录结构

```
claude-code-plugin/
├── .claude-plugin/plugin.json       # 插件清单（3 个技能）
├── bin/lit-search.py                # CLI 搜索工具（arXiv + Semantic Scholar）
├── skills/
│   ├── search/SKILL.md              # 搜索技能
│   ├── analyze/SKILL.md             # 分析技能
│   └── synthesize/SKILL.md          # 综述技能
└── README.md
```

## 依赖

无。`lit-search.py` 使用 Python 标准库（urllib, json, xml）。

## License

MIT
