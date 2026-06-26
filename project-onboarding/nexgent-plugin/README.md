# project-onboarding (Nexgent Plugin)

项目自动入门 — 7 个 Python 工具，自动扫描项目结构和配置。

## 安装

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/project-onboarding/nexgent-plugin
```

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

## 测试

```bash
cd project-onboarding/nexgent-plugin
python -c "
from onboarding_tools import call_tool
result = call_tool('onboarding_scan', {'path': '.', 'depth': 2})
print(f'Languages: {result[\"languages\"]}')
print(f'Frameworks: {len(result[\"frameworks\"])}')
"
```

## 依赖

无外部依赖。纯 Python 标准库实现。

## License

MIT
