# adversarial-review — 多视角对抗式代码审查

整合 6 个审查视角（安全、性能、架构、代码质量、测试质量、API 设计），统一发现格式，健康评分系统，迭代修复循环。

## 安装

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/adversarial-review
```

## 使用

```
/adversarial-review                          # 快速模式：6 视角依次审查
/adversarial-review --deep                   # 深度模式：详细分析 + 修复建议
/adversarial-review --fix                    # 修复模式：自动修复 + 验证
/adversarial-review src/api                  # 指定路径
/adversarial-review --perspective security   # 单视角
```

## 6 个审查视角

| 视角 | 检查内容 |
|------|----------|
| Security | OWASP Top 10、密钥泄露、注入、认证缺陷 |
| Performance | O(n) 分析、内存分配、热路径、N+1 查询 |
| Architecture | 变更传播、知识重复、依赖混乱、领域模型失真 |
| Code Quality | 命名、可读性、错误处理、静默失败 |
| Test Quality | 行为覆盖率、Mock 滥用、测试脆弱性 |
| API Design | 向后兼容、类型安全、不变量表达 |

## 健康评分

0-100 分，按严重程度加权（Critical -15, Warning -5, Suggestion -1）。

## team-coord 集成

当与 team-coord 共存时，lead 可 spawn 6 个 reviewer worker 并行审查。参见 `references/team-coord-guide.md`。

## License

MIT
