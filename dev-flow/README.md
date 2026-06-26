# dev-flow

一站式开发工作流插件。一个插件覆盖开发全生命周期：项目入门 → 依赖审计 → 代码审查 → 变更日志 → 决策记录 → 跨会话记忆。

## 为什么是 1 个插件而不是 6 个？

真实开发场景是：一个 PR 流程里你需要 audit + review + changelog + ADR，不是一个一个手动调。碎片化插件创造的是伪需求，不是真实价值。

## 安装

### Claude Code

```bash
claude install-plugin github:csxq0605/plugins
```

### Nexgent

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/dev-flow/nexgent-plugin
```

## 使用

```
/dev-flow                                # 显示当前项目状态和下一步建议
/dev-flow onboard                        # 项目入门扫描
/dev-flow audit                          # 依赖安全审计
/dev-flow review                         # 代码审查（6 视角）
/dev-flow review --fix                   # 代码审查 + 自动修复
/dev-flow changelog                      # 生成变更日志
/dev-flow changelog --suggest-bump       # 建议版本号
/dev-flow adr                            # 记录架构决策
/dev-flow adr list                       # 列出所有决策
/dev-flow recall                         # 查看记忆
/dev-flow recall --query "auth"          # 搜索记忆
/dev-flow save                           # 保存当前工作状态
/dev-flow resume                         # 恢复上次工作状态
```

## 工作流阶段

| 阶段 | 功能 | 输出 |
|------|------|------|
| Onboard | 项目扫描 | 项目概览 + 可执行命令 |
| Audit | 依赖安全 | 漏洞报告 + 修复命令 |
| Develop | 开发中 | 决策记录 + 发现保存 |
| Review | 代码审查 | 健康评分 + 分级发现 |
| Changelog | 发布准备 | CHANGELOG.md + 版本建议 |
| Remember | 记忆持久化 | 跨会话上下文 |

## 存储

所有数据存储在 `.dev-flow/` 目录：

```
.dev-flow/
├── config.json
├── sessions/
├── decisions/
├── findings/
├── handoffs/
└── index.json
```

## License

MIT
