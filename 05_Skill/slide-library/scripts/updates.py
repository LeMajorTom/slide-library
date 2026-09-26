#!/usr/bin/env python3
"""Inspect releases. GitHub metadata reads are opt-in; no installation or execution."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener
from zipfile import ZipFile, BadZipFile

VERSION_FILE = Path(__file__).resolve().parents[1] / "version.json"
GITHUB_HOSTS = {"github.com", "release-assets.githubusercontent.com", "objects.githubusercontent.com"}


def github_base(repository):
    if not isinstance(repository, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Expected a GitHub repository in owner/name format")
    if repository.split("/")[1] in {".", ".."}:
        raise ValueError("Invalid GitHub repository name")
    return "https://github.com/" + repository


def validate_github_url(url):
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or parsed.hostname not in GITHUB_HOSTS or
            parsed.username or parsed.password or parsed.port not in {None, 443}):
        raise ValueError("Update request must stay on GitHub's HTTPS release hosts")


class GitHubRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_github_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_release(repository):
    url = github_base(repository) + "/releases/latest/download/release.json"
    request = Request(url, headers={"User-Agent": "Slide-Library-update-check", "Accept": "application/json"})
    with build_opener(GitHubRedirects()).open(request, timeout=15) as response:
        validate_github_url(response.geturl())
        payload = response.read(256 * 1024 + 1)
    if len(payload) > 256 * 1024:
        raise ValueError("Release metadata is too large")
    release = metadata(json.loads(payload))
    if release.get("github_repository") != repository:
        raise ValueError("Release repository does not match the configured publisher")
    packages = release.get("packages")
    entry = packages.get("skill") if isinstance(packages, dict) else None
    expected = "slide-library-skill-" + release["version"] + ".zip"
    if (not isinstance(entry, dict) or entry.get("filename") != expected or
            not isinstance(entry.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]) or
            type(entry.get("bytes")) is not int or not 0 < entry["bytes"] <= 50 * 1024 * 1024):
        raise ValueError("Invalid skill package in GitHub release metadata")
    return release


def version_tuple(value):
    if not isinstance(value, str) or not re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", value):
        raise ValueError("Expected a stable version in major.minor.patch format")
    return tuple(int(x) for x in value.split("."))


def metadata(data):
    if not isinstance(data, dict) or data.get("name") != "slide-library":
        raise ValueError("This is not a Slide Library release")
    version_tuple(data.get("version"))
    schema = data.get("workspace_schema_version")
    if type(schema) is not int or schema < 1:
        raise ValueError("Missing or invalid workspace schema version")
    return data


def read_metadata(path):
    path = Path(path)
    if path.stat().st_size > 256 * 1024:
        raise ValueError("Release metadata is too large")
    return metadata(json.loads(path.read_text(encoding="utf-8")))


def inspect_package(path):
    path = Path(path)
    if path.stat().st_size > 50 * 1024 * 1024:
        raise ValueError("Core skill ZIP exceeds inspection limits")
    with ZipFile(path, "r") as archive:
        entries = archive.infolist()
        names = [e.filename for e in entries]
        if len(entries) > 2000 or sum(e.file_size for e in entries) > 100 * 1024 * 1024:
            raise ValueError("Core skill ZIP exceeds inspection limits")
        if len(set(names)) != len(names):
            raise ValueError("Duplicate ZIP entries")
        for e in entries:
            p = PurePosixPath(e.filename)
            if (p.is_absolute() or ".." in p.parts or "\\" in e.filename or
                    not p.parts or p.parts[0] != "slide-library" or
                    stat.S_ISLNK(e.external_attr >> 16)):
                raise ValueError("Unexpected or unsafe ZIP entry")
        if "slide-library/SKILL.md" not in names or "slide-library/version.json" not in names:
            raise ValueError("Expected a versioned standalone Slide Library skill ZIP, not a plugin or profile")
        if archive.getinfo("slide-library/version.json").file_size > 256 * 1024:
            raise ValueError("Package metadata is too large")
        data = metadata(json.loads(archive.read("slide-library/version.json")))
        if archive.testzip() is not None:
            raise ValueError("ZIP integrity check failed")
    return data, hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_size


def check(installed, release_path=None, package_path=None, release_data=None):
    installed = metadata(installed)
    result = {"installed_version": installed["version"], "installation": "unchanged",
              "automatic_installation": False, "workspace_modified": False}
    if release_path is not None and release_data is not None:
        raise ValueError("Choose one release metadata source")
    if not release_path and not package_path and release_data is None:
        return dict(result, status="no_update_source",
                    message="No release was checked. Use --online for configured GitHub releases, or supply release.json/a skill ZIP.")
    release = read_metadata(release_path) if release_path else metadata(release_data) if release_data is not None else None
    checksum_status = "not_checked"
    if package_path:
        candidate, sha, size = inspect_package(package_path)
        if release:
            if (candidate["version"] != release["version"] or
                    candidate["workspace_schema_version"] != release["workspace_schema_version"]):
                raise ValueError("Package version or schema does not match the release metadata")
            packages = release.get("packages")
            if not isinstance(packages, dict) or not isinstance(packages.get("skill"), dict):
                raise ValueError("Release metadata is missing the skill package checksum")
            expected = packages["skill"]
            if expected.get("sha256") != sha or expected.get("bytes") != size:
                raise ValueError("Package checksum or size does not match the release metadata")
            checksum_status = "matches_supplied_manifest"
        result["package"] = str(Path(package_path).resolve())
    else:
        candidate = release
    installed_version, candidate_version = version_tuple(installed["version"]), version_tuple(candidate["version"])
    status = ("update_available" if candidate_version > installed_version else
              "same_version" if candidate_version == installed_version else "installed_newer")
    return dict(result, status=status, candidate_version=candidate["version"],
                workspace_schema_compatible=(installed["workspace_schema_version"] == candidate["workspace_schema_version"]),
                checksum=checksum_status, publisher_authenticity="not_verified",
                installation_route="manual_upload_in_claude_customize_skills")


def check_online(installed, package_path=None):
    repository = installed.get("github_repository")
    if not repository:
        return dict(check(installed), message="No GitHub repository is configured. Supply a release file or skill ZIP.")
    release = fetch_release(repository)
    result = check(installed, package_path=package_path, release_data=release)
    base = github_base(repository) + "/releases"
    result.update(checked_source=base + "/latest/download/release.json",
                  release_url=base + "/tag/v" + release["version"],
                  download_url=base + "/download/v" + release["version"] + "/" + release["packages"]["skill"]["filename"])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["version", "check"])
    parser.add_argument("--release", type=Path, help="Explicitly supplied release.json")
    parser.add_argument("--package", type=Path, help="Explicitly supplied standalone skill ZIP")
    parser.add_argument("--online", action="store_true", help="Read the configured GitHub release manifest (no credentials)")
    args = parser.parse_args()
    if args.online and (args.release or args.command != "check"):
        parser.error("--online is for check and cannot be combined with --release")
    try:
        installed = read_metadata(VERSION_FILE)
        result = (installed if args.command == "version" else check_online(installed, args.package)
                  if args.online else check(installed, args.release, args.package))
        print(json.dumps(result, indent=2))
    except URLError as exc:
        print(json.dumps({"status": "check_failed", "message": "GitHub release is unavailable. Check network access, repository visibility and whether a release exists.",
                          "installation": "unchanged"}), file=sys.stderr)
        return 1
    except (ValueError, OSError, BadZipFile, KeyError, RuntimeError) as exc:
        print(json.dumps({"status": "check_failed", "message": str(exc), "installation": "unchanged"}), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
