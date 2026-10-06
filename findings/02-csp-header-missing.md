# Content Security Policy (CSP) Header Not Set

## Title
Content Security Policy (CSP) Header Not Set

## Severity
**Medium**

## Classification
- **OWASP Top 10 Mapping:** A05:2021 - Security Misconfiguration
- **CWE ID:** CWE-693 (Protection Mechanism Failure)
- **Detection method:** DAST (OWASP ZAP, rule 10038)

## Affected Component
- **URL:** `http://localhost:3000`
- **Scope:** Site-wide (missing on all responses checked)

## Description
A Content Security Policy (CSP) is an HTTP response header that tells the browser which sources of content (scripts, styles, images, etc.) are allowed to load on a page. Without it, the browser has no restrictions beyond its own defaults, making it easier for malicious scripts, for example, those injected through a Cross-Site Scripting (XSS) vulnerability, to execute successfully, since there's no policy blocking them.

Juice Shop does not send a `Content-Security-Policy` header in its responses, leaving this layer of defense absent.

## Steps to Reproduce
1. With Juice Shop running locally, open the browser's developer tools (F12) and go to the Network tab, or use a tool like ZAP or `curl -I http://localhost:3000`.
2. Inspect the response headers for the main page.
3. Observe that no `Content-Security-Policy` header is present.

## Impact
CSP is a defense-in-depth control, it doesn't fix an underlying vulnerability like XSS by itself, but it significantly limits what an attacker can do if one exists. Without CSP:
- A successful XSS attack has no additional browser-level barrier.
- Inline scripts, third-party script injection, and data exfiltration via unexpected domains are all easier for an attacker to pull off.

This is a lower-severity finding on its own, but it compounds the risk of other vulnerabilities on the site (such as the SQL injection documented separately), which is why it's still worth fixing.

## Recommendation
- Add a `Content-Security-Policy` header to all responses, starting with a reasonably strict policy such as:
  ```
  Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'
  ```
- Use a library like [Helmet](https://helmetjs.github.io/) (for Express/Node.js apps) to set this and other security headers consistently, rather than configuring each manually.
- Test the policy in a report-only mode first (`Content-Security-Policy-Report-Only`) to catch any legitimate resources it would block before enforcing it.

## References
- OWASP Top 10:2021 - A05 Security Misconfiguration: https://owasp.org/Top10/A05_2021-Security_Misconfiguration/
- CWE-693: https://cwe.mitre.org/data/definitions/693.html
- MDN - Content-Security-Policy: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy