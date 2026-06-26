# adr-generator (Nexgent Plugin)

架构决策记录生成器 — 6 个 Python 工具，创建、管理和索引 ADR。

## 安装

```bash
/plugin install https://github.com/csxq0605/plugins/tree/master/adr-generator/nexgent-plugin
```

## 工具列表

| 工具 | 用途 |
|------|------|
| `adr_create` | 创建新 ADR |
| `adr_list` | 列出所有 ADR |
| `adr_show` | 查看 ADR 详情 |
| `adr_update_status` | 更新 ADR 状态 |
| `adr_index` | 生成 ADR 索引 |
| `adr_search` | 搜索 ADR |

## 测试

```bash
cd adr-generator/nexgent-plugin
python -c "
from adr_tools import call_tool
import tempfile, shutil
tmpdir = tempfile.mkdtemp()
result = call_tool('adr_create', {
    'path': tmpdir,
    'title': 'Use PostgreSQL',
    'template': 'madr',
    'context': 'Need a reliable database',
    'decision': 'Use PostgreSQL 15',
})
print(f'Created: ADR-{result[\"number\"]:04d}')
call_tool('adr_update_status', {'path': tmpdir, 'number': 1, 'status': 'accepted'})
index = call_tool('adr_index', {'path': tmpdir})
print(index[:200])
shutil.rmtree(tmpdir)
"
```

## 依赖

无外部依赖。纯 Python 标准库实现。

## License

MIT
