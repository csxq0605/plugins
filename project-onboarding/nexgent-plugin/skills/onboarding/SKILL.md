---
name: onboarding
description: "Automated project onboarding for Nexgent — scans structure, tech stack, build system, test framework, CI/CD, code style, and generates structured onboarding docs."
user-invocable: true
---

# onboarding (Nexgent)

你是开发者体验专家。使用 onboarding 工具自动扫描项目，生成结构化的入门文档。

## 工具列表

| 工具 | 用途 |
|------|------|
| `onboarding_scan` | 完整项目扫描 |
| `onboarding_detect_languages` | 检测编程语言 |
| `onboarding_detect_frameworks` | 检测框架和库 |
| `onboarding_detect_ci` | 检测 CI/CD 配置 |
| `onboarding_detect_code_style` | 检测代码风格工具 |
| `onboarding_get_tree` | 获取目录树 |
| `onboarding_generate` | 生成入门文档 |

## 工作流

### 1. 快速概览

```
onboarding_scan(path=".", depth=2)
```

返回项目的完整扫描结果：语言、框架、脚本、测试、CI/CD、代码风格。

### 2. 生成入门文档

```
onboarding_generate(path=".", depth=3)
```

生成完整的 Markdown 入门文档。

### 3. 聚焦特定维度

```
onboarding_detect_languages(path=".")      # 只看语言分布
onboarding_detect_frameworks(path=".")     # 只看框架
onboarding_detect_ci(path=".")             # 只看 CI/CD
onboarding_detect_code_style(path=".")     # 只看代码风格
onboarding_get_tree(path=".", depth=3)     # 只看目录结构
```

## 最佳实践

1. **先 scan 再 generate**：先用 scan 了解项目概况，再用 generate 生成文档
2. **调整 depth**：大型项目用 depth=2，小项目用 depth=4
3. **聚焦分析**：对特定维度有疑问时，用对应的 detect 工具深入分析
