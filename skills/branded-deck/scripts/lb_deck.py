"""Build branded decks on the corporate template with python-pptx (brand from brand.json).

Usage (from Python):
    import sys; sys.path.insert(0, "<plugin>/skills/branded-deck/scripts")
    from lb_deck import *
    prs = new_deck()
    s = add_slide(prs, "cover", title="Breaking Cross-Links", subtitle="...", tagline="Investor update | Nov 2026")
    s = add_slide(prs, "content", title="Takeaway as a sentence", body=["Point", ("Sub-point", 1)])
    save(prs, "out.pptx")

Run `python3 lb_deck.py --layouts` to print every layout and its fields.
"""
import copy
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt, Emu

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets"
TEMPLATE = ASSETS / "templates" / "Brand_Corporate_Template.potx"

import json as _json
BRAND = _json.loads((ROOT / "brand.json").read_text(encoding="utf-8"))
_C, _T = BRAND["colors"], BRAND["tints"]

PRIMARY, ACCENT, HIGHLIGHT, SECONDARY = _C["primary"], _C["accent"], _C["highlight"], _C["secondary"]
POSITIVE, MILESTONE, EXTRA = _C["positive"], _C["milestone"], _C["extra"]
TEXT, MUTED, LINE, ZEBRA = _C["text"], _C["muted"], _C["border"], _C["zebra"]
REFERENCE, COMPARATOR = _C["reference"], _C["comparator"]
TINT = dict(_T)
CHART_COLORS = [PRIMARY, ACCENT, SECONDARY, MILESTONE, HIGHLIGHT, EXTRA]

# Content area on layouts with the standard header/footer (inches)
CONTENT = dict(left=0.45, top=1.2, width=9.1, height=4.05)

# Friendly layout keys -> (template layout name, {field: placeholder idx})
LAYOUTS = {
    "cover": ("Cover", {"title": 102, "subtitle": 103, "tagline": 104}),
    "cover-photo": ("Cover Photo", {"photo": 100, "title": 103, "subtitle": 104, "tagline": 105}),
    "agenda": ("Agenda", {"title": 103, "body": 104}),
    "section": ("Section", {"title": 102, "body": 103}),
    "section-number": ("Section Number", {"number": 101, "title": 103, "body": 104}),
    "section-light": ("Section Light", {"number": 102, "title": 104, "body": 105}),
    "photo-divider": ("Photo Divider", {"photo": 100, "title": 103, "body": 104}),
    "content": ("Title and Content", {"title": 105, "body": 106}),
    "content-subheading": ("Title Subheading Content", {"title": 105, "subheading": 106, "body": 107}),
    "two-content": ("Two Content", {"title": 105, "left": 106, "right": 107}),
    "comparison": ("Comparison", {"title": 105, "left_head": 108, "right_head": 109, "left": 110, "right": 111}),
    "content-picture": ("Content with Picture", {"title": 105, "subheading": 106, "body": 107, "photo": 108}),
    "chart": ("Chart", {"title": 105, "chart": 106, "takeaway_head": 108, "takeaway": 109, "source": 110}),
    "table": ("Table", {"title": 105, "subheading": 106, "table": 107, "source": 108}),
    "title-only": ("Title Only", {"title": 105}),
    "blank": ("Blank", {}),
    "statement": ("Statement", {"title": 105, "statement": 107}),
    "big-number": ("Big Number", {"number": 104, "label": 105, "title": 106, "body": 108}),
    "quote": ("Quote", {"quote": 104, "name": 106, "role": 107}),
    "disclaimer": ("Disclaimer", {"title": 105, "body": 106}),
    "closing": ("Closing", {"title": 101, "body": 102}),
}
BULLET_FIELDS = {"body", "left", "right", "takeaway"}
NO_BULLET_LAYOUTS = {"big-number", "disclaimer", "section", "section-number", "section-light", "photo-divider", "closing", "cover", "cover-photo"}

_DISCLAIMER = [
    "This presentation contains forward-looking statements about {name}'s product candidates, development plans, timelines, regulatory pathway, market opportunity and potential transactions. Words such as “expect,” “plan,” “target,” “will” and similar expressions identify forward-looking statements.",
    "These statements are based on current expectations and preclinical data and involve risks and uncertainties, including the outcome of clinical trials, regulatory review, manufacturing, financing and competition. Actual results may differ materially. Preclinical results, including animal and ex vivo human-tissue studies, may not predict clinical outcomes.",
    "This presentation is confidential and is not an offer to sell or a solicitation of an offer to buy any securities. Market data are drawn from third-party sources that {name} has not independently verified.",
]

DISCLAIMER_TEXT = [t.replace("{name}", BRAND["name"]) for t in _DISCLAIMER]


def rgb(h):
    return RGBColor.from_string(h)


def new_deck(template=TEMPLATE):
    """Open the corporate template as a presentation with all sample slides removed."""
    tmp = Path(tempfile.mkdtemp()) / "lb.pptx"
    with zipfile.ZipFile(template) as zi, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
        for it in zi.infolist():
            d = zi.read(it.filename)
            if it.filename == "[Content_Types].xml":
                d = d.replace(b"presentationml.template.main+xml", b"presentationml.presentation.main+xml")
            zo.writestr(it, d)
    prs = Presentation(str(tmp))
    sld_ids = prs.slides._sldIdLst
    for sid in list(sld_ids):
        prs.part.drop_rel(sid.get(qn("r:id")))
        sld_ids.remove(sid)
    # remove the sample-slide section list so PowerPoint doesn't need to repair the file
    ext = prs.part._element.find(qn("p:extLst"))
    if ext is not None:
        prs.part._element.remove(ext)
    prs.core_properties.title = BRAND["name"]
    prs.core_properties.author = BRAND["name"]
    prs.core_properties.last_modified_by = BRAND["name"]
    return prs


def _layout(prs, name):
    for l in prs.slide_layouts:
        if l.name == name:
            return l
    raise KeyError(f"Layout {name!r} not in template")


def _fade(slide):
    sld = slide._element
    if sld.find(qn("p:transition")) is not None:
        return
    tr = etree.SubElement(sld, qn("p:transition"))
    tr.set("spd", "med")
    etree.SubElement(tr, qn("p:fade"))
    # p:transition must come right after p:clrMapOvr (or p:cSld)
    anchor = sld.find(qn("p:clrMapOvr"))
    if anchor is None:
        anchor = sld.find(qn("p:cSld"))
    anchor.addnext(tr)


def _layout_size(shape):
    """Font size (pt) the template layout defines for this placeholder's first level."""
    try:
        base = shape._base_placeholder
        sz = base._element.xpath(".//a:lstStyle/a:lvl1pPr/a:defRPr/@sz")
        if not sz:
            sz = base._element.xpath(".//a:p/a:r/a:rPr/@sz")
        return int(sz[0]) / 100 if sz else None
    except Exception:
        return None


def _set_text(shape, value, bullets, numbered=False):
    """value: str | list[str | (str, level) | dict(text, level, bold)]."""
    size = _layout_size(shape)
    tf = shape.text_frame
    items = value if isinstance(value, list) else [value]
    tf.clear()
    for i, it in enumerate(items):
        if isinstance(it, tuple):
            it = {"text": it[0], "level": it[1]}
        elif isinstance(it, str):
            it = {"text": it}
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        lvl = it.get("level", 0)
        lines = it["text"].split("\n")
        for j, line in enumerate(lines):
            r = p.add_run()
            r.text = line
            if j < len(lines) - 1:
                r._r.addnext(etree.Element(qn("a:br")))
            if size:
                r.font.size = Pt(size - 2 * lvl)
            if it.get("bold"):
                r.font.bold = True
        pPr = p._p.get_or_add_pPr()
        for tag in ("a:buChar", "a:buAutoNum", "a:buNone"):
            for e in pPr.findall(qn(tag)):
                pPr.remove(e)
        if numbered:
            etree.SubElement(pPr, qn("a:buAutoNum"), type="arabicPeriod")
            pPr.set("marL", "457200"); pPr.set("indent", "-457200")
            sa = etree.SubElement(pPr, qn("a:spcAft")); etree.SubElement(sa, qn("a:spcPts"), val="1400")
            pPr.insert(0, sa)
        elif bullets:
            if lvl == 0:
                pPr.set("marL", "342900"); pPr.set("indent", "-342900")
                etree.SubElement(pPr, qn("a:buChar"), char="\u2022")
            else:
                pPr.set("marL", str(342900 + 342900 * lvl)); pPr.set("indent", "-228600")
                etree.SubElement(pPr, qn("a:buChar"), char="\u2013")
            sa = etree.Element(qn("a:spcAft")); etree.SubElement(sa, qn("a:spcPts"), val="600")
            pPr.insert(0, sa)
        else:
            etree.SubElement(pPr, qn("a:buNone"))
            pPr.set("marL", "0"); pPr.set("indent", "0")
            if len(items) > 1:
                sa = etree.Element(qn("a:spcAft")); etree.SubElement(sa, qn("a:spcPts"), val="800")
                pPr.insert(0, sa)


def add_slide(prs, layout, notes=None, **fields):
    """Add a slide from a friendly layout key and fill its fields (see LAYOUTS).

    Text fields take a string or a list (bullets: str, (str, level) or dict).
    'photo' takes an image path (cropped to fill). 'chart' takes dict(kind, categories, series, ...).
    'table' takes a list of rows (first row = header).
    """
    name, roles = LAYOUTS[layout]
    slide = prs.slides.add_slide(_layout(prs, name))
    phs = {ph.placeholder_format.idx: ph for ph in slide.placeholders}
    for key, val in fields.items():
        if key not in roles:
            raise KeyError(f"{layout!r} has no field {key!r}; fields: {list(roles)}")
        ph = phs.get(roles[key])
        if ph is None:
            continue
        if key == "photo":
            picture_in(slide, ph, val)
        elif key == "chart":
            add_chart(slide, box=_box(ph), **val)
            ph._element.getparent().remove(ph._element)
        elif key == "table":
            add_table(slide, val, box=_box(ph))
            ph._element.getparent().remove(ph._element)
        else:
            bullets = key in BULLET_FIELDS and layout not in NO_BULLET_LAYOUTS
            _set_text(ph, val, bullets, numbered=(layout == "agenda" and key == "body"))
    # remove placeholders left empty so no "Click to add" prompts remain
    for ph in list(slide.placeholders):
        if ph.placeholder_format.type is not None and ph.placeholder_format.idx in roles.values():
            if ph.has_text_frame and not ph.text_frame.text.strip():
                ph._element.getparent().remove(ph._element)
    if notes:
        slide.notes_slide.notes_text_frame.text = notes
    _fade(slide)
    return slide


def _box(ph):
    return (ph.left, ph.top, ph.width, ph.height)


def picture_in(slide, ph, path):
    """Place an image cropped to fill a placeholder's box, then remove the placeholder."""
    from PIL import Image
    left, top, w, h = _box(ph)
    ph._element.getparent().remove(ph._element)
    return add_picture_fill(slide, path, left, top, w, h)


def add_picture_fill(slide, path, left, top, width, height):
    from PIL import Image
    iw, ih = Image.open(path).size
    pic = slide.shapes.add_picture(str(path), left, top, width, height)
    box_r, img_r = width / height, iw / ih
    if img_r > box_r:
        c = (1 - box_r / img_r) / 2
        pic.crop_left = pic.crop_right = c
    else:
        c = (1 - img_r / box_r) / 2
        pic.crop_top = pic.crop_bottom = c
    # send behind other shapes so overlays on the layout stay visible
    sp_tree = slide.shapes._spTree
    sp_tree.remove(pic._element)
    sp_tree.insert(2, pic._element)
    return pic


def add_text(slide, text, left, top, width, height, size=14, color=TEXT, bold=False, italic=False,
             align="left", valign="top", font=None):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = {"top": MSO_ANCHOR.TOP, "middle": MSO_ANCHOR.MIDDLE, "bottom": MSO_ANCHOR.BOTTOM}[valign]
    for i, line in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}[align]
        r = p.add_run()
        r.text = line
        f = r.font
        f.size, f.bold, f.italic = Pt(size), bold, italic
        f.color.rgb = rgb(color)
        if font:
            f.name = font
    return tb


def add_box(slide, left, top, width, height, fill=TINT["accent"], line=None, rounded=False):
    from pptx.enum.shapes import MSO_SHAPE
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE,
                                 Inches(left), Inches(top), Inches(width), Inches(height))
    shp.fill.solid()
    shp.fill.fore_color.rgb = rgb(fill)
    if line:
        shp.line.color.rgb = rgb(line)
        shp.line.width = Pt(0.75)
    else:
        shp.line.fill.background()
    shp.shadow.inherit = False
    if rounded:
        shp.adjustments[0] = 0.08
    return shp


def stat_cards(slide, stats, top=1.35, height=1.9, fill=TINT["accent"]):
    """stats: list of (big_number, label). Lays out 2-4 cards across the content width."""
    n = len(stats)
    gap = 0.2
    w = (CONTENT["width"] - gap * (n - 1)) / n
    for i, (num, label) in enumerate(stats):
        x = CONTENT["left"] + i * (w + gap)
        add_box(slide, x, top, w, height, fill)
        add_text(slide, num, x, top + 0.12, w, height * 0.5, size=44 if n <= 3 else 36, color=PRIMARY, bold=True, align="center", valign="middle")
        add_text(slide, label, x + 0.2, top + height * 0.58, w - 0.4, height * 0.4, size=14, align="center")


def banner(slide, text, top=4.35, height=0.8, fill=PRIMARY, color="FFFFFF", size=20):
    add_box(slide, CONTENT["left"], top, CONTENT["width"], height, fill)
    add_text(slide, text, CONTENT["left"] + 0.2, top, CONTENT["width"] - 0.4, height, size=size, color=color, bold=True, align="center", valign="middle")


def add_table(slide, rows, box=None, left=None, top=None, width=None, col_widths=None, highlight_row=None,
              total_row=False, numeric_cols=(), font_size=12):
    """Brand table: navy header, zebra rows, thin gray borders, right-aligned numeric columns."""
    if box is None:
        box = (Inches(left or CONTENT["left"]), Inches(top or 1.6), Inches(width or CONTENT["width"]), Inches(0.4 * len(rows)))
    l, t, w, _ = box
    nr, nc = len(rows), len(rows[0])
    gt = slide.shapes.add_table(nr, nc, l, t, w, Inches(0.4 * nr))
    tbl = gt.table
    # strip the default table style so our fills show
    tblPr = tbl._tbl.tblPr
    for attr in ("bandRow", "firstRow"):
        tblPr.set(attr, "0")
    sid = tblPr.find(qn("a:tableStyleId"))
    if sid is not None:
        sid.text = "{5940675A-B579-460E-94D1-54222C63F5DA}"  # "No Style, Table Grid"
    if col_widths:
        for i, cw in enumerate(col_widths):
            tbl.columns[i].width = Inches(cw)
    for r in range(nr):
        tbl.rows[r].height = Inches(0.4)
        for c in range(nc):
            cell = tbl.cell(r, c)
            cell.margin_left = cell.margin_right = Inches(0.08)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.text = str(rows[r][c])
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.RIGHT if c in numeric_cols else PP_ALIGN.LEFT
            f = p.runs[0].font if p.runs else p.font
            f.size = Pt(font_size)
            f.name = "Calibri"
            header = r == 0
            last = total_row and r == nr - 1
            f.bold = header or last
            f.color.rgb = rgb("FFFFFF" if header else (PRIMARY if last else TEXT))
            cell.fill.solid()
            if header:
                cell.fill.fore_color.rgb = rgb(PRIMARY)
            elif last:
                cell.fill.fore_color.rgb = rgb(TINT["gray"])
            elif highlight_row == r:
                cell.fill.fore_color.rgb = rgb(TINT["accent"])
            else:
                cell.fill.fore_color.rgb = rgb(ZEBRA if r % 2 == 0 else "FFFFFF")
            _cell_borders(cell)
    return gt


def _cell_borders(cell, color=LINE, w=6350):
    tcPr = cell._tc.get_or_add_tcPr()
    for tag in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
        ln = etree.SubElement(tcPr, qn(tag), w=str(w))
        sf = etree.SubElement(ln, qn("a:solidFill"))
        etree.SubElement(sf, qn("a:srgbClr"), val=color)
    # schema order: borders must precede fill
    fill = tcPr.find(qn("a:solidFill"))
    if fill is not None:
        tcPr.remove(fill)
        tcPr.append(fill)


def add_chart(slide, kind="column", categories=(), series=None, box=None, title=None, colors=None,
              number_format='0', show_values=True, legend=None, left=None, top=None, width=None, height=None):
    """kind: column | bar | line | doughnut | stacked. series: {name: [values]}."""
    types = {"column": XL_CHART_TYPE.COLUMN_CLUSTERED, "bar": XL_CHART_TYPE.BAR_CLUSTERED, "line": XL_CHART_TYPE.LINE_MARKERS,
             "doughnut": XL_CHART_TYPE.DOUGHNUT, "stacked": XL_CHART_TYPE.COLUMN_STACKED}
    cd = CategoryChartData()
    cd.categories = list(categories)
    for name, vals in (series or {}).items():
        cd.add_series(name, list(vals))
    if box is None:
        box = (Inches(left or 0.45), Inches(top or 1.2), Inches(width or 6.0), Inches(height or 3.85))
    gf = slide.shapes.add_chart(types[kind], *box, cd)
    ch = gf.chart
    ch.font.name = "Calibri"
    ch.font.size = Pt(11)
    ch.font.color.rgb = rgb("4B5563")
    colors = colors or CHART_COLORS
    if title:
        ch.has_title = True
        ch.chart_title.text_frame.text = title
        tp = ch.chart_title.text_frame.paragraphs[0]
        tp.runs[0].font.size = Pt(13)
        tp.runs[0].font.bold = True
        tp.runs[0].font.color.rgb = rgb(PRIMARY)
    else:
        ch.has_title = False
    nser = len(series or {})
    ch.has_legend = legend if legend is not None else (nser > 1 or kind == "doughnut")
    if ch.has_legend:
        ch.legend.position = XL_LEGEND_POSITION.BOTTOM
        ch.legend.include_in_layout = False
    plot = ch.plots[0]
    if kind == "doughnut":
        for i, pt in enumerate(plot.series[0].points):
            pt.format.fill.solid()
            pt.format.fill.fore_color.rgb = rgb(colors[i % len(colors)])
    else:
        if kind in ("column", "bar", "stacked"):
            plot.gap_width = 70
        single = nser == 1 and kind in ("column", "bar") and len(colors) >= len(categories) and colors is not CHART_COLORS
        for i, s in enumerate(plot.series):
            if kind == "line":
                s.format.line.color.rgb = rgb(colors[i % len(colors)])
                s.format.line.width = Pt(2.25)
                s.smooth = False
            elif single:
                for j, pt in enumerate(s.points):
                    pt.format.fill.solid()
                    pt.format.fill.fore_color.rgb = rgb(colors[j])
            else:
                s.format.fill.solid()
                s.format.fill.fore_color.rgb = rgb(colors[i % len(colors)])
        va = ch.value_axis
        va.has_major_gridlines = True
        va.major_gridlines.format.line.color.rgb = rgb("E5E7EB")
        va.format.line.fill.background()
        va.tick_labels.font.size = Pt(10)
        ch.category_axis.tick_labels.font.size = Pt(11)
        ch.category_axis.format.line.color.rgb = rgb(_C["rule"])
    if show_values:
        plot.has_data_labels = True
        dl = plot.data_labels
        dl.number_format = number_format
        dl.number_format_is_linked = False
        dl.font.size = Pt(11)
        if kind in ("column", "bar"):
            dl.position = XL_LABEL_POSITION.OUTSIDE_END
        if kind == "doughnut":
            dl.font.color.rgb = rgb("FFFFFF")
    return gf


def add_icon(slide, category, name, left, top, size=0.6, style="circle"):
    """style: circle | dark | white. See assets/icons/INDEX.md for names."""
    folder = {"circle": "png-circle", "dark": "png-dark", "white": "png-white"}[style]
    path = ASSETS / "icons" / folder / category / f"{name}.png"
    return slide.shapes.add_picture(str(path), Inches(left), Inches(top), Inches(size), Inches(size))


def add_disclaimer(prs):
    return add_slide(prs, "disclaimer", title="Forward-Looking Statements", body=DISCLAIMER_TEXT)


def save(prs, out):
    out = Path(out)
    prs.save(str(out))
    return out


def print_layouts():
    for k, (name, roles) in LAYOUTS.items():
        print(f"{k:20s} {name:30s} fields: {', '.join(roles) or '(none)'}")


if __name__ == "__main__":
    if "--layouts" in sys.argv:
        print_layouts()
    else:
        print(__doc__)
