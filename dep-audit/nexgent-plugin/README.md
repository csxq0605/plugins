# dep-audit (Nexgent Plugin)

依赖漏洞审计 — 4 个 Python 工具，自动解析依赖文件并查询 OSV 漏洞数据库。

## 安装

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/dep-audit/nexgent-plugin
```

## 工具列表

| 工具 | 用途 |
|------|------|
| `audit_scan_deps` | 扫描所有依赖 |
| `audit_check_vulns` | 查询 OSV 漏洞数据库 |
| `audit_full` | 完整审计（扫描 + 漏洞 + 修复建议） |
| `audit_generate_report` | 生成 Markdown 审计报告 |

## 支持的生态系统

| 依赖文件 | 生态系统 |
|----------|----------|
| package.json | npm |
| requirements.txt / pyproject.toml | PyPI |
| Cargo.toml | crates.io |
| go.mod | Go |
| Gemfile | RubyGems |
| composer.json | Packagist |
| pom.xml / build.gradle | Maven |

## 测试

```bash
cd dep-audit/nexgent-plugin
python -c "
from audit_tools import call_tool
# 测试 OSV API
result = call_tool('audit_check_vulns', {'path': '.'})
print(f'Vulnerabilities: {len(result.get(\"vulnerabilities\", []))}')
"
```

## 依赖

无外部依赖。使用 Python 标准库调用 OSV API。

## License

MIT
