#!/usr/bin/env python3
"""
邮箱配置脚本
用法:
  python email_setup.py --check                                    # 检查是否已配置
  python email_setup.py --email your@email.com --password pass     # 配置邮箱
  python email_setup.py --email your@email.com --password pass --preset gmail  # 使用预设
  python email_setup.py --test                                     # 测试连接
  python email_setup.py --info                                     # 查看配置
"""

import argparse
import json
import smtplib
import imaplib
from pathlib import Path

CONFIG_DIR = Path.home() / ".email"
CONFIG_FILE = CONFIG_DIR / "email_config.json"

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
    }
}


def load_config():
    """加载邮件配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            if config.get("email") and config.get("password"):
                return config
    return None


def save_config(config):
    """保存邮件配置"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def test_connection(config):
    """测试邮件服务器连接"""
    errors = []

    # 测试 IMAP
    print("Testing IMAP connection...")
    try:
        imap = imaplib.IMAP4_SSL(config["imap_server"], config["imap_port"])
        imap.login(config["email"], config["password"])
        imap.logout()
        print("  [OK] IMAP connection successful")
    except imaplib.IMAP4.error as e:
        errors.append(f"IMAP login failed: {str(e)}")
        print(f"  [FAIL] IMAP login failed: {e}")
    except Exception as e:
        errors.append(f"IMAP connection failed: {str(e)}")
        print(f"  [FAIL] IMAP connection failed: {e}")

    # 测试 SMTP
    print("Testing SMTP connection...")
    try:
        if config["smtp_port"] == 587:
            smtp = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
            smtp.starttls()
        else:
            smtp = smtplib.SMTP_SSL(config["smtp_server"], config["smtp_port"])
        smtp.login(config["email"], config["password"])
        smtp.quit()
        print("  [OK] SMTP connection successful")
    except smtplib.SMTPAuthenticationError as e:
        errors.append(f"SMTP login failed: {str(e)}")
        print(f"  [FAIL] SMTP login failed: {e}")
    except Exception as e:
        errors.append(f"SMTP connection failed: {str(e)}")
        print(f"  [FAIL] SMTP connection failed: {e}")

    return len(errors) == 0, errors


def check_config():
    """检查是否已配置"""
    config = load_config()
    if config:
        print(f"[OK] Email configured: {config['email']}")
        print(f"   Server: {config['imap_server']}:{config['imap_port']}")
        return True
    else:
        print("[NOT CONFIGURED] Email not configured")
        return False


def show_config():
    """显示当前配置"""
    config = load_config()
    if not config:
        print("[NOT CONFIGURED] Email not configured")
        return

    print("[EMAIL CONFIG]")
    print(f"   Email: {config['email']}")
    print(f"   Name: {config.get('name', 'N/A')}")
    print(f"   IMAP: {config['imap_server']}:{config['imap_port']}")
    print(f"   SMTP: {config['smtp_server']}:{config['smtp_port']}")
    print(f"   Password: {'*' * 8}")


def main():
    parser = argparse.ArgumentParser(description="邮箱配置脚本")
    parser.add_argument("--check", action="store_true", help="检查是否已配置")
    parser.add_argument("--test", action="store_true", help="测试邮箱连接")
    parser.add_argument("--info", action="store_true", help="查看当前配置")
    parser.add_argument("--email", help="邮箱地址")
    parser.add_argument("--password", help="邮箱密码")
    parser.add_argument("--name", help="发件人姓名")
    parser.add_argument("--preset", choices=list(EMAIL_PRESETS.keys()), help="邮箱预设")
    parser.add_argument("--imap-server", help="自定义IMAP服务器")
    parser.add_argument("--imap-port", type=int, help="自定义IMAP端口")
    parser.add_argument("--smtp-server", help="自定义SMTP服务器")
    parser.add_argument("--smtp-port", type=int, help="自定义SMTP端口")
    args = parser.parse_args()

    # 检查配置
    if args.check:
        check_config()
        return

    # 测试连接
    if args.test:
        config = load_config()
        if not config:
            print("[ERROR] Email not configured, please configure first")
            return
        success, errors = test_connection(config)
        if success:
            print("\n[SUCCESS] Email connection test passed")
        else:
            print("\n[FAIL] Email connection test failed")
            print("Error details:")
            for err in errors:
                print(f"  - {err}")
            print("\nSuggestions:")
            print("  1. Check if email address and password are correct")
            print("  2. Gmail/QQ mail etc. need to use app-specific password")
            print("  3. Verify server address and port are correct")
        return

    # 查看配置
    if args.info:
        show_config()
        return

    # 配置邮箱
    if args.email and args.password:
        # 确定服务器配置
        if args.preset and args.preset in EMAIL_PRESETS:
            server_config = EMAIL_PRESETS[args.preset].copy()
        else:
            # 尝试自动检测
            domain = args.email.split("@")[1] if "@" in args.email else ""
            preset = None
            for key, val in EMAIL_PRESETS.items():
                if domain in key or domain in val.get("name", ""):
                    preset = key
                    server_config = val.copy()
                    break
            else:
                server_config = {"imap_server": "", "imap_port": 993, "smtp_server": "", "smtp_port": 465}

        # 用户自定义覆盖
        if args.imap_server:
            server_config["imap_server"] = args.imap_server
        if args.imap_port:
            server_config["imap_port"] = args.imap_port
        if args.smtp_server:
            server_config["smtp_server"] = args.smtp_server
        if args.smtp_port:
            server_config["smtp_port"] = args.smtp_port

        config = {
            "imap_server": server_config["imap_server"],
            "imap_port": server_config["imap_port"],
            "smtp_server": server_config["smtp_server"],
            "smtp_port": server_config["smtp_port"],
            "email": args.email,
            "password": args.password,
            "name": args.name or args.email.split("@")[0],
            "preset": args.preset or "custom"
        }

        # 测试连接
        print("Testing email connection...")
        success, errors = test_connection(config)
        if not success:
            print("\n[FAIL] Email connection test failed, config not saved")
            print("Error details:")
            for err in errors:
                print(f"  - {err}")
            print("\nSuggestions:")
            print("  1. Check if email address and password are correct")
            print("  2. Gmail/QQ mail etc. need to use app-specific password")
            print("  3. Verify server address and port are correct")
            return

        # 保存配置
        save_config(config)
        print(f"\n[SUCCESS] Email configured: {config['email']}")
        print(f"   Config file: {CONFIG_FILE}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
