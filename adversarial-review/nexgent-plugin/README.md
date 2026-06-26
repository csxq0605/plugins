# adversarial-review (Nexgent Plugin)

多视角对抗式代码审查 — Python 工具实现，提供 6 个审查管理工具。

## 安装

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/adversarial-review/nexgent-plugin
```

## 工具列表

| 工具 | 用途 |
|------|------|
| `review_start` | 启动审查会话 |
| `review_add_finding` | 添加发现 |
| `review_get_findings` | 获取发现（支持过滤） |
| `review_health_score` | 计算健康评分 |
| `review_export` | 导出报告（json/markdown/sarif） |
| `review_list_sessions` | 列出所有会话 |

## 测试

```bash
cd adversarial-review/nexgent-plugin
python -c "from review_tools import get_tools, call_tool; print(len(get_tools()), 'tools')"
```

## 依赖

无外部依赖。纯 Python 标准库实现。

## License

MIT
