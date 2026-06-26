# session-memory (Nexgent Plugin)

跨会话持久化记忆 — 9 个 Python 工具，管理会话、决策、发现和交接文档。

## 安装

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/session-memory/nexgent-plugin
```

## 工具列表

| 工具 | 用途 |
|------|------|
| `memory_save_session` | 保存会话摘要 |
| `memory_save_decision` | 保存决策记录 |
| `memory_save_finding` | 保存发现/洞察 |
| `memory_save_handoff` | 保存交接文档 |
| `memory_recall` | 搜索和回忆记忆 |
| `memory_list` | 列出所有记忆 |
| `memory_delete` | 删除记忆 |
| `memory_cleanup` | 清理过期记忆 |
| `memory_generate_handoff` | 生成交接文档 |

## 测试

```bash
cd session-memory/nexgent-plugin
python -c "
from memory_tools import call_tool
import tempfile, shutil
tmpdir = tempfile.mkdtemp()
call_tool('memory_save_session', {'path': tmpdir, 'summary': 'test', 'tags': ['test']})
result = call_tool('memory_list', {'path': tmpdir})
print(f'Memories: {len(result)}')
shutil.rmtree(tmpdir)
"
```

## 依赖

无外部依赖。纯 Python 标准库实现。

## License

MIT
