# Outreach Plugin for Codex

学术套磁全流程自动化 Codex 插件：材料解析、教授调研、可视化报告、个性化邮件生成、邮件收发。

## 安装

### Codex App

在 Codex App 的插件市场页面添加 GitHub marketplace，不需要 clone 本仓库，也不需要填写本地路径：

```text
Marketplace source: csxq0605/plugins
Ref: master
Sparse paths:
  .agents
  outreach/codex-plugin
```

添加后安装插件：

```text
Marketplace: csxq0605-plugins
Plugin: outreach
```

安装完成后，重新开启一个 Codex 对话以加载 `outreach` skill。

### 命令行等价方式

```bash
codex plugin marketplace add csxq0605/plugins --ref master --sparse .agents --sparse outreach/codex-plugin
codex plugin add outreach@csxq0605-plugins
```

Windows PowerShell 若因执行策略拦截 `codex.ps1`，可使用 `codex.cmd`：

```bash
codex.cmd plugin marketplace add csxq0605/plugins --ref master --sparse .agents --sparse outreach/codex-plugin
codex.cmd plugin add outreach@csxq0605-plugins
```

## 使用

Codex 中直接用自然语言触发即可：

```text
用 outreach 配置邮箱
用 outreach 解析我的 CV
用 outreach 调研 MIT CS 的 AI 方向教授
用 outreach 生成 MIT CS 的 HTML 报告
用 outreach 为 MIT CS 的教授生成套磁邮件
用 outreach 发送邮件给 MIT CS Professor_Name
```

## 脚本

- `scripts/pipeline.py`：调研自动化
- `scripts/email_setup.py`：邮箱配置
- `scripts/email_send.py`：邮件发送
- `scripts/email_batch.py`：批量发送
- `scripts/email_list.py`：邮件查看

脚本运行时请始终传 `--path <项目根目录>`，让任务数据写入用户项目下的 `.outreach/`。

## 数据位置

- 邮箱配置：`~/.outreach/email_config.json`
- 项目数据：`<项目根目录>/.outreach/`
- 发送日志：`<项目根目录>/.outreach/logs/`

## License

MIT
