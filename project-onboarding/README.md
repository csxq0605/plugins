# project-onboarding — 项目自动入门

自动扫描项目结构、技术栈、构建系统、测试框架、CI/CD、代码风格，生成结构化的入门文档。让新开发者 5 分钟了解项目全貌。

## 安装

### Claude Code

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/project-onboarding/claude-code-plugin
```

### Nexgent

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/project-onboarding/nexgent-plugin
```

## 使用

```
/onboarding                              # 完整扫描
/onboarding --quick                      # 快速概览
/onboarding --focus tech-stack           # 聚焦技术栈
/onboarding --focus build                # 聚焦构建系统
/onboarding --focus test                 # 聚焦测试
/onboarding --focus ci                   # 聚焦 CI/CD
/onboarding --focus code-style           # 聚焦代码风格
```

## 7 个检测维度

| 维度 | 检测内容 |
|------|----------|
| 项目身份 | 名称、描述、主语言、包管理器 |
| 目录结构 | 源码/测试/配置目录，文件数量统计 |
| 技术栈 | 框架、ORM、状态管理、UI 库（按语言分组） |
| 构建系统 | npm scripts、Makefile、Docker、环境变量 |
| 测试框架 | Jest/Vitest/pytest/Playwright 等，测试目录 |
| CI/CD | GitHub Actions/GitLab CI/CircleCI 等流水线 |
| 代码风格 | Linter、Formatter、Git hooks、提交规范 |

## 支持的语言/框架

JavaScript, TypeScript, Python, Rust, Go, Java, Kotlin, Ruby, PHP, C/C++, C#, Swift, Dart, Elixir, Haskell, Scala, Clojure...

## team-coord 集成

Lead 可分配 3 个 worker 并行扫描不同维度。参见 `references/team-coord-guide.md`。

## License

MIT
