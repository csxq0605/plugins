# dep-audit — 依赖漏洞审计

扫描项目依赖文件，查询 OSV 漏洞数据库，检测已知 CVE，给出修复命令和健康评分。

## 安装

### Claude Code

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/dep-audit/claude-code-plugin
```

### Nexgent

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/dep-audit/nexgent-plugin
```

## 使用

```
/audit                                   # 完整审计
/audit --quick                           # 快速扫描（只检查直接依赖）
/audit --focus vulnerabilities          # 聚焦漏洞
/audit --focus outdated                 # 聚焦过期依赖
/audit --focus licenses                 # 聚焦许可证
/audit --severity critical              # 只报告 Critical
```

## 核心能力

| 能力 | 说明 |
|------|------|
| 依赖解析 | 解析 package.json, requirements.txt, pyproject.toml, Cargo.toml, go.mod |
| 漏洞查询 | 查询 OSV (Open Source Vulnerability) 数据库，覆盖 npm/PyPI/crates.io/Go/Maven |
| 修复建议 | 给出具体的升级命令（`npm install pkg@version`） |
| 健康评分 | 100 - (Critical×25 + High×10 + Medium×3 + Low×1) |

## 漏洞严重程度

| 等级 | 权重 | 典型漏洞 |
|------|------|----------|
| Critical (×25) | 远程代码执行、SQL 注入、认证绕过 |
| High (×10) | XSS、路径遍历、SSRF、权限提升 |
| Medium (×3) | CSRF、信息泄露、DoS |
| Low (×1) | 缺少安全头、弱加密 |

## team-coord 集成

Lead 可分配 worker 按生态系统并行查询漏洞。参见 `references/team-coord-guide.md`。

## License

MIT
