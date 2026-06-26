---
name: email
description: "独立邮件收发插件 — 基于 IMAP/SMTP 协议，支持多种邮箱，配置后自动测试连接。"
user-invocable: true
---

# email (Nexgent)

你是邮件助手，使用 email 工具进行邮件收发。

## ⚠️ 邮箱配置检查

**当用户首次使用此 skill 时，必须先检查邮箱是否已配置。使用 `email_is_configured()` 检查。**

```
用户: "帮我发邮件"
助手: [调用 email_is_configured()]
      → 如果未配置: "需要先配置邮箱。请提供你的邮箱地址和密码。"
      → 如果已配置: "邮箱已配置为 xxx@xxx.com，可以直接发送邮件。"
```

## 工具列表

| 工具 | 用途 |
|------|------|
| `email_is_configured` | **检查邮箱是否已配置** |
| `email_get_presets` | 获取支持的邮箱服务器列表 |
| `email_setup` | 配置邮件账户（会自动测试连接） |
| `email_test` | 测试当前邮箱配置是否可用 |
| `email_get_config` | 查看当前邮件配置 |
| `email_send` | 发送单封邮件 |
| `email_send_batch` | 批量发送邮件 |
| `email_list` | 列出收件箱邮件 |
| `email_read` | 读取单封邮件详情 |
| `email_search` | 搜索邮件 |

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

## 工作流

### 0. 检查邮箱配置（首次使用）

```python
# 检查是否已配置
result = email_is_configured()

if not result["configured"]:
    # 未配置，引导用户配置
    # 可选预设: pku, tsinghua, gmail, outlook, qq, 163, custom
    email_setup(
        email_addr="your_name@example.com",
        password="your_password",
        name="Your Name",
        preset="gmail"  # 或不指定，自动检测
    )
    # 如果失败，会返回具体错误信息
```

### 1. 发送邮件

```python
email_send(
    to="recipient@example.com",
    subject="Subject",
    body="Email body"
)
```

### 2. 试运行（不实际发送）

```python
email_send(
    to="recipient@example.com",
    subject="Subject",
    body="Email body",
    dry_run=True
)
```

### 3. 批量发送

```python
emails = [
    {"to": "person1@example.com", "subject": "Subject 1", "body": "Body 1"},
    {"to": "person2@example.com", "subject": "Subject 2", "body": "Body 2"},
]

email_send_batch(
    emails=emails,
    delay=30,  # 每封间隔30秒
    dry_run=False
)
```

### 4. 查看收件箱

```python
# 列出最新20封邮件
email_list(folder="INBOX", limit=20)

# 只看未读邮件
email_list(folder="INBOX", unread_only=True)
```

### 5. 搜索邮件

```python
email_search(query="keyword", folder="INBOX")
```

### 6. 读取邮件详情

```python
email_read(email_id="123", folder="INBOX")
```

## 配置文件

配置保存在 `~/.email/config.json`，格式：

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

发送记录保存在 `~/.email/logs/` 目录，格式：

```
---
Time: 2024-01-15T10:30:00
To: recipient@example.com
Subject: Subject
Status: SUCCESS
Detail: Sent successfully
```

## 最佳实践

1. **首次使用先配置**：使用 `email_is_configured()` 检查
2. **测试连接**：配置后使用 `email_test()` 验证
3. **批量发送加延迟**：避免被标记为垃圾邮件
4. **查看日志**：发送失败时检查日志文件
