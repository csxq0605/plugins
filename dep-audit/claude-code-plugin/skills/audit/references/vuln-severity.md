# Vulnerability Severity Scoring

## CVSS v3.1 Score Ranges

| Severity | Score Range | Description |
|----------|-------------|-------------|
| Critical | 9.0 - 10.0 | Immediate exploitation, full system compromise |
| High | 7.0 - 8.9 | Significant impact, relatively easy to exploit |
| Medium | 4.0 - 6.9 | Moderate impact, some conditions required |
| Low | 0.1 - 3.9 | Limited impact, difficult to exploit |
| None | 0.0 | No security impact |

## Common Vulnerability Types

### Critical (fix immediately)

- **Remote Code Execution (RCE)**: Attacker can execute arbitrary code
- **SQL Injection**: Database compromise through unparameterized queries
- **Authentication Bypass**: Access without valid credentials
- **Deserialization Attacks**: Code execution through malicious serialized data
- **Prototype Pollution** (JS): Object prototype manipulation leading to RCE

### High (fix within 24-48 hours)

- **Cross-Site Scripting (XSS)**: Stored or reflected XSS in web apps
- **Path Traversal**: Access to files outside intended directory
- **Server-Side Request Forgery (SSRF)**: Internal network access
- **Privilege Escalation**: Gaining higher access levels
- **Sensitive Data Exposure**: Leaking credentials, tokens, PII

### Medium (fix within 1 week)

- **Cross-Site Request Forgery (CSRF)**: Unauthorized actions on behalf of users
- **Open Redirect**: Redirecting users to malicious sites
- **Information Disclosure**: Leaking non-sensitive system information
- **Denial of Service (DoS)**: Service disruption through resource exhaustion

### Low (fix when convenient)

- **Missing Security Headers**: Missing CSP, HSTS, etc.
- **Verbose Error Messages**: Stack traces in production
- **Weak Cryptography**: Using deprecated algorithms (MD5, SHA1)
- **Clickjacking**: UI redress attacks

## OSV Database

The [OSV (Open Source Vulnerability)](https://osv.dev) database provides:

- Unified vulnerability format across ecosystems
- API access at `https://api.osv.dev`
- Covers: npm, PyPI, Go, Rust, Maven, RubyGems, Packagist, and more
- Free, no API key required

### API Usage

```bash
# Query by package
curl -s "https://api.osv.dev/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"package": {"name": "lodash", "ecosystem": "npm"}}'

# Query by version
curl -s "https://api.osv.dev/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"package": {"name": "lodash", "ecosystem": "npm"}, "version": "4.17.15"}'

# Get specific vulnerability
curl -s "https://api.osv.dev/v1/vulns/{id}"
```

## Fix Strategies

### Immediate Patching

```bash
# npm: upgrade to patched version
npm install {package}@{patched_version}

# pip: upgrade
pip install --upgrade {package}

# cargo: update
cargo update -p {package}
```

### Pinning

```bash
# npm: pin to safe version
npm install {package}@{safe_version} --save-exact

# pip: pin in requirements.txt
{package}=={safe_version}
```

### Replacement

When no patch is available:
1. Find an alternative package with similar functionality
2. Migrate to the alternative
3. Remove the vulnerable package

### Workarounds

When immediate upgrade is not possible:
1. Disable the vulnerable feature
2. Add input validation/sanitization
3. Apply WAF rules
4. Monitor for exploitation attempts
