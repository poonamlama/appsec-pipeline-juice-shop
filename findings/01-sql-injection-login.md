# SQL Injection in Product Search Endpoint

## Title
SQL Injection in Product Search Endpoint

## Severity
**High**

## Classification
- **OWASP Top 10 Mapping:** A03:2021 – Injection
- **CWE ID:** CWE-89 (Improper Neutralization of Special Elements used in an SQL Command)
- **WASC ID:** 19

## Affected Component
- **URL:** `http://localhost:3000/rest/products/search?q=`
- **Parameter:** `q` (URL query string)
- **Input Vector:** URL Query String

## Description
The product search endpoint accepts a `q` parameter and passes it into a backend SQL query without proper sanitization or parameterization. Submitting a single quote and parenthesis (`'(`) as the search term breaks out of the intended query structure, causing the database to throw a raw syntax error. This confirms that user-supplied input reaches the SQL engine directly, which is the root cause of a SQL injection vulnerability.

## Steps to Reproduce
1. Start the application locally (`docker run --rm -p 3000:3000 bkimminich/juice-shop`).
2. Navigate to the following URL in a browser:
   ```
   http://localhost:3000/rest/products/search?q=%27%28
   ```
   (This is `q='(`, URL-encoded.)
3. Observe the server's response.

**Expected behavior:** The application should handle the unexpected input gracefully, e.g., return an empty result set or a generic "invalid input" message.

**Actual behavior:** The application returns an HTTP 500 error, exposing internal implementation details.

## Evidence
Raw server response:
```
OWASP Juice Shop (Express ^4.22.1)
500 Error: SQLITE_ERROR: near "(": syntax error
```

This was also flagged automatically by OWASP ZAP's active scanner (rule 40018 – SQL Injection), with Risk: High, Confidence: Low (confirmed manually as above to remove ambiguity).

## Impact
The `q` parameter is concatenated directly into a backend SQL query rather than passed through a parameterized query or safe query builder. An attacker could exploit this to:
- Extract unauthorized data from the database (e.g., via UNION-based injection)
- Bypass application logic or filters
- Potentially modify or delete data, depending on database permissions

The error response also discloses internal implementation details — database engine (SQLite), backend framework (Express), and application version (^4.22.1) — which could help an attacker plan further attacks.

## Recommendation
- Use parameterized queries or an ORM's safe query-building methods (e.g., Sequelize's parameter binding) instead of building SQL strings via concatenation.
- Apply input validation/allow-listing on the `q` parameter as a defense-in-depth measure.
- Disable verbose error messages in production; return a generic error response instead of raw stack traces or database errors.

## References
- OWASP Top 10:2021 – A03 Injection: https://owasp.org/Top10/A03_2021-Injection/
- CWE-89: https://cwe.mitre.org/data/definitions/89.html
