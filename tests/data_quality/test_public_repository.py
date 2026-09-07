from __future__ import annotations

import re
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEXT_SUFFIXES = {
    ".css",
    ".env",
    ".example",
    ".html",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".sql",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
EXCLUDED_PARTS = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "coverage",
    "dist",
    "node_modules",
    "output",
}


def _public_files() -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        tracked = [PROJECT_ROOT / line for line in result.stdout.splitlines() if line]
        if tracked:
            return [path for path in tracked if path.is_file()]
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    return [
        path
        for path in PROJECT_ROOT.rglob("*")
        if path.is_file()
        and not any(part in EXCLUDED_PARTS for part in path.parts)
        and not ("data" in path.parts and "demo" in path.parts and path.suffix == ".duckdb")
    ]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def test_public_repository_contains_no_obvious_credentials_or_private_keys() -> None:
    prefix = "sk" + "-"
    patterns = {
        "private_key": re.compile("BEGIN " + r"(?:RSA |EC |OPENSSH )?PRIVATE KEY"),
        "provider_api_token": re.compile(re.escape(prefix) + r"[A-Za-z0-9_-]{20,}"),
        "github_personal_token": re.compile("gh" + r"[pousr]_[A-Za-z0-9]{30,}"),
        "aws_access_key": re.compile("AK" + r"IA[0-9A-Z]{16}"),
        "credential_url": re.compile(r"(?:postgres|mysql)://[^\s/:]+:[^\s/@]+@", re.IGNORECASE),
        "assigned_secret": re.compile(
            r"(?i)(?:api[_-]?key|secret|password|token)\s*=\s*['\"][^'\"]{8,}['\"]"
        ),
    }
    findings: list[str] = []
    for path in _public_files():
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"Dockerfile", "Makefile"}:
            continue
        text = _read_text(path)
        for label, pattern in patterns.items():
            if pattern.search(text):
                findings.append(f"{path.relative_to(PROJECT_ROOT)}: {label}")
    assert not findings, "Potential credentials found:\n" + "\n".join(findings)


def test_no_local_environment_or_large_binary_is_publication_candidate() -> None:
    files = _public_files()
    forbidden_environment_files = [
        path.relative_to(PROJECT_ROOT)
        for path in files
        if path.name.startswith(".env") and path.name != ".env.example"
    ]
    assert not forbidden_environment_files
    oversized = [
        f"{path.relative_to(PROJECT_ROOT)} ({path.stat().st_size} bytes)"
        for path in files
        if path.stat().st_size > 10 * 1024 * 1024
    ]
    assert not oversized, "Files over 10 MiB should not be published:\n" + "\n".join(oversized)


def test_public_repository_contains_no_local_windows_path_or_personal_mailbox() -> None:
    local_root = re.compile(r"[A-Za-z]:\\" + r"Users\\[^\\\s]+", re.IGNORECASE)
    personal_mailbox = re.compile(r"[A-Za-z0-9._%+-]+@(?:qq|163|126)\.com", re.IGNORECASE)
    findings: list[str] = []
    for path in _public_files():
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {
            "Dockerfile",
            "Makefile",
            "LICENSE",
        }:
            continue
        text = _read_text(path)
        if local_root.search(text):
            findings.append(f"{path.relative_to(PROJECT_ROOT)}: local_path")
        if personal_mailbox.search(text):
            findings.append(f"{path.relative_to(PROJECT_ROOT)}: personal_mailbox")
    assert not findings, "Local-machine or personal-mailbox traces found:\n" + "\n".join(findings)


def test_recruiter_facing_text_contains_no_stale_fact_reconciliation_traces() -> None:
    narrative_files = [
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "README_zh.md",
        PROJECT_ROOT / "scripts" / "portfolio_data.py",
        PROJECT_ROOT / "analytics" / "methodology" / "registry.py",
        *sorted((PROJECT_ROOT / "docs").glob("*.md")),
    ]
    forbidden = (
        "Growth Analytics " + "Decision Platform",
        "用户增长全链路分析与实验决策平台",
        "没有一组一致",
        "没有一组完全一致",
        "没有一致的绝对效果量",
        "为避免公开事实冲突",
        "贡献待补数",
        "绝对提升未知",
        "统计与业务门通过",
        "策略推广并持续优化",
        "上手漏斗排除",
        "被排除的原因",
        "negative evidence / " + "exclusion",
        "4" + ".9%",
        "44" + ".9%",
    )
    findings: list[str] = []
    for path in narrative_files:
        text = _read_text(path)
        for phrase in forbidden:
            if phrase.casefold() in text.casefold():
                findings.append(f"{path.relative_to(PROJECT_ROOT)}: {phrase}")
    assert not findings, "Stale or unbounded recruiter-facing wording found:\n" + "\n".join(
        findings
    )
