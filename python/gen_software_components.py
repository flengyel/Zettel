#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


def run_command(command: list[str], timeout: int = 8) -> str:
    if not command:
        return ""

    executable = shutil.which(command[0])
    if executable is None:
        return ""

    try:
        result = subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""

    text = (result.stdout or result.stderr).strip()
    return text.splitlines()[0].strip() if text else ""


def winget_version(package_id: str) -> str:
    if shutil.which("winget") is None:
        return ""

    try:
        result = subprocess.run(
            ["winget", "list", "--id", package_id, "--exact"],
            text=True,
            capture_output=True,
            check=False,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""

    for line in result.stdout.splitlines():
        if package_id not in line:
            continue

        # winget table output is not a stable API. This extracts the first
        # plausible version-looking token after the package id.
        tail = line.split(package_id, 1)[1]
        match = re.search(r"\b\d+(?:\.\d+)+(?:[-+.\w]*)?\b", tail)
        return match.group(0) if match else line.strip()

    return ""


def obsidian_plugin_version(vault_path: Path, plugin_id: str) -> str:
    manifest = vault_path / ".obsidian" / "plugins" / plugin_id / "manifest.json"
    if not manifest.is_file():
        return ""

    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""

    return str(data.get("version", "")).strip()


def probe_version(item: dict[str, Any]) -> str:
    probe = item.get("probe") or {}
    probe_type = probe.get("type")

    if probe_type == "command":
        return run_command(list(probe.get("command") or []))

    if probe_type == "winget":
        return winget_version(str(probe.get("id") or ""))

    if probe_type == "manual":
        return str(item.get("version") or "")

    return str(item.get("version") or "")


def repository_status(repo_root: Path, path_text: str) -> str:
    return "present" if (repo_root / path_text).exists() else "missing"


def split_repo_files(items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {
        "repository_support": [],
        "local_diagnostics": [],
        "historical": [],
    }

    for item in items:
        category = item.get("category", "repository_support")
        grouped.setdefault(category, []).append(item)

    return grouped


def render_markdown(data: dict[str, Any], repo_root: Path) -> str:
    vault_path = Path(str(data.get("vault_path", ""))).expanduser()
    grouped_files = split_repo_files(list(data.get("repository_files", [])))

    lines: list[str] = []

    lines.append(f"# {data.get('title', 'Zettelkasten software environment')}")
    lines.append("")
    lines.append("This page records the software environment and repository tools used with my digital Zettelkasten.")
    lines.append("")
    lines.append(f"Last checked: {data.get('last_checked', '')}")
    lines.append("")

    lines.append("## Zettelkasten software environment")
    lines.append("")
    lines.append("| Component | Role | Version probe |")
    lines.append("|---|---|---|")

    for item in data.get("external_software", []):
        version = probe_version(item) or "not detected"
        lines.append(f"| {item.get('name', '')} | {item.get('role', '')} | {version} |")

    lines.append("")
    lines.append("## Obsidian plugins")
    lines.append("")
    lines.append("| Plugin | Role | Version |")
    lines.append("|---|---|---|")

    for item in data.get("obsidian_plugins", []):
        plugin_id = str(item.get("id", ""))
        version = obsidian_plugin_version(vault_path, plugin_id) or "not detected"
        lines.append(f"| {item.get('name', plugin_id)} | {item.get('role', '')} | {version} |")

    lines.append("")
    lines.append("## Repository support tools")
    lines.append("")
    lines.append("These files support note creation, validation, export, or repository documentation.")
    lines.append("")
    lines.append("| Path | Role | Status |")
    lines.append("|---|---|---|")

    for item in grouped_files.get("repository_support", []):
        path = str(item.get("path", ""))
        status = repository_status(repo_root, path)
        lines.append(f"| `{path}` | {item.get('role', '')} | {status} |")

    lines.append("")
    lines.append("## Local diagnostics")
    lines.append("")
    lines.append("These files are local diagnostics. They may contain local paths and are not portable tools.")
    lines.append("")
    lines.append("| Path | Role | Status |")
    lines.append("|---|---|---|")

    for item in grouped_files.get("local_diagnostics", []):
        path = str(item.get("path", ""))
        status = repository_status(repo_root, path)
        lines.append(f"| `{path}` | {item.get('role', '')} | {status} |")

    historical = grouped_files.get("historical", [])
    if historical:
        lines.append("")
        lines.append("## Historical notes")
        lines.append("")
        lines.append("| Path | Role | Status |")
        lines.append("|---|---|---|")

        for item in historical:
            path = str(item.get("path", ""))
            status = repository_status(repo_root, path)
            lines.append(f"| `{path}` | {item.get('role', '')} | {status} |")

    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("Version probes are best-effort. GUI applications and Obsidian plugins may require manual correction.")
    lines.append("Repository-file status is generated by checking whether the listed file exists.")
    lines.append("")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the Zettelkasten software components Wiki page."
    )
    parser.add_argument(
        "--manifest",
        default="MANIFEST.software.yaml",
        help="software manifest YAML file",
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="repository root",
    )
    parser.add_argument(
        "--out",
        default="generated/Zettelkasten-software-components.md",
        help="output Markdown path",
    )

    args = parser.parse_args(argv)

    repo_root = Path(args.repo).resolve()
    manifest_path = (repo_root / args.manifest).resolve()
    output_path = (repo_root / args.out).resolve()

    if not manifest_path.is_file():
        print(f"Missing manifest: {manifest_path}", file=sys.stderr)
        return 2

    try:
        data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        print(f"Invalid YAML in {manifest_path}: {exc}", file=sys.stderr)
        return 2

    if not isinstance(data, dict):
        print(f"Manifest must contain a YAML mapping: {manifest_path}", file=sys.stderr)
        return 2

    markdown = render_markdown(data, repo_root)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())