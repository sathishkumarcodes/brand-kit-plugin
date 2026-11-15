#!/usr/bin/env python3
"""Re-skin the Office templates (.potx / .dotx / .pptx / .docx) from one brand config to another.

    python3 scripts/rebrand_templates.py --from brand.json --to my_brand.json \
        --in assets/templates/Brand_Corporate_Template.potx --out My_Corporate_Template.potx

What it changes:
  * theme colors (dark 2, accents 1-6, hyperlinks, light 2) and every hard-coded brand color, role by role
  * logo, reversed logo, corner accents and cover art images (matched by content, replaced by the new files)
  * company name, legal name, footer text, website and city wherever they appear as text
  * document author metadata
Options:
  --strip-slides        remove all slides from a .potx/.pptx, keeping masters and layouts
  --layout-prefix OLD   remove a prefix such as "LB " from layout names

Brand configs are JSON files like brand.json. Asset paths are resolved relative to the config file.
"""
import argparse
import hashlib
import io
import json
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

from PIL import Image

THEME_ROLES = {"dk1": "text", "dk2": "primary", "lt2": "background", "accent1": "accent", "accent2": "highlight",
               "accent3": "secondary", "accent4": "positive", "accent5": "milestone", "accent6": "extra",
               "hlink": "accent", "folHlink": "secondary"}
TEXT_KEYS = ["footer", "legal_name", "name", "website", "city", "tagline"]


def load(path):
    path = Path(path).resolve()
    cfg = json.loads(path.read_text())
    cfg["_dir"] = path.parent
    return cfg


def color_map(a, b):
    m = {}
    for group in ("colors", "tints"):
        for k, v in a.get(group, {}).items():
            nv = b.get(group, {}).get(k)
            if nv and v.upper() not in m:
                m[v.upper()] = nv.upper()
    return m


def text_pairs(a, b):
    pairs = []
    for k in TEXT_KEYS:
        if a.get(k) and b.get(k):
            pairs.append((a[k], b[k]))
            if k == "legal_name":
                pairs.append((a[k].upper(), b[k].upper()))
    # compact forms such as "AcmeBio" or the wordmark
    if a.get("name") and b.get("name"):
        pairs.append((a["name"].replace(" ", ""), b["name"].replace(" ", "")))
    if a.get("wordmark") and b.get("wordmark"):
        pairs.append((a["wordmark"], b["wordmark"]))
    pairs.sort(key=lambda p: -len(p[0]))
    return pairs


def media_map(a, b):
    """md5 of each old brand image -> bytes of the matching new image."""
    out = {}
    for k, rel in a.get("assets", {}).items():
        old = (a["_dir"] / rel)
        new_rel = b.get("assets", {}).get(k)
        if not old.exists() or not new_rel:
            continue
        new = b["_dir"] / new_rel
        if new.exists():
            out[hashlib.md5(old.read_bytes()).hexdigest()] = new.read_bytes()
    return out


def recolor_xml(x, cmap):
    def sub(m):
        return m.group(1) + cmap.get(m.group(2).upper(), m.group(2)) + m.group(3)
    return re.sub(r'((?:srgbClr val|w:color|w:fill|w:val|fill|color)=")([0-9A-Fa-f]{6})(")', sub, x)


def retheme(x, a, b):
    for slot, role in THEME_ROLES.items():
        new = b["colors"].get(role)
        if new:
            x = re.sub(rf'(<a:{slot}>\s*<a:srgbClr val=")[0-9A-Fa-f]{{6}}(")', rf"\g<1>{new.upper()}\2", x)
    x = re.sub(r'(<a:clrScheme name=")[^"]*(")', rf'\g<1>{b["name"]}\2', x)
    return x


def strip_slides(src, dst):
    from pptx import Presentation
    from pptx.oxml.ns import qn
    tmp = Path(tempfile.mkdtemp()) / "x.pptx"
    with zipfile.ZipFile(src) as zi, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
        for it in zi.infolist():
            d = zi.read(it.filename)
            if it.filename == "[Content_Types].xml":
                d = d.replace(b"presentationml.template.main+xml", b"presentationml.presentation.main+xml")
            zo.writestr(it, d)
    prs = Presentation(str(tmp))
    ids = prs.slides._sldIdLst
    for sid in list(ids):
        prs.part.drop_rel(sid.get(qn("r:id")))
        ids.remove(sid)
    ext = prs.part._element.find(qn("p:extLst"))
    if ext is not None:
        prs.part._element.remove(ext)
    prs.save(str(dst))


APP_XML = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
           '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
           'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
           '<Application>{app}</Application><Company>{company}</Company></Properties>')


def rebrand(src, dst, a, b, strip=False, layout_prefix=None):
    src, dst = Path(src), Path(dst)
    work = Path(tempfile.mkdtemp()) / ("in" + src.suffix)
    if strip and src.suffix in (".potx", ".pptx"):
        strip_slides(src, work)
    else:
        shutil.copy(src, work)
    cmap, pairs, mmap = color_map(a, b), text_pairs(a, b), media_map(a, b)
    template = dst.suffix in (".potx", ".dotx")
    with zipfile.ZipFile(work) as zi, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zo:
        for it in zi.infolist():
            d = zi.read(it.filename)
            name = it.filename
            if name.endswith((".xml", ".rels")):
                x = d.decode("utf-8")
                if name == "[Content_Types].xml":
                    if dst.suffix == ".potx":
                        x = x.replace("presentationml.presentation.main+xml", "presentationml.template.main+xml")
                    elif dst.suffix == ".pptx":
                        x = x.replace("presentationml.template.main+xml", "presentationml.presentation.main+xml")
                    elif dst.suffix == ".dotx":
                        x = x.replace("wordprocessingml.document.main+xml", "wordprocessingml.template.main+xml")
                    elif dst.suffix == ".docx":
                        x = x.replace("wordprocessingml.template.main+xml", "wordprocessingml.document.main+xml")
                elif name == "docProps/app.xml":
                    app = "Microsoft Office PowerPoint" if "ppt/" in "".join(zi.namelist()) else "Microsoft Office Word"
                    x = APP_XML.format(app=app, company=b["legal_name"])
                else:
                    if "theme" in name:
                        x = retheme(x, a, b)
                    x = recolor_xml(x, cmap)
                    for old, new in pairs:
                        x = x.replace(old, new)
                    if layout_prefix:
                        x = x.replace(f'<p:cSld name="{layout_prefix}', '<p:cSld name="')
                    if name == "docProps/core.xml":
                        x = re.sub(r"<dc:creator>[^<]*</dc:creator>", f"<dc:creator>{b['name']}</dc:creator>", x)
                        x = re.sub(r"<cp:lastModifiedBy>[^<]*</cp:lastModifiedBy>", f"<cp:lastModifiedBy>{b['name']}</cp:lastModifiedBy>", x)
                d = x.encode("utf-8")
            elif "/media/" in name:
                h = hashlib.md5(d).hexdigest()
                if h in mmap:
                    try:
                        old_size = Image.open(io.BytesIO(d)).size
                        im = Image.open(io.BytesIO(mmap[h]))
                        if im.size != old_size:
                            im = im.resize(old_size, Image.LANCZOS)
                        buf = io.BytesIO(); im.save(buf, "PNG"); d = buf.getvalue()
                    except Exception:
                        d = mmap[h]
            zo.writestr(it, d)
    return dst


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from", dest="src_cfg", required=True)
    ap.add_argument("--to", dest="dst_cfg", required=True)
    ap.add_argument("--in", dest="inp", required=True, nargs="+")
    ap.add_argument("--out", help="output file (single input) or folder (several inputs)")
    ap.add_argument("--strip-slides", action="store_true")
    ap.add_argument("--layout-prefix")
    args = ap.parse_args()
    a, b = load(args.src_cfg), load(args.dst_cfg)
    for f in args.inp:
        f = Path(f)
        if len(args.inp) == 1 and args.out and Path(args.out).suffix:
            out = Path(args.out)
        else:
            folder = Path(args.out or ".")
            folder.mkdir(parents=True, exist_ok=True)
            out = folder / f.name
        print(rebrand(f, out, a, b, args.strip_slides, args.layout_prefix))


if __name__ == "__main__":
    main()
