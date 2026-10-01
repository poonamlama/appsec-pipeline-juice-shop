"""
summarize_findings.py

Reads a ZAP JSON scan report and prints a short, prioritized summary of
the security findings: what was found, how severe it is, and which
OWASP Top 10 category it maps to.

Usage:
    python summarize_findings.py path/to/zap-report.json

If no path is given, it looks for zap-report/zap-report.json by default
(the location our GitHub Actions pipeline saves it to).
"""

import json
import sys
from pathlib import Path

# ZAP uses a numeric "riskcode" for severity. This dictionary translates
# that number into a human-readable word, and also lets us sort findings
# from most to least severe later on.
RISK_LEVELS = {
    "3": "High",
    "2": "Medium",
    "1": "Low",
    "0": "Informational",
}

# A small lookup table mapping common CWE IDs (which ZAP reports) to their
# matching OWASP Top 10 (2021) category. This isn't exhaustive -- it just
# covers the kinds of issues you're likely to see from a baseline scan --
# but it's exactly the kind of mapping a real AppSec engineer keeps handy.
CWE_TO_OWASP = {
    "89": "A03:2021 - Injection",
    "79": "A03:2021 - Injection (XSS)",
    "352": "A01:2021 - Broken Access Control",
    "200": "A01:2021 - Broken Access Control (Information Exposure)",
    "284": "A01:2021 - Broken Access Control",
    "16": "A05:2021 - Security Misconfiguration",
    "693": "A05:2021 - Security Misconfiguration",
    "1021": "A05:2021 - Security Misconfiguration (Clickjacking)",
    "614": "A05:2021 - Security Misconfiguration (Cookie flags)",
}


def load_report(path):
    """Open the JSON file and return it as a Python dictionary."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_alerts(report):
    """
    ZAP's JSON report nests alerts under report["site"][0]["alerts"].
    This pulls that list out. If the structure is slightly different
    (ZAP has changed its format before), this gives a clear error
    instead of a confusing crash.
    """
    try:
        sites = report["site"]
    except KeyError:
        raise ValueError("Unexpected report format: no 'site' key found.")

    alerts = []
    for site in sites:
        alerts.extend(site.get("alerts", []))
    return alerts


def summarize(alerts):
    """
    Build a simplified list of findings: name, risk level, CWE ID,
    OWASP mapping, and how many instances were found. Sorted so the
    most severe issues appear first.
    """
    summary = []
    for alert in alerts:
        risk_code = alert.get("riskcode", "0")
        cwe_id = str(alert.get("cweid", ""))
        summary.append({
            "name": alert.get("name", "Unnamed finding"),
            "risk": RISK_LEVELS.get(risk_code, "Unknown"),
            "risk_code": int(risk_code),
            "cwe_id": cwe_id,
            "owasp_category": CWE_TO_OWASP.get(cwe_id, "Not mapped"),
            "instances": len(alert.get("instances", [])),
        })

    # Sort by risk_code descending (3 = High comes first, 0 = Info last)
    summary.sort(key=lambda item: item["risk_code"], reverse=True)
    return summary


def print_summary(summary):
    print("=" * 60)
    print("SECURITY SCAN SUMMARY")
    print("=" * 60)

    if not summary:
        print("No findings in this report.")
        return

    for item in summary:
        print(f"\n[{item['risk']}] {item['name']}")
        print(f"  CWE: {item['cwe_id'] or 'N/A'}  |  OWASP: {item['owasp_category']}")
        print(f"  Instances found: {item['instances']}")

    # A quick count by severity, useful for a one-line "state of the app" view
    counts = {}
    for item in summary:
        counts[item["risk"]] = counts.get(item["risk"], 0) + 1

    print("\n" + "-" * 60)
    print("Totals:", ", ".join(f"{level}: {count}" for level, count in counts.items()))
    print("-" * 60)


def main():
    # Figure out which file to read: either the path given on the command
    # line, or our pipeline's default location.
    if len(sys.argv) > 1:
        report_path = Path(sys.argv[1])
    else:
        report_path = Path("zap-report/zap-report.json")

    if not report_path.exists():
        print(f"Could not find report file at: {report_path}")
        print("Pass the path as an argument, e.g.:")
        print("  python summarize_findings.py path/to/zap-report.json")
        sys.exit(1)

    report = load_report(report_path)
    alerts = extract_alerts(report)
    summary = summarize(alerts)
    print_summary(summary)


if __name__ == "__main__":
    main()