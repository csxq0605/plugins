# Email Protocol -- Reference Doc

> This doc defines the email sending protocol for Claude Code plugin.

---

## Configuration Check

Before any email operation, check configuration:

```bash
python scripts/email_setup.py --check
```

If not configured:

```bash
python scripts/email_setup.py --email user@example.com --password pass --preset pku
```

---

## Supported Presets

| Preset | Server | Port |
|--------|--------|------|
| `pku` | mail.stu.pku.edu.cn | 993/465 |
| `tsinghua` | mail.tsinghua.edu.cn | 993/465 |
| `gmail` | imap.gmail.com | 993/587 |
| `outlook` | outlook.office365.com | 993/587 |
| `qq` | imap.qq.com | 993/465 |
| `163` | imap.163.com | 993/465 |

---

## Sending Email

### Single Email

```bash
python scripts/email_send.py --to recipient@example.com --subject "Subject" --body "Body"
```

### Dry Run

```bash
python scripts/email_send.py --to recipient@example.com --subject "Subject" --body "Body" --dry-run
```

### Batch Send

```bash
python scripts/email_batch.py --csv recipients.csv --delay 30
python scripts/email_batch.py --csv recipients.csv --delay 30 --dry-run
```

---

## Viewing Email

### List Inbox

```bash
python scripts/email_list.py --limit 20
python scripts/email_list.py --unread
```

### Search

```bash
python scripts/email_list.py --search "keyword"
```

### Read Email

```bash
python scripts/email_list.py --read 123
```

---

## Error Handling

| Error | Solution |
|-------|----------|
| `AUTHENTICATIONFAILED` | Check password or use app password |
| `Connection refused` | Verify server settings |
| `Timeout` | Check network |

---

## Logging

Logs are saved to `~/.email/logs/` directory.
