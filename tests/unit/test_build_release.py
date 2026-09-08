from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import pytest

from scripts.build_release import (
    ReleasePolicyError,
    build_release,
    inspect_release_tree,
    main,
)


def _write(path: Path, value: str = "clean publication content\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_builds_deterministic_bundle_with_manifest_and_checksum(tmp_path: Path) -> None:
    source = tmp_path / "portfolio"
    destination = source / "deliverables"
    _write(source / "README.md", "# Evidence-led growth portfolio\n")
    _write(source / "src" / "analysis.py", "VALUE = 42\n")

    marker = "excluded build artifact"
    assigned_value = "api_" + "key" + " = '1234567890abcdef'\n"
    for relative, value in (
        (Path(".git/config"), marker),
        (Path(".env.production"), assigned_value),
        (Path(".pytest_cache/state"), marker),
        (Path("coverage.xml"), marker),
        (Path("node_modules/pkg/index.js"), marker),
        (Path("output/debug.txt"), marker),
        (Path("pytest-results.xml"), marker),
        (Path("data/local.duckdb"), marker),
        (Path("playwright-report/index.html"), marker),
        (Path("test-results/trace.zip"), marker),
    ):
        _write(source / relative, value)

    first = build_release(source, destination, release_name="growth-portfolio")
    first_archive_bytes = first.archive_path.read_bytes()
    second = build_release(source, destination, release_name="growth-portfolio")

    assert second.archive_path.read_bytes() == first_archive_bytes
    assert first.file_count == 2
    assert first.sha256 == _sha256(first.archive_path)
    assert first.checksum_path.read_text(encoding="utf-8") == (
        f"{first.sha256}  growth-portfolio.zip\n"
    )

    manifest = json.loads(first.manifest_path.read_text(encoding="utf-8"))
    assert manifest["archive_sha256"] == first.sha256
    assert manifest["file_count"] == 2
    assert [item["path"] for item in manifest["files"]] == ["README.md", "src/analysis.py"]
    assert all("Users" not in json.dumps(item) for item in manifest["files"])

    with zipfile.ZipFile(first.archive_path) as archive:
        assert archive.namelist() == [
            "growth-portfolio/README.md",
            "growth-portfolio/src/analysis.py",
        ]
        assert archive.read("growth-portfolio/src/analysis.py") == b"VALUE = 42\n"
        assert all(info.date_time == (1980, 1, 1, 0, 0, 0) for info in archive.infolist())


def test_keeps_safe_environment_templates_but_excludes_local_environment(tmp_path: Path) -> None:
    source = tmp_path / "portfolio"
    destination = tmp_path / "release"
    _write(source / "README.md")
    _write(source / ".env.example", "APP_MODE=example-only\n")
    _write(source / ".env", "APP_MODE=private-local-value\n")
    _write(source / "web" / ".env.local", "VITE_API_BASE_URL=http://127.0.0.1:8000\n")

    artifact = build_release(source, destination, release_name="safe-template")

    with zipfile.ZipFile(artifact.archive_path) as archive:
        names = archive.namelist()
        assert "safe-template/.env.example" in names
        assert "safe-template/.env" not in names
        assert "safe-template/web/.env.local" not in names


def test_excludes_worktree_git_pointer_file(tmp_path: Path) -> None:
    source = tmp_path / "worktree"
    _write(source / "README.md")
    local_value = "gitdir: " + "C:" + "/" + "Users" + "/example/project/.git/worktrees/release\n"
    _write(source / ".git", local_value)
    artifact = build_release(source, tmp_path / "release", release_name="worktree-source")
    with zipfile.ZipFile(artifact.archive_path) as archive:
        assert archive.namelist() == ["worktree-source/README.md"]


def test_rejects_local_absolute_path_without_writing_outputs(tmp_path: Path) -> None:
    source = tmp_path / "portfolio"
    destination = tmp_path / "release"
    local_value = "C:" + "\\Users\\someone\\Desktop\\draft.csv"
    _write(source / "README.md", local_value)

    with pytest.raises(ReleasePolicyError) as error:
        build_release(source, destination)

    assert [(item.category, item.path, item.line) for item in error.value.findings] == [
        ("local_absolute_path", "README.md", 1)
    ]
    assert not destination.exists()


def test_rejects_assigned_credential_without_echoing_value(tmp_path: Path) -> None:
    source = tmp_path / "portfolio"
    destination = tmp_path / "release"
    private_value = "ultra-private-value-123456"
    assignment = "client_" + "secret" + f" = '{private_value}'\n"
    _write(source / "settings.txt", assignment)

    with pytest.raises(ReleasePolicyError) as error:
        build_release(source, destination)

    assert error.value.findings[0].category == "assigned_credential"
    assert private_value not in str(error.value)
    assert not destination.exists()


def test_check_only_returns_nonzero_and_does_not_create_output(tmp_path: Path) -> None:
    source = tmp_path / "portfolio"
    destination = tmp_path / "release"
    setting_name = "client_" + "secret"
    setting_value = "private-" + "value-123456"
    _write(source / "settings.ini", f"{setting_name} = '{setting_value}'\n")

    exit_code = main(
        [
            "--source",
            str(source),
            "--output-dir",
            str(destination),
            "--check-only",
        ]
    )

    assert exit_code == 2
    assert not destination.exists()


def test_allows_explicit_placeholder_but_rejects_real_value(tmp_path: Path) -> None:
    source = tmp_path / "portfolio"
    placeholder_name = "auth_" + "token"
    _write(source / "example.txt", placeholder_name + " = 'replace-me'\n")

    _, findings = inspect_release_tree(source)

    assert findings == []


def test_rejects_unquoted_assigned_value(tmp_path: Path) -> None:
    source = tmp_path / "portfolio"
    variable_name = "access_" + "token"
    _write(source / "settings.ini", variable_name + " = abcdefghijklmnopqrstuvwx\n")

    _, findings = inspect_release_tree(source)

    assert [(item.category, item.path) for item in findings] == [
        ("assigned_credential", "settings.ini")
    ]
