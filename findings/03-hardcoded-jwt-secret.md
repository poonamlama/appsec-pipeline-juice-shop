# Hardcoded JWT Signing Secret

## Title
Hardcoded JWT Signing Secret in Source Code

## Severity
**Medium-High**

## Classification
- **OWASP Top 10 Mapping:** A02:2021 - Cryptographic Failures
- **CWE ID:** CWE-798 (Use of Hard-coded Credentials)
- **Detection method:** SAST (Semgrep, rule `javascript.jsonwebtoken.security.jwt-hardcode.hardcoded-jwt-secret`)

## Affected Component
- **File:** `lib/insecurity.ts`
- **Line:** 54 (secret used to sign authentication tokens)

## Description
The application uses JSON Web Tokens (JWT) to authenticate logged-in users. The secret key used to sign and verify these tokens is hardcoded directly in the source code rather than loaded from an environment variable or a secure secrets manager. Since the source code is version-controlled (and, in this case, publicly available on GitHub), the signing secret is effectively public.

## Steps to Reproduce
1. Open `lib/insecurity.ts` in the repository and locate the JWT signing call (line 54).
2. Observe that the secret argument is a literal string in the code rather than a reference like `process.env.JWT_SECRET`.
3. Because this value never changes between deployments and is visible to anyone with repository access, no further exploitation steps are needed to confirm the issue, the secret is exposed by the code itself.

## Impact
Anyone with access to the source code (which includes the public internet, for an open-source project like this) can read the signing secret. With it, an attacker could:
- Forge a valid JWT for any user, including an administrator account, without knowing that user's password.
- Bypass authentication entirely, since the server will treat any token signed with this secret as legitimate.

This is a critical weakness in applications where the secret is meant to be private; it undermines the entire authentication system regardless of how strong individual user passwords are.

## Recommendation
- Move the JWT signing secret into an environment variable (e.g., `process.env.JWT_SECRET`) and never commit it to source control.
- Use a secrets manager (such as AWS Secrets Manager, Azure Key Vault, or HashiCorp Vault) in production environments rather than plain environment variables where possible.
- Rotate the secret immediately if it has ever been exposed, since all tokens signed with it become invalid after rotation (forcing all users to re-authenticate, which is the correct remediation step).
- Add a pre-commit or CI check (such as a secrets-scanning tool like Gitleaks or TruffleHog) to catch hardcoded secrets before they're merged.

## Note on Detection Method
This finding was discovered through **Static Application Security Testing (SAST)** using Semgrep, scanning the application's source code directly, rather than through dynamic scanning (DAST) of the running application. This demonstrates why both approaches matter: a hardcoded secret like this may not be detectable by only interacting with the live application (DAST), since the secret itself isn't transmitted in normal use. Only reading the source code reveals it.

## References
- OWASP Top 10:2021 - A02 Cryptographic Failures: https://owasp.org/Top10/A02_2021-Cryptographic_Failures/
- CWE-798: https://cwe.mitre.org/data/definitions/798.html