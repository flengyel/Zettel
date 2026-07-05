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

    def run_generator(self, case_root: Path, manifest_name: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(self.generator),
                "--manifest",
                manifest_name,
                "--repo",
                str(case_root),
            ],
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


if __name__ == "__main__":
    unittest.main()
