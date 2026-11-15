"""Build branded Word documents on the templates with python-docx (brand from brand.json).

    import sys; sys.path.insert(0, "<plugin>/skills/branded-document/scripts")
    from lb_doc import *

    # Report / proposal / SOP / brief
    d = new_report(title="Quarterly Board Update", subtitle="Program status and 2027 plan",
                   meta={"Prepared by": "Name Surname", "Date": "November 15, 2026", "Version": "1.0"},
                   toc=True)
    h1(d, "1. Executive Summary"); p(d, "Lead with the conclusion.")
    callout(d, "Key takeaway: ...")
    bullets(d, ["One", ("Sub-point", 1), "Two"]); numbered(d, ["Step", "Step"])
    table(d, [["Program", "Stage"], ["ACM-101", "Preclinical"]], caption="Table 1. Programs.")
    save(d, "report.docx")

    # Letter on letterhead
    d = new_letter(date="November 15, 2026", recipient=["Name", "Title", "Org", "Street", "City, ST ZIP"],
                   subject="Subject", salutation="Dear Dr. Lee,",
                   paragraphs=["Para 1", "Para 2"], signoff="Sincerely,",
                   signer=["Name Surname, PhD", "Title", BRAND["legal_name"]])
    save(d, "letter.docx")

    # Memo
    d = new_memo(to="All staff", frm="Jane Doe, CEO", date="November 15, 2026", subject="...")
    h2(d, "Purpose"); p(d, "...")
"""
import copy
import tempfile
import zipfile
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Inches, Emu

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets"
LETTERHEAD = ASSETS / "templates" / "Brand_Letterhead.dotx"
REPORT = ASSETS / "templates" / "Brand_Document_Template.dotx"

import json as _json
BRAND = _json.loads((ROOT / "brand.json").read_text(encoding="utf-8"))
_C, _T = BRAND["colors"], BRAND["tints"]
PRIMARY, ACCENT, HIGHLIGHT, SECONDARY, TEXT, MUTED = (_C["primary"], _C["accent"], _C["highlight"], _C["secondary"],
                                                    _C["text"], _C["muted"])
CONTENT_WIDTH_IN = 6.75  # 8.5in page minus 0.875in margins


def _open_template(path):
    tmp = Path(tempfile.mkdtemp()) / "lb.docx"
    with zipfile.ZipFile(path) as zi, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
        for it in zi.infolist():
            d = zi.read(it.filename)
            if it.filename == "[Content_Types].xml":
                d = d.replace(b"wordprocessingml.template.main+xml", b"wordprocessingml.document.main+xml")
            zo.writestr(it, d)
    doc = Document(str(tmp))
    body = doc.element.body
    for el in list(body):
        if el.tag != qn("w:sectPr"):
            body.remove(el)
    return doc


def _style(par, style_id):
    pPr = par._p.get_or_add_pPr()
    ps = pPr.find(qn("w:pStyle"))
    if ps is None:
        ps = OxmlElement("w:pStyle")
        pPr.insert(0, ps)
    ps.set(qn("w:val"), style_id)
    return par


def _runs(par, text, color=None, bold=None, italic=None, size=None):
    """text may contain **bold** segments."""
    parts = text.split("**")
    for i, seg in enumerate(parts):
        if not seg:
            continue
        r = par.add_run(seg)
        if i % 2 == 1:
            r.bold = True
        if bold:
            r.bold = True
        if italic:
            r.italic = True
        if color:
            r.font.color.rgb = RGBColor.from_string(color)
        if size:
            r.font.size = Pt(size)
    return par


def p(doc, text="", style=None, **kw):
    par = doc.add_paragraph()
    if style:
        _style(par, style)
    return _runs(par, text, **kw)


def h1(doc, text): return p(doc, text, "Heading1")
def h2(doc, text): return p(doc, text, "Heading2")
def h3(doc, text): return p(doc, text, "Heading3")
def callout(doc, text): return p(doc, text, "Callout")
def quote(doc, text): return p(doc, text, "Quote")
def small(doc, text): return p(doc, text, "SmallPrint")
def caption(doc, text): return p(doc, text, "Caption")


def page_break(doc):
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def _numbering_ids(doc):
    """Return (bullet_numId, number_abstractId) from the template's numbering part."""
    numbering = doc.part.numbering_part.element
    bullet_abs = number_abs = None
    for a in numbering.findall(qn("w:abstractNum")):
        fmt = a.find(".//" + qn("w:numFmt")).get(qn("w:val"))
        aid = a.get(qn("w:abstractNumId"))
        if fmt == "bullet":
            bullet_abs = aid  # last bullet definition = brand bullets
        elif fmt == "decimal" and number_abs is None:
            number_abs = aid
    bullet_num = None
    for n in numbering.findall(qn("w:num")):
        if n.find(qn("w:abstractNumId")).get(qn("w:val")) == bullet_abs:
            bullet_num = n.get(qn("w:numId"))
    return bullet_num, number_abs


def _new_num(doc, abstract_id):
    numbering = doc.part.numbering_part.element
    ids = [int(n.get(qn("w:numId"))) for n in numbering.findall(qn("w:num"))]
    nid = str(max(ids) + 1)
    num = OxmlElement("w:num")
    num.set(qn("w:numId"), nid)
    a = OxmlElement("w:abstractNumId")
    a.set(qn("w:val"), abstract_id)
    num.append(a)
    ov = OxmlElement("w:lvlOverride")
    ov.set(qn("w:ilvl"), "0")
    so = OxmlElement("w:startOverride")
    so.set(qn("w:val"), "1")
    ov.append(so)
    num.append(ov)
    numbering.append(num)
    return nid


def _list_par(doc, text, num_id, level):
    par = doc.add_paragraph()
    pPr = par._p.get_or_add_pPr()
    numPr = OxmlElement("w:numPr")
    il = OxmlElement("w:ilvl"); il.set(qn("w:val"), str(level))
    ni = OxmlElement("w:numId"); ni.set(qn("w:val"), num_id)
    numPr.append(il); numPr.append(ni)
    pPr.append(numPr)
    return _runs(par, text)


def bullets(doc, items):
    """items: str or (str, level) with level 0 or 1."""
    num_id, _ = _numbering_ids(doc)
    for it in items:
        text, lvl = (it, 0) if isinstance(it, str) else it
        _list_par(doc, text, num_id, lvl)


def numbered(doc, items):
    """A numbered list that restarts at 1."""
    _, abs_id = _numbering_ids(doc)
    nid = _new_num(doc, abs_id)
    for t in items:
        _list_par(doc, t, nid, 0)


def _shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def _borders(table, color=None):
    color = color or _C["border"]
    tblPr = table._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{edge}")
        e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "4"); e.set(qn("w:color"), color)
        b.append(e)
    # schema order: tblBorders goes before shd/tblLayout/tblCellMar/tblLook
    for tag in ("w:shd", "w:tblLayout", "w:tblCellMar", "w:tblLook"):
        nxt = tblPr.find(qn(tag))
        if nxt is not None:
            nxt.addprevious(b)
            return
    tblPr.append(b)


def table(doc, rows, col_widths=None, numeric_cols=(), total_row=False, caption_text=None, caption=None):
    """Brand table: navy header, zebra rows, gray borders. col_widths in inches (sum ~6.75)."""
    nr, nc = len(rows), len(rows[0])
    t = doc.add_table(rows=nr, cols=nc)
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    _borders(t)
    widths = col_widths or [CONTENT_WIDTH_IN / nc] * nc
    for r in range(nr):
        for c in range(nc):
            cell = t.cell(r, c)
            cell.width = Inches(widths[c])
            par = cell.paragraphs[0]
            par.paragraph_format.space_after = Pt(0)
            if c in numeric_cols:
                par.alignment = 2
            header, last = r == 0, total_row and r == nr - 1
            run = par.add_run(str(rows[r][c]))
            run.font.size = Pt(10)
            run.bold = header or last
            run.font.color.rgb = RGBColor.from_string("FFFFFF" if header else (PRIMARY if last else TEXT))
            _shade(cell, PRIMARY if header else (_T["gray"] if last else (_C["zebra"] if r % 2 == 0 else "FFFFFF")))
    # repeat header row on each page
    trPr = t.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader"); th.set(qn("w:val"), "true"); trPr.append(th)
    cap = caption or caption_text
    if cap:
        p(doc, cap, "Caption")
    else:
        doc.add_paragraph()
    return t


def image(doc, path, width_in=6.0, caption_text=None):
    doc.add_picture(str(path), width=Inches(width_in))
    if caption_text:
        p(doc, caption_text, "Caption")


def toc(doc):
    h1(doc, "Contents")
    par = doc.add_paragraph()
    r = par.add_run()
    for kind, txt in (("begin", None), (None, 'TOC \\o "1-3" \\h \\z \\u'), ("separate", None), ("end", None)):
        if kind:
            fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), kind)
            if kind == "begin":
                fc.set(qn("w:dirty"), "true")
            r._r.append(fc)
            if kind == "separate":
                t = OxmlElement("w:t"); t.text = "Right-click and choose Update Field to build the table of contents."
                r._r.append(t)
        else:
            it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = txt
            r._r.append(it)
    # ask Word to refresh fields on open
    settings = doc.settings.element
    if settings.find(qn("w:updateFields")) is None:
        uf = OxmlElement("w:updateFields"); uf.set(qn("w:val"), "true"); settings.append(uf)


def new_report(title, subtitle="", meta=None, toc=False, confidential=True):
    """Cover page + optional table of contents, on the document template (headers/footers kept)."""
    doc = _open_template(REPORT)
    cover = doc.add_paragraph()
    cover.paragraph_format.space_before = Pt(20)
    cover.paragraph_format.space_after = Pt(90)
    cover.add_run().add_picture(str(ASSETS / "logos" / "logo_full_color.png"), width=Inches(1.55))
    p(doc, title, "Title")
    if subtitle:
        p(doc, subtitle, "Subtitle")
    rule = doc.add_paragraph()
    pPr = rule._p.get_or_add_pPr()
    bdr = OxmlElement("w:pBdr"); top = OxmlElement("w:top")
    for k, v in (("val", "single"), ("sz", "24"), ("color", HIGHLIGHT), ("space", "1")):
        top.set(qn(f"w:{k}"), v)
    bdr.append(top); pPr.append(bdr)
    ind = OxmlElement("w:ind"); ind.set(qn("w:right"), "8600"); pPr.append(ind)
    for k, v in (meta or {}).items():
        par = doc.add_paragraph(); par.paragraph_format.space_after = Pt(2)
        _runs(par, f"{k}: ", color=PRIMARY, bold=True); _runs(par, v)
    page_break(doc)
    if toc:
        globals()["toc"](doc)
        page_break(doc)
    _set_header_title(doc, title)
    return doc


def _set_header_title(doc, title):
    """Replace the 'Document Title' text in the running header."""
    for sec in doc.sections:
        for hdr in (sec.header, sec.first_page_header):
            for t in hdr._element.iter(qn("w:t")):
                if t.text == "Document Title":
                    t.text = title


def new_letter(date, recipient, subject=None, salutation="Dear Sir or Madam,", paragraphs=(), signoff="Sincerely,",
               signer=None, bullet_items=None):
    signer = signer or ("Name Surname", "Title", BRAND["legal_name"])
    doc = _open_template(LETTERHEAD)
    p(doc, date).paragraph_format.space_after = Pt(18)
    for i, line in enumerate(recipient):
        par = p(doc, line)
        par.paragraph_format.space_after = Pt(0 if i < len(recipient) - 1 else 18)
    if subject:
        par = doc.add_paragraph(); _runs(par, "Re: ", color=PRIMARY, bold=True); _runs(par, subject)
        par.paragraph_format.space_after = Pt(12)
    p(doc, salutation)
    for t in paragraphs:
        p(doc, t)
    if bullet_items:
        bullets(doc, bullet_items)
    par = p(doc, signoff); par.paragraph_format.space_before = Pt(12); par.paragraph_format.space_after = Pt(36)
    for i, line in enumerate(signer):
        par = p(doc, line, color=[PRIMARY, SECONDARY, MUTED][min(i, 2)], bold=(i == 0))
        par.paragraph_format.space_after = Pt(0)
    return doc


def new_memo(to, frm, date, subject, cc=None):
    """Memo on the document template's running header/footer (no cover)."""
    doc = _open_template(REPORT)
    _set_header_title(doc, "Memorandum")
    # memo has no cover: drop the special first-page header/footer
    for sec in doc.sections:
        sec.different_first_page_header_footer = False
    par = p(doc, "Memorandum", "Title")
    for k, v in (("To:", to), ("From:", frm), ("CC:", cc), ("Date:", date), ("Subject:", subject)):
        if not v:
            continue
        par = doc.add_paragraph(); par.paragraph_format.space_after = Pt(3)
        par.paragraph_format.tab_stops.add_tab_stop(Inches(1.0))
        _runs(par, k, color=PRIMARY, bold=True); par.add_run("\t" + v)
    rule = doc.add_paragraph()
    pPr = rule._p.get_or_add_pPr(); bdr = OxmlElement("w:pBdr"); b = OxmlElement("w:bottom")
    for k, v in (("val", "single"), ("sz", "12"), ("color", PRIMARY), ("space", "1")):
        b.set(qn(f"w:{k}"), v)
    bdr.append(b); pPr.append(bdr)
    return doc


def save(doc, out):
    doc.core_properties.author = BRAND["name"]
    doc.save(str(out))
    return Path(out)
