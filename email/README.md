# 📧 Email Plugin — 独立邮件收发插件

基于 IMAP/SMTP 协议的完整邮件收发功能，支持多种邮箱服务器。

## 安装

### Claude Code

```bash
claude install-plugin github:csxq0605/plugins
```

### Nexgent

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/email/nexgent-plugin
```

## 功能特性

- 📧 **邮箱配置**：自动检测并引导配置，支持多种邮箱，配置后自动测试连接
- 📬 **邮件发送**：支持单封发送、批量发送、试运行模式
- 📥 **邮件接收**：查看收件箱、搜索邮件、读取邮件详情
- 📊 **发送日志**：记录所有发送记录，便于追踪

## 支持的邮箱

| 邮箱 | 预设 | 说明 |
|------|------|------|
| 北京大学 | `pku` | mail.stu.pku.edu.cn |
| 清华大学 | `tsinghua` | mail.tsinghua.edu.cn |
| Gmail | `gmail` | 需要应用专用密码 |
| Outlook | `outlook` | outlook.office365.com |
| QQ邮箱 | `qq` | 需要应用专用密码 |
| 163邮箱 | `163` | 需要开启IMAP/SMTP |
| 自定义 | `custom` | 自己指定服务器 |

## 目录结构

```
email/
├── claude-code-plugin/        # Claude Code 插件
│   ├── .claude-plugin/plugin.json
│   ├── CLAUDE.md
│   ├── README.md
│   ├── scripts/
│   │   ├── email_setup.py     # 邮箱配置脚本
│   │   ├── email_send.py      # 邮件发送脚本
│   │   ├── email_batch.py     # 批量发送脚本
│   │   └── email_list.py      # 邮件查看脚本
│   └── skills/email/
│       └── SKILL.md
└── nexgent-plugin/            # Nexgent 插件
    ├── __init__.py
    ├── plugin.json
    ├── README.md
    ├── email_tools.py         # 邮件工具定义
    ├── references/
    ├── skills/email/
    │   └── SKILL.md
    └── tests/
        ├── __init__.py
        ├── test_email.py
        └── pytest.ini
```

## 使用方式

### Claude Code

```bash
# 配置邮箱
/email "配置邮箱"

# 查看收件箱
/email "查看收件箱"

# 发送邮件
/email "发送邮件给 xxx@example.com"

# 搜索邮件
/email "搜索邮件 PhD"
```

### Nexgent

```python
# 检查是否已配置
email_is_configured()

# 配置邮箱
email_setup(
    email_addr="your@stu.pku.edu.cn",
    password="your_password",
    name="Your Name",
    preset="pku"
)

# 发送邮件
email_send(
    to="recipient@example.com",
    subject="Subject",
    body="Body"
)

# 查看收件箱
email_list(folder="INBOX", limit=20)
```

## 测试

```bash
# 单元测试
cd email/nexgent-plugin && python -m pytest tests/ -v
```

## 配置文件

配置保存在 `~/.email/config.json`：

```json
{
  "imap_server": "mail.stu.pku.edu.cn",
  "imap_port": 993,
  "smtp_server": "mail.stu.pku.edu.cn",
  "smtp_port": 465,
  "email": "user@stu.pku.edu.cn",
  "password": "password",
  "name": "User Name",
  "preset": "pku"
}
```

## 日志文件

发送记录保存在 `~/.email/logs/` 目录。

## 注意事项

1. **Gmail/QQ邮箱**：需要使用应用专用密码，不是普通密码
2. **批量发送**：建议每封间隔 30 秒，避免被标记为垃圾邮件
3. **配置安全**：密码保存在本地配置文件，请勿泄露

## License

MIT
