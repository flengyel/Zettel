#!/usr/bin/env python3
"""Prepare Zettel wiki pages and README for a Pandoc book build.

Reads book.yaml, processes each listed source file, and writes rewritten
copies to a build directory. Chapter order determines cross-reference
direction, so nothing here needs to know where a target chapter sits.

Transformations, in order of application per file:

1. Remove GitHub's injected anchor lines ("[#purpose](#purpose)").
2. Demote every ATX heading by one level, skipping fenced code blocks.
3. Rewrite [[Page Name]] wikilinks to Pandoc internal links.
4. Rewrite absolute wiki URLs to internal links.
5. Emit a chapter heading from the book.yaml title.

Fenced-block tracking is what makes sed insufficient: README.md contains a
note-specification block whose lines begin with '#', and those must not move.
"""

import argparse
import pathlib
import re
import sys

import yaml

ANCHOR_LINE = re.compile(r"^\[#[-\w]+\]\(#[-\w]+\)\s*$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
ATX = re.compile(r"^(#{1,6})(\s+)(.*)$")
WIKILINK = re.compile(r"\[\[([^\]|]+?)\]\]")
WIKI_URL = re.compile(
    r"\[([^\]]+)\]\(https://github\.com/flengyel/Zettel/wiki/([-\w]+)\)"
)


def slug(text):
    """Pandoc's auto_identifiers slug for a heading or page name."""
    s = text.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    return s.strip("-")


def strip_anchor_lines(lines):
    return [ln for ln in lines if not ANCHOR_LINE.match(ln)]


def demote_headings(lines):
    """Add one '#' to each ATX heading outside fenced code blocks."""
    out = []
    fence = None
    for ln in lines:
        m = FENCE.match(ln)
        if m:
            token = m.group(1)[0]
            if fence is None:
                fence = token
            elif fence == token:
                fence = None
            out.append(ln)
            continue
        if fence is None:
            h = ATX.match(ln)
            if h and len(h.group(1)) < 6:
                ln = "#" + ln
        out.append(ln)
    return out


def strip_trailing_space(lines):
    """Remove trailing whitespace outside fenced code blocks.

    Two or more trailing spaces are a Markdown hard line break. Pandoc's
    HTML and EPUB writers emit <br/>, so stray trailing space breaks
    paragraphs mid-sentence. Inside fences the spaces may be significant:
    the Alphanumeric Index chapter documents index-entry lines whose two
    trailing spaces are part of the specified form.
    """
    out = []
    fence = None
    for ln in lines:
        m = FENCE.match(ln)
        if m:
            token = m.group(1)[0]
            if fence is None:
                fence = token
            elif fence == token:
                fence = None
            out.append(ln)
            continue
        out.append(ln.rstrip() if fence is None else ln)
    return out


def rewrite_links(lines, titles):
    """Point wikilinks and wiki URLs at chapter anchors within the book.

    Code fences are skipped: the configuration page and the README both
    show WikiLink and note-template syntax inside fenced blocks, and those
    examples are the subject matter, not links.
    """

    def wl(m):
        target = m.group(1).strip()
        key = slug(target)
        label = titles.get(key, target)
        return f"[{label}](#{key})"

    out = []
    fence = None
    for ln in lines:
        m = FENCE.match(ln)
        if m:
            token = m.group(1)[0]
            if fence is None:
                fence = token
            elif fence == token:
                fence = None
            out.append(ln)
            continue
        if fence is None:
            ln = WIKILINK.sub(wl, ln)
            ln = WIKI_URL.sub(lambda m: f"[{m.group(1)}](#{slug(m.group(2))})", ln)
        out.append(ln)
    return "\n".join(out)


def process(path, title, titles):
    raw = path.read_text(encoding="utf-8").splitlines()
    lines = demote_headings(strip_anchor_lines(raw))
    lines = strip_trailing_space(lines)
    body = rewrite_links(lines, titles)
    heading = f"# {title} {{#{slug(title)}}}\n"
    return heading + "\n" + body.strip() + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("book", type=pathlib.Path, help="book.yaml")
    ap.add_argument("--src", type=pathlib.Path, default=pathlib.Path("."))
    ap.add_argument("--out", type=pathlib.Path, default=pathlib.Path("build"))
    args = ap.parse_args()

    spec = yaml.safe_load(args.book.read_text(encoding="utf-8"))
    entries = list(spec.get("chapters", [])) + list(spec.get("appendices", []))

    # Anchor table: every slug a cross-reference might use for a chapter.
    titles = {}
    for e in entries:
        stem = pathlib.Path(e["file"]).stem
        titles[slug(stem)] = e["title"]
        titles[slug(stem.replace("-", " "))] = e["title"]
        titles[slug(e["title"])] = e["title"]

    args.out.mkdir(parents=True, exist_ok=True)
    written = []
    for e in entries:
        src = args.src / e["file"]
        if not src.exists():
            sys.exit(f"missing source: {src}")
        dst = args.out / e["file"]
        dst.write_text(process(src, e["title"], titles), encoding="utf-8")
        written.append(dst)

    for p in written:
        print(p)


if __name__ == "__main__":
    main()
