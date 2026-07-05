from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest


class SoftwareInventoryGeneratorTests(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[1]
        self.generator = self.repo_root / "python" / "gen_software_components.py"

    def write_manifest(self, path: Path, vault_path: Path, obsidian_plugins: bool) -> None:
        manifest = "\n".join(
            [
                "title: Zettelkasten software inventory",
                "include_h1: false",
                f"vault_path: {json.dumps(vault_path.as_posix())}",
                f"obsidian_plugins: {str(obsidian_plugins).lower()}",
                "component_sections: []",
                "components: []",
                "sync_and_replication: []",
                "repository_file_sections: []",
                "repository_files: []",
                "",
            ]
        )
        path.write_text(manifest, encoding="utf-8")

    def write_plugin_manifest(
        self,
        vault_path: Path,
        plugin_id: str,
        name: str,
        description: str,
        version: str,
    ) -> None:
        plugin_dir = vault_path / ".obsidian" / "plugins" / plugin_id
        plugin_dir.mkdir(parents=True)
        (plugin_dir / "manifest.json").write_text(
            json.dumps(
                {
                    "id": plugin_id,
                    "name": name,
                    "description": description,
                    "version": version,
                }
            ),
            encoding="utf-8",
        )

    def run_generator(
        self,
        case_root: Path,
        manifest_name: str,
        *extra_args: str,
    ) -> subprocess.CompletedProcess[str]:
        command = [
            sys.executable,
            str(self.generator),
            "--manifest",
            manifest_name,
            "--repo",
            str(case_root),
        ]
        command.extend(extra_args)

        return subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_obsidian_plugins_true_reads_manifest_files(self):
        with tempfile.TemporaryDirectory() as directory:
            case_root = Path(directory)
            vault_path = case_root / "fake_vault"
            manifest_path = case_root / "MANIFEST.software.yaml"

            self.write_plugin_manifest(
                vault_path,
                "beta-plugin",
                "Beta Plugin",
                "Beta description",
                "0.4.5",
            )
            self.write_plugin_manifest(
                vault_path,
                "alpha-plugin",
                "Alpha Plugin",
                "Alpha description",
                "1.2.3",
            )
            self.write_manifest(manifest_path, vault_path, obsidian_plugins=True)

            result = self.run_generator(case_root, manifest_path.name)

            self.assertEqual(result.returncode, 0, result.stderr)
            output_path = case_root / "generated" / "Zettelkasten-software-inventory.md"
            self.assertTrue(output_path.is_file())
            self.assertFalse((case_root / "Zettelkasten-software-configuration.md").exists())

            markdown = output_path.read_text(encoding="utf-8")
            self.assertIn("## Obsidian plugins", markdown)
            self.assertIn("| Plugin | Description | Version |", markdown)
            self.assertIn("| Alpha Plugin | Alpha description | 1.2.3 |", markdown)
            self.assertIn("| Beta Plugin | Beta description | 0.4.5 |", markdown)
            self.assertLess(
                markdown.index("| Alpha Plugin | Alpha description | 1.2.3 |"),
                markdown.index("| Beta Plugin | Beta description | 0.4.5 |"),
            )

    def test_obsidian_plugins_false_omits_plugin_section(self):
        with tempfile.TemporaryDirectory() as directory:
            case_root = Path(directory)
            vault_path = case_root / "fake_vault"
            manifest_path = case_root / "MANIFEST.software.yaml"

            self.write_plugin_manifest(
                vault_path,
                "alpha-plugin",
                "Alpha Plugin",
                "Alpha description",
                "1.2.3",
            )
            self.write_plugin_manifest(
                vault_path,
                "beta-plugin",
                "Beta Plugin",
                "Beta description",
                "0.4.5",
            )
            self.write_manifest(manifest_path, vault_path, obsidian_plugins=False)

            result = self.run_generator(case_root, manifest_path.name)

            self.assertEqual(result.returncode, 0, result.stderr)
            output_path = case_root / "generated" / "Zettelkasten-software-inventory.md"
            self.assertTrue(output_path.is_file())
            self.assertFalse((case_root / "Zettelkasten-software-configuration.md").exists())

            markdown = output_path.read_text(encoding="utf-8")
            self.assertNotIn("## Obsidian plugins", markdown)
            self.assertNotIn("| Plugin | Description | Version |", markdown)
            self.assertNotIn("Alpha Plugin", markdown)
            self.assertNotIn("Beta Plugin", markdown)

    def test_manual_wiki_configuration_page_output_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            case_root = Path(directory)
            vault_path = case_root / "fake_vault"
            manifest_path = case_root / "MANIFEST.software.yaml"

            self.write_manifest(manifest_path, vault_path, obsidian_plugins=False)

            result = self.run_generator(
                case_root,
                manifest_path.name,
                "--out",
                "Zettelkasten-software-configuration.md",
            )

            self.assertEqual(result.returncode, 2)
            self.assertFalse((case_root / "Zettelkasten-software-configuration.md").exists())
            self.assertFalse(
                (case_root / "generated" / "Zettelkasten-software-inventory.md").exists()
            )
            self.assertIn(
                "Refusing to write manual Wiki page name: Zettelkasten-software-configuration.md",
                result.stderr,
            )
            self.assertIn(
                "The software generator writes only generated/Zettelkasten-software-inventory.md.",
                result.stderr,
            )

    def test_noncanonical_inventory_output_path_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            case_root = Path(directory)
            vault_path = case_root / "fake_vault"
            manifest_path = case_root / "MANIFEST.software.yaml"

            self.write_manifest(manifest_path, vault_path, obsidian_plugins=False)

            result = self.run_generator(
                case_root,
                manifest_path.name,
                "--out",
                "generated/not-the-inventory.md",
            )

            self.assertEqual(result.returncode, 2)
            self.assertFalse(
                (case_root / "generated" / "not-the-inventory.md").exists()
            )
            self.assertFalse(
                (case_root / "generated" / "Zettelkasten-software-inventory.md").exists()
            )
            self.assertFalse((case_root / "Zettelkasten-software-configuration.md").exists())
            self.assertIn(
                "Refusing to write non-canonical software inventory path:",
                result.stderr,
            )
            self.assertIn(
                "generated/not-the-inventory.md",
                result.stderr.replace("\\", "/"),
            )
            self.assertIn(
                "The software generator writes only generated/Zettelkasten-software-inventory.md.",
                result.stderr,
            )



if __name__ == "__main__":
    unittest.main()
