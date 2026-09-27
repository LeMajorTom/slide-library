"""End-to-end helper workflow and regressions for reference/profile integrity."""
import base64
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

SCRIPTS = Path(__file__).resolve().parents[2] / "05_Skill/slide-library/scripts"
sys.path.insert(0, str(SCRIPTS))
import library
import workspace as w


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve() / "Workspace with spaces"
        w.setup(self.root, "Example Company")

    def tearDown(self):
        self.temp.cleanup()

    def cli(self, command, *args):
        run = subprocess.run([sys.executable, str(SCRIPTS / "workspace.py"), command,
                              "--root", str(self.root), *map(str, args)], capture_output=True, text=True)
        self.assertEqual(0, run.returncode, run.stderr)
        return json.loads(run.stdout)

    def design(self):
        return {"name": "Synthetic design", "status": "ready", "source_ids": [],
                "visual_review": "Synthetic test specification, not a real slide inspection",
                "rules": {"slide_cm": {"width": 30, "height": 20},
                          "content": {"x": 1, "y": 3, "w": 28, "bottom": 18},
                          "font": "Arial", "colors": {"primary": "224466"}}, "patterns": []}

    def content(self):
        path = self.root / "00_Throw_In/company.txt"
        path.write_text("Example Company provides manufacturing services.")
        plan = {"files": {i["candidate_id"]: {"scope": "reusable"} for i in w.scan(self.root)["files"]}}
        imported = w.import_files(self.root, plan)["imported"][0]
        return {"id": "company-example", "label": "Example Company", "kind": "company",
                "scope": "reusable", "status": "source_grounded", "facts": [
                    {"id": "services", "text": path.name, "evidence": [{"source_id": imported["source_id"],
                     "paragraph": 1, "quote": "provides manufacturing services"}]}]}

    def test_cli_curate_search_export_restore(self):
        record = self.content()
        record["facts"][0]["text"] = "Provides manufacturing services."
        capture = Path(self.temp.name) / "records.json"
        capture.write_text(json.dumps([record]))
        self.assertEqual(["company-example"], self.cli("save-records", "--file", capture)["saved"])
        self.assertEqual("company-example", library.search(self.root / "02_Library", "manufacturing")[0]["id"])
        capture.write_text(json.dumps(self.design()))
        self.cli("save-design", "--file", capture)
        self.cli("finalize")
        output = Path(self.temp.name) / "profile.zip"
        exported = self.cli("export", "--out", output)
        with ZipFile(output) as archive:
            prefix = exported["skill_name"] + "/"
            records = json.loads(archive.read(prefix + "content.json"))
            self.assertEqual(record, {k: v for k, v in records[0].items() if k != "assets"})
            self.assertEqual("224466", json.loads(archive.read(prefix + "design/profile.json"))["rules"]["colors"]["primary"])
            self.assertTrue(archive.read(prefix + "SKILL.md").startswith(b"---\n"))
            sources = json.loads(archive.read(prefix + "sources.json"))
            sid = record["facts"][0]["evidence"][0]["source_id"]
            self.assertEqual("company.txt", sources[sid]["filename"])
            self.assertEqual(64, len(sources[sid]["sha256"]))
            self.assertNotIn("snapshot", sources[sid])
            self.assertFalse(any("extract.json" in name or "source.txt" in name for name in archive.namelist()))
        self.cli("archive", "--name", "Example Company")
        self.cli("restore", "--name", "Example Company")
        self.assertEqual("draft", w.require(self.root)["status"])
        self.assertTrue((self.root / "01_Examples/Documents/company.txt").is_file())

    def test_record_batch_rollback_and_previous_version(self):
        record = self.content()
        w.save_records(self.root, record)
        path = self.root / "02_Library/records/company-example.json"
        before = path.read_bytes()
        invalid = json.loads(before)
        invalid["facts"][0]["evidence"][0]["quote"] = "fabricated claim"
        new = dict(record, id="new-company")
        with self.assertRaisesRegex(ValueError, "quote not found"):
            w.save_records(self.root, [new, invalid])
        self.assertEqual(before, path.read_bytes())
        self.assertFalse((path.parent / "new-company.json").exists())
        record["label"] = "Updated display name"
        w.save_records(self.root, record)
        self.assertEqual(before, next((self.root / "02_Library/.versions").glob("*.json")).read_bytes())

    def test_portable_photo_provenance_and_unresolved_exclusion(self):
        png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a7WQAAAAASUVORK5CYII=")
        for name, data in [("portrait.png", png), ("unlabeled.png", png + b"fixture")]:
            (self.root / "00_Throw_In" / name).write_bytes(data)
        plan = {"files": {i["candidate_id"]: {"scope": "reusable"} for i in w.scan(self.root)["files"]}}
        w.import_files(self.root, plan)
        assets = list(w.refresh_assets(self.root)["assets"].values())
        portrait = next(a for a in assets if a["path"].endswith("/portrait.png"))
        w.labels(self.root, {portrait["id"]: {"status": "source_labeled", "label": "Fictional test person",
                 "entity_id": "person-test", "evidence": "Fixture caption explicitly labels portrait.png",
                 "use": "portrait"}})
        w.save_design(self.root, self.design())
        exported = w.export_profile(self.root, Path(self.temp.name) / "photo-profile.zip")
        with ZipFile(exported["package"]) as archive:
            prefix = exported["skill_name"] + "/"
            packed = json.loads(archive.read(prefix + "assets.json"))
            self.assertEqual(1, len(packed))
            self.assertEqual(portrait["id"], packed[0]["id"])
            self.assertEqual(png, archive.read(prefix + packed[0]["path"]))
            sources = json.loads(archive.read(prefix + "sources.json"))
            self.assertEqual("portrait.png", sources[portrait["source_id"]]["filename"])
            self.assertEqual(portrait["sha256"], sources[portrait["source_id"]]["sha256"])
        # A new process can reload the on-disk mapping and reimport without losing it.
        self.assertEqual([], self.cli("import")["imported"])
        saved = w.load(self.root, "02_Library/assets.json")["assets"][portrait["id"]]
        self.assertEqual("source_labeled", saved["association"]["status"])
        self.assertEqual("person-test", saved["association"]["entity_id"])

    def test_identical_photos_keep_distinct_exported_filenames(self):
        png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a7WQAAAAASUVORK5CYII=")
        names = {"portrait-A.png", "team-photo.png"}
        for name in names:
            (self.root / "00_Throw_In" / name).write_bytes(png)
        plan = {"files": {i["candidate_id"]: {"scope": "reusable"} for i in w.scan(self.root)["files"]}}
        w.import_files(self.root, plan)
        assets = list(w.refresh_assets(self.root)["assets"].values())
        self.assertEqual(2, len(assets))
        self.assertEqual(1, len({a["source_id"] for a in assets}))
        w.labels(self.root, {a["id"]: {"status": "source_labeled", "label": "Fictional person",
                 "evidence": "Explicit test caption", "use": "portrait"} for a in assets})
        w.save_design(self.root, self.design())
        exported = w.export_profile(self.root, Path(self.temp.name) / "duplicate-profile.zip")
        with ZipFile(exported["package"]) as archive:
            prefix = exported["skill_name"] + "/"
            packed = json.loads(archive.read(prefix + "assets.json"))
            self.assertEqual(names, {a["filename"] for a in packed})
            original_names = {a["id"]: Path(a["path"]).name for a in assets}
            for asset in packed:
                self.assertEqual(original_names[asset["id"]], asset["filename"])
                self.assertEqual(png, archive.read(prefix + asset["path"]))

    def test_missing_photo_source_blocks_export_cleanly(self):
        png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a7WQAAAAASUVORK5CYII=")
        (self.root / "00_Throw_In/portrait.png").write_bytes(png)
        plan = {"files": {i["candidate_id"]: {"scope": "reusable"} for i in w.scan(self.root)["files"]}}
        w.import_files(self.root, plan)
        asset = next(iter(w.refresh_assets(self.root)["assets"].values()))
        w.labels(self.root, {asset["id"]: {"status": "source_labeled", "label": "Fictional person",
                 "evidence": "Explicit test caption", "use": "portrait"}})
        w.save_design(self.root, self.design())
        source = self.root / "02_Library/sources" / asset["source_id"] / "extract.json"
        source.unlink()
        result = w.check(self.root)
        self.assertFalse(result["valid"])
        self.assertFalse(result["ready"])
        output = Path(self.temp.name) / "missing-source.zip"
        with self.assertRaisesRegex(ValueError, "Missing asset source"):
            w.export_profile(self.root, output)
        self.assertFalse(output.exists())

    def test_invalid_design_reference_and_geometry_rejected(self):
        original = self.design()
        w.save_design(self.root, original)
        for kind in ["reference", "negative_gap", "infinite", "missing_asset", "reserved_export"]:
            profile = json.loads(json.dumps(original))
            if kind == "reference":
                profile["patterns"] = [{"id": "team", "reference": {"source_id": "missing", "slide": 1}}]
            elif kind == "negative_gap":
                profile["rules"]["layouts"] = {"two": {"widths": [20, 20], "gap": -20}}
            elif kind == "infinite":
                profile["rules"]["slide_cm"]["width"] = float("inf")
            elif kind == "missing_asset":
                profile["export_files"] = ["missing.png"]
            else:
                profile["export_files"] = ["profile.json"]
            with self.assertRaises(ValueError):
                w.save_design(self.root, profile)
            self.assertEqual(original, w.load(self.root, "03_Design/profile.json"))

    def test_reuse_exception_excludes_hidden_slides_and_notes(self):
        source = {"source": {"scope": "project", "project": "client", "reusable_slides": [1, 2]},
                  "slides": [{"number": 1, "hidden": True, "shapes": [{"id": "2"}]},
                             {"number": 2, "hidden": False, "shapes": [{"id": "3"}]}]}
        self.assertFalse(library.evidence_in_scope(source, {"slide": 1, "shape_id": "2"}, None))
        self.assertFalse(library.evidence_in_scope(source, {"slide": 2}, None))
        self.assertFalse(library.evidence_in_scope(source, {"slide": 2, "shape_id": "absent"}, None))
        self.assertTrue(library.evidence_in_scope(source, {"slide": 2, "shape_id": "3"}, None))

    def test_potx_import_reads_master_template_without_slides(self):
        path = self.root / "00_Throw_In/brand.potx"
        with ZipFile(path, "w") as archive:
            archive.writestr("ppt/presentation.xml", '<p:presentation xmlns:p="' + library.NS["p"] +
                             '"><p:sldSz cx="10800000" cy="7200000"/></p:presentation>')
        original = path.read_bytes()
        result = w.import_files(self.root)
        self.assertEqual([], result["errors"])
        self.assertEqual("extracted", result["imported"][0]["extraction_status"])
        self.assertEqual(original, (self.root / "01_Examples/Presentations/brand.potx").read_bytes())

    def test_portrait_boolean_alone_is_not_export_evidence(self):
        record = self.content()
        sid = record["facts"][0]["evidence"][0]["source_id"]
        folder = self.root / "02_Library/sources" / sid
        source = library.read_json(folder / "extract.json")
        # Synthetic extracted-shape fixture isolates the attribution/export gate.
        source["slides"] = [{"number": 1, "hidden": False, "shapes": [
            {"id": "8", "media": ["media/portrait.png"], "text": ""}]}]
        library.write_json(folder / "extract.json", source)
        (folder / "media").mkdir()
        (folder / "media/portrait.png").write_bytes(b"synthetic preview bytes")
        record["assets"] = [{"role": "portrait", "source_id": sid, "slide": 1,
                             "shape_id": "8", "media": "media/portrait.png", "identity_verified": True}]
        w.save_records(self.root, record)
        w.save_design(self.root, self.design())
        first = w.export_profile(self.root, Path(self.temp.name) / "unverified.zip")
        with ZipFile(first["package"]) as archive:
            data = json.loads(archive.read(first["skill_name"] + "/content.json"))
            self.assertEqual([], data[0]["assets"])
            self.assertFalse(any(name.endswith("portrait.png") for name in archive.namelist()))
        record["assets"][0]["identity_evidence"] = "Explicit user mapping in this synthetic test"
        w.save_records(self.root, record)
        second = w.export_profile(self.root, Path(self.temp.name) / "verified.zip")
        with ZipFile(second["package"]) as archive:
            data = json.loads(archive.read(second["skill_name"] + "/content.json"))
            self.assertTrue(archive.read(second["skill_name"] + "/" + data[0]["assets"][0]["package_path"]))

    def test_standalone_association_cannot_skip_evidence_by_direct_edit(self):
        png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a7WQAAAAASUVORK5CYII=")
        (self.root / "00_Throw_In/image.png").write_bytes(png)
        w.import_files(self.root)
        assets = w.load(self.root, "02_Library/assets.json")
        asset = next(iter(assets["assets"].values()))
        asset["association"] = {"status": "user_confirmed", "label": "Someone", "evidence": ""}
        w.save(self.root, "02_Library/assets.json", assets)
        self.assertFalse(w.check(self.root)["valid"])

    def test_capture_rejects_broken_citations_and_preserves_extract(self):
        record = self.content()
        w.save_records(self.root, record)
        sid = record["facts"][0]["evidence"][0]["source_id"]
        path = self.root / "02_Library/sources" / sid / "extract.json"
        before = path.read_bytes()
        with self.assertRaisesRegex(ValueError, "invalidate existing evidence"):
            w.capture_text(self.root, sid, {"method": "Synthetic recapture", "paragraphs": [
                {"number": 1, "text": "Unrelated replacement paragraph"}]})
        self.assertEqual(before, path.read_bytes())
        self.assertTrue(library.validate(self.root / "02_Library")["valid"])
        w.capture_text(self.root, sid, {"method": "Synthetic additive capture", "paragraphs": [
            {"number": 1, "text": "Example Company provides manufacturing services."},
            {"number": 2, "text": "Additional verified source text."}]})
        self.assertTrue(library.validate(self.root / "02_Library")["valid"])

    def test_unrelated_invalid_record_does_not_block_curation_or_design(self):
        record = self.content()
        broken = json.loads(json.dumps(record))
        broken["id"] = "broken-company"
        broken["facts"][0]["evidence"][0]["quote"] = "absent quote"
        library.write_json(self.root / "02_Library/records/broken-company.json", broken)
        result = w.save_records(self.root, record)
        self.assertEqual([record["id"]], result["saved"])
        self.assertFalse(result["validation"]["valid"])
        result = w.save_design(self.root, self.design())
        self.assertFalse(result["valid"])
        self.assertTrue((self.root / "03_Design/profile.json").is_file())
        with self.assertRaisesRegex(ValueError, "not ready"):
            w.export_profile(self.root, Path(self.temp.name) / "invalid.zip")

    def test_scope_demotion_revokes_old_evidence_and_search(self):
        record = self.content()
        w.save_records(self.root, record)
        sid = record["facts"][0]["evidence"][0]["source_id"]
        source_path = self.root / "02_Library/sources" / sid / "extract.json"
        source = library.read_json(source_path)
        source["slides"] = [{"number": 1, "hidden": False, "title": "Company", "text": "manufacturing",
                             "shapes": [{"id": "3", "text": "manufacturing"}]}]
        library.write_json(source_path, source)
        plan = {"files": {i["candidate_id"]: {"scope": "project", "project": "client-a"}
                          for i in w.scan(self.root)["files"]}}
        result = w.import_files(self.root, plan)
        self.assertEqual([], result["errors"])
        entry = result["imported"][0]
        self.assertNotEqual(sid, entry["source_id"])
        self.assertIsNone(entry["duplicate_of"])
        self.assertEqual(entry["source_id"], library.read_json(source_path)["source"]["scope_replaced_by"])
        self.assertFalse(library.validate(self.root / "02_Library")["valid"])
        self.assertEqual([], library.search(self.root / "02_Library", "manufacturing", raw=True))
        plan = {"files": {i["candidate_id"]: {"scope": "reusable"} for i in w.scan(self.root)["files"]}}
        w.import_files(self.root, plan)
        self.assertNotIn("scope_replaced_by", library.read_json(source_path)["source"])
        self.assertTrue(library.validate(self.root / "02_Library")["valid"])

    def test_import_recovery_with_missing_index(self):
        path = self.root / "00_Throw_In/recover.txt"
        path.write_text("preserved original")
        sha = w.digest(path)
        sid, _ = w.register_source(self.root, path, {"scope": "reusable"})
        entry = {"id": "recovered-file", "path": "01_Examples/Documents/recover.txt",
                 "source_id": sid, "sha256": sha}
        w.save(self.root, ".slide-library/imports/job.json", {
            "status": "prepared", "from": "00_Throw_In/recover.txt", "entry": entry})
        (self.root / ".slide-library/index.json").unlink()
        self.assertEqual(["recovered-file"], w.recover(self.root))
        self.assertEqual(sha, w.digest(self.root / entry["path"]))
        self.assertEqual(entry, w.load(self.root, ".slide-library/index.json")["files"][entry["id"]])

    def test_legacy_partial_design_reports_error(self):
        library.write_json(self.root / "02_Library/design/profile.json", {"rules": {"content": {"x": 1}}})
        result = library.validate(self.root / "02_Library")
        self.assertFalse(result["valid"])
        self.assertIn("design: incomplete or invalid dimensions", result["errors"])


if __name__ == "__main__":
    unittest.main()
