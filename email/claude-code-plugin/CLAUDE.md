# Email Plugin for Claude Code

## 概述

独立邮件收发插件，基于 IMAP/SMTP 协议，支持多种邮箱服务器。

## 安装

```bash
claude install-plugin github:csxq0605/plugins
```

## 使用方式

```
/email "配置邮箱"
/email "查看收件箱"
/email "发送邮件给 xxx@example.com"
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

## 配置文件

配置保存在 `~/.email/config.json`。

## 日志文件

发送记录保存在 `~/.email/logs/` 目录。
