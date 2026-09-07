from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import zipfile
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

POLICY_VERSION = "1.0"
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
TEXT_ENCODINGS = ("utf-8", "utf-8-sig", "utf-16")

EXCLUDED_DIRECTORY_NAMES = frozenset(
    {
        ".cache",
        ".git",
        ".hg",
        ".idea",
        ".mypy_cache",
        ".next",
        ".nox",
        ".npm",
        ".output",
        ".parcel-cache",
        ".playwright-cli",
        ".pnpm-store",
        ".pytest_cache",
        ".ruff_cache",
        ".svn",
        ".tox",
        ".venv",
        ".vite",
        ".vscode",
        "__pycache__",
        "blob-report",
        "build",
        "cache",
        "coverage",
        "deliverables",
        "dist",
        "htmlcov",
        "logs",
        "node_modules",
        "output",
        "outputs",
        "playwright-report",
        "test-results",
        "tmp",
        "venv",
    }
)
EXCLUDED_FILE_NAMES = frozenset(
    {
        ".coverage",
        ".ds_store",
        "coverage.xml",
        "desktop.ini",
        "junit.xml",
        "npm-debug.log",
        "playwright-report.json",
        "pnpm-debug.log",
        "pytest-results.xml",
        "thumbs.db",
        "trace.zip",
        "yarn-debug.log",
        "yarn-error.log",
    }
)
EXCLUDED_FILE_SUFFIXES = frozenset(
    {
        ".accdb",
        ".bak",
        ".bson",
        ".db",
        ".db3",
        ".db-shm",
        ".db-wal",
        ".db-journal",
        ".duckdb",
        ".duckdb.wal",
        ".fdb",
        ".leveldb",
        ".lmdb",
        ".log",
        ".mdb",
        ".pyo",
        ".pyc",
        ".rdb",
        ".realm",
        ".s3db",
        ".sqlite",
        ".sqlite-shm",
        ".sqlite-wal",
        ".sqlite3",
        ".sqlitedb",
        ".tmp",
        ".trace",
        ".wal",
    }
)
PLACEHOLDER_VALUES = frozenset(
    {
        "changeme",
        "example",
        "example-only",
        "none",
        "not-set",
        "placeholder",
        "redacted",
        "replace-me",
        "sample",
        "test-only",
        "your-value",
    }
)


class ReleaseBuildError(RuntimeError):
    """Base error for a release build that cannot be completed safely."""


class ReleasePolicyError(ReleaseBuildError):
    """Raised when a publication candidate violates the release policy."""

    def __init__(self, findings: Sequence[ScanFinding]) -> None:
        self.findings = list(findings)
        details = "\n".join(f"- {finding.render()}" for finding in self.findings)
        super().__init__(f"Release policy rejected {len(self.findings)} finding(s):\n{details}")


@dataclass(frozen=True)
class ScanFinding:
    category: str
    path: str
    line: int | None = None

    def render(self) -> str:
        location = f"{self.path}:{self.line}" if self.line is not None else self.path
        return f"{location} [{self.category}]"


@dataclass(frozen=True)
class ReleaseArtifact:
    archive_path: Path
    manifest_path: Path
    checksum_path: Path
    sha256: str
    file_count: int
    total_bytes: int


@dataclass(frozen=True)
class _ReleaseFile:
    source_path: Path
    relative_path: PurePosixPath
    size: int
    sha256: str


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _has_excluded_suffix(name: str) -> bool:
    lowered = name.casefold()
    return any(lowered.endswith(suffix) for suffix in EXCLUDED_FILE_SUFFIXES)


def _is_playwright_artifact(path: Path) -> bool:
    lowered_parts = tuple(part.casefold() for part in path.parts)
    if any(part.startswith(".playwright") for part in lowered_parts):
        return True
    name = path.name.casefold()
    return name.startswith("playwright-") and name.endswith((".log", ".json", ".zip"))


def _is_excluded(relative_path: Path) -> bool:
    lowered_parts = tuple(part.casefold() for part in relative_path.parts)
    directory_parts = lowered_parts[:-1]
    if any(part in EXCLUDED_DIRECTORY_NAMES for part in directory_parts):
        return True
    if any(part.endswith(".cache") for part in directory_parts):
        return True
    name = relative_path.name.casefold()
    if name.startswith(".env") and name != ".env.example":
        return True
    if name in EXCLUDED_FILE_NAMES or _has_excluded_suffix(name):
        return True
    return _is_playwright_artifact(relative_path)


def _is_excluded_directory(relative_path: Path) -> bool:
    lowered_parts = tuple(part.casefold() for part in relative_path.parts)
    return any(
        part in EXCLUDED_DIRECTORY_NAMES
        or part.startswith(".env")
        or part.endswith(".cache")
        or part.endswith("-cache")
        or part.startswith(".playwright")
        for part in lowered_parts
    )


def _is_within(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
    except ValueError:
        return False
    return True


def _collect_candidate_paths(source_root: Path, output_directory: Path) -> list[Path]:
    candidates: list[Path] = []
    for current_root, directory_names, file_names in os.walk(source_root, topdown=True):
        current = Path(current_root)
        retained_directories: list[str] = []
        for name in sorted(directory_names, key=str.casefold):
            path = current / name
            relative = path.relative_to(source_root)
            resolved = path.resolve()
            if path.is_symlink() or _is_excluded_directory(relative):
                continue
            if resolved == output_directory or _is_within(resolved, output_directory):
                continue
            retained_directories.append(name)
        directory_names[:] = retained_directories

        for name in sorted(file_names, key=str.casefold):
            path = current / name
            if path.is_symlink() or not path.is_file():
                continue
            resolved = path.resolve()
            if _is_within(resolved, output_directory):
                continue
            relative = path.relative_to(source_root)
            if not _is_excluded(relative):
                candidates.append(path)
    return sorted(candidates, key=lambda item: item.relative_to(source_root).as_posix())


def _decode_for_scan(data: bytes) -> str:
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16", errors="ignore")
    if data.startswith(b"\xef\xbb\xbf"):
        return data.decode("utf-8-sig", errors="ignore")
    sample = data[:8192]
    control_bytes = sum(byte < 9 or 13 < byte < 32 for byte in sample)
    if b"\x00" in sample or (sample and control_bytes / len(sample) > 0.05):
        printable_runs = re.findall(rb"[\x20-\x7e]{8,}", data)
        return "\n".join(run.decode("ascii") for run in printable_runs)
    for encoding in TEXT_ENCODINGS:
        try:
            return data.decode(encoding)
        except UnicodeError:
            continue
    return data.decode("utf-8", errors="ignore")


def _line_number(text: str, start: int) -> int:
    return text.count("\n", 0, start) + 1


def _local_path_patterns() -> tuple[re.Pattern[str], ...]:
    slash = "/"
    return (
        re.compile(r"(?i)(?<![A-Za-z0-9])[A-Za-z]:[\\/](?![\\/])"),
        re.compile(re.escape(slash) + r"(?:Users|home)/[^/\s]+/"),
        re.compile(re.escape(slash) + r"mnt/[a-z]/(?:Users|home)/[^/\s]+/", re.IGNORECASE),
        re.compile(r"\\\\[^\\\s]+\\[^\\\s]+\\"),
    )


def _credential_patterns() -> tuple[tuple[str, re.Pattern[str]], ...]:
    provider_prefix = "s" + "k" + "-"
    github_prefix = "g" + "h"
    aws_prefix = "AK" + "IA"
    slack_prefix = "xo" + "x"
    bearer_word = "Bear" + "er"
    query_names = (
        "access_" + "token",
        "api_" + "key",
        "secret",
        "token",
    )
    private_header = "BEGIN " + "PRIVATE KEY"
    return (
        ("private_credential", re.compile(re.escape(private_header))),
        (
            "private_credential",
            re.compile("BEGIN " + r"(?:RSA |EC |OPENSSH )?" + re.escape("PRIVATE KEY")),
        ),
        ("provider_credential", re.compile(re.escape(provider_prefix) + r"[A-Za-z0-9_-]{20,}")),
        (
            "repository_credential",
            re.compile(re.escape(github_prefix) + r"[pousr]_[A-Za-z0-9]{30,}"),
        ),
        ("cloud_credential", re.compile(re.escape(aws_prefix) + r"[0-9A-Z]{16}")),
        ("cloud_credential", re.compile(r"AIza[0-9A-Za-z_-]{30,}")),
        (
            "service_credential",
            re.compile(re.escape(slack_prefix) + r"[abprs]-[A-Za-z0-9-]{20,}"),
        ),
        ("payment_credential", re.compile(r"(?:sk|rk)_live_[A-Za-z0-9]{16,}")),
        (
            "authorization_credential",
            re.compile(rf"(?i)\b{re.escape(bearer_word)}\s+[A-Za-z0-9._~+/=-]{{20,}}"),
        ),
        (
            "credential_in_url",
            re.compile(r"(?i)(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?)://[^\s/:]+:[^\s/@]+@"),
        ),
        (
            "credential_in_url",
            re.compile(rf"(?i)[?&](?:{'|'.join(query_names)})=[A-Za-z0-9._~+/=-]{{12,}}"),
        ),
    )


def _credential_names_pattern() -> str:
    names = (
        "api[_-]?" + "key",
        "access[_-]?" + "token",
        "auth[_-]?" + "token",
        "aws[_-]?" + "secret" + "[_-]?access[_-]?" + "key",
        "client[_-]?" + "secret",
        "private[_-]?" + "key",
        "pass" + "word",
        "pass" + "wd",
        "secret",
        "token",
    )
    return "|".join(names)


def _quoted_credential_pattern() -> re.Pattern[str]:
    names = _credential_names_pattern()
    return re.compile(
        rf"(?i)(?:{names})[\"']?\s*[:=]\s*(?P<quote>[\"'])"
        r"(?P<value>[^\r\n'\"]{8,})(?P=quote)"
    )


def _unquoted_credential_pattern() -> re.Pattern[str]:
    names = _credential_names_pattern()
    return re.compile(
        rf"(?im)(?:{names})\s*[:=]\s*"
        r"(?P<value>[A-Za-z0-9_./+\-=]{12,})\s*(?:#.*)?$"
    )


def _is_placeholder(value: str) -> bool:
    normalized = value.strip().casefold()
    if normalized in PLACEHOLDER_VALUES:
        return True
    return normalized.startswith(("example-", "placeholder-", "replace-", "your-"))


def _scan_text(relative_path: PurePosixPath, text: str) -> list[ScanFinding]:
    display_path = relative_path.as_posix()
    findings: list[ScanFinding] = []
    scanners: list[tuple[str, re.Pattern[str]]] = [
        ("local_absolute_path", pattern) for pattern in _local_path_patterns()
    ]
    scanners.extend(_credential_patterns())
    for category, pattern in scanners:
        for match in pattern.finditer(text):
            findings.append(ScanFinding(category, display_path, _line_number(text, match.start())))
    for assignment_pattern in (_quoted_credential_pattern(), _unquoted_credential_pattern()):
        for match in assignment_pattern.finditer(text):
            if not _is_placeholder(match.group("value")):
                findings.append(
                    ScanFinding(
                        "assigned_credential",
                        display_path,
                        _line_number(text, match.start()),
                    )
                )
    return findings


def _deduplicate_findings(findings: Iterable[ScanFinding]) -> list[ScanFinding]:
    return sorted(
        set(findings),
        key=lambda finding: (finding.path, finding.line or 0, finding.category),
    )


def inspect_release_tree(
    source_root: Path,
    *,
    output_directory: Path | None = None,
) -> tuple[list[_ReleaseFile], list[ScanFinding]]:
    """Collect and validate every file eligible for publication."""
    root = source_root.expanduser().resolve()
    if not root.is_dir():
        raise ReleaseBuildError(f"Source directory does not exist: {root}")
    output = (output_directory or root / "deliverables").expanduser().resolve()

    findings: list[ScanFinding] = []
    release_files: list[_ReleaseFile] = []
    for path in _collect_candidate_paths(root, output):
        relative = PurePosixPath(path.relative_to(root).as_posix())
        data = path.read_bytes()
        findings.extend(_scan_text(relative, _decode_for_scan(data)))
        release_files.append(
            _ReleaseFile(
                source_path=path,
                relative_path=relative,
                size=len(data),
                sha256=_sha256_bytes(data),
            )
        )
    return release_files, _deduplicate_findings(findings)


def _validate_release_name(release_name: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", release_name):
        raise ReleaseBuildError(
            "Release name must start with an alphanumeric character and contain only "
            "letters, numbers, dots, underscores, or hyphens."
        )
    if release_name in {".", ".."}:
        raise ReleaseBuildError("Release name cannot be a relative-directory marker.")
    return release_name


def _write_zip(path: Path, release_name: str, release_files: Sequence[_ReleaseFile]) -> None:
    with zipfile.ZipFile(
        path, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for item in release_files:
            archive_name = PurePosixPath(release_name) / item.relative_path
            data = item.source_path.read_bytes()
            if len(data) != item.size or _sha256_bytes(data) != item.sha256:
                raise ReleaseBuildError(
                    f"Source file changed after validation: {item.relative_path.as_posix()}"
                )
            info = zipfile.ZipInfo(archive_name.as_posix(), date_time=ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED)


def _manifest_payload(
    *,
    release_name: str,
    archive_name: str,
    archive_sha256: str,
    release_files: Sequence[_ReleaseFile],
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "policy_version": POLICY_VERSION,
        "release_name": release_name,
        "archive": archive_name,
        "archive_sha256": archive_sha256,
        "file_count": len(release_files),
        "total_uncompressed_bytes": sum(item.size for item in release_files),
        "files": [
            {
                "path": item.relative_path.as_posix(),
                "size": item.size,
                "sha256": item.sha256,
            }
            for item in release_files
        ],
    }


def _write_text(path: Path, value: str) -> None:
    path.write_text(value, encoding="utf-8", newline="\n")


def build_release(
    source_root: Path,
    output_directory: Path,
    *,
    release_name: str | None = None,
) -> ReleaseArtifact:
    """Validate a source tree and atomically publish ZIP, manifest, and checksum files."""
    root = source_root.expanduser().resolve()
    output = output_directory.expanduser().resolve()
    name = _validate_release_name(release_name or root.name)

    release_files, findings = inspect_release_tree(root, output_directory=output)
    if findings:
        raise ReleasePolicyError(findings)
    if not release_files:
        raise ReleaseBuildError("No publishable files remain after exclusions.")

    output.mkdir(parents=True, exist_ok=True)
    archive_path = output / f"{name}.zip"
    manifest_path = output / f"{name}.manifest.json"
    checksum_path = output / f"{name}.sha256"

    with tempfile.TemporaryDirectory(prefix="release-build-", dir=output) as temporary:
        stage = Path(temporary)
        staged_archive = stage / archive_path.name
        staged_manifest = stage / manifest_path.name
        staged_checksum = stage / checksum_path.name

        _write_zip(staged_archive, name, release_files)
        archive_sha256 = _sha256_file(staged_archive)
        manifest = _manifest_payload(
            release_name=name,
            archive_name=archive_path.name,
            archive_sha256=archive_sha256,
            release_files=release_files,
        )
        _write_text(staged_manifest, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        _write_text(staged_checksum, f"{archive_sha256}  {archive_path.name}\n")

        os.replace(staged_archive, archive_path)
        os.replace(staged_manifest, manifest_path)
        os.replace(staged_checksum, checksum_path)

    return ReleaseArtifact(
        archive_path=archive_path,
        manifest_path=manifest_path,
        checksum_path=checksum_path,
        sha256=archive_sha256,
        file_count=len(release_files),
        total_bytes=sum(item.size for item in release_files),
    )


def _parser() -> argparse.ArgumentParser:
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description="Validate a publication tree and create a deterministic release bundle."
    )
    parser.add_argument("--source", type=Path, default=project_root)
    parser.add_argument("--output-dir", type=Path, default=project_root / "deliverables")
    parser.add_argument("--name", dest="release_name")
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Validate the source tree without writing release artifacts.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.check_only:
            release_files, findings = inspect_release_tree(
                args.source,
                output_directory=args.output_dir,
            )
            if findings:
                raise ReleasePolicyError(findings)
            if not release_files:
                raise ReleaseBuildError("No publishable files remain after exclusions.")
            print(f"Release check passed: {len(release_files)} file(s).")
            return 0

        artifact = build_release(
            args.source,
            args.output_dir,
            release_name=args.release_name,
        )
    except ReleaseBuildError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(f"Archive: {artifact.archive_path}")
    print(f"Manifest: {artifact.manifest_path}")
    print(f"SHA256: {artifact.sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
