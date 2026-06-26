# Superpowers Workflow — project-onboarding 集成

当用户要求使用 superpowers 工作流时，project-onboarding 在以下阶段被调用：

## Step 0: 项目文档布局 阶段

在开始任何开发前，使用 project-onboarding 扫描现有项目，生成结构化的项目概览。

### 调用方式

```
# 完整扫描
onboarding_scan(path=".", depth=3)

# 生成入门文档
onboarding_generate(path=".", depth=3)

# 聚焦特定维度
onboarding_detect_frameworks(path=".")
onboarding_detect_ci(path=".")
onboarding_detect_code_style(path=".")
```

### 输出用途

扫描结果直接用于：
- **overview.md** — 系统架构概览、技术栈
- **vision.md** — 项目背景（如果已有项目）
- **specs** — 影响设计约束的技术栈信息

### 与 team-coord 集成

Lead 可分配 3 个 worker 并行扫描：
- Worker A → 目录结构 + 技术栈
- Worker B → 构建系统 + 测试框架
- Worker C → CI/CD + 代码风格

Lead 合并结果生成完整的项目概览文档。
