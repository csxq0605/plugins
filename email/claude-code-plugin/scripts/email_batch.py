#!/usr/bin/env python3
"""
批量邮件发送脚本
用法: python email_batch.py --csv professors.csv [--delay 30] [--dry-run]
"""

import argparse
import csv
import json
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime

CONFIG_FILE = Path.home() / ".email" / "email_config.json"

# 日志默认放在当前目录/.email/logs/ (项目级)
# 可通过 --path 参数指定其他位置
DEFAULT_LOGS_DIR = Path.cwd() / ".email" / "logs"

def get_logs_dir(path=None):
    """获取日志目录，优先使用指定路径，否则用当前目录"""
    if path:
        return Path(path).resolve() / ".email" / "logs"
    return DEFAULT_LOGS_DIR


def load_config():
    """加载邮件配置"""
    if not CONFIG_FILE.exists():
        print("❌ 未找到邮件配置，请先运行 email_setup.py")
        return None
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_professors(csv_path, school=None, limit=None):
    """加载教授列表"""
    professors = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if school and school.lower() not in row.get("school", "").lower():
                continue
            professors.append(row)
    if limit:
        professors = professors[:limit]
    return professors


def send_email(config, to, subject, body, dry_run=False):
    """发送单封邮件"""
    if dry_run:
        return True, "DRY RUN"

    try:
        msg = MIMEMultipart()
        msg["From"] = f"{config['name']} <{config['email']}>"
        msg["To"] = to
        msg["Subject"] = subject
        msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
        msg.attach(MIMEText(body, "plain", "utf-8"))

        smtp = smtplib.SMTP_SSL(config["smtp_server"], config["smtp_port"])
        smtp.login(config["email"], config["password"])
        smtp.sendmail(config["email"], [to], msg.as_string())
        smtp.quit()

        return True, "发送成功"
    except Exception as e:
        return False, str(e)


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
    parser = argparse.ArgumentParser(description="批量发送邮件")
    parser.add_argument("--csv", required=True, help="教授列表CSV文件")
    parser.add_argument("--school", help="只处理指定学校")
    parser.add_argument("--limit", type=int, help="最多处理N个教授")
    parser.add_argument("--delay", type=int, default=30, help="每封邮件间隔秒数")
    parser.add_argument("--dry-run", action="store_true", help="试运行")
    parser.add_argument("--subject", help="邮件主题（从文件读取）")
    parser.add_argument("--body", help="邮件正文（从文件读取）")
    parser.add_argument("--path", help="Project root path. Logs will be stored in <path>/.email/logs/")
    args = parser.parse_args()

    # 初始化日志目录
    global LOGS_DIR
    LOGS_DIR = get_logs_dir(args.path)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # 加载配置
    config = load_config()
    if not config:
        return

    # 加载教授列表
    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"❌ CSV文件不存在: {csv_path}")
        return

    professors = load_professors(csv_path, args.school, args.limit)
    if not professors:
        print("❌ 没有匹配的教授")
        return

    print(f"📋 共 {len(professors)} 位教授")

    if args.dry_run:
        print("🔍 DRY RUN 模式\n")

    # 检查是否有邮件草稿目录
    email_drafts_dir = Path.home() / ".email" / "schools"

    results = {"success": 0, "failed": 0}

    for i, prof in enumerate(professors, 1):
        print(f"\n{'='*60}")
        print(f"[{i}/{len(professors)}] {prof['name']} @ {prof['school']}")
        print(f"  邮箱: {prof['email']}")

        # 查找邮件草稿
        school_dept = f"{prof['school']}_{prof.get('department', 'CS')}"
        prof_dir = email_drafts_dir / school_dept / prof['name'].replace(' ', '_')
        email_file = prof_dir / "email_draft.md"

        if email_file.exists():
            # 从草稿读取
            content = email_file.read_text("utf-8")
            lines = content.split("\n")
            subject = lines[0].replace("# ", "").strip() if lines[0].startswith("# ") else f"Prospective PhD Student - {prof['name']}"
            body = "\n".join(lines[2:]).strip() if len(lines) > 2 else content
        elif args.subject and args.body:
            # 使用命令行参数
            subject = args.subject
            body = Path(args.body).read_text("utf-8") if Path(args.body).exists() else args.body
        else:
            print(f"  ⚠️  未找到邮件草稿，跳过")
            continue

        print(f"  📧 主题: {subject}")

        # 发送
        success, detail = send_email(config, prof['email'], subject, body, args.dry_run)

        if success:
            print(f"  ✅ {'已生成 (dry run)' if args.dry_run else '发送成功'}")
            results["success"] += 1
        else:
            print(f"  ❌ 发送失败: {detail[:100]}")
            results["failed"] += 1

        log_email(prof['email'], subject, body, success, detail)

        # 间隔等待
        if i < len(professors) and not args.dry_run:
            print(f"  ⏳ 等待 {args.delay} 秒...")
            time.sleep(args.delay)

    # 汇总
    print(f"\n{'='*60}")
    print(f"📊 完成汇总:")
    print(f"   成功: {results['success']}")
    print(f"   失败: {results['failed']}")
    print(f"   日志: {LOGS_DIR}")


if __name__ == "__main__":
    main()
