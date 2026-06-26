# Review Checklist

## Security 视角

**密钥泄露（Critical）**：
- API 密钥、token、密码硬编码
- 数据库连接串明文
- 私钥文件提交

**注入漏洞（Critical）**：
- SQL 注入：字符串拼接 SQL
- XSS：未转义用户输入
- 命令注入：os.system(), exec()
- SSRF：用户可控 URL
- 路径遍历：用户输入拼接路径

**认证缺陷（High）**：
- JWT 未验证签名
- 弱密码哈希（MD5/SHA1）
- 缺少 CSRF 保护

**配置问题（High）**：
- CORS 允许所有来源
- 调试模式开启
- 缺少安全头

## Performance 视角

**算法复杂度（Warning）**：
- 嵌套循环 O(n²)+
- 循环内数据库查询（N+1）
- 递归无缓存

**内存分配（Warning）**：
- 大对象循环创建
- 未关闭资源
- 事件监听器未移除

**热路径（Warning）**：
- 高频函数中低效操作
- 同步 I/O 阻塞事件循环

## Architecture 视角

**R1 认知过载（Warning）**：
- 函数 > 20 行
- 嵌套 > 3 层
- 参数 > 4 个

**R2 变更传播（Critical）**：
- 改一个文件需改多个不相关文件
- 全局状态依赖

**R3 知识重复（Warning）**：
- 同一决策多处表达
- 复制粘贴代码块

**R5 依赖混乱（Critical）**：
- 循环依赖
- 上层依赖下层实现细节

## Code Quality 视角

**命名（Warning）**：
- 变量名不描述用途
- 缩写不标准

**错误处理（Critical）**：
- 静默失败（空 catch）
- 过于宽泛异常捕获

## Test Quality 视角

**覆盖率（Warning）**：
- 关键路径无测试
- 边界条件未测试

**测试质量（Warning）**：
- 测试实现细节而非行为
- 过度 Mock

## API Design 视角

**向后兼容（Critical）**：
- 删除公开 API 无废弃期
- 修改函数签名

**类型安全（Warning）**：
- 使用 any 类型
- 缺少输入验证
