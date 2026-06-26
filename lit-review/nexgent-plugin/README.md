# lit-review (Nexgent Plugin)

系统性文献调研 — 14 个 Python 工具，覆盖搜索、论文管理、分析、综合。

## 安装

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/lit-review/nexgent-plugin
```

## 工具列表

| 工具 | 用途 |
|------|------|
| `lit_set_key` | 设置 Semantic Scholar API key |
| `lit_get_config` | 查看配置 |
| `lit_search_web` | 在线搜索论文（arXiv + Semantic Scholar） |
| `lit_citations` | 获取论文的引用 |
| `lit_references` | 获取论文的参考文献 |
| `lit_recommend` | 获取推荐论文 |
| `lit_create_workspace` | 创建研究工作区 |
| `lit_add_paper` | 添加论文到工作区 |
| `lit_get_paper` | 获取论文详情 |
| `lit_list_papers` | 列出工作区论文 |
| `lit_search_local` | 本地论文搜索 |
| `lit_add_analysis` | 添加论文分析结果 |
| `lit_synthesize` | 获取综合数据 |
| `lit_list_workspaces` | 列出所有工作区 |

## 测试

```bash
cd lit-review/nexgent-plugin
python -c "from lit_tools import get_tools, call_tool; print(len(get_tools()), 'tools')"
```

## 依赖

无外部依赖。搜索引擎使用 Python 标准库。

## License

MIT
