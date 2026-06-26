# Email Plugin for Nexgent

独立邮件收发插件，基于 IMAP/SMTP 协议。

## 功能

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
/plugin install https://github.com/csxq0605/plugins/tree/master/email/nexgent-plugin
```

## 使用

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
```

## 测试

```bash
python -m pytest tests/ -v
```
