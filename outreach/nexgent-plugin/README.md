# Outreach Plugin for Nexgent

学术套磁全流程自动化插件。

## 功能

### 调研工具

- `outreach_parse_materials` — 解析个人材料（CV、研究计划等）
- `outreach_list_profiles` — 列出已解析的材料
- `outreach_research_professor` — 调研单个教授
- `outreach_get_research` — 获取教授调研报告
- `outreach_generate_report` — 生成HTML可视化报告
- `outreach_generate_email` — 生成个性化套磁邮件
- `outreach_list_professors` — 列出已调研的教授

### 邮件工具

- `email_is_configured` — 检查邮箱是否已配置
- `email_get_presets` — 获取支持的邮箱服务器列表
- `email_setup` — 配置邮件账户（会自动测试连接）
- `email_test` — 测试当前邮箱配置是否可用
- `email_get_config` — 查看当前邮件配置
- `email_send` — 发送单封邮件
- `email_send_batch` — 批量发送邮件
- `email_list` — 列出收件箱邮件
- `email_read` — 读取单封邮件详情
- `email_search` — 搜索邮件

## 安装

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/outreach/nexgent-plugin
```

## 使用

```python
# 配置邮箱
email_setup(email_addr="...", password="...", preset="pku")

# 解析材料
outreach_parse_materials(file_path="cv.pdf")

# 调研教授
outreach_research_professor(
    name="Kaiming He",
    school="MIT",
    dept="CS",
    homepage="https://kaiminghe.com/",
    research_keywords="computer vision"
)

# 生成报告
outreach_generate_report(school="MIT", dept="CS")

# 生成邮件
outreach_generate_email(school="MIT", dept="CS", professor="Kaiming He")

# 发送邮件
email_send(to="...", subject="...", body="...")
```

## 测试

```bash
python -m pytest tests/ -v
```

## License

MIT
