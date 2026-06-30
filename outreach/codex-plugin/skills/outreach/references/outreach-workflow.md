# Outreach Workflow -- Reference Doc

> This doc defines the outreach workflow for the Codex plugin.

---

## User Prompts

### Email Configuration

```bash
用 outreach 配置邮箱
python <plugin_root>/scripts/email_setup.py --check
python <plugin_root>/scripts/email_setup.py --email user@example.com --password pass --preset pku
python <plugin_root>/scripts/email_setup.py --test
```

### Material Upload

```bash
用 outreach 解析我的 CV
```

Files are stored in `.outreach/inbox/` (project-level)

### Professor Research

```bash
用 outreach 调研 MIT CS
用 outreach 调研 MIT CS --direction AI,NLP
```

Research reports are saved to `.outreach/schools/{School}_{Dept}/{Prof_Name}/research.md` (project-level)

### Report Generation

```bash
用 outreach 生成报告 MIT CS
```

HTML reports are saved to `.outreach/schools/{School}_{Dept}/report.html` (project-level)

### Email Generation

```bash
用 outreach 生成邮件 MIT CS
用 outreach 生成邮件 MIT CS --prof Smith
```

Email drafts are saved to `.outreach/schools/{School}_{Dept}/{Prof_Name}/email_draft.md` (project-level)

### Email Sending

```bash
用 outreach 发送邮件给 MIT CS Prof_Name
用 outreach 批量发送 MIT CS
用 outreach 查看收件箱
```

---

## Directory Structure

**Config** (user-level, `~/.outreach/`):
```
~/.outreach/
└── email_config.json   # Email configuration
```

**Task files** (project-level, `<project>/.outreach/`):
```
.outreach/
├── inbox/              # Uploaded files
├── profiles/           # Parsed materials
├── schools/
│   └── {School}_{Dept}/
│       ├── professors.csv
│       ├── report.html
│       ├── assets/
│       │   └── style.css
│       └── {Prof_Name}/
│           ├── research.md
│           └── email_draft.md
└── logs/               # Send logs
```

---

## Workflow

1. Check email config -> `用 outreach 配置邮箱`
2. Upload materials -> `用 outreach 解析我的 CV`
3. Research professors -> `用 outreach 调研 MIT CS`
4. Generate report -> `用 outreach 生成报告 MIT CS`
5. Generate emails -> `用 outreach 生成邮件 MIT CS`
6. Send emails -> `用 outreach 发送邮件给 MIT CS Prof_Name`

---

## Error Handling

| Issue | Command |
|-------|---------|
| Email not configured | `用 outreach 配置邮箱` |
| PDF parsing failed | Ask user for text version |
| Research failed | Retry or skip professor |
| Send failed | Check logs in `.outreach/logs/` |
