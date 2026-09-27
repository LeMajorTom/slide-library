#!/usr/bin/env python3
"""Build the Claude plugin and standalone skill ZIPs from the same source."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
from zipfile import ZipFile, ZIP_DEFLATED

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "05_Skill/slide-library"
PLUGIN = HERE / "slide-library"
RELEASE = json.loads((SOURCE / "version.json").read_text())
VERSION = RELEASE["version"]


def archive(folder, output, prefix=""):
    with ZipFile(output, "w", ZIP_DEFLATED) as bundle:
        for path in sorted(folder.rglob("*")):
            if path.is_symlink():
                raise ValueError("Do not package symlinks")
            if path.is_file() and "__pycache__" not in path.parts and path.name != ".DS_Store":
                rel = path.relative_to(folder).as_posix()
                bundle.write(path, prefix + rel)


def main():
    # Test before replacing generated packages; never publish from a failing build.
    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(HERE / "tests")],
                   check=True, cwd=HERE.parent)
    if PLUGIN.exists():
        marker = PLUGIN / ".claude-plugin/plugin.json"
        if not marker.is_file() or json.loads(marker.read_text()).get("name") != "slide-library":
            raise ValueError("Refusing to replace an unrelated folder")
        shutil.rmtree(PLUGIN)
    (PLUGIN / ".claude-plugin").mkdir(parents=True)
    manifest = {"name": "slide-library", "version": VERSION,
                "description": "Build a personal slide library and design from mixed references, then complete rough slides in Claude for PowerPoint.",
                "author": {"name": "Slide Library"},
                "keywords": ["powerpoint", "presentations", "design", "content-library"]}
    (PLUGIN / ".claude-plugin/plugin.json").write_text(json.dumps(manifest, indent=2) + "\n")
    skill = PLUGIN / "skills/slide-library"
    shutil.copytree(SOURCE, skill, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))
    # An empty directory left by an earlier Codex draft is not a Claude component.
    empty_agents = skill / "agents"
    if empty_agents.exists() and not any(empty_agents.iterdir()):
        empty_agents.rmdir()
    commands = {
        "setup": "Create a personal slide workspace and learn references.",
        "build": "Complete rough PowerPoint slides or a chat outline.",
        "update": "Sort and learn new references, photos and documents.",
        "export": "Export a ready setup as a personal profile skill for PowerPoint.",
        "restore": "Restore an explicitly named archived setup without deleting files.",
        "version": "Show the active core skill version.",
        "check-updates": "Check GitHub Releases or compare a supplied release or skill ZIP.",
        "upgrade": "Check a new skill ZIP and guide its manual installation in Claude.",
        "list": "List accessible saved slide setups.",
        "use": "Select a saved slide setup or design profile.",
        "delete-setup": "Archive a named setup while preserving its source files.",
        "help": "Show Slide Library commands and starting examples."
    }
    (PLUGIN / "commands").mkdir()
    for name, description in commands.items():
        text = "---\ndescription: " + description + "\n---\n\n"
        text += "Read the Slide Library skill at " + "$" + "{CLAUDE_PLUGIN_ROOT}/skills/slide-library/SKILL.md.\n"
        text += "Run its " + name + " workflow using the user's arguments below.\n"
        text += "Check runtime capabilities, follow the command contract and report actual results.\n\n"
        text += "User arguments: $ARGUMENTS\n"
        (PLUGIN / "commands" / (name + ".md")).write_text(text)
    readme = (HERE / "README.md").read_text().replace("@VERSION@", VERSION)
    (PLUGIN / "README.md").write_text(readme)
    dist = HERE / "dist"
    dist.mkdir(exist_ok=True)
    plugin_zip = dist / ("slide-library-" + VERSION + ".zip")
    skill_zip = dist / ("slide-library-skill-" + VERSION + ".zip")
    archive(PLUGIN, plugin_zip)
    archive(skill, skill_zip, "slide-library/")
    checksums = []
    packages = {}
    for path in [plugin_zip, skill_zip]:
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        checksums.append(sha + "  " + path.name)
        packages["skill" if path == skill_zip else "plugin"] = {
            "filename": path.name, "sha256": sha, "bytes": path.stat().st_size}
        print(str(path) + " (" + str(path.stat().st_size) + " bytes)")
    (dist / "SHA256SUMS.txt").write_text("\n".join(checksums) + "\n")
    release = dict(RELEASE, packages=packages, distribution="github_releases")
    text = json.dumps(release, indent=2) + "\n"
    (dist / "release.json").write_text(text)
    (dist / ("release-" + VERSION + ".json")).write_text(text)
    subprocess.run([sys.executable, str(HERE / "validate_package.py")], check=True, cwd=HERE.parent)


if __name__ == "__main__":
    main()
