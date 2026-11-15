#!/usr/bin/env python3
"""Mechanical first pass of a brand + claims review (brand from brand.json).

    python3 brand_audit.py <file.pptx|.docx|.pdf|.txt|.md|.html> [--json]

Flags risky claims, unqualified efficacy numbers, name misuse, leftover placeholders,
off-brand fonts and colors (pptx/docx) and a missing forward-looking-statements slide.
This is a screen, not a verdict: Claude must still read the flagged text in context.
"""
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
BRAND = json.loads((_ROOT / "brand.json").read_text(encoding="utf-8"))
PALETTE = {v.upper() for v in list(BRAND["colors"].values()) + list(BRAND["tints"].values())} | {
    # neutrals and the scientific semantic palette
    "FFFFFF", "000000", "E5E7EB", "4B5563", "9CA3AF", "D6E6F5", "FDE2E3", "DCEFE2", "ECE6FA", "B9A6EA", "FFF1CC",
    "E8F3F8", "EEF0F3", "6CB4EE", "2475B8", "E31E24", "2E7D4F", "8E6BD8", "F2A900", "4A90A4", "93A9C4",
}
_COMPACT = BRAND["name"].replace(" ", "")
BRAND_FONTS = {"arial", "calibri", "carlito", "+mj-lt", "+mn-lt", "georgia", "symbol", "wingdings"}

RULES = [
    # (severity, pattern, message)
    ("HIGH", r"\bcur(e|es|ed|ing)\b", "Says 'cure'. Use 'is designed to' / 'aims to' until clinical data exist."),
    ("HIGH", r"\bwill (restore|reverse|repair|eliminate|fix|treat)\b", "Promises an outcome ('will ...'). Use 'is designed to' / 'aims to' / 'is expected to'."),
    ("HIGH", r"\b(first|only)\b[^.\n]{0,60}\b(medicine|drug|therap\w*|treatment|company)\b[^.\n]{0,40}\b(repair|rejuvenat|restor|revers|soften|treat)", "'First'/'only' claim. Check prior art and competitors; say 'a new approach' or 'next-generation', or source and scope the claim."),
    ("HIGH", r"\b(100%|completely|totally)\s+safe\b|\bsafe and effective\b|\bno side effects\b|\bis safe\b|\bproven safe\b", "Safety claim. Say 'well tolerated in preclinical studies'."),
    ("HIGH", r"\b(proven|clinically proven|guarantee[sd]?)\b", "'Proven'/'guaranteed' is not supportable before clinical data."),
    ("MEDIUM", r"\bFDA[- ]approved\b|\bapproved by (the )?FDA\b", "Check context: an investigational product is not FDA approved. Use only for competitors or approved reference products, and say so explicitly."),
    ("MEDIUM", r"\b(breakthrough|revolutionary|game[- ]chang\w*|miracle|cutting[- ]edge)\b", "Hype word. Replace with a specific fact."),
    ("MEDIUM", r"\b(far superior|vastly superior|dramatically|unprecedented)\b", "Overstated comparison. State the measured difference with model and n."),
    ("MEDIUM", r"\b(10|ten)[- ]?(x|times)\b", "Fold-change claim. Check the ratio against both underlying numbers and name the model."),
    ("LOW", r"\b" + _COMPACT + r"\b", f"Write '{BRAND['name']}' in running text; the wordmark is for the logo only."),
]
EFFICACY = re.compile(r"\b\d{1,3}(\.\d)?\s?%\s*(restoration|restored|improvement|increase|reduction|response|of healthy)?", re.I)
EFFICACY_CONTEXT = re.compile(r"restor|efficac|respon|reduc|improv|inhibit|activity|clearance|fibros", re.I)
MODEL_WORDS = re.compile(r"\b(mouse|mice|murine|rat|rabbit|primate|ex vivo|in vivo|in vitro|donor|human tissue|preclinical|cell line|n\s?=)", re.I)
PLACEHOLDERS = re.compile(r"555-01\d\d|\(555\) 010-|Name Surname|First Last|lorem ipsum|\bTBD\b|\bTBC\b|\bXXX+\b|Click to add|Job Title|Recipient Name|email@example\.com|\[[A-Z][^\]]{2,30}\]", re.I)


def units_pptx(path):
    from pptx import Presentation
    prs = Presentation(path)
    out = []
    for i, s in enumerate(prs.slides, 1):
        texts = []
        for shp in s.shapes:
            if shp.has_text_frame:
                texts.append(shp.text_frame.text)
            if getattr(shp, "has_table", False) and shp.has_table:
                for row in shp.table.rows:
                    texts.append(" | ".join(c.text for c in row.cells))
        if s.has_notes_slide:
            n = s.notes_slide.notes_text_frame.text
            if n.strip():
                texts.append("[notes] " + n)
        out.append((f"slide {i}", "\n".join(texts)))
    return out


def units_docx(path):
    from docx import Document
    d = Document(path)
    out = [(f"paragraph {i}", p.text) for i, p in enumerate(d.paragraphs, 1) if p.text.strip()]
    for ti, t in enumerate(d.tables, 1):
        for ri, row in enumerate(t.rows, 1):
            out.append((f"table {ti} row {ri}", " | ".join(c.text for c in row.cells)))
    return out


def units_pdf(path):
    import subprocess
    txt = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, text=True).stdout
    return [(f"page {i}", t) for i, t in enumerate(txt.split("\f"), 1) if t.strip()]


def units_text(path):
    raw = Path(path).read_text(encoding="utf-8", errors="ignore")
    if path.lower().endswith((".html", ".htm")):
        raw = re.sub(r"<[^>]+>", " ", raw)
    return [(f"line {i}", l) for i, l in enumerate(raw.splitlines(), 1) if l.strip()]


def styling(path):
    """Fonts and colors used in an Office file's slide/document XML (not masters/layouts)."""
    fonts, colors = Counter(), Counter()
    with zipfile.ZipFile(path) as z:
        for n in z.namelist():
            if re.match(r"(ppt/slides/slide\d+\.xml|ppt/charts/chart\d+\.xml|word/document\.xml)$", n):
                x = z.read(n).decode("utf8", "ignore")
                for f in re.findall(r'<a:latin typeface="([^"]+)"', x) + re.findall(r'w:ascii="([^"]+)"', x):
                    fonts[f] += 1
                for c in re.findall(r'(?:srgbClr val|w:color w:val|w:fill)="([0-9A-Fa-f]{6})"', x):
                    colors[c.upper()] += 1
    return fonts, colors


def audit(path):
    ext = Path(path).suffix.lower()
    units = {".pptx": units_pptx, ".potx": units_pptx, ".docx": units_docx, ".dotx": units_docx, ".pdf": units_pdf}.get(ext, units_text)(path)
    findings = []
    for where, text in units:
        for sev, pat, msg in RULES:
            for m in re.finditer(pat, text, re.I if _COMPACT not in pat else 0):
                findings.append({"severity": sev, "where": where, "match": m.group(0), "issue": msg, "context": _ctx(text, m)})
        # efficacy numbers without a model named nearby
        for m in EFFICACY.finditer(text):
            window = text[max(0, m.start() - 160): m.end() + 160]
            if EFFICACY_CONTEXT.search(window) and not MODEL_WORDS.search(text):
                findings.append({"severity": "MEDIUM", "where": where, "match": m.group(0), "context": _ctx(text, m),
                                 "issue": "Efficacy number without the model (e.g. mouse, ex vivo human tissue, cell line) and duration on the same slide or paragraph."})
        for m in PLACEHOLDERS.finditer(text):
            findings.append({"severity": "MEDIUM", "where": where, "match": m.group(0), "context": _ctx(text, m),
                             "issue": "Placeholder or unconfirmed contact detail left in."})
    report = {"file": str(path), "units_checked": len(units), "findings": findings}
    if ext in (".pptx", ".potx", ".docx", ".dotx"):
        fonts, colors = styling(path)
        report["off_brand_fonts"] = {f: n for f, n in fonts.items() if f.lower() not in BRAND_FONTS}
        report["off_palette_colors"] = {c: n for c, n in colors.most_common() if c not in PALETTE}
    if ext in (".pptx", ".potx"):
        alltext = " ".join(t for _, t in units).lower()
        if len(units) >= 8 and "forward-looking" not in alltext:
            report["findings"].append({"severity": "HIGH", "where": "deck", "match": "", "context": "",
                                       "issue": "No forward-looking-statements disclaimer. Investor or external decks need one near the front."})
    return report


def _ctx(text, m):
    s = text[max(0, m.start() - 70): m.end() + 70].replace("\n", " ")
    return ("..." if m.start() > 70 else "") + s.strip() + ("..." if m.end() + 70 < len(text) else "")


def to_markdown(r):
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    f = sorted(r["findings"], key=lambda x: (order[x["severity"]], x["where"]))
    lines = [f"# Brand and claims audit: {Path(r['file']).name}", "",
             f"Checked {r['units_checked']} sections. Findings: " + ", ".join(f"{s} {sum(1 for x in f if x['severity']==s)}" for s in order), ""]
    if f:
        lines += ["| Severity | Where | Found | Issue | Context |", "| --- | --- | --- | --- | --- |"]
        for x in f:
            lines.append(f"| {x['severity']} | {x['where']} | {x['match']} | {x['issue']} | {x['context'].replace('|', '/')} |")
    if r.get("off_brand_fonts"):
        lines += ["", "**Off-brand fonts:** " + ", ".join(f"{k} ({v})" for k, v in r["off_brand_fonts"].items())]
    if r.get("off_palette_colors"):
        lines += ["", "**Off-palette colors:** " + ", ".join(f"#{k} ({v})" for k, v in list(r["off_palette_colors"].items())[:15])]
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    rep = audit(sys.argv[1])
    print(json.dumps(rep, indent=1) if "--json" in sys.argv else to_markdown(rep))
