#!/usr/bin/env python3
"""
邮件发送脚本
用法: python email_send.py --to recipient@email.com --subject "Subject" --body "Body"
"""

import argparse
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime

CONFIG_FILE = Path.home() / ".outreach" / "email_config.json"

# 日志默认放在当前目录/.outreach/logs/ (项目级)
# 可通过 --path 参数指定其他位置
DEFAULT_LOGS_DIR = Path.cwd() / ".outreach" / "logs"

def get_logs_dir(path=None):
    """获取日志目录，优先使用指定路径，否则用当前目录"""
    if path:
        return Path(path).resolve() / ".outreach" / "logs"
    return DEFAULT_LOGS_DIR


def load_config():
    """加载邮件配置"""
    if not CONFIG_FILE.exists():
        print("❌ 未找到邮件配置，请先运行 email_setup.py")
        return None
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def send_email(to, subject, body, cc=None, bcc=None, html=False, dry_run=False):
    """发送邮件"""
    config = load_config()
    if not config:
        return False

    if dry_run:
        print("📧 试运行模式，邮件未实际发送")
        print(f"   发件人: {config['name']} <{config['email']}>")
        print(f"   收件人: {to}")
        if cc:
            print(f"   抄送: {cc}")
        if bcc:
            print(f"   密送: {bcc}")
        print(f"   主题: {subject}")
        print(f"   正文:\n{body[:500]}...")
        return True

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
        smtp = smtplib.SMTP_SSL(config["smtp_server"], config["smtp_port"])
        smtp.login(config["email"], config["password"])
        smtp.sendmail(config["email"], recipients, msg.as_string())
        smtp.quit()

        # 记录日志
        log_email(to, subject, body, True, "发送成功")

        print(f"✅ 邮件已发送给 {to}")
        return True
    except Exception as e:
        log_email(to, subject, body, False, str(e))
        print(f"❌ 发送失败: {e}")
        return False


def log_email(to, subject, body, success, detail):
    """记录发送日志"""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.log"
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


def main():
    parser = argparse.ArgumentParser(description="发送邮件")
    parser.add_argument("--to", required=True, help="收件人邮箱")
    parser.add_argument("--subject", required=True, help="邮件主题")
    parser.add_argument("--body", required=True, help="邮件正文")
    parser.add_argument("--body-file", help="从文件读取邮件正文")
    parser.add_argument("--cc", help="抄送")
    parser.add_argument("--bcc", help="密送")
    parser.add_argument("--html", action="store_true", help="HTML格式")
    parser.add_argument("--dry-run", action="store_true", help="试运行")
    parser.add_argument("--path", help="Project root path. Logs will be stored in <path>/.outreach/logs/")
    args = parser.parse_args()

    # 初始化日志目录
    global LOGS_DIR
    LOGS_DIR = get_logs_dir(args.path)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # 读取正文
    body = args.body
    if args.body_file:
        body = Path(args.body_file).read_text("utf-8")

    send_email(args.to, args.subject, body, args.cc, args.bcc, args.html, args.dry_run)


if __name__ == "__main__":
    main()
