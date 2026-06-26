---
name: email
description: "独立邮件收发插件 — 基于 IMAP/SMTP 协议，支持多种邮箱，配置后自动测试连接。Trigger on: '发邮件', '收邮件', '配置邮箱', '查看邮件', 'send email', 'email'."
user-invocable: true
allowed-tools: Bash(python*), Read, Write, Edit, Glob, Grep, AskUserQuestion
---

# email — 独立邮件收发插件

你是邮件助手，帮助用户配置邮箱、发送邮件、查看邮件。

## ⚠️ 邮箱配置检查

**当用户首次使用此 skill 时，必须先检查邮箱是否已配置。如果未配置，主动引导用户完成配置。**

```
用户: "帮我发邮件"
助手: [检查邮箱配置]
      → 如果未配置: "需要先配置邮箱。请提供你的邮箱地址和密码。"
      → 如果已配置: "邮箱已配置为 xxx@xxx.com，可以直接发送邮件。"
```

## 调用方式

```
/email "配置邮箱"                              # 配置邮箱
/email "查看邮箱配置"                          # 查看当前配置
/email "测试邮箱"                              # 测试连接
/email "查看收件箱"                            # 查看邮件列表
/email "搜索邮件 PhD"                          # 搜索邮件
/email "发送邮件给 xxx@example.com"            # 发送邮件
/email "批量发送"                              # 批量发送
```

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

## 工具脚本

### 邮箱配置

```bash
# 检查是否已配置
python scripts/email_setup.py --check

# 配置邮箱（自动测试连接）
python scripts/email_setup.py --email your@gmail.com --password your_password --name "Your Name"

# 使用预设配置
python scripts/email_setup.py --email your@stu.pku.edu.cn --password your_password --preset pku

# 测试邮箱连接
python scripts/email_setup.py --test

# 查看当前配置
python scripts/email_setup.py --info
```

### 发送邮件

```bash
# 发送单封邮件
python scripts/email_send.py --to recipient@example.com --subject "Subject" --body "Body"

# 试运行
python scripts/email_send.py --to recipient@example.com --subject "Subject" --body "Body" --dry-run

# 批量发送
python scripts/email_batch.py --csv recipients.csv --delay 30
python scripts/email_batch.py --csv recipients.csv --delay 30 --dry-run
```

### 查看邮件

```bash
# 查看收件箱
python scripts/email_list.py --limit 20

# 只看未读
python scripts/email_list.py --unread

# 搜索邮件
python scripts/email_list.py --search "keyword"

# 读取邮件
python scripts/email_list.py --read 123
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

发送记录保存在 `~/.email/logs/` 目录。

## 用户交互指令

| 指令 | 说明 |
|------|------|
| "配置邮箱" | 配置邮箱（首次使用） |
| "查看邮箱配置" | 查看当前配置 |
| "测试邮箱" | 测试邮箱连接 |
| "查看收件箱" | 查看邮件列表 |
| "搜索邮件 [关键词]" | 搜索邮件 |
| "发送邮件给 [邮箱]" | 发送邮件 |
| "批量发送" | 批量发送邮件 |

## 最佳实践

1. **首次使用先配置**：检查邮箱是否已配置
2. **测试连接**：配置后测试是否成功
3. **批量发送加延迟**：避免被标记为垃圾邮件
4. **查看日志**：发送失败时检查日志
