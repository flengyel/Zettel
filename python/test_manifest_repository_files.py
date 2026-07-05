"""Tests for MANIFEST.software.yaml repository-file coverage."""

from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPOSITORY_ROOT / "MANIFEST.software.yaml"
CHECKED_PREFIXES = ("python/", "scripts/", "doc/")
IGNORED_DIRECTORY_NAMES = {
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
}
IGNORED_SUFFIXES = {
    ".pyc",
    ".pyo",
}


def _strip_optional_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def manifest_repository_paths() -> set[str]:
    """Return repository_files paths from MANIFEST.software.yaml."""
    paths: set[str] = set()
    in_repository_files = False

    for raw_line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()

        if line == "repository_files:":
            in_repository_files = True
            continue

        if not in_repository_files:
            continue

        if line and not line.startswith("  "):
            break

        stripped = line.strip()
        if not stripped.startswith("- path:"):
            continue

        path = _strip_optional_quotes(stripped.removeprefix("- path:"))
        paths.add(path.replace("\\", "/"))

    return paths


def is_ignored_repository_file(path: Path) -> bool:
    if any(part in IGNORED_DIRECTORY_NAMES for part in path.parts):
        return True
    return path.suffix.lower() in IGNORED_SUFFIXES


def actual_repository_paths_under_checked_prefixes() -> set[str]:
    """Return actual files under the checked repository prefixes."""
    paths: set[str] = set()

    for prefix in CHECKED_PREFIXES:
        directory = REPOSITORY_ROOT / prefix.rstrip("/")
        if not directory.exists():
            continue

        for path in directory.rglob("*"):
            if not path.is_file():
                continue
            if is_ignored_repository_file(path.relative_to(REPOSITORY_ROOT)):
                continue
            paths.add(path.relative_to(REPOSITORY_ROOT).as_posix())

    return paths


def only_checked_prefixes(paths: set[str]) -> set[str]:
    return {path for path in paths if path.startswith(CHECKED_PREFIXES)}


def format_mismatch(missing_from_manifest: list[str], missing_from_repository: list[str]) -> str:
    lines = [
        "MANIFEST.software.yaml repository_files does not match files under python/, scripts/, and doc/.",
    ]

    if missing_from_manifest:
        lines.append("")
        lines.append("Files present in the repository but missing from MANIFEST.software.yaml:")
        lines.extend(f"  - {path}" for path in missing_from_manifest)

    if missing_from_repository:
        lines.append("")
        lines.append("Manifest entries under checked prefixes whose files are missing:")
        lines.extend(f"  - {path}" for path in missing_from_repository)

    return "\n".join(lines)


class ManifestRepositoryFileCoverageTests(unittest.TestCase):
    def test_manifest_matches_python_scripts_and_doc_files(self) -> None:
        manifest_paths = only_checked_prefixes(manifest_repository_paths())
        actual_paths = actual_repository_paths_under_checked_prefixes()

        missing_from_manifest = sorted(actual_paths - manifest_paths)
        missing_from_repository = sorted(manifest_paths - actual_paths)

        self.assertFalse(
            missing_from_manifest or missing_from_repository,
            format_mismatch(missing_from_manifest, missing_from_repository),
        )


if __name__ == "__main__":
    unittest.main()
