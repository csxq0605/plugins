# dev-flow (Nexgent Plugin)

一站式开发工作流 — 6 个核心工具覆盖开发全生命周期。

## 安装

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/dev-flow/nexgent-plugin
```

## 工具列表

| 工具 | 用途 |
|------|------|
| `devflow_onboard` | 项目入门扫描（技术栈、构建系统、测试框架、CI/CD） |
| `devflow_audit` | 依赖安全审计（OSV 漏洞查询、过期检测、许可证检查） |
| `devflow_review` | 代码审查（6 视角：安全、性能、架构、质量、测试、API） |
| `devflow_changelog` | 变更日志生成（conventional commits 解析、semver 建议） |
| `devflow_adr` | 架构决策记录（MADR/Y-Statement 模板、状态管理） |
| `devflow_memory` | 跨会话记忆（保存/恢复/搜索/交接） |

## 测试

```bash
cd dev-flow/nexgent-plugin
python -m pytest tests/ -v
```

## License

MIT
