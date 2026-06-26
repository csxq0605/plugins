# outreach (Nexgent Plugin)

学术套磁全流程自动化 — 7 个 Python 工具，覆盖材料解析、教授调研、报告生成、邮件撰写。

## 安装

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/outreach/nexgent-plugin
```

## 工具列表

| 工具 | 用途 |
|------|------|
| `outreach_parse_materials` | 解析个人材料（CV、研究计划、成绩单） |
| `outreach_list_profiles` | 列出已解析材料 |
| `outreach_research_professor` | 调研教授（研究方向、发表统计、学生去向） |
| `outreach_get_research` | 获取调研报告 |
| `outreach_generate_report` | 生成 HTML 可视化报告 |
| `outreach_generate_email` | 生成个性化套磁邮件 |
| `outreach_list_professors` | 列出已调研教授 |

## 测试

```bash
cd outreach/nexgent-plugin
python -c "from outreach_tools import get_tools, call_tool; print(len(get_tools()), 'tools')"
```

## License

MIT
