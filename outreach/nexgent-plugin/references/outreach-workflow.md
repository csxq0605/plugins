# Outreach Workflow -- Reference Doc

> This doc defines the complete outreach workflow for academic professor research and cold emailing.
> Language convention: narrative in Chinese, all technical terms / commands in English.

---

## Overview

The outreach workflow consists of 7 stages:

1. Email Configuration
2. Material Upload
3. Material Parsing
4. Professor Research
5. Report Generation
6. Email Draft Generation
7. Email Sending

---

## Stage 0: Email Configuration

### Check First

Always check if email is configured:

```python
result = email_is_configured()
if not result["configured"]:
    email_setup(email_addr="...", password="...", preset="pku")
```

### Auto-Detection

The system automatically detects email provider based on domain:
- `@stu.pku.edu.cn` -> `pku` preset
- `@mail.tsinghua.edu.cn` -> `tsinghua` preset
- `@gmail.com` -> `gmail` preset
- etc.

---

## Stage 1: Material Upload

### Supported Formats

- PDF (requires pdfplumber)
- Word (requires python-docx)
- Markdown
- Plain text

### File Location

Files are stored in `~/.outreach/inbox/`

---

## Stage 2: Material Parsing

### Extracted Information

The system extracts:
- Name
- Email address
- School/University
- GPA
- Research interests
- Skills
- Publications (if any)

### Storage

Parsed materials are saved to `~/.outreach/profiles/`

---

## Stage 3: Professor Research

### Data Sources

1. Professor homepage (most authoritative)
2. Google Scholar (publication data)
3. Department website (recruitment info)
4. Semantic Scholar (paper details)
5. RateMyProfessor (student reviews)
6. OpenReview (review style)

### Research Content

For each professor, research:
- Basic info (name, title, lab, research areas)
- Publication stats (h-index, paper count, top venues)
- Student outcomes (where graduates go)
- Research group (size, atmosphere, publication cycle)
- Advisor style (hands-on, hands-off, collaborative)
- Match analysis (direction match, skill match)
- Application advice (recruiting?, best contact time)

### Storage

Research reports are saved to:
```
~/.outreach/schools/{School}_{Dept}/{Prof_Name}/research.md
```

---

## Stage 4: Report Generation

### HTML Report Features

- Dark theme, responsive design
- Search and filter functionality
- Sort by match score, h-index, or name
- Expandable professor cards
- Tab-based content organization
- Match score color coding (green/yellow/red)

### Report Structure

```
~/.outreach/schools/{School}_{Dept}/
├── professors.csv      # Professor list
├── report.html         # Main report
├── index.html          # Same as report.html
├── assets/
│   └── style.css       # Stylesheet
└── {Prof_Name}/
    ├── research.md     # Research report
    └── email_draft.md  # Email draft
```

---

## Stage 5: Email Draft Generation

### Email Template

```
SUBJECT: Prospective PhD Student - [Name] - [Research Direction]

Dear Professor [Name],

[Paragraph 1: Mention specific research, explain interest]

[Paragraph 2: Introduce relevant experience and skills]

[Paragraph 3: Explain how research plan aligns]

[Paragraph 4: Ask about openings, express anticipation]

Best regards,
[Name]
[School/Major]
[Email]
```

### Personalization

Emails are personalized based on:
- Professor's specific research (cite papers/projects)
- User's relevant experience
- Match analysis recommendations
- Application advice

---

## Stage 6: Email Sending

### Pre-Send Checklist

1. ✅ Email configured and tested
2. ✅ Email draft generated
3. ✅ User reviewed and approved
4. ✅ Dry run completed (optional but recommended)

### Sending Protocol

```python
# 1. Dry run first
email_send(to="...", subject="...", body="...", dry_run=True)

# 2. User confirms

# 3. Send
email_send(to="...", subject="...", body="...")

# 4. Check result
```

### Batch Sending

For multiple professors:

```python
emails = [
    {"to": "prof1@uni.edu", "subject": "...", "body": "..."},
    {"to": "prof2@uni.edu", "subject": "...", "body": "..."},
]

email_send_batch(emails=emails, delay=30)
```

---

## Error Handling

### Common Issues

| Issue | Solution |
|-------|----------|
| PDF parsing failed | Ask user for text version |
| Web scraping failed | Try alternative source |
| Professor info incomplete | Mark missing fields, continue |
| Email send failed | Check logs, verify config |

### Retry Logic

- Web requests: 3 retries with 5s delay
- Email send: No automatic retry, log failure

---

## Privacy & Security

1. **User Data**: CV, transcripts used only for email generation
2. **Professor Data**: From public sources only
3. **Email Config**: Stored locally, not transmitted
4. **Logs**: Do not log email body content

---

## Summary Flow

```
User: "Help me research MIT CS professors"

1. Check email config
   -> If not configured: guide setup
   -> If configured: continue

2. Upload materials
   -> Parse CV/research plan
   -> Extract key info

3. Research professors
   -> Search department website
   -> For each professor:
      - Research homepage
      - Check Google Scholar
      - Analyze match with user

4. Generate report
   -> Create HTML visualization
   -> Include all research data

5. Generate emails
   -> Personalize for each professor
   -> Save drafts

6. Send emails
   -> User reviews
   -> Dry run (optional)
   -> Send with delay
   -> Log results
```

---

## Best Practices

1. **Always check email config first**
2. **Use dry run before real send**
3. **30s delay between batch emails**
4. **Review drafts before sending**
5. **Check logs after sending**
6. **Cache research results** (avoid re-research)
