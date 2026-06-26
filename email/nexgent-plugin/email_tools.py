#!/usr/bin/env python3
"""
Email Tools - 独立邮件插件
基于 IMAP/SMTP 协议的邮件收发工具
"""

import os
import json
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# 配置文件路径 (用户级配置，放在 ~/.email/)
CONFIG_DIR = Path.home() / ".email"
CONFIG_FILE = CONFIG_DIR / "config.json"

# 日志默认放在当前目录/.email/logs/ (项目级)
# 可通过 path 参数指定其他位置
DEFAULT_LOGS_DIR = Path.cwd() / ".email" / "logs"

def get_logs_dir(path=None):
    """获取日志目录，优先使用指定路径，否则用当前目录"""
    if path:
        return Path(path).resolve() / ".email" / "logs"
    return DEFAULT_LOGS_DIR

# 初始化日志目录
LOGS_DIR = DEFAULT_LOGS_DIR
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# 常见邮箱服务器配置
EMAIL_PRESETS = {
    "pku": {
        "name": "北京大学邮箱",
        "imap_server": "mail.stu.pku.edu.cn",
        "imap_port": 993,
        "smtp_server": "mail.stu.pku.edu.cn",
        "smtp_port": 465
    },
    "tsinghua": {
        "name": "清华大学邮箱",
        "imap_server": "mail.tsinghua.edu.cn",
        "imap_port": 993,
        "smtp_server": "mail.tsinghua.edu.cn",
        "smtp_port": 465
    },
    "gmail": {
        "name": "Gmail",
        "imap_server": "imap.gmail.com",
        "imap_port": 993,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587
    },
    "outlook": {
        "name": "Outlook/Hotmail",
        "imap_server": "outlook.office365.com",
        "imap_port": 993,
        "smtp_server": "smtp.office365.com",
        "smtp_port": 587
    },
    "qq": {
        "name": "QQ邮箱",
        "imap_server": "imap.qq.com",
        "imap_port": 993,
        "smtp_server": "smtp.qq.com",
        "smtp_port": 465
    },
    "163": {
        "name": "163邮箱",
        "imap_server": "imap.163.com",
        "imap_port": 993,
        "smtp_server": "smtp.163.com",
        "smtp_port": 465
    },
    "custom": {
        "name": "自定义",
        "imap_server": "",
        "imap_port": 993,
        "smtp_server": "",
        "smtp_port": 465
    }
}


def _load_config() -> Optional[Dict[str, str]]:
    """加载邮件配置，如果未配置返回None"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            if config.get("email") and config.get("password"):
                return config
    return None


def _save_config(config: Dict[str, str]):
    """保存邮件配置"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def _test_connection(config: Dict[str, str]) -> Dict[str, Any]:
    """测试邮件服务器连接"""
    errors = []

    # 测试 IMAP
    try:
        imap = imaplib.IMAP4_SSL(config["imap_server"], config["imap_port"])
        imap.login(config["email"], config["password"])
        imap.logout()
    except imaplib.IMAP4.error as e:
        errors.append(f"IMAP login failed: {str(e)}")
    except Exception as e:
        errors.append(f"IMAP connection failed: {str(e)}")

    # 测试 SMTP
    try:
        if config["smtp_port"] == 587:
            smtp = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
            smtp.starttls()
        else:
            smtp = smtplib.SMTP_SSL(config["smtp_server"], config["smtp_port"])
        smtp.login(config["email"], config["password"])
        smtp.quit()
    except smtplib.SMTPAuthenticationError as e:
        errors.append(f"SMTP login failed: {str(e)}")
    except Exception as e:
        errors.append(f"SMTP connection failed: {str(e)}")

    if errors:
        return {
            "success": False,
            "error": "Email connection test failed",
            "details": errors,
            "suggestion": "Please check:\n1. Email address and password are correct\n2. Gmail/QQ mail need app-specific password\n3. Server address and port are correct"
        }

    return {"success": True}


def email_is_configured() -> Dict[str, Any]:
    """
    检查邮箱是否已配置

    Returns:
        配置状态
    """
    config = _load_config()
    if config:
        return {
            "configured": True,
            "email": config["email"],
            "name": config.get("name", ""),
            "server": f"{config['imap_server']}:{config['imap_port']}"
        }
    return {"configured": False}


def email_get_presets() -> Dict[str, Any]:
    """
    获取支持的邮箱服务器预设

    Returns:
        预设列表
    """
    return {
        "success": True,
        "presets": {k: v["name"] for k, v in EMAIL_PRESETS.items()}
    }


def email_setup(
    email_addr: str,
    password: str,
    name: str = "",
    preset: str = None,
    imap_server: str = None,
    imap_port: int = None,
    smtp_server: str = None,
    smtp_port: int = None
) -> Dict[str, Any]:
    """
    配置邮件账户

    Args:
        email_addr: 邮箱地址
        password: 邮箱密码或应用专用密码
        name: 发件人姓名
        preset: 邮箱预设（pku/tsinghua/gmail/outlook/qq/163）
        imap_server: 自定义IMAP服务器地址
        imap_port: 自定义IMAP端口
        smtp_server: 自定义SMTP服务器地址
        smtp_port: 自定义SMTP端口

    Returns:
        配置结果
    """
    # 确定服务器配置
    if preset and preset in EMAIL_PRESETS:
        server_config = EMAIL_PRESETS[preset].copy()
    else:
        # 尝试自动检测
        domain = email_addr.split("@")[1] if "@" in email_addr else ""
        preset = None
        for key, val in EMAIL_PRESETS.items():
            if key != "custom" and domain in key:
                preset = key
                server_config = val.copy()
                break
        else:
            server_config = EMAIL_PRESETS["custom"].copy()

    # 用户自定义覆盖
    if imap_server:
        server_config["imap_server"] = imap_server
    if imap_port:
        server_config["imap_port"] = imap_port
    if smtp_server:
        server_config["smtp_server"] = smtp_server
    if smtp_port:
        server_config["smtp_port"] = smtp_port

    config = {
        "imap_server": server_config["imap_server"],
        "imap_port": server_config["imap_port"],
        "smtp_server": server_config["smtp_server"],
        "smtp_port": server_config["smtp_port"],
        "email": email_addr,
        "password": password,
        "name": name or email_addr.split("@")[0],
        "preset": preset or "custom"
    }

    # 测试连接
    test_result = _test_connection(config)
    if not test_result["success"]:
        return test_result

    # 保存配置
    _save_config(config)

    return {
        "success": True,
        "message": f"Email configured successfully: {email_addr}",
        "config": {
            "email": email_addr,
            "name": config["name"],
            "imap_server": config["imap_server"],
            "imap_port": config["imap_port"],
            "smtp_server": config["smtp_server"],
            "smtp_port": config["smtp_port"]
        }
    }


def email_test() -> Dict[str, Any]:
    """
    测试当前邮箱配置是否可用

    Returns:
        测试结果
    """
    config = _load_config()
    if not config:
        return {
            "success": False,
            "error": "Email not configured, please use email_setup first"
        }

    return _test_connection(config)


def email_get_config() -> Dict[str, Any]:
    """
    获取当前邮件配置

    Returns:
        配置信息（隐藏密码）
    """
    config = _load_config()
    if not config:
        return {
            "success": False,
            "error": "Email not configured, please use email_setup first"
        }

    return {
        "success": True,
        "configured": True,
        "config": {
            "email": config["email"],
            "name": config["name"],
            "imap_server": config["imap_server"],
            "imap_port": config["imap_port"],
            "smtp_server": config["smtp_server"],
            "smtp_port": config["smtp_port"],
            "password": "***configured***"
        }
    }


def email_send(
    to: str,
    subject: str,
    body: str,
    cc: str = None,
    bcc: str = None,
    html: bool = False,
    dry_run: bool = False,
    path: str = None
) -> Dict[str, Any]:
    """
    发送邮件

    Args:
        to: 收件人邮箱（多个用逗号分隔）
        subject: 邮件主题
        body: 邮件正文
        cc: 抄送（可选，多个用逗号分隔）
        bcc: 密送（可选，多个用逗号分隔）
        html: 是否为HTML格式
        dry_run: 试运行模式（不实际发送）
        path: 项目根路径，日志将存储在 <path>/.email/logs/

    Returns:
        发送结果
    """
    # Dry run mode doesn't need config
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "message": "Dry run mode, email not sent",
            "preview": {
                "from": "dry-run@example.com",
                "to": to,
                "cc": cc,
                "bcc": bcc,
                "subject": subject,
                "body": body[:500] + "..." if len(body) > 500 else body
            }
        }

    config = _load_config()
    if not config:
        return {
            "success": False,
            "error": "Email not configured, please use email_setup first"
        }

    try:
        # 创建邮件
        msg = MIMEMultipart()
        msg["From"] = f"{config['name']} <{config['email']}>"
        msg["To"] = to
        msg["Subject"] = subject
        msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")

        if cc:
            msg["Cc"] = cc
        if bcc:
            msg["Bcc"] = bcc

        # 添加正文
        if html:
            msg.attach(MIMEText(body, "html", "utf-8"))
        else:
            msg.attach(MIMEText(body, "plain", "utf-8"))

        # 收件人列表
        recipients = [addr.strip() for addr in to.split(",")]
        if cc:
            recipients.extend([addr.strip() for addr in cc.split(",")])
        if bcc:
            recipients.extend([addr.strip() for addr in bcc.split(",")])

        # 发送邮件
        if config["smtp_port"] == 587:
            smtp = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
            smtp.starttls()
        else:
            smtp = smtplib.SMTP_SSL(config["smtp_server"], config["smtp_port"])
        smtp.login(config["email"], config["password"])
        smtp.sendmail(config["email"], recipients, msg.as_string())
        smtp.quit()

        # 记录日志
        _log_email(to, subject, body, True, "Sent successfully", path)

        return {
            "success": True,
            "message": f"Email sent to {to}",
            "details": {
                "from": config["email"],
                "to": to,
                "subject": subject,
                "time": datetime.now().isoformat()
            }
        }
    except Exception as e:
        # 记录失败日志
        _log_email(to, subject, body, False, str(e), path)

        return {
            "success": False,
            "error": f"Failed to send: {str(e)}"
        }


def email_send_batch(
    emails: List[Dict[str, str]],
    delay: int = 30,
    dry_run: bool = False,
    path: str = None
) -> Dict[str, Any]:
    """
    批量发送邮件

    Args:
        emails: 邮件列表，每项包含 to, subject, body
        delay: 每封邮件间隔秒数
        dry_run: 试运行模式
        path: 项目根路径，日志将存储在 <path>/.email/logs/

    Returns:
        批量发送结果
    """
    import time

    results = {
        "total": len(emails),
        "success": 0,
        "failed": 0,
        "details": []
    }

    for i, mail in enumerate(emails, 1):
        print(f"[{i}/{len(emails)}] Sending to {mail['to']}...")

        result = email_send(
            to=mail["to"],
            subject=mail["subject"],
            body=mail["body"],
            dry_run=dry_run,
            path=path
        )

        if result["success"]:
            results["success"] += 1
        else:
            results["failed"] += 1

        results["details"].append({
            "to": mail["to"],
            "subject": mail["subject"],
            "success": result["success"],
            "error": result.get("error")
        })

        # 间隔等待
        if i < len(emails) and not dry_run:
            print(f"  Waiting {delay} seconds...")
            time.sleep(delay)

    return results


def email_list(
    folder: str = "INBOX",
    limit: int = 20,
    unread_only: bool = False
) -> Dict[str, Any]:
    """
    列出邮件

    Args:
        folder: 邮件文件夹（INBOX, Sent, Drafts等）
        limit: 返回数量限制
        unread_only: 只显示未读邮件

    Returns:
        邮件列表
    """
    config = _load_config()
    if not config:
        return {
            "success": False,
            "error": "Email not configured, please use email_setup first"
        }

    try:
        # 连接 IMAP
        imap = imaplib.IMAP4_SSL(config["imap_server"], config["imap_port"])
        imap.login(config["email"], config["password"])

        # 选择文件夹
        imap.select(folder)

        # 搜索邮件
        if unread_only:
            status, messages = imap.search(None, "UNSEEN")
        else:
            status, messages = imap.search(None, "ALL")

        if status != "OK":
            return {"success": False, "error": "Failed to search emails"}

        # 获取邮件ID列表
        email_ids = messages[0].split()
        if not email_ids:
            return {
                "success": True,
                "count": 0,
                "emails": []
            }

        # 取最新的N封
        email_ids = email_ids[-limit:]
        email_ids.reverse()

        emails = []
        for eid in email_ids:
            status, msg_data = imap.fetch(eid, "(RFC822)")
            if status != "OK":
                continue

            # 解析邮件
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            # 解析主题
            subject = msg["Subject"]
            if subject:
                decoded = decode_header(subject)
                subject = decoded[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode(decoded[0][1] or "utf-8")

            # 解析发件人
            from_addr = msg["From"]

            # 解析日期
            date = msg["Date"]

            # 获取正文
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

            emails.append({
                "id": eid.decode(),
                "from": from_addr,
                "subject": subject,
                "date": date,
                "body_preview": body[:200] + "..." if len(body) > 200 else body,
                "is_read": "\\Seen" in str(msg_data)
            })

        imap.logout()

        return {
            "success": True,
            "count": len(emails),
            "folder": folder,
            "emails": emails
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get emails: {str(e)}"
        }


def email_read(email_id: str, folder: str = "INBOX") -> Dict[str, Any]:
    """
    读取单封邮件

    Args:
        email_id: 邮件ID
        folder: 邮件文件夹

    Returns:
        邮件详情
    """
    config = _load_config()
    if not config:
        return {
            "success": False,
            "error": "Email not configured, please use email_setup first"
        }

    try:
        # 连接 IMAP
        imap = imaplib.IMAP4_SSL(config["imap_server"], config["imap_port"])
        imap.login(config["email"], config["password"])

        # 选择文件夹
        imap.select(folder)

        # 获取邮件
        status, msg_data = imap.fetch(email_id.encode(), "(RFC822)")
        if status != "OK":
            return {"success": False, "error": "Failed to get email"}

        # 解析邮件
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        # 解析主题
        subject = msg["Subject"]
        if subject:
            decoded = decode_header(subject)
            subject = decoded[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode(decoded[0][1] or "utf-8")

        # 解析收件人
        to = msg["To"]
        cc = msg["Cc"]

        # 解析日期
        date = msg["Date"]

        # 获取正文
        body = ""
        html_body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                elif content_type == "text/html":
                    html_body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
        else:
            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

        imap.logout()

        return {
            "success": True,
            "email": {
                "id": email_id,
                "from": msg["From"],
                "to": to,
                "cc": cc,
                "subject": subject,
                "date": date,
                "body": body,
                "html_body": html_body
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to read email: {str(e)}"
        }


def _log_email(to: str, subject: str, body: str, success: bool, detail: str, path: str = None):
    """记录邮件发送日志"""
    logs_dir = get_logs_dir(path)
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"
    status = "SUCCESS" if success else "FAILED"
    entry = f"""
---
Time: {datetime.now().isoformat()}
To: {to}
Subject: {subject}
Status: {status}
Detail: {detail[:200]}
"""
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry)


def email_search(
    query: str,
    folder: str = "INBOX",
    limit: int = 10
) -> Dict[str, Any]:
    """
    搜索邮件

    Args:
        query: 搜索关键词
        folder: 邮件文件夹
        limit: 返回数量限制

    Returns:
        搜索结果
    """
    config = _load_config()
    if not config:
        return {
            "success": False,
            "error": "Email not configured, please use email_setup first"
        }

    try:
        # 连接 IMAP
        imap = imaplib.IMAP4_SSL(config["imap_server"], config["imap_port"])
        imap.login(config["email"], config["password"])

        # 选择文件夹
        imap.select(folder)

        # 搜索邮件
        status, messages = imap.search(None, f'(OR SUBJECT "{query}" BODY "{query}")')

        if status != "OK":
            # 尝试简单搜索
            status, messages = imap.search(None, f'SUBJECT "{query}"')

        if status != "OK":
            return {"success": False, "error": "Search failed"}

        # 获取邮件ID列表
        email_ids = messages[0].split()
        if not email_ids:
            return {
                "success": True,
                "count": 0,
                "query": query,
                "emails": []
            }

        # 取最新的N封
        email_ids = email_ids[-limit:]
        email_ids.reverse()

        emails = []
        for eid in email_ids:
            status, msg_data = imap.fetch(eid, "(RFC822)")
            if status != "OK":
                continue

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject = msg["Subject"]
            if subject:
                decoded = decode_header(subject)
                subject = decoded[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode(decoded[0][1] or "utf-8")

            emails.append({
                "id": eid.decode(),
                "from": msg["From"],
                "subject": subject,
                "date": msg["Date"]
            })

        imap.logout()

        return {
            "success": True,
            "count": len(emails),
            "query": query,
            "emails": emails
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Search failed: {str(e)}"
        }
