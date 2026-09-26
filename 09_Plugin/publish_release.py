#!/usr/bin/env python3
"""Publish the checked packages from a matching GitHub Actions version tag."""
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent


def release_inputs(repository, tag, manifest):
    if repository != manifest.get("github_repository"):
        raise ValueError("Repository differs from the configured update source")
    if tag != "v" + manifest["version"]:
        raise ValueError("Version tag differs from the package version")
    names = [manifest["packages"][key]["filename"] for key in ("skill", "plugin")]
    names += ["release.json", "release-" + manifest["version"] + ".json", "SHA256SUMS.txt"]
    return names


def main():
    from validate_package import check
    check()
    dist = HERE / "dist"
    manifest = json.loads((dist / "release.json").read_text())
    repository, tag = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_REF_NAME")
    if os.environ.get("GITHUB_ACTIONS") != "true" or os.environ.get("GITHUB_REF_TYPE") != "tag":
        raise ValueError("Publishing requires the GitHub Actions tag workflow")
    names = release_inputs(repository, tag, manifest)
    paths = [dist / name for name in names]
    if not all(path.is_file() for path in paths):
        raise ValueError("Release assets are incomplete")
    notes = dist / "release-notes.md"
    notes.write_text("\n".join("- " + item for item in manifest["release_notes"]) +
                     "\n\nUpload the standalone skill ZIP under Claude Customize > Skills. "
                     "Core updates preserve your separate workspace and personal profile.\n")
    # Keep the release hidden until every asset upload has completed successfully.
    subprocess.run(["gh", "release", "create", tag, "--repo", repository, "--verify-tag", "--draft",
                    "--title", "Slide Library " + manifest["version"], "--notes-file", str(notes)] +
                   [str(path) for path in paths], check=True)
    subprocess.run(["gh", "release", "edit", tag, "--repo", repository,
                    "--draft=false", "--latest"], check=True)


if __name__ == "__main__":
    main()
