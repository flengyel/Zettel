# `python/zettel_diagnostics.py`

## Purpose

`zettel_diagnostics.py` is a read-only diagnostic script for Markdown Zettels. It replaces the older local graph scripts by combining validator-compatible issue counts, word-count data, Markdown summaries, CSV output, and optional Matplotlib PNG plots in one argument-driven command.

The script does not modify checked Markdown files. It rejects an output directory inside a supplied input directory so diagnostic artifacts are not accidentally written into the private vault.

## Replaces

The script replaces these older local diagnostics:

```text
python/zk_validation_stats.py
python/word_count_histogram.py
python/output.png
```

Those files contained hardcoded local paths, interactive plotting behavior, or generated local output. `zettel_diagnostics.py` accepts paths as command-line arguments and uses the current validator API.

## Usage

From the repository root, print a Markdown summary to standard output:

```powershell
python .\python\zettel_diagnostics.py C:\Users\fleng\Zettelkasten --no-index-links --no-index-inventory
```

Write Markdown and CSV artifacts outside the vault:

```powershell
python .\python\zettel_diagnostics.py C:\Users\fleng\Zettelkasten --no-index-links --out-dir $env:TEMP\zettel-diagnostics
```

Include Matplotlib plots:

```powershell
python .\python\zettel_diagnostics.py C:\Users\fleng\Zettelkasten --no-index-links --out-dir $env:TEMP\zettel-diagnostics --plots
```

Scan recursively while excluding subtrees:

```powershell
python .\python\zettel_diagnostics.py C:\Users\fleng\Zettelkasten --recursive --exclude "Templates/**" --exclude "Projects/**" --no-index-links --out-dir $env:TEMP\zettel-diagnostics
```

Return success after writing diagnostics even when issues are found:

```powershell
python .\python\zettel_diagnostics.py C:\Users\fleng\Zettelkasten --no-index-links --out-dir $env:TEMP\zettel-diagnostics --zero-exit
```

## Outputs

Without `--out-dir`, the script prints a Markdown summary to standard output.

When `--out-dir` is supplied, the script writes deterministic artifact names:

```text
zettel-diagnostics-summary.md
zettel-diagnostics-issue-counts.csv
zettel-diagnostics-issues.csv
zettel-diagnostics-file-diagnostics.csv
zettel-diagnostics-word-count-bins.csv
```

When `--plots` is also supplied, it writes PNG plots with Matplotlib:

```text
zettel-diagnostics-issue-counts.png
zettel-diagnostics-word-counts.png
```

Matplotlib is imported only when `--plots` is supplied. Seaborn is not required.

## Output boundary

The output directory must not be inside any supplied input directory. This prevents accidental writes into the private vault when the vault is passed as the input directory.

For example, this is refused:

```powershell
python .\python\zettel_diagnostics.py C:\Users\fleng\Zettelkasten --out-dir C:\Users\fleng\Zettelkasten\diagnostics
```

Use a temporary directory or another directory outside the vault instead.

## Validator compatibility

The script imports and uses current validator functions from `zettel_validate.py`:

```python
from zettel_validate import ZettelValidator, index_inventory_issues, iter_markdown_files
```

It supports the validator's current scan and index options:

```text
--recursive
--exclude
--no-index-links
--no-index-inventory
```

Validation failures and index-inventory failures are reported as inspectable artifacts rather than repaired. The script is diagnostic only.

## Exit status

```text
0  no validation or index-inventory failures, or --zero-exit was supplied
1  validation or index-inventory failures found
2  invocation error, missing path, no Markdown files, output-boundary violation, or missing Matplotlib for --plots
```
