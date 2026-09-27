#!/usr/bin/env python3
"""Check the generated skill files, local links, ZIP layout and archive integrity."""
import hashlib
import json
from pathlib import Path
import re
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent


def check():
    plugin = ROOT / "slide-library"
    manifest = json.loads((plugin / ".claude-plugin/plugin.json").read_text())
    assert manifest["name"] == plugin.name
    skill = plugin / "skills/slide-library"
    text = (skill / "SKILL.md").read_text()
    header = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    assert header, "Missing skill frontmatter"
    # This skill intentionally uses only unquoted single-line name/description fields.
    fields = dict(line.split(": ", 1) for line in header.group(1).splitlines())
    assert set(fields) == {"name", "description"}
    assert fields["name"] == skill.name
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", fields["name"])
    assert 0 < len(fields["description"]) <= 200
    assert ": " not in fields["description"], "Quote a YAML value containing a colon"
    for path in skill.rglob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if "://" not in target:
                assert (path.parent / target.split("#")[0]).exists(), (path, target)
    commands = {p.stem for p in (plugin / "commands").glob("*.md")}
    assert commands == {"setup", "build", "update", "use", "list", "delete-setup", "restore", "export", "help", "version", "check-updates", "upgrade"}
    outputs = {}
    version = manifest["version"]
    release = json.loads((ROOT / "dist/release.json").read_text())
    assert release["version"] == version
    assert json.loads((skill / "version.json").read_text())["version"] == version
    for filename, required in [
        (f"slide-library-{version}.zip", ".claude-plugin/plugin.json"),
        (f"slide-library-skill-{version}.zip", "slide-library/SKILL.md")
    ]:
        path = ROOT / "dist" / filename
        with ZipFile(path) as archive:
            assert archive.testzip() is None
            names = archive.namelist()
            assert required in names
            assert not any(".." in Path(n).parts or Path(n).is_absolute() for n in names)
            assert not any("__pycache__" in n or n.endswith(".pyc") for n in names)
            assert not any(n.endswith((".pptx", ".png", ".jpg", ".eml")) for n in names), "No company source files belong in this release"
            embedded = "skills/slide-library/" if required.startswith(".claude") else "slide-library/"
            for source in skill.rglob("*"):
                if source.is_file():
                    rel = source.relative_to(skill).as_posix()
                    assert archive.read(embedded + rel) == source.read_bytes(), "Stale ZIP entry: " + rel
        outputs[filename] = {"bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        entry = release["packages"]["plugin" if required.startswith(".claude") else "skill"]
        assert entry == dict(outputs[filename], filename=filename)
    print(json.dumps({"valid": True, "skill_frontmatter": "passed", "local_links": "passed", "archives": outputs}, indent=2))


if __name__ == "__main__":
    check()
