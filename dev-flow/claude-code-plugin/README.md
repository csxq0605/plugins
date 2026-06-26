# dev-flow — Claude Code 插件

一站式开发工作流。一个插件覆盖：项目入门 → 依赖审计 → 代码审查（6 视角）→ 变更日志 → 架构决策记录 → 跨会话记忆。

## 安装

```bash
claude install-plugin github:csxq0605/plugins
```

## 使用

```
/dev-flow                                # 显示项目状态和下一步建议
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

## License

MIT
