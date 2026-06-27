# Outreach Plugin for Claude Code

## 概述

学术套磁全流程自动化插件，支持材料解析、教授调研、可视化报告、个性化邮件生成、邮件收发。

## 安装

```bash
claude install-plugin github:csxq0605/plugins
```

## 使用方式

```
/outreach "配置邮箱"
/outreach "这是我的CV"
/outreach "调研 MIT CS"
/outreach "生成报告 MIT CS"
/outreach "生成邮件 MIT CS"
/outreach "发送邮件给 MIT CS Professor_Name"
```

## 工作流程

1. **配置邮箱** - 首次使用自动检测并引导配置
2. **上传材料** - 解析 CV、研究计划、成绩单
3. **调研教授** - 从学院官网、Google Scholar 等获取信息
4. **生成报告** - 生成交互式 HTML 可视化报告
5. **生成邮件** - 基于调研报告生成个性化套磁邮件
6. **发送邮件** - 试运行 → 确认 → 正式发送

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

- 邮箱配置: `~/.outreach/email_config.json`（用户级，跨项目共享）
- 调研数据: `.outreach/schools/`（项目级）
- 个人材料: `.outreach/profiles/`（项目级）
- 发送日志: `.outreach/logs/`（项目级）

## 与 Email 插件的关系

Outreach 插件内置了邮件功能，可以独立使用。如果只需要邮件功能，可以使用独立的 Email 插件。
