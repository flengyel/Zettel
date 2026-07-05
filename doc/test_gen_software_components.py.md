# `python/test_gen_software_components.py`

## Purpose

`test_gen_software_components.py` tests the software-inventory generator with a temporary repository case and a temporary fake Obsidian vault.

The tests verify the generator contract for Obsidian plugin inventory and protected output paths:

- when `obsidian_plugins: true` is set in `MANIFEST.software.yaml`, plugin metadata is read from `.obsidian/plugins/*/manifest.json` and written to the generated software inventory page;
- when `obsidian_plugins: false` is set, the generated page omits the Obsidian plugin section even if plugin manifests exist;
- attempts to write the manually authored Wiki configuration page are refused;
- attempts to write any non-canonical inventory output path are refused.

## Usage

Run this test file directly from the repository root:

```powershell
python python\test_gen_software_components.py
```

Run all repository Python tests:

```powershell
python -m unittest discover -s python -p "test*.py"
```

## Test framework

The file uses Python's built-in `unittest` framework and standard-library modules only.

It can be run directly because it ends with:

```python
if __name__ == "__main__":
    unittest.main()
```

## Temporary test case

Each test creates a temporary case root with:

```text
MANIFEST.software.yaml
fake_vault/.obsidian/plugins/alpha-plugin/manifest.json
fake_vault/.obsidian/plugins/beta-plugin/manifest.json
```

The generated output is written inside the temporary case root:

```text
generated/Zettelkasten-software-inventory.md
```

The protected manual Wiki page path is also tested inside the temporary case root:

```text
Zettelkasten-software-configuration.md
```

The non-canonical inventory output path is tested inside the temporary generated directory:

```text
generated/not-the-inventory.md
```

## Current tests

### `test_obsidian_plugins_true_reads_manifest_files`

This test writes two fake Obsidian plugin manifests:

```json
{"id":"alpha-plugin","name":"Alpha Plugin","description":"Alpha description","version":"1.2.3"}
```

```json
{"id":"beta-plugin","name":"Beta Plugin","description":"Beta description","version":"0.4.5"}
```

It writes a minimal `MANIFEST.software.yaml` with:

```yaml
obsidian_plugins: true
```

Then it runs:

```text
python/gen_software_components.py
```

against the temporary case root.

The test asserts that:

- the generator exits with status `0`;
- `generated/Zettelkasten-software-inventory.md` is created;
- `Zettelkasten-software-configuration.md` is not created;
- the generated page contains `## Obsidian plugins`;
- the plugin table header is `| Plugin | Description | Version |`;
- the generated page contains `| Alpha Plugin | Alpha description | 1.2.3 |`;
- the generated page contains `| Beta Plugin | Beta description | 0.4.5 |`;
- `Alpha Plugin` appears before `Beta Plugin`.

Expected plugin table fragment:

```markdown
## Obsidian plugins

Plugins installed inside the Obsidian vault.

| Plugin | Description | Version |
|---|---|---|
| Alpha Plugin | Alpha description | 1.2.3 |
| Beta Plugin | Beta description | 0.4.5 |
```

### `test_obsidian_plugins_false_omits_plugin_section`

This test writes the same fake plugin manifests, but writes a minimal `MANIFEST.software.yaml` with:

```yaml
obsidian_plugins: false
```

Then it runs:

```text
python/gen_software_components.py
```

against the temporary case root.

The test asserts that:

- the generator exits with status `0`;
- `generated/Zettelkasten-software-inventory.md` is created;
- `Zettelkasten-software-configuration.md` is not created;
- the generated page does not contain `## Obsidian plugins`;
- the generated page does not contain `| Plugin | Description | Version |`;
- the generated page does not contain `Alpha Plugin`;
- the generated page does not contain `Beta Plugin`.

### `test_manual_wiki_configuration_page_output_is_refused`

This test writes a minimal `MANIFEST.software.yaml` and then asks the generator to write the manually authored Wiki configuration page name:

```text
Zettelkasten-software-configuration.md
```

It runs:

```text
python/gen_software_components.py --out Zettelkasten-software-configuration.md
```

against the temporary case root.

The test asserts that:

- the generator exits with status `2`;
- `Zettelkasten-software-configuration.md` is not created;
- `generated/Zettelkasten-software-inventory.md` is not created as a side effect;
- standard error contains `Refusing to write manual Wiki page name: Zettelkasten-software-configuration.md`;
- standard error contains `The software generator writes only generated/Zettelkasten-software-inventory.md.`.

### `test_noncanonical_inventory_output_path_is_refused`

This test writes a minimal `MANIFEST.software.yaml` and then asks the generator to write a generated Markdown file whose path is not the canonical inventory path:

```text
generated/not-the-inventory.md
```

It runs:

```text
python/gen_software_components.py --out generated/not-the-inventory.md
```

against the temporary case root.

The test asserts that:

- the generator exits with status `2`;
- `generated/not-the-inventory.md` is not created;
- `generated/Zettelkasten-software-inventory.md` is not created as a side effect;
- `Zettelkasten-software-configuration.md` is not created;
- standard error contains `Refusing to write non-canonical software inventory path:`;
- standard error contains `generated/not-the-inventory.md`;
- standard error contains `The software generator writes only generated/Zettelkasten-software-inventory.md.`.


## Repository boundary

The test reads `python/gen_software_components.py` from the repository under test.

All generated files, fake plugin manifests, and temporary manifests are written under temporary directories created by `tempfile.TemporaryDirectory()`.

The test does not use the private Zettelkasten vault.
