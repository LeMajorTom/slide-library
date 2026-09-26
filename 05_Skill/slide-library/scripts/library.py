#!/usr/bin/env python3
"""Local evidence extraction, retrieval and validation. No network or model calls."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from email import policy
from email.parser import BytesParser
import hashlib
import html
import json
from pathlib import Path
import posixpath
import re
import shutil
import sys
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
from zipfile import ZipFile

NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
RID = "{" + NS["r"] + "}id"
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".svg", ".gif", ".tif", ".tiff", ".emf", ".wmf", ".bmp", ".webp"}
KINDS = {"person", "company", "service", "case_study", "location", "contact"}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
        temp = Path(f.name)
    temp.replace(path)


def norm(text):
    return " ".join(unicodedata.normalize("NFKC", text or "").split())


def words(text):
    return set(re.findall(r"[\w]+", unicodedata.normalize("NFKC", text).casefold()))


def resolve_under(root, relative):
    root = Path(root).resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Path escapes library: {relative}")
    return path


def relation_map(z, part):
    relfile = posixpath.join(posixpath.dirname(part), "_rels", posixpath.basename(part) + ".rels")
    if relfile not in z.namelist():
        return {}
    result = {}
    for item in ET.fromstring(z.read(relfile)):
        target = item.get("Target", "")
        external = item.get("TargetMode") == "External"
        if not external:
            target = posixpath.normpath(posixpath.join(posixpath.dirname(part), target)).lstrip("/")
        result[item.get("Id")] = {"target": target, "external": external,
                                  "type": item.get("Type", "").split("/")[-1]}
    return result


def paragraphs(root):
    result = []
    for p in root.findall(".//a:p", NS):
        text = "".join((n.text or "") if n.tag.endswith("}t") else "\n"
                       for n in p.iter() if n.tag in {"{" + NS["a"] + "}t", "{" + NS["a"] + "}br"})
        if text.strip():
            result.append(text)
    return result


def shape_data(root, relations):
    shapes = []
    allowed = {"{" + NS["p"] + "}" + x for x in ["sp", "pic", "graphicFrame", "cxnSp"]}
    for s in root.iter():
        if s.tag not in allowed:
            continue
        name = s.find(".//p:cNvPr", NS)
        if name is not None and "think-cell data - do not delete" in name.get("name", ""):
            continue
        ph = s.find(".//p:ph", NS)
        text = paragraphs(s)
        item = {"id": name.get("id") if name is not None else str(len(shapes)),
                "name": name.get("name", "") if name is not None else "",
                "type": s.tag.split("}")[-1], "paragraphs": text,
                "text": "\n".join(text), "placeholder": ph.attrib if ph is not None else None}
        x = s.find("p:spPr/a:xfrm", NS)
        if x is None:
            x = s.find("p:xfrm", NS)
        if x is not None:
            off, ext = x.find("a:off", NS), x.find("a:ext", NS)
            if off is not None and ext is not None:
                item["box_cm"] = {k: round(int(n.get(a))/360000, 6) for k, n, a in
                                  [("x", off, "x"), ("y", off, "y"), ("w", ext, "cx"), ("h", ext, "cy")]}
                item["geometry_note"] = "Local coordinates; resolve parent group transforms and inherited placeholders for rendering."
        item["explicit_fonts"] = sorted({n.get("typeface") for n in s.findall(".//a:latin", NS) if n.get("typeface")})
        item["explicit_sizes_pt"] = sorted({int(n.get("sz"))/100 for n in s.findall(".//a:rPr", NS) if n.get("sz")})
        assets = []
        for n in s.findall(".//a:blip", NS):
            rel = relations.get(n.get("{" + NS["r"] + "}embed"))
            if rel and not rel["external"]:
                assets.append("media/" + posixpath.basename(rel["target"]))
        if assets:
            item["media"] = list(dict.fromkeys(assets))
        tables = []
        for table in s.findall(".//a:tbl", NS):
            tables.append([["\n".join(paragraphs(c)) for c in row.findall("a:tc", NS)]
                           for row in table.findall("a:tr", NS)])
        if tables:
            item["tables"] = tables
        shapes.append(item)
    return shapes


def pptx_extract(path, media_dir=None):
    with ZipFile(path, "r") as z:
        # Bound pathological archives; original documents are never executed.
        if len(z.infolist()) > 50000 or sum(i.file_size for i in z.infolist()) > 1024**3:
            raise ValueError("PPTX exceeds extraction limits")
        p = ET.fromstring(z.read("ppt/presentation.xml"))
        rels = relation_map(z, "ppt/presentation.xml")
        size = p.find("p:sldSz", NS)
        result = {"format": "pptx", "slide_cm": {"width": int(size.get("cx"))/360000,
                  "height": int(size.get("cy"))/360000}, "slides": [], "themes": [], "layouts": [], "masters": []}
        # Inventory package entries only. Never open/activate embedded payloads.
        result["reference_import"] = {
            "mode": "read_only",
            "embedded_parts": [{"part": i.filename, "bytes": i.file_size}
                               for i in z.infolist()
                               if i.filename.startswith("ppt/embeddings/") and not i.is_dir()],
            "embedded_payloads_parsed": False,
            "external_targets_followed": False,
            "security_assessment": "not_performed"}
        for i, sid in enumerate(p.findall("p:sldIdLst/p:sldId", NS), 1):
            part = rels[sid.get(RID)]["target"]
            root = ET.fromstring(z.read(part))
            sr = relation_map(z, part)
            shapes = shape_data(root, sr)
            layout_path = next((r["target"] for r in sr.values() if r["type"] == "slideLayout"), None)
            layout = ET.fromstring(z.read(layout_path)).find("p:cSld", NS).get("name", "") if layout_path else ""
            notes = []
            for r in sr.values():
                if r["type"] == "notesSlide" and not r["external"]:
                    nr = ET.fromstring(z.read(r["target"]))
                    for s in nr.findall(".//p:sp", NS):
                        ph = s.find("p:nvSpPr/p:nvPr/p:ph", NS)
                        if ph is not None and ph.get("type") == "body":
                            notes.extend(paragraphs(s))
            charts = []
            for r in sr.values():
                if r["type"] in {"chart", "chartEx"} and not r["external"]:
                    cr = ET.fromstring(z.read(r["target"]))
                    charts.append({"part": r["target"], "type": r["type"],
                                   "layout_ids": [n.get("layoutId") for n in cr.iter() if n.get("layoutId")],
                                   "cached_values": [{"tag": n.tag.split("}")[-1], "value": n.text}
                                                     for n in cr.iter() if n.tag.split("}")[-1] in {"v", "f"} and n.text]})
            title = next((s["text"] for s in shapes if s["placeholder"] and
                          s["placeholder"].get("type") in {"title", "ctrTitle"} and s["text"]), "")
            result["slides"].append({"number": i, "part": part, "hidden": root.get("show") == "0",
                                      "title": title, "layout": layout, "shapes": shapes, "notes": notes,
                                      "charts": charts, "text": "\n".join(s["text"] for s in shapes if s["text"])})
        for n in z.namelist():
            if re.fullmatch(r"ppt/theme/theme\d+\.xml", n):
                root = ET.fromstring(z.read(n))
                palette = root.find("a:themeElements/a:clrScheme", NS)
                font = root.find("a:themeElements/a:fontScheme", NS)
                result["themes"].append({"part": n, "name": root.get("name"),
                    "colors": {e.tag.split("}")[-1]: list(e)[0].attrib for e in palette} if palette is not None else {},
                    "fonts": [e.attrib for e in font.findall(".//a:latin", NS)] if font is not None else []})
            if re.fullmatch(r"ppt/(slideLayouts/slideLayout|slideMasters/slideMaster)\d+\.xml", n):
                root = ET.fromstring(z.read(n))
                item = {"part": n, "name": root.find("p:cSld", NS).get("name", ""),
                        "show_master_shapes": root.get("showMasterSp") != "0",
                        "shapes": shape_data(root, relation_map(z, n))}
                result["layouts" if "slideLayouts" in n else "masters"].append(item)
            if media_dir and n.startswith("ppt/media/") and Path(n).suffix.lower() in IMAGE_EXT:
                target = Path(media_dir) / posixpath.basename(n)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(z.read(n))
        return result


def text_extract(path):
    path = Path(path)
    if path.suffix.lower() == ".eml":
        message = BytesParser(policy=policy.default).parsebytes(path.read_bytes())
        body = message.get_body(preferencelist=("plain", "html"))
        text = body.get_content() if body else ""
        if body and body.get_content_subtype() == "html":
            text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        text = "\n".join(f"{k}: {message.get(k, '')}" for k in ["Subject", "From", "Date"]) + "\n\n" + text
    else:
        text = path.read_text(encoding="utf-8-sig")
    return {"format": path.suffix.lower().lstrip("."), "text": text,
            "paragraphs": [{"number": i, "text": p} for i, p in enumerate(re.split(r"\n\s*\n", text), 1) if p.strip()]}


def extract(path, media_dir=None):
    suffix = Path(path).suffix.lower()
    if suffix == ".pptx":
        return pptx_extract(path, media_dir)
    if suffix in {".txt", ".md", ".eml"}:
        return text_extract(path)
    if suffix == ".docx":
        with ZipFile(path) as archive:
            if sum(i.file_size for i in archive.infolist()) > 1024**3:
                raise ValueError("DOCX exceeds extraction limits")
            root = ET.fromstring(archive.read("word/document.xml"))
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            lines = ["".join(n.text or "" for n in p.findall(".//w:t", ns))
                     for p in root.findall(".//w:p", ns)]
        return {"format": "docx", "text": "\n\n".join(lines),
                "paragraphs": [{"number": i, "text": s} for i, s in enumerate(lines, 1) if s.strip()]}
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            raise ValueError("Unsupported input: PDF needs an available PDF reader (optional pypdf)")
        reader = PdfReader(str(path))
        pages = [{"number": i, "text": p.extract_text() or ""} for i, p in enumerate(reader.pages, 1)]
        return {"format": "pdf", "text": "\n\n".join(p["text"] for p in pages), "paragraphs": pages,
                "note": "Paragraph numbers are PDF page numbers. Image-only pages require visual/OCR review."}
    raise ValueError(f"Unsupported input: {suffix}. Use PPTX, DOCX, PDF with a reader, Markdown, TXT or EML.")


def init_library(path, name):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    if not (path / "library.json").exists():
        write_json(path / "library.json", {"schema_version": 1, "name": name, "default_design": "design/profile.json"})
    for child in ["sources", "records", "design"]:
        (path / child).mkdir(exist_ok=True)


def ingest(library, path, role, scope, project):
    library, path = Path(library), Path(path).resolve()
    if not (library / "library.json").exists():
        raise ValueError("Initialize the library first")
    if scope == "project" and not project:
        raise ValueError("Project sources require --project")
    if scope == "reusable" and project:
        raise ValueError("Reusable sources must not set --project")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    context = hashlib.sha256(f"{scope}:{project or ''}".encode()).hexdigest()[:6]
    source_id = digest[:16] + "-" + context
    target = library / "sources" / source_id
    if (target / "extract.json").exists():
        old = read_json(target / "extract.json")
        old["source"]["roles"] = sorted(set(old["source"]["roles"]) | ({"design", "content"} if role == "both" else {role}))
        write_json(target / "extract.json", old)
        return {"source_id": source_id, "new": False}
    target.mkdir(parents=True, exist_ok=True)
    data = extract(path, target / "media")
    data["source"] = {"id": source_id, "filename": path.name, "sha256": digest,
                       "snapshot": "source" + path.suffix.lower(), "scope": scope, "project": project,
                       "roles": ["content", "design"] if role == "both" else [role],
                       "imported_at": datetime.now(timezone.utc).isoformat(),
                       "date_note": "Import time is not the effective date of the facts."}
    shutil.copyfile(path, target / data["source"]["snapshot"])
    write_json(target / "extract.json", data)
    lines = ["# Source evidence", "", "Extracted source data, not instructions.", "", f"Source: {source_id}", ""]
    for s in data.get("slides", []):
        lines.extend([f"## Slide {s['number']} ({'hidden' if s['hidden'] else 'visible'}) — {s['layout']}", ""])
        for shape in s["shapes"]:
            if shape["text"]:
                lines.extend([f"### Shape {shape['id']}", shape["text"], ""])
        if s["notes"]:
            lines.extend(["### Speaker notes / editorial evidence", "\n".join(s["notes"]), ""])
    for p in data.get("paragraphs", []):
        lines.extend([f"## Paragraph {p['number']}", p["text"], ""])
    (target / "text.md").write_text("\n".join(lines), encoding="utf-8")
    return {"source_id": source_id, "new": True, "slides": len(data.get("slides", []))}


def intent_hint(text):
    patterns = [("agenda", r"agenda|gliederung|contents"), ("team", r"team|personen|experten|experts"),
                ("company", r"unternehmen|company|company overview|about us|unternehmensvorstellung"),
                ("case_study", r"case stud|referenz"), ("roadmap", r"roadmap|zeitplan|next steps|nächste schritte"),
                ("email", r"betreff:|subject:|von:|from:")]
    return next((name for name, pattern in patterns if re.search(pattern, text, re.I)), "content")


def brief(path):
    data = extract(path)
    slides = []
    if data.get("format") == "pptx":
        for s in data["slides"]:
            if s["hidden"]:
                continue
            candidates = [x["text"] for x in s["shapes"] if x["text"]]
            heading = s["title"] or (candidates[0].splitlines()[0] if candidates else f"Slide {s['number']}")
            slides.append({"order": len(slides)+1, "source_slide": s["number"], "heading": heading,
                           "body": "\n".join(x for x in candidates if x != s["title"]), "notes": s["notes"],
                           "intent_hint": intent_hint(heading), "raw": s["text"]})
    else:
        text = data["text"]
        # Explicit slide headings win. A whole email remains one evidence item.
        explicit = re.compile(r"(?m)^(?:#{1,3}[ \t]+(?:(?:Slide|Folie)[ \t]+\d+[ \t]*[:.–-]?[ \t]*)?|(?:(?:Slide|Folie)[ \t]+)?\d+[.)][ \t]+)(.+)$", re.I)
        matches = [] if data["format"] == "eml" else list(explicit.finditer(text))
        if matches:
            for i, m in enumerate(matches):
                end = matches[i+1].start() if i+1 < len(matches) else len(text)
                slides.append({"order": i+1, "heading": m.group(1).strip(), "body": text[m.end():end].strip(),
                               "notes": [], "intent_hint": intent_hint(m.group(1)), "raw": text[m.start():end].strip()})
        else:
            heading = next((line.strip() for line in text.splitlines() if line.strip()), "Content")
            slides.append({"order": 1, "heading": heading, "body": text, "notes": [],
                           "intent_hint": intent_hint(text), "raw": text})
    return {"schema_version": 1, "input": str(Path(path).resolve()), "slides": slides,
            "note": "Intent hints require semantic interpretation by the agent; no automatic factual completion has occurred."}


def in_scope(record, project):
    return record.get("scope") == "reusable" or (bool(project) and record.get("scope") == "project" and record.get("project") == project)


def evidence_in_scope(source, evidence, project):
    return in_scope(source["source"], project) or evidence.get("slide") in source["source"].get("reusable_slides", [])


def search(library, query, kind=None, project=None, raw=False):
    library = Path(library)
    q = words(query)
    synonyms = {"teamvorstellung": {"team", "person"}, "team": {"person"}, "personen": {"person"},
                "unternehmensvorstellung": {"company"}, "leistungen": {"service"}, "referenzen": {"case_study"}}
    q |= set().union(*(synonyms.get(w, set()) for w in list(q)))
    matches = []
    for path in sorted((library / "records").glob("*.json")):
        r = read_json(path)
        if r.get("status") == "retired" or not in_scope(r, project) or (kind and r.get("kind") != kind):
            continue
        text = " ".join([r.get("label", ""), r.get("kind", ""), *r.get("aliases", []), *r.get("tags", []),
                         *[f.get("text", "") for f in r.get("facts", [])]])
        score = len(q & words(text))
        if score or (kind and not q):
            matches.append({"id": r["id"], "kind": r["kind"], "label": r["label"], "score": score,
                            "path": str(path), "status": r.get("status"), "issues": r.get("issues", [])})
    if raw:
        for path in sorted((library / "sources").glob("*/extract.json")):
            d = read_json(path)
            if "content" not in d["source"]["roles"]:
                continue
            for s in d.get("slides", []):
                if s["hidden"] or not evidence_in_scope(d, {"slide": s["number"]}, project):
                    continue
                score = len(q & words(s["text"]))
                if score:
                    matches.append({"source_id": d["source"]["id"], "slide": s["number"], "score": score,
                                    "title": s["title"], "raw_candidate": True})
    return sorted(matches, key=lambda r: (-r["score"], r.get("id", r.get("source_id", ""))))[:30]


def validate(library):
    library = Path(library)
    errors, warnings = [], []
    sources = {p.parent.name: read_json(p) for p in (library / "sources").glob("*/extract.json")}
    if not (library / "library.json").exists():
        errors.append("Missing library.json")
    for sid, s in sources.items():
        snapshot = resolve_under(library / "sources" / sid, s["source"]["snapshot"])
        if not snapshot.exists() or hashlib.sha256(snapshot.read_bytes()).hexdigest() != s["source"]["sha256"]:
            errors.append(f"{sid}: missing or modified source snapshot")
    records = []
    for path in sorted((library / "records").glob("*.json")):
        r = read_json(path); records.append(r)
        label = r.get("id", path.name)
        if r.get("kind") not in KINDS or not r.get("label") or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", label):
            errors.append(f"{label}: invalid identity/kind")
        if r.get("status") not in {"source_grounded", "reviewed", "needs_review", "retired"}:
            errors.append(f"{label}: invalid status")
        if r.get("scope") not in {"reusable", "project"} or (r.get("scope") == "project" and not r.get("project")):
            errors.append(f"{label}: invalid scope")
        ids = [f.get("id") for f in r.get("facts", [])]
        if len(ids) != len(set(ids)) or None in ids:
            errors.append(f"{label}: duplicate or missing fact IDs")
        for fact in r.get("facts", []):
            if not fact.get("text") or not fact.get("evidence"):
                errors.append(f"{label}/{fact.get('id')}: missing text/evidence")
            for e in fact.get("evidence", []):
                source = sources.get(e.get("source_id"))
                if not source:
                    errors.append(f"{label}: unknown source {e.get('source_id')}"); continue
                if not evidence_in_scope(source, e, r.get("project") if r.get("scope") == "project" else None):
                    errors.append(f"{label}: cross-project/reusable scope violation")
                if "slide" in e:
                    slide = next((s for s in source.get("slides", []) if s["number"] == e["slide"]), None)
                    shape = next((s for s in (slide or {}).get("shapes", []) if s["id"] == str(e.get("shape_id"))), None)
                    text = shape["text"] if shape else ""
                    if slide and slide["hidden"]:
                        warnings.append(f"{label}: fact cites hidden slide {e['slide']}")
                else:
                    paragraph = next((p for p in source.get("paragraphs", []) if p["number"] == e.get("paragraph")), None)
                    text = paragraph["text"] if paragraph else ""
                if not e.get("quote") or norm(e["quote"]) not in norm(text):
                    errors.append(f"{label}/{fact.get('id')}: quote not found at cited object")
        for asset in r.get("assets", []):
            source = sources.get(asset.get("source_id"))
            if not source:
                errors.append(f"{label}: unknown asset source"); continue
            if not evidence_in_scope(source, asset, r.get("project") if r.get("scope") == "project" else None):
                errors.append(f"{label}: asset scope violation")
            slide = next((s for s in source.get("slides", []) if s["number"] == asset.get("slide")), {})
            shape = next((s for s in slide.get("shapes", []) if s["id"] == str(asset.get("shape_id"))), {})
            if asset.get("media") not in shape.get("media", []) or not resolve_under(library / "sources" / asset["source_id"], asset.get("media", "")).is_file():
                errors.append(f"{label}: invalid asset link")
            if asset.get("role") == "portrait" and not asset.get("identity_verified"):
                warnings.append(f"{label}: portrait identity not verified; do not use automatically")
    all_ids = [r.get("id") for r in records]
    if len(all_ids) != len(set(all_ids)):
        errors.append("Duplicate record IDs")
    profile_path = library / "design/profile.json"
    if profile_path.exists():
        p = read_json(profile_path)
        for sid in p.get("source_ids", []):
            if sid not in sources:
                errors.append(f"design: unknown source {sid}")
        if p.get("template") and not resolve_under(library, p["template"]).is_file():
            errors.append("design: missing template")
        rules = p.get("rules", {}); c = rules.get("content", {}); size = rules.get("slide_cm", {})
        if c and (c["x"] < 0 or c["y"] < 0 or c["x"]+c["w"] > size["width"]+0.001 or c["bottom"] > size["height"]):
            errors.append("design: content outside slide")
        for name, layout in rules.get("layouts", {}).items():
            widths = layout.get("widths", [])
            if widths and sum(widths) + max(0, len(widths)-1)*layout.get("gap", 0) > c["w"]+0.001:
                errors.append(f"design/{name}: columns exceed content width")
        foot = rules.get("footnotes", {})
        if foot and (foot["top"]-foot.get("gap", 0) <= c["y"] or foot["bottom"] > size["height"]):
            errors.append("design: invalid footnote reservation")
        for pattern in p.get("patterns", []):
            ref = pattern.get("reference", {})
            if ref and not any(s["number"] == ref.get("slide") for s in sources.get(ref.get("source_id"), {}).get("slides", [])):
                errors.append(f"design/{pattern.get('id')}: unknown reference slide")
    else:
        warnings.append("No curated design profile yet")
    return {"sources": len(sources), "records": len(records), "kinds": dict(Counter(r.get("kind") for r in records)),
            "errors": errors, "warnings": sorted(set(warnings)), "valid": not errors}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    a = sub.add_parser("init"); a.add_argument("--library", required=True); a.add_argument("--name", required=True)
    a = sub.add_parser("ingest"); a.add_argument("--library", required=True); a.add_argument("paths", nargs="+")
    a.add_argument("--role", choices=["design", "content", "both"], default="both")
    a.add_argument("--scope", choices=["reusable", "project"], default="project"); a.add_argument("--project")
    a = sub.add_parser("search"); a.add_argument("--library", required=True); a.add_argument("--query", required=True)
    a.add_argument("--kind", choices=sorted(KINDS)); a.add_argument("--project"); a.add_argument("--raw", action="store_true")
    a = sub.add_parser("brief"); a.add_argument("path"); a.add_argument("--out", required=True)
    a = sub.add_parser("validate"); a.add_argument("--library", required=True)
    args = p.parse_args()
    try:
        if args.command == "init":
            init_library(args.library, args.name); result = {"library": str(Path(args.library).resolve())}
        elif args.command == "ingest":
            result = [ingest(args.library, x, args.role, args.scope, args.project) for x in args.paths]
        elif args.command == "search":
            result = search(args.library, args.query, args.kind, args.project, args.raw)
        elif args.command == "brief":
            result = brief(args.path); write_json(args.out, result); result = {"out": args.out, "slides": len(result["slides"])}
        else:
            result = validate(args.library)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if isinstance(result, dict) and result.get("valid") is False else 0
    except (ValueError, OSError, KeyError, ET.ParseError) as e:
        print(f"Error: {e}", file=sys.stderr); return 2


if __name__ == "__main__":
    sys.exit(main())
