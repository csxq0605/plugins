# Workflow Detail

## Onboard 阶段详情

### 扫描维度

| 维度 | 检测内容 | 工具 |
|------|----------|------|
| 项目身份 | 名称、描述、主语言 | package.json, README |
| 目录结构 | 源码/测试/配置目录 | find, ls |
| 技术栈 | 框架、ORM、状态管理 | package.json, requirements.txt |
| 构建系统 | npm scripts, Makefile, Docker | 配置文件检测 |
| 测试框架 | Jest, pytest, Playwright | 依赖检测 |
| CI/CD | GitHub Actions, GitLab CI | .github/workflows/ |
| 代码风格 | ESLint, Prettier, Ruff | 配置文件检测 |

### 支持的语言

JavaScript, TypeScript, Python, Rust, Go, Java, Kotlin, Ruby, PHP, C/C++, C#, Swift, Dart, Elixir, Haskell, Scala

## Audit 阶段详情

### 支持的生态系统

| 依赖文件 | 生态系统 |
|----------|----------|
| package.json | npm |
| requirements.txt / pyproject.toml | PyPI |
| Cargo.toml | crates.io |
| go.mod | Go |
| Gemfile | RubyGems |
| composer.json | Packagist |
| pom.xml / build.gradle | Maven |

### 漏洞严重程度

| 等级 | 权重 | 典型漏洞 |
|------|------|----------|
| Critical (×25) | RCE, SQLi, 认证绕过 |
| High (×10) | XSS, SSRF, 权限提升 |
| Medium (×3) | CSRF, 信息泄露 |
| Low (×1) | 缺少安全头, 弱加密 |

### 健康评分

```
score = 100 - (Critical×25 + High×10 + Medium×3 + Low×1)
```

## Review 阶段详情

### 6 视角检查清单

见 `review-checklist.md`

### 发现格式

```json
{
  "id": "SEC-001",
  "perspective": "security",
  "severity": "critical",
  "title": "SQL Injection",
  "file": "src/db.py",
  "line": 42,
  "evidence": "query = f'SELECT * FROM users WHERE id={uid}'",
  "risk": "Arbitrary SQL execution",
  "fix": "Use parameterized queries",
  "confidence": 95,
  "ref": "CWE-89"
}
```

### 健康评分

```
score = 100 - (Critical×15 + Warning×5 + Suggestion×1)
```

## Changelog 阶段详情

### Conventional Commits

```
type(scope): description

feat(auth): add login page
fix(api): handle timeout
feat!: redesign response format
```

### Semver 规则

- Breaking change → major
- feat → minor
- fix/perf → patch

### 输出格式

Keep a Changelog 格式：
```markdown
## [version] - date

### Added
- feat(auth): add login page

### Fixed
- fix(api): handle timeout
```

## ADR 阶段详情

### MADR 模板

```markdown
# NNNN. Title

## Status
Accepted

## Context
背景描述

## Decision
决策内容

## Consequences
正面/负面后果
```

### 状态流转

```
Proposed → Accepted → Deprecated
         → Superseded by ADR-XXXX
```

## Memory 阶段详情

### 记忆类型

| 类型 | 用途 | 过期 |
|------|------|------|
| session | 会话摘要 | 30天 |
| decision | 架构决策 | 永不 |
| finding | 发现/洞察 | 90天 |
| handoff | 交接文档 | 7天 |
