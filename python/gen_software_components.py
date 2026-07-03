#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ctypes
import json
import os
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import yaml

DEFAULT_OUTPUT = "generated/Zettelkasten-software-inventory.md"
MANUAL_WIKI_PAGE_NAMES = {"Zettelkasten-software-configuration.md"}


@dataclass(frozen=True)
class Section:
    key: str
    heading: str
    description: str = ""


def generated_timestamp() -> str:
    """Return the local timestamp for this generator run."""
    return datetime.now().astimezone().isoformat(timespec="seconds")


def expand_path(raw_path: str) -> Path:
    """Expand Windows-style environment variables and return a Path."""
    return Path(os.path.expanduser(os.path.expandvars(raw_path)))


def first_existing_path(paths: Iterable[str]) -> Path | None:
    for raw_path in paths:
        if not raw_path:
            continue
        path = expand_path(str(raw_path))
        if path.exists():
            return path
    return None


def first_existing_file(paths: Iterable[str]) -> Path | None:
    for raw_path in paths:
        if not raw_path:
            continue
        path = expand_path(str(raw_path))
        if path.is_file():
            return path
    return None


def run_command(command: list[str], timeout: int = 8) -> str:
    """Run a CLI command and return the first output line.

    This is intended only for command-line tools such as pandoc, miktex, py,
    and git. Do not use command probes for GUI applications.
    """
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
        tail = line.split(package_id, 1)[1]
        match = re.search(r"\b\d+(?:\.\d+)+(?:[-+.\w]*)?\b", tail)
        return match.group(0) if match else line.strip()

    return ""


def read_json_version(paths: list[str]) -> str:
    path = first_existing_path(paths)
    if path is None or not path.is_file():
        return ""

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""

    return str(data.get("version", "")).strip()


def read_application_ini_version(paths: list[str]) -> str:
    path = first_existing_path(paths)
    if path is None or not path.is_file():
        return ""

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", ";")):
            continue
        if stripped.lower().startswith("version="):
            return stripped.split("=", 1)[1].strip()

    return ""


class _VS_FIXEDFILEINFO(ctypes.Structure):
    _fields_ = [
        ("dwSignature", ctypes.c_uint32),
        ("dwStrucVersion", ctypes.c_uint32),
        ("dwFileVersionMS", ctypes.c_uint32),
        ("dwFileVersionLS", ctypes.c_uint32),
        ("dwProductVersionMS", ctypes.c_uint32),
        ("dwProductVersionLS", ctypes.c_uint32),
        ("dwFileFlagsMask", ctypes.c_uint32),
        ("dwFileFlags", ctypes.c_uint32),
        ("dwFileOS", ctypes.c_uint32),
        ("dwFileType", ctypes.c_uint32),
        ("dwFileSubtype", ctypes.c_uint32),
        ("dwFileDateMS", ctypes.c_uint32),
        ("dwFileDateLS", ctypes.c_uint32),
    ]


def windows_exe_version(path: Path) -> str:
    """Read a Windows executable version resource without launching it."""
    if os.name != "nt" or not path.is_file():
        return ""

    try:
        version = ctypes.windll.version
        size = version.GetFileVersionInfoSizeW(str(path), None)
        if not size:
            return ""

        buffer = ctypes.create_string_buffer(size)
        if not version.GetFileVersionInfoW(str(path), 0, size, buffer):
            return ""

        pointer = ctypes.c_void_p()
        length = ctypes.c_uint()
        if not version.VerQueryValueW(buffer, "\\", ctypes.byref(pointer), ctypes.byref(length)):
            return ""

        if pointer.value is None:
            return ""

        info = _VS_FIXEDFILEINFO.from_address(pointer.value)
        if info.dwSignature != 0xFEEF04BD:
            return ""

        major = info.dwProductVersionMS >> 16
        minor = info.dwProductVersionMS & 0xFFFF
        build = info.dwProductVersionLS >> 16
        patch = info.dwProductVersionLS & 0xFFFF
        parts = [major, minor, build, patch]

        while len(parts) > 2 and parts[-1] == 0:
            parts.pop()

        return ".".join(str(part) for part in parts)
    except Exception:
        return ""


def nearby_metadata_version(exe_path: Path) -> str:
    """Look for common metadata files near a GUI executable.

    This avoids launching GUI programs. It works for some Electron apps and
    application.ini-based applications, but may legitimately fail.
    """
    app_dir = exe_path.parent
    json_candidates = [
        app_dir / "resources" / "app" / "package.json",
        app_dir / "resources" / "app.asar.unpacked" / "package.json",
        app_dir / "package.json",
    ]

    version = read_json_version([str(path) for path in json_candidates])
    if version:
        return version

    ini_candidates = [
        app_dir / "application.ini",
        app_dir.parent / "application.ini",
    ]
    return read_application_ini_version([str(path) for path in ini_candidates])


def file_version(paths: list[str]) -> str:
    """Return a GUI executable version/status without launching the executable."""
    path = first_existing_file(paths)
    if path is None:
        return ""

    version = nearby_metadata_version(path)
    if version:
        return version

    version = windows_exe_version(path)
    if version:
        return version

    return "installed; version unavailable"


def probe_version(item: dict[str, Any]) -> str:
    probe = item.get("probe") or {}
    probe_type = str(probe.get("type") or "").strip()
    fallback = str(item.get("version") or "").strip()

    if probe_type == "command":
        return run_command([str(part) for part in probe.get("command") or []]) or fallback

    if probe_type == "winget":
        return winget_version(str(probe.get("id") or "")) or fallback

    if probe_type == "manual":
        return fallback or "manual"

    if probe_type == "file_version":
        paths = probe.get("paths")
        if paths is None:
            paths = [probe.get("path", "")]
        return file_version([str(path) for path in paths]) or fallback

    if probe_type == "json_version":
        paths = probe.get("paths")
        if paths is None:
            paths = [probe.get("path", "")]
        return read_json_version([str(path) for path in paths]) or fallback

    if probe_type == "application_ini":
        paths = probe.get("paths")
        if paths is None:
            paths = [probe.get("path", "")]
        return read_application_ini_version([str(path) for path in paths]) or fallback

    return fallback


def read_obsidian_plugin_manifests(vault_path: Path) -> list[dict[str, str]]:
    plugins_dir = vault_path / ".obsidian" / "plugins"
    if not plugins_dir.is_dir():
        return []

    plugins: list[dict[str, str]] = []

    for manifest in sorted(plugins_dir.glob("*/manifest.json")):
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        if not isinstance(data, dict):
            continue

        plugin_id = str(data.get("id") or manifest.parent.name).strip()
        name = str(data.get("name") or plugin_id).strip()
        description = str(data.get("description") or "").strip()
        version = str(data.get("version") or "").strip()

        plugins.append(
            {
                "id": plugin_id,
                "name": name,
                "description": description,
                "version": version,
            }
        )

    return sorted(plugins, key=lambda item: item["name"].casefold())


def repository_status(repo_root: Path, path_text: str) -> str:
    return "present" if (repo_root / path_text).exists() else "missing"


def table_cell(value: Any) -> str:
    text = str(value or "").replace("\r\n", " ").replace("\r", " ").replace("\n", " ").strip()
    return text.replace("|", r"\|")


def section_list(raw_sections: list[dict[str, Any]], fallback: list[Section]) -> list[Section]:
    if not raw_sections:
        return fallback

    result: list[Section] = []
    for item in raw_sections:
        key = str(item.get("key") or "").strip()
        if not key:
            continue
        result.append(
            Section(
                key=key,
                heading=str(item.get("heading") or key).strip(),
                description=str(item.get("description") or "").strip(),
            )
        )

    return result or fallback


def grouped_by_key(
    items: list[dict[str, Any]], key_name: str, default: str
) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        grouped[str(item.get(key_name) or default)].append(item)
    return dict(grouped)


def render_component_section(lines: list[str], section: Section, items: list[dict[str, Any]]) -> None:
    if not items:
        return

    lines.append(f"## {section.heading}")
    lines.append("")
    if section.description:
        lines.append(section.description)
        lines.append("")

    lines.append("| Component | Role | Version/status |")
    lines.append("|---|---|---|")

    for item in items:
        version = probe_version(item) or "not detected"
        lines.append(
            "| "
            f"{table_cell(item.get('name', ''))} | "
            f"{table_cell(item.get('role', ''))} | "
            f"{table_cell(version)} |"
        )

    lines.append("")


def render_obsidian_plugins(lines: list[str], data: dict[str, Any], vault_path: Path) -> None:
    if data.get("obsidian_plugins") is not True:
        return

    plugins = read_obsidian_plugin_manifests(vault_path)

    lines.append("## Obsidian plugins")
    lines.append("")
    lines.append("Plugins installed inside the Obsidian vault.")
    lines.append("")

    if not plugins:
        lines.append("No Obsidian plugin manifests were found.")
        lines.append("")
        return

    lines.append("| Plugin | Description | Version |")
    lines.append("|---|---|---|")

    for item in plugins:
        lines.append(
            "| "
            f"{table_cell(item.get('name', ''))} | "
            f"{table_cell(item.get('description', ''))} | "
            f"{table_cell(item.get('version', 'not detected') or 'not detected')} |"
        )

    lines.append("")


def render_sync(lines: list[str], data: dict[str, Any]) -> None:
    items = list(data.get("sync_and_replication", []))
    if not items:
        return

    lines.append("## Sync and replication")
    lines.append("")
    lines.append(
        "These components replicate the Zettelkasten vault and belong to operational infrastructure."
    )
    lines.append("")
    lines.append("| Component | Host | Role | Version/status |")
    lines.append("|---|---|---|---|")

    for item in items:
        version = probe_version(item) or "manual"
        lines.append(
            "| "
            f"{table_cell(item.get('name', ''))} | "
            f"{table_cell(item.get('host', ''))} | "
            f"{table_cell(item.get('role', ''))} | "
            f"{table_cell(version)} |"
        )

    lines.append("")


def render_repository_files(lines: list[str], data: dict[str, Any], repo_root: Path) -> None:
    fallback_sections = [
        Section(
            "repository_support_files",
            "Repository support files",
            "Files that support note creation, validation, export, repository documentation, Wiki publishing, or bootstrapping.",
        ),
        Section(
            "local_diagnostics",
            "Local diagnostics",
            "Local scripts for inspecting the vault. These may contain local paths and are not portable tools.",
        ),
    ]
    sections = section_list(list(data.get("repository_file_sections", [])), fallback_sections)
    grouped = grouped_by_key(list(data.get("repository_files", [])), "category", "repository_support_files")

    for section in sections:
        items = grouped.get(section.key, [])
        if not items:
            continue

        lines.append(f"## {section.heading}")
        lines.append("")
        if section.description:
            lines.append(section.description)
            lines.append("")

        lines.append("| Path | Role | Status |")
        lines.append("|---|---|---|")

        for item in items:
            path = str(item.get("path", ""))
            status = repository_status(repo_root, path)
            lines.append(
                "| "
                f"`{table_cell(path)}` | "
                f"{table_cell(item.get('role', ''))} | "
                f"{table_cell(status)} |"
            )

        lines.append("")


def render_component_key(
    lines: list[str],
    sections_by_key: dict[str, Section],
    components_by_section: dict[str, list[dict[str, Any]]],
    rendered_component_sections: set[str],
    key: str,
) -> None:
    section = sections_by_key.get(key)
    if section is None:
        return

    render_component_section(lines, section, components_by_section.get(key, []))
    rendered_component_sections.add(key)


def render_remaining_component_sections(
    lines: list[str],
    component_sections: list[Section],
    components_by_section: dict[str, list[dict[str, Any]]],
    rendered_component_sections: set[str],
) -> None:
    for section in component_sections:
        if section.key in rendered_component_sections:
            continue
        render_component_section(lines, section, components_by_section.get(section.key, []))
        rendered_component_sections.add(section.key)


def component_context(data: dict[str, Any]) -> tuple[
    dict[str, Section], list[Section], dict[str, list[dict[str, Any]]]
]:
    default_component_sections = [
        Section(
            "zettelkasten_software",
            "Zettelkasten software",
            "Software used directly with the Zettelkasten.",
        ),
        Section(
            "export_software",
            "Export software",
            "Software used to export notes and work with LaTeX or PDF output.",
        ),
        Section(
            "repository_tools",
            "Repository tools",
            "Software used to maintain this repository and generated Wiki documentation. These tools are not required merely to use the Zettelkasten.",
        ),
    ]
    component_sections = section_list(
        list(data.get("component_sections", [])), default_component_sections
    )
    sections_by_key = {section.key: section for section in component_sections}
    components_by_section = grouped_by_key(
        list(data.get("components", [])), "section", "zettelkasten_software"
    )
    return sections_by_key, component_sections, components_by_section


def maybe_render_h1(lines: list[str], data: dict[str, Any], fallback_title: str) -> None:
    if data.get("include_h1", True):
        lines.append(f"# {data.get('title', fallback_title)}")
        lines.append("")


def render_notes(lines: list[str]) -> None:
    lines.append("## Notes")
    lines.append("")
    lines.append(
        "Version probes are best-effort. GUI application versions and add-on versions may require manual entry."
    )
    lines.append(
        "Obsidian plugin names, descriptions, and versions are read from the vault's "
        "`.obsidian/plugins/*/manifest.json` files when available."
    )
    lines.append("Repository-file status is generated by checking whether the listed file exists.")
    lines.append("")


def render_markdown(data: dict[str, Any], repo_root: Path, timestamp: str | None = None) -> str:
    vault_path = expand_path(str(data.get("vault_path", "")))
    lines: list[str] = []

    maybe_render_h1(lines, data, "Zettelkasten software inventory")

    lines.append(
        "This page records the software inventory, synchronization components, "
        "repository tools, and support files used with my digital Zettelkasten."
    )
    lines.append("")
    lines.append(f"Last checked: {timestamp or generated_timestamp()}")
    lines.append("")

    sections_by_key, component_sections, components_by_section = component_context(data)
    rendered_component_sections: set[str] = set()

    render_component_key(
        lines,
        sections_by_key,
        components_by_section,
        rendered_component_sections,
        "zettelkasten_software",
    )
    render_obsidian_plugins(lines, data, vault_path)
    render_component_key(
        lines,
        sections_by_key,
        components_by_section,
        rendered_component_sections,
        "export_software",
    )
    render_sync(lines, data)
    render_component_key(
        lines,
        sections_by_key,
        components_by_section,
        rendered_component_sections,
        "repository_tools",
    )
    render_remaining_component_sections(
        lines, component_sections, components_by_section, rendered_component_sections
    )
    render_repository_files(lines, data, repo_root)
    render_notes(lines)

    return "\n".join(lines)


def is_manual_wiki_page_output(path: Path) -> bool:
    return path.name in MANUAL_WIKI_PAGE_NAMES


def write_page(data: dict[str, Any], repo_root: Path, output_path: Path, timestamp: str | None = None) -> int:
    if is_manual_wiki_page_output(output_path):
        print(
            f"Refusing to write manual Wiki page name: {output_path.name}",
            file=sys.stderr,
        )
        print(
            "The software generator writes only Zettelkasten-software-inventory.md.",
            file=sys.stderr,
        )
        return 2

    markdown = render_markdown(data, repo_root, timestamp=timestamp)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    print(f"Wrote {output_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the Zettelkasten software inventory Wiki page."
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
        default=DEFAULT_OUTPUT,
        help="output Markdown path",
    )

    args = parser.parse_args(argv)
    repo_root = Path(args.repo).resolve()
    manifest_path = (repo_root / args.manifest).resolve()

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

    output_path = (repo_root / args.out).resolve()
    return write_page(data, repo_root, output_path, timestamp=generated_timestamp())


if __name__ == "__main__":
    raise SystemExit(main())
