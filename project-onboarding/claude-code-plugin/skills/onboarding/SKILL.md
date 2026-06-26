---
name: onboarding
description: "Automated project onboarding — scans structure, tech stack, build system, test framework, CI/CD, code style, and generates structured onboarding docs. Trigger on: 'onboard me', 'project overview', 'how to start', 'project structure', 'tech stack', 'getting started', 'new to this project'."
user-invocable: true
---

# onboarding — 项目自动入门

你是开发者体验专家。自动扫描项目，生成结构化的入门文档，让新开发者 5 分钟内了解项目全貌。

## 铁律

1. **先扫描，后总结。** 不要猜测，用工具验证。
2. **按优先级排序。** 新开发者最需要知道：怎么跑起来、怎么测试、代码在哪里。
3. **给出可执行的命令。** 不要只说"用 npm"，要给出具体的 `npm install && npm run dev`。
4. **识别非显而易见的约定。** 项目特有的命名规则、目录约定、提交规范。

## 调用方式

```
/onboarding                              # 完整扫描
/onboarding --quick                      # 快速概览（30 秒）
/onboarding --focus tech-stack           # 聚焦技术栈
/onboarding --focus build                # 聚焦构建系统
/onboarding --focus test                 # 聚焦测试
/onboarding --focus ci                   # 聚焦 CI/CD
/onboarding --focus code-style           # 聚焦代码风格
/onboarding --format markdown            # 输出 Markdown
/onboarding --format json                # 输出 JSON
```

## 扫描流程

### Phase 1: 项目身份（10 秒）

```bash
# 1. 根目录文件
ls -la .                     # 隐藏文件、配置文件

# 2. 读取关键标识文件（按存在性检查）
cat package.json 2>/dev/null     # Node.js
cat Cargo.toml 2>/dev/null       # Rust
cat pyproject.toml 2>/dev/null   # Python (modern)
cat setup.py 2>/dev/null         # Python (legacy)
cat go.mod 2>/dev/null           # Go
cat pom.xml 2>/dev/null          # Java (Maven)
cat build.gradle 2>/dev/null     # Java (Gradle)
cat Gemfile 2>/dev/null          # Ruby
cat composer.json 2>/dev/null    # PHP
cat CMakeLists.txt 2>/dev/null   # C/C++
cat Makefile 2>/dev/null         # Make-based

# 3. README
cat README.md 2>/dev/null || cat README.rst 2>/dev/null || cat README 2>/dev/null
```

**输出**：
- 项目名称
- 一句话描述
- 主要语言
- 包管理器

### Phase 2: 目录结构（10 秒）

```bash
# 1. 顶层目录（排除依赖目录）
find . -maxdepth 1 -type d \
  ! -name node_modules ! -name .git ! -name __pycache__ \
  ! -name target ! -name .venv ! -name venv ! -name dist \
  ! -name build ! -name .next ! -name .nuxt | sort

# 2. 源代码目录识别
# 常见模式：src/, lib/, app/, pkg/, cmd/, internal/
ls -d src/ lib/ app/ pkg/ cmd/ internal/ 2>/dev/null

# 3. 关键配置目录
ls -d .github/ .gitlab-ci.d/ .circleci/ configs/ deploy/ k8s/ docker/ 2>/dev/null

# 4. 文件数量统计
find . -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" 2>/dev/null | grep -v node_modules | wc -l
find . -name "*.py" 2>/dev/null | grep -v __pycache__ | grep -v .venv | wc -l
find . -name "*.rs" 2>/dev/null | grep -v target | wc -l
find . -name "*.go" 2>/dev/null | wc -l
find . -name "*.java" 2>/dev/null | grep -v target | wc -l
```

**输出**：
- 目录树（深度 2-3 层）
- 各语言文件数量
- 源码/测试/配置目录标注

### Phase 3: 技术栈检测（20 秒）

按语言分组检测框架和库：

#### Node.js / TypeScript

```bash
# 框架检测
grep -q '"react"' package.json && echo "React"
grep -q '"vue"' package.json && echo "Vue"
grep -q '"@angular/core"' package.json && echo "Angular"
grep -q '"svelte"' package.json && echo "Svelte"
grep -q '"next"' package.json && echo "Next.js"
grep -q '"nuxt"' package.json && echo "Nuxt"
grep -q '"express"' package.json && echo "Express"
grep -q '"fastify"' package.json && echo "Fastify"
grep -q '"nestjs"' package.json && echo "NestJS"
grep -q '"hono"' package.json && echo "Hono"

# TypeScript
grep -q '"typescript"' package.json && echo "TypeScript"
[ -f tsconfig.json ] && echo "TypeScript (tsconfig found)"

# ORM
grep -q '"prisma"' package.json && echo "Prisma"
grep -q '"drizzle-orm"' package.json && echo "Drizzle"
grep -q '"typeorm"' package.json && echo "TypeORM"
grep -q '"sequelize"' package.json && echo "Sequelize"

# 状态管理
grep -q '"zustand"' package.json && echo "Zustand"
grep -q '"jotai"' package.json && echo "Jotai"
grep -q '"@reduxjs/toolkit"' package.json && echo "Redux Toolkit"
grep -q '"pinia"' package.json && echo "Pinia"
grep -q '"vuex"' package.json && echo "Vuex"
```

#### Python

```bash
# 框架检测
grep -q 'django' requirements*.txt 2>/dev/null && echo "Django"
grep -q 'flask' requirements*.txt 2>/dev/null && echo "Flask"
grep -q 'fastapi' requirements*.txt 2>/dev/null && echo "FastAPI"
grep -q 'torch' requirements*.txt 2>/dev/null && echo "PyTorch"
grep -q 'tensorflow' requirements*.txt 2>/dev/null && echo "TensorFlow"
grep -q 'transformers' requirements*.txt 2>/dev/null && echo "Hugging Face Transformers"

# pyproject.toml 检测
grep -A5 '\[tool.poetry\]' pyproject.toml 2>/dev/null && echo "Poetry"
grep -A5 '\[build-system\]' pyproject.toml 2>/dev/null
```

#### Rust

```bash
# 框架检测
grep -q 'actix-web' Cargo.toml 2>/dev/null && echo "Actix Web"
grep -q 'axum' Cargo.toml 2>/dev/null && echo "Axum"
grep -q 'tokio' Cargo.toml 2>/dev/null && echo "Tokio"
grep -q 'serde' Cargo.toml 2>/dev/null && echo "Serde"
grep -q 'clap' Cargo.toml 2>/dev/null && echo "Clap (CLI)"
grep -q 'tauri' Cargo.toml 2>/dev/null && echo "Tauri"
```

**输出**：
- 框架列表（带版本）
- 关键依赖分类（框架、ORM、状态管理、UI 库、工具链）

### Phase 4: 构建和运行（10 秒）

```bash
# 1. 脚本命令
cat package.json | python3 -c "import sys,json; d=json.load(sys.stdin); [print(f'  {k}: {v}') for k,v in d.get('scripts',{}).items()]" 2>/dev/null

# 2. Makefile 目标
grep -E '^[a-zA-Z_-]+:' Makefile 2>/dev/null | head -20

# 3. Docker
cat Dockerfile 2>/dev/null | head -5
cat docker-compose.yml 2>/dev/null | head -20

# 4. 环境变量
cat .env.example 2>/dev/null || cat .env.template 2>/dev/null
```

**输出**：
- 核心命令（install, dev, build, test, lint）
- Docker 支持情况
- 必需的环境变量

### Phase 5: 测试框架（10 秒）

```bash
# Node.js 测试
grep -q '"jest"' package.json && echo "Jest"
grep -q '"vitest"' package.json && echo "Vitest"
grep -q '"mocha"' package.json && echo "Mocha"
grep -q '"@playwright/test"' package.json && echo "Playwright"
grep -q '"cypress"' package.json && echo "Cypress"

# Python 测试
grep -q 'pytest' requirements*.txt 2>/dev/null && echo "pytest"
grep -q 'unittest' requirements*.txt 2>/dev/null && echo "unittest"

# Rust 测试
grep -q '\[dev-dependencies\]' Cargo.toml 2>/dev/null && echo "Rust built-in test"

# 测试目录
ls -d tests/ test/ __tests__/ spec/ e2e/ cypress/ 2>/dev/null

# 覆盖率配置
[ -f .nycrc ] || [ -f jest.config.js ] || [ -f vitest.config.ts ] && echo "Coverage configured"
```

**输出**：
- 测试框架
- 测试目录位置
- 运行测试的命令
- E2E 测试情况

### Phase 6: CI/CD（10 秒）

```bash
# GitHub Actions
ls .github/workflows/*.yml 2>/dev/null
cat .github/workflows/*.yml 2>/dev/null | grep -E '^\s*name:|jobs:|steps:' | head -20

# GitLab CI
cat .gitlab-ci.yml 2>/dev/null | head -20

# CircleCI
cat .circleci/config.yml 2>/dev/null | head -20

# 其他 CI
cat Jenkinsfile 2>/dev/null | head -10
cat .travis.yml 2>/dev/null | head -10
```

**输出**：
- CI 平台
- 流水线阶段
- 自动化检查（lint, test, build, deploy）

### Phase 7: 代码风格（10 秒）

```bash
# Linter
[ -f .eslintrc.js ] || [ -f .eslintrc.json ] || [ -f eslint.config.js ] && echo "ESLint"
[ -f .prettierrc ] || [ -f prettier.config.js ] && echo "Prettier"
[ -f .flake8 ] || [ -f setup.cfg ] && echo "flake8"
[ -f pyproject.toml ] && grep -q '\[tool.ruff\]' pyproject.toml && echo "Ruff"
[ -f rustfmt.toml ] && echo "rustfmt"
[ -f .clang-format ] && echo "clang-format"

# EditorConfig
[ -f .editorconfig ] && echo "EditorConfig"

# Git hooks
[ -f .husky/pre-commit ] && echo "Husky pre-commit"
[ -f .pre-commit-config.yaml ] && echo "pre-commit"

# 提交规范
grep -q '"commitlint"' package.json && echo "Commitlint"
[ -f commitlint.config.js ] && echo "Commitlint"
grep -q '"standard-version"' package.json && echo "Standard Version"
grep -q '"semantic-release"' package.json && echo "Semantic Release"
```

**输出**：
- Linter 和 formatter
- Git hooks
- 提交规范
- 代码风格指南链接

## 输出格式

### 快速模式

```markdown
# Project Onboarding: {项目名}

## 一句话
{从 README 提取或自己总结}

## 快速开始
```bash
git clone {repo_url}
cd {project}
{install_command}
{dev_command}
```

## 技术栈
- **语言**: {language} {version}
- **框架**: {framework} {version}
- **包管理**: {package_manager}
- **测试**: {test_framework}

## 关键命令
| 命令 | 用途 |
|------|------|
| `{install}` | 安装依赖 |
| `{dev}` | 启动开发服务器 |
| `{build}` | 构建生产版本 |
| `{test}` | 运行测试 |
| `{lint}` | 代码检查 |

## 目录结构
```
{关键目录树}
```
```

### 完整模式

在快速模式基础上，增加：

```markdown
## 技术栈详情

### 框架和库
| 分类 | 名称 | 版本 | 用途 |
|------|------|------|------|
| ... | ... | ... | ... |

### 配置文件
| 文件 | 用途 |
|------|------|
| tsconfig.json | TypeScript 配置 |
| ... | ... |

## 构建系统

### 开发环境要求
- Node.js >= 18
- Python >= 3.10
- Docker (可选)

### 环境变量
| 变量 | 必需 | 说明 |
|------|------|------|
| DATABASE_URL | ✅ | 数据库连接 |
| ... | ... | ... |

## 测试

### 测试结构
```
tests/
├── unit/          # 单元测试
├── integration/   # 集成测试
└── e2e/           # 端到端测试
```

### 运行测试
```bash
{test_command}              # 所有测试
{test_command} --watch      # 监听模式
{test_command} --coverage   # 覆盖率
```

## CI/CD

### 流水线
{CI 配置摘要}

### 自动化检查
- ✅ Lint on commit
- ✅ Test on PR
- ✅ Build on merge
- ✅ Deploy on tag

## 代码风格

### 格式化
- {formatter} — 自动格式化
- {linter} — 代码检查

### Git 约定
- 分支命名: {branch_convention}
- 提交格式: {commit_format}
- PR 模板: {pr_template_path}

## 架构概览

{从代码结构推断的架构模式}

### 关键模块
| 模块 | 职责 | 入口文件 |
|------|------|----------|
| ... | ... | ... |

## 常见问题

### Q: {常见问题 1}
A: {答案}

### Q: {常见问题 2}
A: {答案}
```

## team-coord 集成

当检测到 team-coord 环境时，可以并行扫描不同维度：

```
# Lead 分配
Worker A → Phase 2-3 (目录结构 + 技术栈)
Worker B → Phase 4-5 (构建 + 测试)
Worker C → Phase 6-7 (CI/CD + 代码风格)
```

## 参考文件

- `references/detection-patterns.md` — 详细的检测模式列表
- `references/team-coord-guide.md` — team-coord 集成指南
