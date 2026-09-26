import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import URLError
from zipfile import ZipFile, ZipInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "05_Skill/slide-library/scripts"))
import updates


class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.installed = self.meta("0.1.2")

    def tearDown(self):
        self.temp.cleanup()

    def meta(self, version, schema=1):
        return {"name": "slide-library", "version": version, "workspace_schema_version": schema}

    def package(self, version="0.1.3", schema=1, extra=None):
        path = self.root / "candidate.zip"
        with ZipFile(path, "w") as z:
            z.writestr("slide-library/SKILL.md", "---\nname: slide-library\n---\n")
            z.writestr("slide-library/version.json", json.dumps(self.meta(version, schema)))
            z.writestr("slide-library/scripts/example.py", "raise RuntimeError('must not execute candidate code')")
            if extra:
                z.writestr(extra, "not executed")
        return path

    def release(self, version="0.1.3", package=None, schema=1):
        path = self.root / "release.json"
        data = self.meta(version, schema)
        if package:
            data["packages"] = {"skill": {"sha256": hashlib.sha256(package.read_bytes()).hexdigest(),
                                          "bytes": package.stat().st_size, "filename": package.name}}
        path.write_text(json.dumps(data))
        return path

    def test_missing_source_is_not_reported_current(self):
        result = updates.check(self.installed)
        self.assertEqual("no_update_source", result["status"])
        self.assertFalse(result["automatic_installation"])
        self.assertEqual([], list(self.root.iterdir()))

    def test_numeric_versions_and_downgrades(self):
        for version, expected in [("0.1.10", "update_available"), ("0.1.2", "same_version"),
                                  ("0.1.1", "installed_newer")]:
            result = updates.check(self.installed, self.release(version))
            self.assertEqual(expected, result["status"])

    def test_package_check_preserves_files_and_does_not_execute(self):
        package = self.package()
        release = self.release(package=package)
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        result = updates.check(self.installed, release, package)
        self.assertEqual("update_available", result["status"])
        self.assertEqual("matches_supplied_manifest", result["checksum"])
        self.assertEqual("unchanged", result["installation"])
        self.assertFalse(result["workspace_modified"])
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})

    def test_package_without_manifest_does_not_claim_publisher_verification(self):
        result = updates.check(self.installed, package_path=self.package())
        self.assertEqual("not_checked", result["checksum"])
        self.assertEqual("not_verified", result["publisher_authenticity"])

    def test_mismatched_hash_version_and_missing_checksum_rejected(self):
        package = self.package()
        release = self.release(package=package)
        with package.open("ab") as stream:
            stream.write(b"changed bytes")
        with self.assertRaisesRegex(ValueError, "checksum"):
            updates.check(self.installed, release, package)
        with self.assertRaisesRegex(ValueError, "version or schema"):
            updates.check(self.installed, self.release("0.1.4", package), package)
        with self.assertRaisesRegex(ValueError, "missing.*checksum"):
            updates.check(self.installed, self.release(), package)

    def test_workspace_schema_change_is_reported_without_migration(self):
        result = updates.check(self.installed, package_path=self.package(schema=2))
        self.assertFalse(result["workspace_schema_compatible"])
        self.assertFalse(result["workspace_modified"])

    def test_unexpected_product_or_version_rejected(self):
        for value in ["0.1.3-beta", "01.2.3", "latest", None]:
            with self.assertRaises(ValueError):
                updates.metadata(self.meta(value))
        with self.assertRaises(ValueError):
            updates.metadata(dict(self.meta("1.0.0"), name="other-skill"))

    def test_unsafe_archive_paths_and_symlinks_rejected(self):
        for name in ["../escape.py", "/slide-library/absolute.py", "slide-library/../escape.py",
                     "slide-library\\escape.py", ".claude-plugin/plugin.json"]:
            with self.assertRaisesRegex(ValueError, "ZIP entry"):
                updates.inspect_package(self.package(extra=name))
        link = ZipInfo("slide-library/link")
        link.create_system = 3
        link.external_attr = 0o120777 << 16
        with self.assertRaisesRegex(ValueError, "ZIP entry"):
            updates.inspect_package(self.package(extra=link))

    def remote_release(self):
        package = self.package()
        release = json.loads(self.release(package=package).read_text())
        release["github_repository"] = "example/slide-library"
        release["packages"]["skill"]["filename"] = "slide-library-skill-0.1.3.zip"
        return release

    def test_online_check_returns_version_specific_download(self):
        installed = dict(self.installed, github_repository="example/slide-library")
        with patch.object(updates, "fetch_release", return_value=self.remote_release()) as fetch:
            result = updates.check_online(installed)
        fetch.assert_called_once_with("example/slide-library")
        self.assertEqual("update_available", result["status"])
        self.assertEqual("https://github.com/example/slide-library/releases/download/v0.1.3/slide-library-skill-0.1.3.zip", result["download_url"])
        self.assertEqual("not_checked", result["checksum"])

    def test_remote_metadata_checks_publisher_and_package(self):
        data = self.remote_release()
        with patch.object(updates, "build_opener") as opener:
            response = opener.return_value.open.return_value.__enter__.return_value
            response.geturl.return_value = "https://release-assets.githubusercontent.com/asset"
            response.read.return_value = json.dumps(data).encode()
            self.assertEqual(data, updates.fetch_release("example/slide-library"))
            data["github_repository"] = "someone/else"
            response.read.return_value = json.dumps(data).encode()
            with self.assertRaisesRegex(ValueError, "repository"):
                updates.fetch_release("example/slide-library")
            data["github_repository"] = "example/slide-library"
            data["packages"]["skill"]["filename"] = "https://other.invalid/run.py"
            response.read.return_value = json.dumps(data).encode()
            with self.assertRaisesRegex(ValueError, "package"):
                updates.fetch_release("example/slide-library")

    def test_remote_size_and_redirect_limits(self):
        with patch.object(updates, "build_opener") as opener:
            response = opener.return_value.open.return_value.__enter__.return_value
            response.geturl.return_value = "https://github.com/example/slide-library/releases/asset"
            response.read.return_value = b" " * (256 * 1024 + 1)
            with self.assertRaisesRegex(ValueError, "too large"):
                updates.fetch_release("example/slide-library")
        for url in ["http://github.com/asset", "https://github.com.evil.invalid/asset", "https://user:secret@github.com/asset", "file:///tmp/asset"]:
            with self.assertRaises(ValueError):
                updates.GitHubRedirects().redirect_request(None, None, 302, "", {}, url)

    def test_online_failure_is_not_a_current_version_result(self):
        installed = dict(self.installed, github_repository="example/slide-library")
        with patch.object(updates, "fetch_release", side_effect=URLError("offline")):
            with self.assertRaises(URLError):
                updates.check_online(installed)
        self.assertEqual("no_update_source", updates.check_online(self.installed)["status"])

    def test_repository_path_validation(self):
        for repository in ["", "../repo", "owner/..", "owner/repo/extra", "https://github.com/owner/repo", "owner/repo?token=secret"]:
            with self.assertRaises(ValueError):
                updates.github_base(repository)


if __name__ == "__main__":
    unittest.main()
