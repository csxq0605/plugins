# Email Protocol -- Reference Doc

> This doc defines the email sending protocol and best practices.
> Language convention: narrative in Chinese, all technical terms / commands in English.

---

## Preconditions

- Email must be configured before sending.
- Configuration is stored in `~/.email/config.json`.
- Use `email_is_configured()` to check before any email operation.

---

## Email Configuration Protocol

### 1. Check Configuration

Always check if email is configured first:

```python
result = email_is_configured()
if not result["configured"]:
    # Guide user to configure
    email_setup(email_addr="...", password="...", preset="pku")
```

### 2. Supported Presets

| Preset | Server | Port | Notes |
|--------|--------|------|-------|
| `pku` | mail.stu.pku.edu.cn | 993/465 | PKU student email |
| `tsinghua` | mail.tsinghua.edu.cn | 993/465 | Tsinghua email |
| `gmail` | imap.gmail.com | 993/587 | Requires app password |
| `outlook` | outlook.office365.com | 993/587 | Microsoft account |
| `qq` | imap.qq.com | 993/465 | Requires app password |
| `163` | imap.163.com | 993/465 | Requires auth code |

### 3. Configuration Testing

After setup, the system automatically tests:
- IMAP connection (receive)
- SMTP connection (Send)

If test fails, the configuration is NOT saved.

---

## Sending Protocol

### 1. Single Email

```python
email_send(
    to="recipient@example.com",
    subject="Subject",
    body="Body content"
)
```

### 2. Dry Run (Recommended)

Always test with dry run first:

```python
email_send(
    to="recipient@example.com",
    subject="Subject",
    body="Body",
    dry_run=True  # Preview without sending
)
```

### 3. Batch Sending

For multiple emails, use batch with delay:

```python
emails = [
    {"to": "person1@example.com", "subject": "...", "body": "..."},
    {"to": "person2@example.com", "subject": "...", "body": "..."},
]

email_send_batch(
    emails=emails,
    delay=30,  # 30 seconds between emails
    dry_run=False
)
```

**Important**: 
- Minimum 30 seconds delay to avoid spam detection
- Maximum 50 emails per batch
- Check logs after batch send

---

## Receiving Protocol

### 1. List Emails

```python
# List latest 20 emails
email_list(folder="INBOX", limit=20)

# List unread only
email_list(folder="INBOX", unread_only=True)
```

### 2. Search Emails

```python
email_search(query="keyword", folder="INBOX", limit=10)
```

### 3. Read Email

```python
email_read(email_id="123", folder="INBOX")
```

---

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `AUTHENTICATIONFAILED` | Wrong password | Check password or use app password |
| `Connection refused` | Wrong server/port | Verify server settings |
| `Timeout` | Network issue | Retry or check network |

### Gmail/QQ Specific

- Gmail: Requires 2FA + App Password
- QQ: Requires IMAP/SMTP enabled + Auth Code

---

## Logging

All sent emails are logged to `~/.email/logs/`:

```
---
Time: 2024-01-15T10:30:00
To: recipient@example.com
Subject: Subject
Status: SUCCESS
Detail: Sent successfully
```

---

## Security

1. **Password Storage**: Stored in local config file, not transmitted
2. **Connection**: Always SSL/TLS encrypted
3. **Logs**: Do not log email body content
4. **Batch Limit**: Prevent accidental mass sending

---

## Summary Flow

```
Check configuration (email_is_configured)
  -> If not configured: guide user to setup
  -> If configured: proceed

Send email:
  -> Dry run first (optional but recommended)
  -> Check result
  -> Log to file

Receive email:
  -> List or search
  -> Read specific email
```
