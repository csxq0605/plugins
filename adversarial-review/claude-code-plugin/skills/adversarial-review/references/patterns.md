# 安全检测模式库

200+ 安全检测正则模式，按类别组织。用于 adversarial-review 的 Security 视角。

## 使用方式

在审查代码时，用 Grep 工具匹配以下模式。每个模式包含：
- 正则表达式
- 严重性（Critical/High/Medium）
- 描述
- 修复建议
- 参考（CWE/OWASP）

---

## 1. 密钥泄露（SECRETS）

### 云服务密钥

| 模式 | 严重性 | 描述 |
|------|--------|------|
| `AKIA[0-9A-Z]{16}` | Critical | AWS Access Key ID |
| `(?i)aws.{0,20}['\"][0-9a-zA-Z/+]{40}['\"]` | Critical | AWS Secret Access Key |
| `ghp_[A-Za-z0-9]{36}` | Critical | GitHub Personal Access Token |
| `gho_[A-Za-z0-9]{36}` | Critical | GitHub OAuth Token |
| `github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}` | Critical | GitHub Fine-grained PAT |
| `glpat-[A-Za-z0-9\-_]{20,}` | Critical | GitLab Personal Access Token |
| `sk-[A-Za-z0-9]{20,}` | Critical | OpenAI API Key |
| `sk-ant-[A-Za-z0-9\-_]{40,}` | Critical | Anthropic API Key |
| `xoxb-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9]*` | Critical | Slack Bot Token |
| `xoxp-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9]*` | Critical | Slack User Token |
| `sk_live_[0-9a-zA-Z]{24,}` | Critical | Stripe Live Secret Key |
| `rk_live_[0-9a-zA-Z]{24,}` | Critical | Stripe Restricted Key |
| `sq0atp-[0-9A-Za-z\-_]{22}` | Critical | Square Access Token |
| `SG\.[A-Za-z0-9\-_]{22}\.[A-Za-z0-9\-_]{43}` | Critical | SendGrid API Key |
| `key-[a-zA-Z0-9]{32}` | Critical | Mailgun API Key |
| `AIza[0-9A-Za-z\-_]{35}` | Critical | Google API Key |
| `[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com` | High | Google OAuth Client ID |

### 数据库连接串

| 模式 | 严重性 | 描述 |
|------|--------|------|
| `(?i)(mysql|postgres|mongodb|redis)://[^\s]+` | Critical | 数据库连接串 |
| `(?i)jdbc:[a-z]+://[^\s]+` | Critical | JDBC 连接串 |
| `(?i)DSN=[^\s]+password=[^\s]+` | Critical | DSN with password |

### 私钥

| 模式 | 严重性 | 描述 |
|------|--------|------|
| `-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----` | Critical | 私钥文件 |
| `-----BEGIN PGP PRIVATE KEY BLOCK-----` | Critical | PGP 私钥 |

---

## 2. 注入漏洞（INJECTION）

### SQL 注入

| 模式 | 严重性 | 描述 |
|------|--------|------|
| `(?i)(SELECT\|INSERT\|UPDATE\|DELETE).{0,100}(\+\|%\|f\|format\|concat)` | Critical | SQL 字符串拼接 |
| `(?i)execute\(.{0,50}(%s\|%d\|\?.\|\$\{)` | Critical | 参数化但可能不安全 |
| `(?i)raw\(.{0,100}(SELECT\|INSERT\|UPDATE\|DELETE)` | Critical | 原始 SQL 查询 |
| `(?i)query\(.{0,50}(\+\|%\|f\|format)` | Critical | 查询字符串拼接 |

### XSS

| 模式 | 严重性 | 描述 |
|------|--------|------|
| `(?i)innerHTML\s*=` | Critical | 直接设置 innerHTML |
| `(?i)v-html\s*=` | High | Vue.js v-html 指令 |
| `(?i)dangerouslySetInnerHTML` | High | React dangerouslySetInnerHTML |
| `(?i)document\.write\(` | Critical | document.write |
| `(?i)\.html\(.{0,50}(\+\|%\|f\|format\|concat)` | High | jQuery .html() with concatenation |

### 命令注入

| 模式 | 严重性 | 描述 |
|------|--------|------|
| `(?i)os\.system\(` | Critical | Python os.system |
| `(?i)os\.popen\(` | Critical | Python os.popen |
| `(?i)exec\(.{0,50}(\+\|%\|f\|format)` | Critical | exec with string formatting |
| `(?i)eval\(` | Critical | eval() |
| `(?i)subprocess\.(call\|run\|Popen).{0,100}shell\s*=\s*True` | Critical | subprocess with shell=True |
| `(?i)child_process\.exec\(` | Critical | Node.js child_process.exec |
| `(?i)`[^`]*\$\{` | Critical | Template literal injection (JS) |

### SSRF

| 模式 | 严重性 | 描述 |
|------|--------|------|
| `(?i)(requests\|http\|urllib\|fetch\|axios).{0,50}(user\|input\|param\|req\.)` | High | 用户可控的 URL 请求 |
| `(?i)http(s)?://.{0,100}(\+\|%\|f\|format\|concat)` | High | URL 字符串拼接 |

### 路径遍历

| 模式 | 严重性 | 描述 |
|------|--------|------|
| `(?i)(open\|readFile\|readFileSync\|fs\.read).{0,50}(\+\|%\|f\|format\|concat)` | Critical | 文件路径拼接 |
| `\.\./` | High | 路径遍历字符（需上下文确认） |

---

## 3. 认证缺陷（AUTH）

| 模式 | 严重性 | 描述 |
|------|--------|------|
| `(?i)jwt\.verify\(.{0,50}algorithms?\s*:\s*\[.*none` | Critical | JWT 允许 none 算法 |
| `(?i)password.{0,20}(md5\|sha1)` | Critical | 弱密码哈希 |
| `(?i)session.{0,20}(secure\s*:\s*false\|httpOnly\s*:\s*false)` | High | 不安全的 cookie 配置 |
| `(?i)csrf.{0,20}(false\|disabled\|skip)` | High | CSRF 保护禁用 |
| `(?i)cors.{0,20}(origin\s*:\s*['\"]?\*\|allow.?all)` | High | CORS 允许所有来源 |

---

## 4. 配置问题（CONFIG）

| 模式 | 严重性 | 描述 |
|------|--------|------|
| `(?i)debug\s*[:=]\s*true` | High | 调试模式开启 |
| `(?i)DEBUG\s*=\s*True` | High | Django DEBUG 模式 |
| `(?i)NODE_ENV\s*!==?\s*['\"]production` | High | 非生产环境检查 |
| `(?i)ALLOWED_HOSTS\s*=\s*\[.*\*` | High | Django 允许所有主机 |
| `(?i)SSL_VERIFY\s*=\s*False` | High | SSL 验证禁用 |
| `(?i)verify\s*=\s*False` | Medium | requests verify=False |

---

## 5. AI 特定（AI）

| 模式 | 严重性 | 描述 |
|------|--------|------|
| `(?i)(openai\|anthropic\|gemini).{0,20}(api.?key\|secret)` | Critical | AI API 密钥引用 |
| `(?i)system.{0,50}(ignore\|forget\|override).{0,50}(previous\|above\|instructions)` | High | 提示注入向量 |
| `(?i)(execute\|eval\|run\|exec).{0,50}(llm\|ai\|model\|gpt\|claude).{0,50}(output\|response\|result)` | Critical | 执行 LLM 输出 |
| `(?i)temperature\s*=\s*[12]\.\d` | Medium | 高温度可能导致不可预测输出 |

---

## 6. 语言特定

### Python

| 模式 | 严重性 | 描述 |
|------|--------|------|
| `(?i)pickle\.loads?\(` | Critical | 不安全的反序列化 |
| `(?i)yaml\.load\([^)]*\)` | Critical | 不安全的 YAML 加载 |
| `(?i)__import__\(` | High | 动态导入 |
| `(?i)input\(` | Medium | Python 2 input() 执行表达式 |

### JavaScript/TypeScript

| 模式 | 严重性 | 描述 |
|------|--------|------|
| `(?i)new Function\(` | Critical | 动态代码执行 |
| `(?i)setTimeout\(.{0,20}['\"]` | High | setTimeout with string |
| `(?i)setInterval\(.{0,20}['\"]` | High | setInterval with string |
| `(?i)postMessage\(.{0,50}\*` | High | postMessage to all origins |

### Go

| 模式 | 严重性 | 描述 |
|------|--------|------|
| `(?i)fmt\.Sprintf.{0,100}(SELECT\|INSERT\|UPDATE\|DELETE)` | Critical | SQL 字符串格式化 |
| `(?i)os/exec.{0,50}Command\(` | Medium | 命令执行（需上下文） |

### Java

| 模式 | 严重性 | 描述 |
|------|--------|------|
| `(?i)Runtime\.getRuntime\(\)\.exec\(` | Critical | 命令执行 |
| `(?i)ProcessBuilder\(` | Medium | 进程构建（需上下文） |
| `(?i)ObjectInputStream\(` | Critical | Java 反序列化 |

---

## 7. 通用模式

| 模式 | 严重性 | 描述 |
|------|--------|------|
| `(?i)(password\|passwd\|pwd)\s*[:=]\s*['\"][^'\"]+['\"]` | Critical | 硬编码密码 |
| `(?i)(secret\|token\|key)\s*[:=]\s*['\"][^'\"]+['\"]` | High | 硬编码密钥/token |
| `(?i)TODO.{0,50}(security\|vuln\|hack\|fix)` | Medium | 安全相关 TODO |
| `(?i)FIXME.{0,50}(security\|vuln\|auth)` | Medium | 安全相关 FIXME |
| `(?i)HACK` | Medium | 代码中的 HACK 标记 |
| `(?i)(disable\|skip\|bypass).{0,20}(auth\|security\|validation)` | High | 禁用安全检查 |

---

## 使用注意事项

1. **上下文很重要**：正则匹配需要结合上下文判断。测试文件中的匹配应降级为 INFO。
2. **框架内置保护**：Django ORM、React 默认转义等框架保护会降低严重性。
3. **去重**：同一模式出现多次时合并为一条发现。
4. **误报控制**：置信度 < 80 的发现降级为 Suggestion。
