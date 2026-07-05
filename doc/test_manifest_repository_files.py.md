# `python/test_manifest_repository_files.py`

## Purpose

`test_manifest_repository_files.py` checks that `MANIFEST.software.yaml` accounts for repository files under the `python/`, `scripts/`, and `doc/` directories.

The test compares the symmetric difference between files on disk and paths listed under `repository_files:` in the manifest. A failure means that a repository script, Python file, or documentation file was added or removed without updating the software inventory manifest.

## Usage

Run this test file directly from the repository root:

```powershell
python python\test_manifest_repository_files.py
```

Run all repository Python tests:

```powershell
python -m unittest discover -s python -p "test*.py"
```

## Test framework

The file uses Python's built-in `unittest` framework.

It reads `MANIFEST.software.yaml` with PyYAML, the same YAML parser used by `python/gen_software_components.py`.

It can be run directly because it ends with:

```python
if __name__ == "__main__":
    unittest.main()
```

## Directories checked

The test checks files under:

```text
python/
scripts/
doc/
```

It ignores generated Python cache files and common cache directories, including:

```text
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.pyc
*.pyo
```

## Current test

### `test_manifest_matches_python_scripts_and_doc_directories`

This test builds two sets:

1. actual files under `python/`, `scripts/`, and `doc/`;
2. manifest paths under `repository_files:` whose paths begin with `python/`, `scripts/`, or `doc/`.

It then compares the two sets.

## Assertions

The test fails if either side of the symmetric difference is non-empty.

A file is reported as missing from the manifest when it exists on disk but is not listed in `MANIFEST.software.yaml`.

A file is reported as missing from the filesystem when it is listed in `MANIFEST.software.yaml` but does not exist in the repository.

## Repository boundary

The test reads only the repository under test.

It does not use the private Zettelkasten vault.

It does not generate or modify the software inventory page.
