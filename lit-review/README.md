# lit-review — 科研文献调研流水线

多源学术搜索（arXiv、Semantic Scholar、Google Scholar）、引用网络分析、子问题分解、结构化综述生成。

## 安装

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/lit-review
```

## 使用

```
/lit-review:search "transformer attention mechanisms"     # 搜索论文
/lit-review:search "LLM agents" --sources arxiv,semantic-scholar --deep
/lit-review:analyze <paper_url>                           # 分析单篇论文
/lit-review:synthesize "研究问题" --papers "url1,url2,..." # 生成综述
```

## 3 个子技能

| 子技能 | 功能 |
|--------|------|
| `search` | 多源搜索、子问题分解、结果去重 |
| `analyze` | 论文摘要、方法论分析、关键发现提取 |
| `synthesize` | 分类法构建、趋势分析、研究空白识别、综述生成 |

## 搜索来源

- **arXiv**: 预印本，覆盖 CS/Physics/Math/Stats
- **Semantic Scholar**: 引用网络、推荐系统、批量查询
- **Google Scholar**: 最广泛的学术搜索

## team-coord 集成

当与 team-coord 共存时，lead 可按子话题分配 worker 并行搜索。参见 `synthesize/references/team-coord-guide.md`。

## License

MIT
