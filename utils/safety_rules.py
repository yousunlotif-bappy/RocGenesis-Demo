import re
from collections import Counter


# =========================
# SAFETY RULE DEFINITIONS
# =========================
SAFETY_RULES = [
    {
        "category": "Secrets",
        "name": "Hardcoded API Key / Secret",
        "pattern": r"(api[_-]?key|secret|token|password)\s*=\s*[\"'][^\"']{6,}[\"']",
        "risk": "High",
        "reason": "Secrets or API keys should not be stored directly in source code.",
        "safe_fix": "Move secrets to environment variables, .env file, or platform secrets such as Hugging Face Secrets.",
    },
    {
        "category": "Secrets",
        "name": "OpenAI/OpenRouter-style API Key",
        "pattern": r"sk-[A-Za-z0-9_\-]{10,}",
        "risk": "High",
        "reason": "A private API key pattern was detected.",
        "safe_fix": "Remove the key from code, rotate the key, and store it in environment variables.",
    },
    {
        "category": "Model Loading",
        "name": "Unsafe Remote Code Trust",
        "pattern": r"trust_remote_code\s*=\s*True",
        "risk": "High",
        "reason": "trust_remote_code=True can execute Python code from a model repository.",
        "safe_fix": "Use trust_remote_code=False unless the model repository is fully audited and trusted.",
    },
    {
        "category": "Shell Command",
        "name": "Remote Script Piped to Shell",
        "pattern": r"(curl|wget).*(\|\s*(bash|sh|python))",
        "risk": "High",
        "reason": "Piping remote scripts directly into bash/sh/python can execute unverified code.",
        "safe_fix": "Download the script first, inspect it, verify the source, then run manually.",
    },
    {
        "category": "Shell Command",
        "name": "Dangerous Recursive Delete",
        "pattern": r"rm\s+-rf\s+(/|\*|~|\$HOME)",
        "risk": "High",
        "reason": "This command can delete critical files or the whole workspace.",
        "safe_fix": "Use a specific safe directory path and confirm before deletion.",
    },
    {
        "category": "Shell Command",
        "name": "Forced Full Permission Change",
        "pattern": r"chmod\s+-R\s+777",
        "risk": "Medium",
        "reason": "chmod -R 777 gives full permissions to everyone and is unsafe.",
        "safe_fix": "Use least-privilege permissions such as chmod 640, 750, or project-specific permissions.",
    },
    {
        "category": "Network",
        "name": "Insecure HTTP URL",
        "pattern": r"http://",
        "risk": "Medium",
        "reason": "HTTP traffic is not encrypted and may expose data.",
        "safe_fix": "Use HTTPS endpoints whenever possible.",
    },
    {
        "category": "App Security",
        "name": "Debug Mode Enabled",
        "pattern": r"debug\s*=\s*True",
        "risk": "Medium",
        "reason": "Debug mode can expose internal errors, stack traces, and sensitive information in production.",
        "safe_fix": "Disable debug mode before deployment.",
    },
    {
        "category": "Input Validation",
        "name": "Raw User Input Without Validation",
        "pattern": r"(user_input|input_text|prompt)\s*=\s*(input|st\.text_input|st\.text_area)",
        "risk": "Medium",
        "reason": "User input should be validated or sanitized before being used by the app or model.",
        "safe_fix": "Add input length limits, allowlists, moderation rules, and safe prompt handling.",
    },
    {
        "category": "Execution",
        "name": "Dynamic Code Execution",
        "pattern": r"\b(eval|exec)\s*\(",
        "risk": "High",
        "reason": "eval() or exec() can run arbitrary code.",
        "safe_fix": "Avoid eval/exec. Use safe parsers or explicit logic instead.",
    },
    {
        "category": "Deserialization",
        "name": "Unsafe Pickle Loading",
        "pattern": r"pickle\.load|pickle\.loads",
        "risk": "High",
        "reason": "Pickle can execute arbitrary code while loading untrusted files.",
        "safe_fix": "Use safer formats like JSON, or only load trusted pickle files.",
    },
    {
        "category": "Dependencies",
        "name": "Unpinned Dependency Install",
        "pattern": r"pip\s+install\s+([A-Za-z0-9_\-\[\]]+)(\s|$)",
        "risk": "Low",
        "reason": "Unpinned dependencies may break reproducibility.",
        "safe_fix": "Pin dependency versions in requirements.txt before final deployment.",
    },
    {
        "category": "Deployment",
        "name": "Public Host Binding",
        "pattern": r"0\.0\.0\.0",
        "risk": "Medium",
        "reason": "Binding to all network interfaces may expose the app publicly.",
        "safe_fix": "Use access control, firewall rules, or trusted hosting configuration.",
    },
    {
        "category": "File Access",
        "name": "Unsafe File Write",
        "pattern": r"open\s*\([^)]*[\"']w[\"']",
        "risk": "Low",
        "reason": "Writing files without validation may overwrite important files.",
        "safe_fix": "Validate file paths and avoid writing outside the project directory.",
    },
    {
        "category": "Dependency Supply Chain",
        "name": "Install From Unverified Git URL",
        "pattern": r"pip\s+install\s+git\+",
        "risk": "Medium",
        "reason": "Installing directly from a Git URL can introduce supply-chain risk.",
        "safe_fix": "Use trusted repositories, pinned commits, or official package releases.",
    },
]


# =========================
# BEST PRACTICE CHECKLIST
# =========================
BEST_PRACTICE_CHECKLIST = [
    "Secrets are stored in environment variables or platform secrets.",
    "No destructive shell commands are included.",
    "No remote script is piped directly into bash/sh/python.",
    "Model loading avoids trust_remote_code=True unless the model repository is audited.",
    "User input has validation, length limits, or moderation rules.",
    "Dependencies are pinned before final deployment.",
    "Debug mode is disabled for production.",
    "ROCm/PyTorch validation commands are included.",
    "Deployment instructions explain safe secret handling.",
    "Generated reports include safety findings and recommended fixes.",
]


# =========================
# INTERNAL HELPERS
# =========================
def _risk_weight(risk: str) -> int:
    if risk == "High":
        return 22
    if risk == "Medium":
        return 10
    if risk == "Low":
        return 4
    return 0


def _risk_level_from_counts(high_count: int, medium_count: int, low_count: int) -> str:
    if high_count > 0:
        return "High"
    if medium_count > 0:
        return "Medium"
    if low_count > 0:
        return "Low"
    return "Low"


def _deployment_readiness(score: int) -> str:
    if score >= 90:
        return "Ready"
    if score >= 75:
        return "Review Recommended"
    if score >= 55:
        return "Needs Fixes"
    return "Not Ready"


# =========================
# MAIN SCAN FUNCTION
# =========================
def scan_text_safety(text: str):
    """
    Scan code, shell commands, dependency files, or deployment config
    and return safety score, risk level, issues, fixes, and checklist.

    This function is deterministic and does not require an API key.
    """

    text = text or ""
    issues = []

    for rule in SAFETY_RULES:
        matches = re.findall(
            rule["pattern"],
            text,
            flags=re.IGNORECASE | re.MULTILINE,
        )

        if matches:
            issues.append(
                {
                    "category": rule["category"],
                    "name": rule["name"],
                    "pattern": rule["pattern"],
                    "risk": rule["risk"],
                    "reason": rule["reason"],
                    "safe_fix": rule["safe_fix"],
                    "matches_found": len(matches),
                }
            )

    penalty = sum(_risk_weight(issue["risk"]) for issue in issues)
    score = max(0, 100 - penalty)

    high_count = sum(1 for issue in issues if issue["risk"] == "High")
    medium_count = sum(1 for issue in issues if issue["risk"] == "Medium")
    low_count = sum(1 for issue in issues if issue["risk"] == "Low")

    risk_level = _risk_level_from_counts(high_count, medium_count, low_count)
    deployment_readiness = _deployment_readiness(score)

    category_counts = dict(Counter(issue["category"] for issue in issues))

    if not issues:
        summary = "No major safety issues detected. The input looks safe for development review."
    else:
        summary = (
            f"{len(issues)} issue(s) detected: "
            f"{high_count} high, {medium_count} medium, {low_count} low risk."
        )

    recommendations = []

    for issue in issues:
        recommendations.append(
            {
                "issue": issue["name"],
                "risk": issue["risk"],
                "fix": issue["safe_fix"],
            }
        )

    if not recommendations:
        recommendations = [
            {
                "issue": "General best practice",
                "risk": "Low",
                "fix": "Continue using environment variables, pinned dependencies, safe model loading, and safe deployment settings.",
            }
        ]

    return {
        "score": score,
        "risk_level": risk_level,
        "summary": summary,
        "issues": issues,
        "high_count": high_count,
        "medium_count": medium_count,
        "low_count": low_count,
        "category_counts": category_counts,
        "recommendations": recommendations,
        "deployment_readiness": deployment_readiness,
        "checklist": BEST_PRACTICE_CHECKLIST,
    }


# =========================
# REPORT BUILDER
# =========================
def build_safety_report(scan_result, scanned_text: str = ""):
    """
    Build a downloadable markdown report for Safety Guard.
    """

    lines = []

    lines.append("# RocGenesis Safety Guard Report")
    lines.append("")

    lines.append("## Summary")
    lines.append(f"- Safety Score: {scan_result.get('score')}/100")
    lines.append(f"- Risk Level: {scan_result.get('risk_level')}")
    lines.append(f"- Deployment Readiness: {scan_result.get('deployment_readiness')}")
    lines.append(f"- Summary: {scan_result.get('summary')}")
    lines.append("")

    lines.append("## Issue Counts")
    lines.append(f"- High Risk: {scan_result.get('high_count', 0)}")
    lines.append(f"- Medium Risk: {scan_result.get('medium_count', 0)}")
    lines.append(f"- Low Risk: {scan_result.get('low_count', 0)}")
    lines.append("")

    lines.append("## Category Breakdown")
    category_counts = scan_result.get("category_counts", {})

    if category_counts:
        for category, count in category_counts.items():
            lines.append(f"- {category}: {count}")
    else:
        lines.append("- No issue categories detected.")

    lines.append("")

    lines.append("## Detected Issues")
    issues = scan_result.get("issues", [])

    if issues:
        for index, issue in enumerate(issues, start=1):
            lines.append(f"### {index}. {issue.get('name')}")
            lines.append(f"- Category: {issue.get('category')}")
            lines.append(f"- Risk: {issue.get('risk')}")
            lines.append(f"- Reason: {issue.get('reason')}")
            lines.append(f"- Safe Fix: {issue.get('safe_fix')}")
            lines.append(f"- Matches Found: {issue.get('matches_found')}")
            lines.append("")
    else:
        lines.append("No critical issues detected.")
        lines.append("")

    lines.append("## Recommended Safe Fixes")

    for rec in scan_result.get("recommendations", []):
        lines.append(
            f"- [{rec.get('risk')}] {rec.get('issue')}: {rec.get('fix')}"
        )

    lines.append("")

    lines.append("## Best-practice Checklist")

    for item in scan_result.get("checklist", []):
        lines.append(f"- [ ] {item}")

    lines.append("")

    lines.append("## Scanned Input Preview")
    lines.append("```text")
    lines.append((scanned_text or "")[:3000])
    lines.append("```")

    return "\n".join(lines)

