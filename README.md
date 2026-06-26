# plugins

Claude Code & Nexgent 插件集合。

## 插件列表

| 插件 | 平台 | 说明 |
|------|------|------|
| [team-coord](./multi-agent/) | Claude Code, Nexgent | 多 agent 团队协调——lead/teammate 角色分离、inbox sync 协议、WHAT vs HOW 原则 |

## 安装

### Claude Code

```bash
# 添加 marketplace（一次性）
/plugin marketplace add csxq0605/plugins

# 安装 team-coord
/plugin install team-coord@plugins
```

### Nexgent

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/multi-agent/nexgent-plugin
```

## License

MIT
