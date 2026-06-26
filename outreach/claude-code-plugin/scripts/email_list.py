#!/usr/bin/env python3
"""
邮件列表查看脚本
用法: python email_list.py [--limit 20] [--unread] [--search "keyword"]
"""

import argparse
import json
import imaplib
import email
from email.header import decode_header
from pathlib import Path

CONFIG_FILE = Path.home() / ".outreach" / "email_config.json"


def load_config():
    """加载邮件配置"""
    if not CONFIG_FILE.exists():
        print("❌ 未找到邮件配置，请先运行 email_setup.py")
        return None
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def list_emails(folder="INBOX", limit=20, unread_only=False, search_query=None):
    """列出邮件"""
    config = load_config()
    if not config:
        return

    try:
        # 连接 IMAP
        imap = imaplib.IMAP4_SSL(config["imap_server"], config["imap_port"])
        imap.login(config["email"], config["password"])

        # 选择文件夹
        imap.select(folder)

        # 搜索邮件
        if search_query:
            status, messages = imap.search(None, f'(OR SUBJECT "{search_query}" BODY "{search_query}")')
        elif unread_only:
            status, messages = imap.search(None, "UNSEEN")
        else:
            status, messages = imap.search(None, "ALL")

        if status != "OK":
            print("❌ 搜索邮件失败")
            return

        # 获取邮件ID列表
        email_ids = messages[0].split()
        if not email_ids:
            print("📭 没有邮件")
            return

        # 取最新的N封
        email_ids = email_ids[-limit:]
        email_ids.reverse()

        print(f"📬 {folder} - 最新 {len(email_ids)} 封邮件\n")

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

            # 检查是否已读
            is_read = "\\Seen" in str(msg_data)
            status_icon = "  " if is_read else "📩"

            print(f"{status_icon} [{eid.decode()}] {date}")
            print(f"   发件人: {from_addr}")
            print(f"   主题: {subject}")
            print()

        imap.logout()
    except Exception as e:
        print(f"❌ 获取邮件失败: {e}")


def read_email(email_id, folder="INBOX"):
    """读取单封邮件"""
    config = load_config()
    if not config:
        return

    try:
        # 连接 IMAP
        imap = imaplib.IMAP4_SSL(config["imap_server"], config["imap_port"])
        imap.login(config["email"], config["password"])

        # 选择文件夹
        imap.select(folder)

        # 获取邮件
        status, msg_data = imap.fetch(email_id.encode(), "(RFC822)")
        if status != "OK":
            print("❌ 获取邮件失败")
            return

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

        print(f"📧 邮件详情\n")
        print(f"主题: {subject}")
        print(f"发件人: {msg['From']}")
        print(f"收件人: {msg['To']}")
        if msg['Cc']:
            print(f"抄送: {msg['Cc']}")
        print(f"日期: {msg['Date']}")
        print(f"\n{'='*60}")

        # 获取正文
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                    print(body)
                    break
        else:
            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
            print(body)

        imap.logout()
    except Exception as e:
        print(f"❌ 读取邮件失败: {e}")


def main():
    parser = argparse.ArgumentParser(description="查看邮件")
    parser.add_argument("--folder", default="INBOX", help="邮件文件夹")
    parser.add_argument("--limit", type=int, default=20, help="显示数量")
    parser.add_argument("--unread", action="store_true", help="只显示未读")
    parser.add_argument("--search", help="搜索关键词")
    parser.add_argument("--read", help="读取指定ID的邮件")
    args = parser.parse_args()

    if args.read:
        read_email(args.read, args.folder)
    else:
        list_emails(args.folder, args.limit, args.unread, args.search)


if __name__ == "__main__":
    main()
