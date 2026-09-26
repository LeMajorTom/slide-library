import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from publish_release import release_inputs


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.manifest = {"github_repository": "example/slide-library", "version": "0.1.3",
                         "packages": {"skill": {"filename": "skill.zip"}, "plugin": {"filename": "plugin.zip"}}}

    def test_release_includes_metadata_and_both_packages(self):
        names = release_inputs("example/slide-library", "v0.1.3", self.manifest)
        self.assertEqual(["skill.zip", "plugin.zip", "release.json", "release-0.1.3.json", "SHA256SUMS.txt"], names)

    def test_mismatched_tag_or_repository_cannot_publish(self):
        for repo, tag in [("other/repo", "v0.1.3"), ("example/slide-library", "v0.1.2"),
                          ("example/slide-library", "main")]:
            with self.assertRaises(ValueError):
                release_inputs(repo, tag, self.manifest)


if __name__ == "__main__":
    unittest.main()
