"""Repair selected structural issues in completed Markdown Zettels.

The repair tool uses :class:`zettel_validate.ZettelValidator` before and after
repairs. Dry run is the default. Files are written only when ``--write`` is
supplied and the repair plan reduces the validation issue count.

The initial repair set is deliberately conservative:

* add a missing YAML ``id`` from the filename stem when the filename stem is a
  valid no-whitespace ID;
* add ``reference-section-title: References`` when that front-matter property
  is missing;
* normalize multiple spaces after the ID in the YAML ``title`` value to one
  separator space, but only when the filename stem and YAML ``id`` agree;
* repair an H1 that copied the complete YAML ``title`` value, but only when
  the filename stem and YAML ``id`` agree;
* append an empty ``## References`` section when the note lacks one and the
  document does not end inside an open fenced code block.

Exit status is 0 when every checked file is valid and no dry-run repairs are
pending, 1 when repairs are available or validation failures remain, and 2 for
invocation/path/write errors.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import Any, TextIO

import yaml

from zettel_validate import ValidationIssue, ZettelValidator, iter_markdown_files


_FRONT_MATTER_DELIMITER = "---"
_REFERENCE_SECTION_TITLE = "References"
_TOP_LEVEL_KEY_RE = re.compile(r"^([A-Za-z0-9_-]+)\s*:")
_REFERENCES_HEADING_RE = re.compile(
    r"^[ \t]{0,3}##[ \t]+References(?:[ \t]+#+[ \t]*)?$"
)
_H1_HEADING_RE = re.compile(
    r"^([ \t]{0,3})#[ \t]+(.+?)(?:[ \t]+#+[ \t]*)?$"
)
_FENCE_RE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})")


def _safe_for_stream(value: object, stream: TextIO) -> str:
    """Return a display string that can be encoded by stream."""

    text = str(value)
    encoding = getattr(stream, "encoding", None)
    if not encoding:
        return text

    try:
        text.encode(encoding)
    except UnicodeEncodeError:
        return text.encode(encoding, errors="backslashreplace").decode(encoding)
    except LookupError:
        return text.encode("ascii", errors="backslashreplace").decode("ascii")
    return text


def _safe_print(value: object = "", *, stream: TextIO) -> None:
    """Print one line without failing on narrow Windows code pages."""

    print(_safe_for_stream(value, stream), file=stream)


@dataclass(frozen=True, slots=True)
class ValidationSnapshot:
    """Validation result for one text version."""

    valid: bool
    issues: tuple[ValidationIssue, ...]

    @property
    def issue_count(self) -> int:
        return len(self.issues)


@dataclass(frozen=True, slots=True)
class RepairAction:
    """One deterministic repair action."""

    code: str
    description: str


@dataclass(frozen=True, slots=True)
class RepairPlan:
    """Before/after validation state for one file."""

    path: Path
    original_text: str
    repaired_text: str
    actions: tuple[RepairAction, ...]
    before: ValidationSnapshot
    after: ValidationSnapshot
    skip_reason: str = ""

    @property
    def changed(self) -> bool:
        return self.repaired_text != self.original_text and bool(self.actions)

    @property
    def improves(self) -> bool:
        return self.changed and self.after.issue_count < self.before.issue_count

    @property
    def blocked(self) -> bool:
        return self.changed and not self.improves


@dataclass(frozen=True, slots=True)
class RepairResult:
    """Write-mode result for one repair plan."""

    plan: RepairPlan
    written: bool
    write_error: str = ""


@dataclass(frozen=True, slots=True)
class _FrontMatterSplit:
    """A normalized Markdown file split at YAML front matter."""

    had_bom: bool
    newline: str
    lines: list[str]
    closing_index: int
    had_final_newline: bool


def _detect_newline(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def _normalize_text(text: str) -> tuple[bool, str]:
    had_bom = text.startswith("\ufeff")
    if had_bom:
        text = text[1:]
    return had_bom, text.replace("\r\n", "\n").replace("\r", "\n")


def _restore_text(
    *,
    had_bom: bool,
    normalized: str,
    newline: str,
    had_final_newline: bool,
) -> str:
    if had_final_newline and not normalized.endswith("\n"):
        normalized += "\n"
    if not had_final_newline:
        normalized = normalized.rstrip("\n")
    restored = normalized.replace("\n", newline)
    return "\ufeff" + restored if had_bom else restored


def _valid_filename_id(note_id: str) -> bool:
    return bool(note_id) and not any(
        character.isspace() or character in "/\\\0" for character in note_id
    )


def _filename_id(path: Path) -> str:
    name = path.name
    return name[:-3] if name.lower().endswith(".md") else path.stem


def _split_front_matter(text: str) -> _FrontMatterSplit | None:
    newline = _detect_newline(text)
    had_bom, normalized = _normalize_text(text)
    had_final_newline = normalized.endswith("\n")
    lines = normalized.split("\n")
    if had_final_newline:
        lines = lines[:-1]

    if not lines or lines[0].strip() != _FRONT_MATTER_DELIMITER:
        return None

    for index in range(1, len(lines)):
        if lines[index].strip() == _FRONT_MATTER_DELIMITER:
            return _FrontMatterSplit(
                had_bom=had_bom,
                newline=newline,
                lines=lines,
                closing_index=index,
                had_final_newline=had_final_newline,
            )

    return None


def _front_matter_keys(lines: Sequence[str]) -> set[str]:
    keys: set[str] = set()
    for line in lines:
        match = _TOP_LEVEL_KEY_RE.match(line)
        if match:
            keys.add(match.group(1))
    return keys


def _first_key_index(lines: Sequence[str], key: str) -> int | None:
    for index, line in enumerate(lines):
        match = _TOP_LEVEL_KEY_RE.match(line)
        if match and match.group(1) == key:
            return index
    return None


def _has_references_heading(normalized_text: str) -> bool:
    fence_character: str | None = None
    fence_length = 0

    for line in normalized_text.split("\n"):
        fence_match = _FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            if fence_character is None:
                fence_character = marker[0]
                fence_length = len(marker)
            elif marker[0] == fence_character and len(marker) >= fence_length:
                fence_character = None
                fence_length = 0
            continue

        if fence_character is None and _REFERENCES_HEADING_RE.match(line):
            return True

    return False



def _has_unclosed_fenced_code_block(normalized_text: str) -> bool:
    fence_character: str | None = None
    fence_length = 0

    for line in normalized_text.split("\n"):
        fence_match = _FENCE_RE.match(line)
        if not fence_match:
            continue

        marker = fence_match.group(1)
        if fence_character is None:
            fence_character = marker[0]
            fence_length = len(marker)
        elif marker[0] == fence_character and len(marker) >= fence_length:
            fence_character = None
            fence_length = 0

    return fence_character is not None



def _front_matter_mapping(lines: Sequence[str]) -> dict[str, Any] | None:
    """Return parsed top-level YAML mapping for repair guards."""

    try:
        parsed = yaml.safe_load("\n".join(lines))
    except yaml.YAMLError:
        return None

    if isinstance(parsed, dict):
        return parsed
    return None


def _h1_headings(body_lines: Sequence[str]) -> list[tuple[int, str, str]]:
    """Return visible H1 body-line indexes, indentation, and heading text."""

    h1_headings: list[tuple[int, str, str]] = []
    fence_character: str | None = None
    fence_length = 0

    for index, line in enumerate(body_lines):
        fence_match = _FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            if fence_character is None:
                fence_character = marker[0]
                fence_length = len(marker)
            elif marker[0] == fence_character and len(marker) >= fence_length:
                fence_character = None
                fence_length = 0
            continue

        if fence_character is None:
            h1_match = _H1_HEADING_RE.match(line)
            if h1_match:
                h1_headings.append(
                    (index, h1_match.group(1), h1_match.group(2).rstrip())
                )

    return h1_headings


def _id_and_title(
    note_path: Path,
    front_matter_lines: Sequence[str],
) -> tuple[str, str] | None:
    front_matter = _front_matter_mapping(front_matter_lines)
    if front_matter is None:
        return None

    note_id = front_matter.get("id")
    full_title = front_matter.get("title")
    if not isinstance(note_id, str) or not isinstance(full_title, str):
        return None

    if not _valid_filename_id(note_id):
        return None
    if _filename_id(note_path) != note_id:
        return None

    return note_id, full_title


def _replace_front_matter_line_value(
    front_matter_lines: list[str],
    key: str,
    value: str,
) -> bool:
    index = _first_key_index(front_matter_lines, key)
    if index is None:
        return False

    line = front_matter_lines[index]
    match = re.match(rf"^({re.escape(key)}\s*:\s*).*$", line)
    if match is None:
        return False

    front_matter_lines[index] = f"{match.group(1)}{value}"
    return True


def _normalize_title_separator_after_id(
    note_path: Path,
    front_matter_lines: list[str],
) -> RepairAction | None:
    """Normalize ``title: <ID>  <TITLE>`` to one separator space."""

    id_and_title = _id_and_title(note_path, front_matter_lines)
    if id_and_title is None:
        return None

    note_id, full_title = id_and_title
    match = re.fullmatch(rf"{re.escape(note_id)}[ \t]{{2,}}(.+?)\s*", full_title)
    if match is None:
        return None

    human_title = match.group(1).rstrip()
    if not human_title:
        return None

    normalized_title = f"{note_id} {human_title}"
    if not _replace_front_matter_line_value(
        front_matter_lines,
        "title",
        normalized_title,
    ):
        return None

    return RepairAction(
        "normalize_title_separator",
        "normalize front-matter title to one separator space after ID",
    )


def _repair_h1_copied_from_frontmatter_title(
    note_path: Path,
    front_matter_lines: Sequence[str],
    body_lines: list[str],
) -> RepairAction | None:
    """Repair ``# <ID> <TITLE>`` to ``# <TITLE>`` when unambiguous."""

    id_and_title = _id_and_title(note_path, front_matter_lines)
    if id_and_title is None:
        return None

    note_id, full_title = id_and_title
    clean_full_title = full_title.rstrip()
    title_prefix = f"{note_id} "
    if not clean_full_title.startswith(title_prefix):
        return None

    human_title = clean_full_title[len(title_prefix) :].rstrip()
    if not human_title:
        return None

    h1_headings = _h1_headings(body_lines)
    if len(h1_headings) != 1:
        return None

    h1_index, indentation, h1_text = h1_headings[0]
    h1_text = h1_text.rstrip()
    h1_copied_title = h1_text == clean_full_title
    h1_copied_title_with_noncanonical_separator = False
    h1_match = re.fullmatch(rf"{re.escape(note_id)}[ \t]+(.+?)", h1_text)
    if h1_match is not None:
        h1_copied_title_with_noncanonical_separator = (
            h1_match.group(1).rstrip() == human_title
        )

    if not h1_copied_title and not h1_copied_title_with_noncanonical_separator:
        return None

    body_lines[h1_index] = f"{indentation}# {human_title}"
    return RepairAction(
        "repair_h1_copied_frontmatter_title",
        "replace H1 copied from full front-matter title with title text after ID",
    )


def _append_references_section(normalized_text: str) -> str:
    stripped = normalized_text.rstrip("\n")
    if stripped:
        return f"{stripped}\n\n## References\n"
    return "## References\n"


def _validate_text(
    text: str,
    path: Path,
    *,
    check_index_links: bool,
) -> ValidationSnapshot:
    validator = ZettelValidator(check_index_links=check_index_links)
    validator.validate(text, fn=str(path), report=False)
    return ValidationSnapshot(valid=not validator.issues, issues=validator.issues)


def plan_repairs(
    path: Path | str,
    text: str,
    *,
    check_index_links: bool = True,
) -> RepairPlan:
    """Plan deterministic repairs for one note without writing it."""

    note_path = Path(path)
    before = _validate_text(text, note_path, check_index_links=check_index_links)

    if any(issue.code in {"invalid_yaml_header", "invalid_yaml"} for issue in before.issues):
        return RepairPlan(
            path=note_path,
            original_text=text,
            repaired_text=text,
            actions=(),
            before=before,
            after=before,
            skip_reason="front matter must be valid before automatic repair",
        )

    split = _split_front_matter(text)
    if split is None:
        return RepairPlan(
            path=note_path,
            original_text=text,
            repaired_text=text,
            actions=(),
            before=before,
            after=before,
            skip_reason="front matter was not repairable",
        )

    front_matter_lines = list(split.lines[1 : split.closing_index])
    body_lines = list(split.lines[split.closing_index + 1 :])
    keys = _front_matter_keys(front_matter_lines)
    actions: list[RepairAction] = []
    skip_reason = ""

    if "id" not in keys:
        note_id = _filename_id(note_path)
        if not _valid_filename_id(note_id):
            return RepairPlan(
                path=note_path,
                original_text=text,
                repaired_text=text,
                actions=(),
                before=before,
                after=before,
                skip_reason="filename stem is not a repairable ID",
            )
        title_index = _first_key_index(front_matter_lines, "title")
        insert_at = title_index if title_index is not None else 0
        front_matter_lines.insert(insert_at, f"id: {note_id}")
        actions.append(
            RepairAction(
                "add_id",
                f"add front-matter id from filename stem: {note_id}",
            )
        )

    if "reference-section-title" not in keys:
        title_index = _first_key_index(front_matter_lines, "title")
        id_index = _first_key_index(front_matter_lines, "id")
        if title_index is not None:
            insert_at = title_index + 1
        elif id_index is not None:
            insert_at = id_index + 1
        else:
            insert_at = len(front_matter_lines)
        front_matter_lines.insert(
            insert_at,
            f"reference-section-title: {_REFERENCE_SECTION_TITLE}",
        )
        actions.append(
            RepairAction(
                "add_reference_section_title",
                "add front-matter reference-section-title: References",
            )
        )

    title_separator_repair = _normalize_title_separator_after_id(
        note_path,
        front_matter_lines,
    )
    if title_separator_repair is not None:
        actions.append(title_separator_repair)

    h1_repair = _repair_h1_copied_from_frontmatter_title(
        note_path,
        front_matter_lines,
        body_lines,
    )
    if h1_repair is not None:
        actions.append(h1_repair)

    normalized = "\n".join(
        [_FRONT_MATTER_DELIMITER]
        + front_matter_lines
        + [_FRONT_MATTER_DELIMITER]
        + body_lines
    )
    if not _has_references_heading(normalized):
        if _has_unclosed_fenced_code_block(normalized):
            skip_reason = (
                "unclosed fenced code block prevents appending a visible "
                "## References section"
            )
        else:
            normalized = _append_references_section(normalized)
            actions.append(
                RepairAction(
                    "add_references_section",
                    "append empty ## References section",
                )
            )

    repaired_text = _restore_text(
        had_bom=split.had_bom,
        normalized=normalized,
        newline=split.newline,
        had_final_newline=split.had_final_newline,
    )
    if not actions:
        repaired_text = text

    after = _validate_text(repaired_text, note_path, check_index_links=check_index_links)
    return RepairPlan(
        path=note_path,
        original_text=text,
        repaired_text=repaired_text,
        actions=tuple(actions),
        before=before,
        after=after,
        skip_reason=skip_reason,
    )


def apply_plan(plan: RepairPlan) -> RepairResult:
    """Write a repair plan only when it improves validation."""

    if not plan.improves:
        return RepairResult(plan=plan, written=False)
    try:
        plan.path.write_text(plan.repaired_text, encoding="utf-8")
    except OSError as exc:
        return RepairResult(plan=plan, written=False, write_error=str(exc))
    return RepairResult(plan=plan, written=True)


def print_plan(
    plan: RepairPlan,
    *,
    written: bool,
    stream: TextIO,
) -> None:
    if plan.actions:
        if written:
            verb = "applied"
        elif plan.blocked:
            verb = "blocked"
        else:
            verb = "would apply"
        _safe_print(f"{plan.path}: {verb} {len(plan.actions)} repair(s):", stream=stream)
        for action in plan.actions:
            _safe_print(f"  - [{action.code}] {action.description}", stream=stream)
    elif plan.skip_reason:
        _safe_print(f"{plan.path}: no safe repair: {plan.skip_reason}", stream=stream)
    else:
        _safe_print(f"{plan.path}: no repairs needed", stream=stream)

    _safe_print(
        f"{plan.path}: validation issues before={plan.before.issue_count}, "
        f"after={plan.after.issue_count}",
        stream=stream,
    )
    if plan.after.issues:
        _safe_print(f"{plan.path}: remaining validation issue(s) after repair plan:", stream=stream)
        for issue in plan.after.issues:
            _safe_print(f"  {issue}", stream=stream)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Repair selected structural issues in Markdown Zettels."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="Markdown files or directories; directories mean their root only unless --recursive is supplied",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="write repairable files whose repair plan reduces validation issues; default is dry run",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="search supplied directories recursively",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="GLOB",
        help="exclude a relative path or filename matching GLOB; may be repeated",
    )
    parser.add_argument(
        "--no-index-links",
        action="store_true",
        help="validate before and after repairs without requiring alphabetic-index links",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="suppress per-file output and print only the summary",
    )
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    expanded_paths = [path.expanduser() for path in args.paths]
    nonexistent = [path for path in expanded_paths if not path.exists()]
    if nonexistent:
        for path in nonexistent:
            _safe_print(f"zettel_repair.py: path not found: {path}", stream=stderr)
        return 2

    files = list(
        iter_markdown_files(
            expanded_paths,
            args.exclude,
            recursive=args.recursive,
        )
    )
    if not files:
        _safe_print("zettel_repair.py: no Markdown files found", stream=stderr)
        return 2

    check_index_links = not args.no_index_links
    would_change_count = 0
    written_count = 0
    blocked_count = 0
    invalid_after_count = 0
    write_errors = 0

    for path in files:
        expanded_path = path.expanduser()
        try:
            text = expanded_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            _safe_print(f"{expanded_path}: could not read file: {exc}", stream=stderr)
            write_errors += 1
            continue

        plan = plan_repairs(expanded_path, text, check_index_links=check_index_links)
        result = RepairResult(plan=plan, written=False)
        if args.write and plan.changed:
            result = apply_plan(plan)
            if result.write_error:
                _safe_print(f"{expanded_path}: could not write file: {result.write_error}", stream=stderr)
                write_errors += 1
        elif plan.changed:
            would_change_count += 1

        if result.written:
            written_count += 1
        if plan.blocked:
            blocked_count += 1
        if plan.after.issues:
            invalid_after_count += 1

        if not args.quiet:
            print_plan(plan, written=result.written, stream=stdout)

    if args.write:
        _safe_print(
            f"Checked {len(files)} file(s): {written_count} written, "
            f"{blocked_count} blocked, {invalid_after_count} invalid after repair.",
            stream=stdout,
        )
    else:
        _safe_print(
            f"Checked {len(files)} file(s): {would_change_count} would change, "
            f"{blocked_count} blocked, {invalid_after_count} invalid after repair plan.",
            stream=stdout,
        )

    if write_errors:
        return 2
    if would_change_count or blocked_count or invalid_after_count:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
