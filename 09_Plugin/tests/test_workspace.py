import base64
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

SCRIPTS = Path(__file__).resolve().parents[2] / "05_Skill/slide-library/scripts"
sys.path.insert(0, str(SCRIPTS))
import workspace as w
import library

PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a7WQAAAAASUVORK5CYII=")


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve() / "My Slide System"
        w.setup(self.root, "Example Company")

    def tearDown(self):
        self.temp.cleanup()

    def drop(self, name, data):
        path = self.root / "00_Throw_In" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def plan(self, **choice):
        return {"files": {i["candidate_id"]: choice for i in w.scan(self.root)["files"]}}

    def design(self):
        w.save(self.root, "03_Design/profile.json", {
            "name": "Example", "status": "ready", "visual_review": "Reviewed sample slides in test fixture",
            "source_ids": [], "rules": {"slide_cm": {"width": 33.87, "height": 19.05},
            "content": {"x": 1, "y": 3, "w": 31, "bottom": 18}, "font": "Arial",
            "colors": {"primary": "24445C"}}, "patterns": []})

    def test_setup_idempotent_and_name_collision(self):
        original = w.require(self.root)["id"]
        self.assertFalse(w.setup(self.root, "Example Company")["created"])
        self.assertEqual(original, w.require(self.root)["id"])
        with self.assertRaises(ValueError):
            w.setup(self.root, "Different Company")

    def test_sort_extract_idempotent_and_no_company_defaults(self):
        self.drop("brief.txt", b"Company overview\n\nFounded in 2005.")
        self.drop("photo.png", PNG)
        report = w.import_files(self.root)
        self.assertFalse(report["errors"])
        self.assertEqual(2, len(report["imported"]))
        self.assertTrue((self.root / "01_Examples/Photos/photo.png").exists())
        self.assertFalse((self.root / "00_Throw_In/photo.png").exists())
        self.assertEqual([], w.import_files(self.root)["imported"])
        self.assertEqual("draft", w.require(self.root)["status"])
        self.assertFalse(w.check(self.root)["ready"])

    def test_pptx_import_preserves_ole_without_reading_payloads(self):
        path = self.root / "00_Throw_In/reference.pptx"
        embedded = {"ppt/embeddings/oleObject5.bin": b"opaque OLE payload\x00\xff",
                    "ppt/embeddings/workbook.xlsx": b"opaque workbook payload"}
        pns, ans, rns = library.NS["p"], library.NS["a"], library.NS["r"]
        def relationships(rows):
            return ('<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                    + ''.join(f'<Relationship Id="{rid}" Type="{rns}/{kind}" Target="{target}"{mode}/>'
                              for rid, kind, target, mode in rows) + '</Relationships>')
        with ZipFile(path, "w") as archive:
            archive.writestr("ppt/presentation.xml", f'''<p:presentation xmlns:p="{pns}" xmlns:r="{rns}">
                <p:sldIdLst><p:sldId id="256" r:id="rSlide"/></p:sldIdLst>
                <p:sldSz cx="12192000" cy="6858000"/></p:presentation>''')
            archive.writestr("ppt/_rels/presentation.xml.rels", relationships([
                ("rSlide", "slide", "slides/slide1.xml", "")]))
            archive.writestr("ppt/slides/slide1.xml", f'''<p:sld xmlns:p="{pns}" xmlns:a="{ans}" xmlns:r="{rns}">
                <p:cSld><p:spTree><p:sp><p:nvSpPr><p:cNvPr id="1" name="Title"/></p:nvSpPr>
                <p:txBody><a:p><a:r><a:t>Reference heading</a:t></a:r></a:p></p:txBody></p:sp>
                <p:graphicFrame><a:graphic><a:graphicData><p:oleObj r:id="rOle" progId="Example.Document">
                <p:embed/><p:pic><p:nvPicPr><p:cNvPr id="2" name="Object preview"/></p:nvPicPr>
                <p:blipFill><a:blip r:embed="rPreview"/></p:blipFill></p:pic></p:oleObj>
                </a:graphicData></a:graphic></p:graphicFrame></p:spTree></p:cSld></p:sld>''')
            archive.writestr("ppt/slides/_rels/slide1.xml.rels", relationships([
                ("rOle", "oleObject", "../embeddings/oleObject5.bin", ""),
                ("rPreview", "image", "../media/image1.png", ""),
                ("rChart", "chart", "../charts/chart1.xml", ""),
                ("rExternal", "oleObject", "https://example.invalid/linked.xlsx", ' TargetMode="External"')]))
            archive.writestr("ppt/charts/chart1.xml", '''<c:chartSpace xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">
                <c:chart><c:numCache><c:pt idx="0"><c:v>42</c:v></c:pt></c:numCache></c:chart></c:chartSpace>''')
            archive.writestr("ppt/charts/_rels/chart1.xml.rels", relationships([
                ("rWorkbook", "package", "../embeddings/workbook.xlsx", "")]))
            archive.writestr("ppt/media/image1.png", PNG)
            for name, data in embedded.items():
                archive.writestr(name, data)
        original = path.read_bytes()
        read = ZipFile.read
        def guarded_read(archive, name, *args, **kwargs):
            part = name.filename if hasattr(name, "filename") else name
            self.assertFalse(part.startswith("ppt/embeddings/"), "Must not parse embedded payloads")
            self.assertFalse(part.startswith("https:"), "Must not follow external targets")
            return read(archive, name, *args, **kwargs)
        with patch.object(ZipFile, "read", guarded_read):
            report = w.import_files(self.root)
        self.assertEqual([], report["errors"])
        self.assertEqual(1, len(report["imported"]))
        archived = self.root / "01_Examples/Presentations/reference.pptx"
        self.assertEqual(original, archived.read_bytes())
        source = next((self.root / "02_Library/sources").iterdir())
        self.assertEqual(original, (source / "source.pptx").read_bytes())
        data = library.read_json(source / "extract.json")
        inventory = data["reference_import"]
        self.assertEqual(set(embedded), {i["part"] for i in inventory["embedded_parts"]})
        self.assertFalse(inventory["embedded_payloads_parsed"])
        self.assertFalse(inventory["external_targets_followed"])
        self.assertEqual("not_performed", inventory["security_assessment"])
        self.assertEqual("Reference heading", data["slides"][0]["text"])
        self.assertEqual("42", data["slides"][0]["charts"][0]["cached_values"][0]["value"])
        self.assertEqual(PNG, (source / "media/image1.png").read_bytes())
        self.assertEqual([], w.import_files(self.root)["imported"])

    def test_colliding_names_do_not_overwrite(self):
        self.drop("notes.txt", b"first")
        w.import_files(self.root)
        self.drop("notes.txt", b"second")
        result = w.import_files(self.root)
        self.assertFalse(result["errors"])
        contents = {p.read_bytes() for p in (self.root / "01_Examples/Documents").glob("*.txt")}
        self.assertEqual({b"first", b"second"}, contents)

    def test_exact_duplicates_retained(self):
        self.drop("one.txt", b"same")
        self.drop("two.txt", b"same")
        result = w.import_files(self.root)
        self.assertEqual(2, len(result["imported"]))
        self.assertTrue(any(r["duplicate_of"] for r in result["imported"]))
        self.assertEqual(2, len(list((self.root / "01_Examples/Documents").glob("*.txt"))))

    def test_nested_bundle_links_remain_intact(self):
        self.drop("project/page.txt", b"See image.png")
        self.drop("project/image.png", PNG)
        result = w.import_files(self.root)
        self.assertFalse(result["errors"])
        self.assertTrue((self.root / "00_Throw_In/project/image.png").exists())
        self.assertEqual([], w.import_files(self.root)["imported"])

    def test_scope_defaults_and_explicit_curation(self):
        self.drop("logo.png", PNG)
        first = w.import_files(self.root)
        self.assertEqual("project", first["imported"][0]["scope"])
        result = w.import_files(self.root, self.plan(scope="reusable", category="Logos", description="Company logo"))
        self.assertEqual("reusable", result["imported"][0]["scope"])
        asset = next(iter(w.refresh_assets(self.root)["assets"].values()))
        self.assertEqual("reusable", asset["scope"])
        self.assertTrue((self.root / "01_Examples/Logos/logo.png").exists())

    def test_names_are_not_inferred_from_filename(self):
        self.drop("Alex_Morgan_portrait.png", PNG)
        w.import_files(self.root)
        asset = next(iter(w.refresh_assets(self.root)["assets"].values()))
        self.assertEqual("unresolved", asset["association"]["status"])
        with self.assertRaises(ValueError):
            w.labels(self.root, {asset["id"]: {"status": "user_confirmed", "label": "Alex"}})
        w.labels(self.root, {asset["id"]: {"status": "user_confirmed", "label": "Alex Morgan",
                 "entity_id": "person-alex", "evidence": "User: Photo 1 is Alex Morgan", "use": "portrait"}})
        self.assertEqual(0, w.review(self.root)["images"])

    def test_numbered_review_escapes_untrusted_text(self):
        self.drop("<script>alert.png", PNG)
        w.import_files(self.root)
        result = w.review(self.root)
        page = Path(result["review"]).read_text()
        self.assertEqual(1, result["images"])
        self.assertIn("&lt;script&gt;", page)
        self.assertNotIn("<script>", page)
        self.assertIn("default-src 'none'", page)
        self.assertTrue(result["mapping"]["1"].startswith("asset-"))

    def test_manual_rename_keeps_asset_mapping(self):
        self.drop("photo.png", PNG)
        w.import_files(self.root)
        asset = next(iter(w.refresh_assets(self.root)["assets"].values()))
        w.labels(self.root, {asset["id"]: {"status": "user_confirmed", "label": "Alex", "evidence": "User supplied"}})
        (self.root / asset["path"]).rename(self.root / "01_Examples/Photos/renamed.png")
        result = w.import_files(self.root)
        self.assertFalse(result["errors"])
        assets = w.refresh_assets(self.root)["assets"]
        self.assertEqual(1, len(assets))
        self.assertEqual("Alex", assets[asset["id"]]["association"]["label"])
        self.assertTrue(w.check(self.root)["valid"])

    def test_replaced_image_does_not_inherit_identity(self):
        self.drop("photo.png", PNG)
        w.import_files(self.root)
        old = next(iter(w.refresh_assets(self.root)["assets"].values()))
        w.labels(self.root, {old["id"]: {"status": "user_confirmed", "label": "Alex", "evidence": "User supplied"}})
        (self.root / old["path"]).write_bytes(PNG + b"different image fixture")
        result = w.import_files(self.root)
        self.assertFalse(result["errors"])
        assets = w.refresh_assets(self.root)["assets"]
        self.assertTrue(assets[old["id"]]["retired"])
        active = [a for a in assets.values() if not a["retired"]]
        self.assertEqual("unresolved", active[0]["association"]["status"])
        self.assertTrue(w.check(self.root)["valid"])

    def test_recovery_after_destination_created(self):
        source = self.drop("notes.txt", b"recover me")
        sha = w.digest(source)
        dest = "01_Examples/Documents/notes.txt"
        target = self.root / dest
        target.parent.mkdir(parents=True)
        target.write_bytes(source.read_bytes())
        sid, _ = w.register_source(self.root, source, {"scope": "reusable", "project": None})
        entry = {"id": "recovery", "path": dest, "sha256": sha, "source_id": sid}
        w.save(self.root, ".slide-library/imports/recovery.json",
               {"status": "prepared", "from": "00_Throw_In/notes.txt", "entry": entry})
        self.assertEqual(["recovery"], w.recover(self.root))
        self.assertFalse(source.exists())
        self.assertEqual(b"recover me", target.read_bytes())
        self.assertEqual([], w.recover(self.root))

    def test_symlink_and_traversal_rejected(self):
        outside = Path(self.temp.name) / "outside.txt"
        outside.write_text("outside")
        (self.root / "00_Throw_In/link.txt").symlink_to(outside)
        self.assertIn("00_Throw_In/link.txt", w.scan(self.root)["skipped"])
        with self.assertRaises(ValueError):
            w.safe(self.root, "../outside.txt")
        (self.root / "02_Library/records/link.json").symlink_to(outside)
        with self.assertRaises(ValueError):
            w.check(self.root)

    def test_archive_preserves_originals_and_requires_name(self):
        source = self.drop("original.txt", b"keep")
        with self.assertRaises(ValueError):
            w.archive(self.root, "wrong")
        w.archive(self.root, "Example Company")
        self.assertEqual(b"keep", source.read_bytes())
        with self.assertRaises(ValueError):
            w.import_files(self.root)
        w.archive(self.root, "Example Company", restore=True)
        self.assertEqual("draft", w.require(self.root)["status"])

    def test_export_requires_design_and_filters_project_assets(self):
        self.drop("private.png", PNG)
        w.import_files(self.root)
        asset = next(iter(w.refresh_assets(self.root)["assets"].values()))
        w.labels(self.root, {asset["id"]: {"status": "user_confirmed", "label": "Private client",
                                         "evidence": "User supplied"}})
        output = Path(self.temp.name) / "profile.zip"
        with self.assertRaises(ValueError):
            w.export_profile(self.root, output)
        self.design()
        report = w.export_profile(self.root, output)
        self.assertEqual(0, report["assets"])
        with ZipFile(output) as z:
            self.assertEqual([], json.loads(z.read(report["skill_name"] + "/assets.json")))
            self.assertFalse(any("/sources/" in name or "private.png" in name for name in z.namelist()))
        with self.assertRaises(ValueError):
            w.export_profile(self.root, output)

    def test_export_includes_explicitly_reusable_asset(self):
        self.drop("logo.png", PNG)
        w.import_files(self.root, self.plan(scope="reusable", category="Logos"))
        asset = next(iter(w.refresh_assets(self.root)["assets"].values()))
        w.labels(self.root, {asset["id"]: {"status": "source_labeled", "label": "Example logo",
                                         "evidence": "Explicit label in supplied brand guide", "use": "logo"}})
        self.design()
        report = w.export_profile(self.root, Path(self.temp.name) / "ready.zip")
        self.assertEqual(1, report["assets"])
        with ZipFile(report["package"]) as z:
            assets = json.loads(z.read(report["skill_name"] + "/assets.json"))
            self.assertEqual(PNG, z.read(report["skill_name"] + "/" + assets[0]["path"]))

    def test_docx_extract_and_english_outline(self):
        doc = self.drop("profile.docx", b"")
        with ZipFile(doc, "w") as z:
            z.writestr("word/document.xml",
                       '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                       '<w:body><w:p><w:r><w:t>Alex Morgan</w:t></w:r></w:p></w:body></w:document>')
        report = w.import_files(self.root)
        self.assertFalse(report["errors"])
        source = self.root / "02_Library/sources" / report["imported"][0]["source_id"] / "extract.json"
        self.assertEqual("Alex Morgan", json.loads(source.read_text())["paragraphs"][0]["text"])
        outline = self.drop("outline.md", b"# Slide 1: Overview\n  1. Detail\n# Slide 2: Team\n")
        slides = library.brief(outline)["slides"]
        self.assertEqual(["Overview", "Team"], [s["heading"] for s in slides])

    def test_design_rollback_and_finalize(self):
        self.design()
        before = (self.root / "03_Design/profile.json").read_bytes()
        invalid = json.loads(before)
        invalid["rules"]["content"]["w"] = 100
        with self.assertRaises(ValueError):
            w.save_design(self.root, invalid)
        self.assertEqual(before, (self.root / "03_Design/profile.json").read_bytes())
        self.assertEqual("ready", w.finalize(self.root)["status"])
        self.assertEqual("ready", w.require(self.root)["status"])
        self.assertEqual(1, len(w.list_setups(self.root.parent)["setups"]))

    def test_reader_capture_preserves_source_and_previous_extract(self):
        original = b"{rtf source text}"
        self.drop("source.rtf", original)
        result = w.import_files(self.root)
        sid = result["imported"][0]["source_id"]
        self.assertEqual("needs_reader", result["imported"][0]["extraction_status"])
        w.capture_text(self.root, sid, {"method": "Verified reader",
                       "paragraphs": [{"number": 1, "text": "source text"}]})
        folder = self.root / "02_Library/sources" / sid
        self.assertEqual(original, (folder / "source.rtf").read_bytes())
        self.assertEqual(1, len(list(folder.glob("extract.previous-*.json"))))
        self.assertEqual("source text", json.loads((folder / "extract.json").read_text())["text"])
        with self.assertRaises(ValueError):
            w.capture_text(self.root, sid, {"method": "Reader", "paragraphs":
                           [{"number": 1, "text": "x"}, {"number": 1, "text": "y"}]})

    def test_export_filters_project_facts(self):
        self.drop("company.txt", b"Provides manufacturing services.")
        self.drop("client.txt", b"Confidential project budget is 42.")
        plan = {"files": {i["candidate_id"]: ({"scope": "reusable"} if "company" in i["path"] else
                         {"scope": "project", "project": "client-a"}) for i in w.scan(self.root)["files"]}}
        result = w.import_files(self.root, plan)
        for item in result["imported"]:
            content = (self.root / item["path"]).read_text()
            record = {"id": "company" if item["scope"] == "reusable" else "client-budget",
                      "kind": "company", "label": "Company", "scope": item["scope"], "project": item["project"],
                      "status": "source_grounded", "facts": [{"id": "fact", "text": content,
                      "evidence": [{"source_id": item["source_id"], "paragraph": 1, "quote": content}]}]}
            w.save(self.root, "02_Library/records/" + record["id"] + ".json", record)
        self.design()
        report = w.export_profile(self.root, Path(self.temp.name) / "public.zip")
        self.assertEqual(1, report["records"])
        with ZipFile(report["package"]) as z:
            content = z.read(report["skill_name"] + "/content.json")
            self.assertNotIn(b"Confidential", content)
        private = w.export_profile(self.root, Path(self.temp.name) / "project.zip", "client-a")
        self.assertEqual(2, private["records"])

    def test_failed_extraction_keeps_original(self):
        original = self.drop("broken.pptx", b"not an archive")
        result = w.import_files(self.root)
        self.assertEqual(1, len(result["errors"]))
        self.assertEqual(b"not an archive", original.read_bytes())


if __name__ == "__main__":
    unittest.main()
