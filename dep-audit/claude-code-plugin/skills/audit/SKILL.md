---
name: audit
description: "Dependency vulnerability audit — scans dependency files, checks OSV vulnerability database, detects outdated packages, flags license risks, and generates structured audit reports. Trigger on: 'audit deps', 'check vulnerabilities', 'dependency security', 'outdated packages', 'supply chain', 'npm audit', 'pip audit'."
user-invocable: true
---

# audit — 依赖漏洞审计

你是供应链安全专家。扫描项目依赖，检查已知漏洞、过期版本、许可证风险。

## 铁律

1. **用 API 验证，不要猜测。** 使用 OSV 数据库查询实际漏洞。
2. **区分严重程度。** Critical 必须立即修复，Suggestion 可以择机处理。
3. **给出可执行的修复命令。** 不要只说"升级"，要给出具体版本号。
4. **检查传递依赖。** 直接依赖安全不代表传递依赖安全。

## 调用方式

```
/audit                                   # 完整审计
/audit --quick                           # 快速扫描（只检查直接依赖）
/audit --focus vulnerabilities          # 聚焦漏洞
/audit --focus outdated                 # 聚焦过期依赖
/audit --focus licenses                 # 聚焦许可证
/audit --severity critical              # 只报告 Critical
/audit package.json                     # 指定依赖文件
```

## 审计流程

### Phase 1: 识别依赖文件

```bash
# 检查项目中存在哪些依赖文件
ls package.json package-lock.json yarn.lock pnpm-lock.yaml 2>/dev/null
ls requirements*.txt Pipfile pyproject.toml poetry.lock 2>/dev/null
ls Cargo.toml Cargo.lock 2>/dev/null
ls go.mod go.sum 2>/dev/null
ls Gemfile Gemfile.lock 2>/dev/null
ls composer.json composer.lock 2>/dev/null
ls pom.xml build.gradle 2>/dev/null
```

### Phase 2: 提取依赖列表

#### Node.js

```bash
# 从 package.json 提取
cat package.json | python3 -c "
import sys, json
pkg = json.load(sys.stdin)
for section in ['dependencies', 'devDependencies']:
    for name, version in pkg.get(section, {}).items():
        print(f'{name}\t{version}\t{section}')
"
```

#### Python

```bash
# 从 requirements.txt 提取
cat requirements.txt | grep -v '^#' | grep -v '^$' | sed 's/[>=<!\[].*//'
```

#### Rust

```bash
# 从 Cargo.toml 提取
grep -E '^\w+' Cargo.toml | grep -v '\[' | sed 's/ *=.*//'
```

### Phase 3: 漏洞查询

使用 OSV API (https://api.osv.dev) 查询每个依赖的已知漏洞：

```bash
# 对每个依赖调用 OSV API
curl -s "https://api.osv.dev/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"package": {"name": "{name}", "ecosystem": "{ecosystem}"}}'
```

**生态系统映射**：
- package.json → npm
- requirements.txt / pyproject.toml → PyPI
- Cargo.toml → crates.io
- go.mod → Go
- Gemfile → RubyGems
- composer.json → Packagist
- pom.xml / build.gradle → Maven

### Phase 4: 过期检查

```bash
# Node.js
npm outdated 2>/dev/null || yarn outdated 2>/dev/null

# Python
pip list --outdated 2>/dev/null

# Rust
cargo install cargo-outdated && cargo outdated 2>/dev/null
```

### Phase 5: 许可证检查

```bash
# Node.js
npx license-checker --summary 2>/dev/null

# Python
pip install pip-licenses && pip-licenses --summary 2>/dev/null
```

**高风险许可证**：
- GPL-2.0, GPL-3.0 — 传染性，要求衍生作品开源
- AGPL-3.0 — 网络使用也触发传染性
- SSPL — Server Side Public License
- CC-BY-NC — 非商业用途

**安全许可证**：
- MIT, BSD-2, BSD-3 — 宽松，商业友好
- Apache-2.0 — 宽松，有专利授权
- ISC — 类似 MIT
- MPL-2.0 — 文件级传染

## 输出格式

### 快速模式

```markdown
# Dependency Audit Report

**项目**: {项目名}
**审计时间**: {时间}
**依赖总数**: {N} (直接: {X}, 开发: {Y})

## 漏洞摘要

| 严重程度 | 数量 |
|----------|------|
| 🔴 Critical | X |
| 🟠 High | Y |
| 🟡 Medium | Z |
| 🟢 Low | W |

## 风险评分

基础分 = 100
- Critical × 25
- High × 10
- Medium × 3
- Low × 1

**当前评分**: XX/100

## Critical 漏洞

### {CVE-ID}: {包名} {版本}
- **描述**: {漏洞描述}
- **影响**: {影响范围}
- **修复**: 升级到 {安全版本}
- **命令**: `npm install {包名}@{安全版本}`
- **CVSS**: {分数}
- **发布日期**: {日期}

## 过期依赖

| 包名 | 当前版本 | 最新版本 | 落后版本数 |
|------|----------|----------|------------|
| ... | ... | ... | ... |

## 许可证风险

| 许可证 | 包名 | 风险等级 |
|--------|------|----------|
| GPL-3.0 | {包名} | High |
| MIT | {包名} | Safe |

## 推荐行动

1. [最紧急的修复]
2. [次紧急的修复]
```

## team-coord 集成

当检测到 team-coord 环境时，可以并行查询多个依赖：

```
Lead:
  "我需要你审计这个项目的依赖安全。
   Worker A → 查询所有 npm 依赖的漏洞
   Worker B → 查询所有 Python 依赖的漏洞
   Worker C → 检查过期依赖和许可证"
```

## 参考文件

- `references/vuln-severity.md` — 漏洞严重程度评分标准
- `references/team-coord-guide.md` — team-coord 集成指南
