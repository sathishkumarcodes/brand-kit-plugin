"""Scientific-figure building blocks (python-pptx native shapes, all editable).

    import sys
    sys.path.insert(0, "<plugin>/skills/branded-deck/scripts")
    sys.path.insert(0, "<plugin>/skills/scientific-figure/scripts")
    from lb_deck import new_deck, add_slide, save
    from lb_sci import *
    prs = new_deck()
    s = add_slide(prs, "title-only", title="ACM-101 Mechanism of Action")
    panel(s, 0.45, 1.6, 2.0, 2.3, "Cornea → aqueous humor")
    prodrug(s, 0.9, 2.3); arrow(s, 2.5, 2.75, 2.9, 2.75)
    legend(s, ["protein", "crosslink", "drug"], 0.45, 4.6)
    save(prs, "figure.pptx")

All positions/sizes are inches. Colors follow the semantic palette (SCI below) - never recolor.
"""
from lxml import etree
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

SCI = {
    "protein": ("D6E6F5", "2475B8"), "crosslink": ("FDE2E3", "E31E24"), "protective": ("DCEFE2", "2E7D4F"),
    "drug": ("ECE6FA", "8E6BD8"), "prodrug": ("B9A6EA", "8E6BD8"), "enzyme": ("FFF1CC", "F2A900"),
    "tissue": ("E8F3F8", "4A90A4"), "inactive": ("EEF0F3", "9CA3AF"),
}
LEGEND_NAMES = {"protein": "Target protein", "crosslink": "Cross-link / damage", "protective": "Protective molecule",
                "drug": "Active drug", "prodrug": "Prodrug", "enzyme": "Activating enzyme",
                "tissue": "Tissue / compartment", "inactive": "Diseased / inactive / control"}
import json as _json
from pathlib import Path as _Path
_BRAND = _json.loads((_Path(__file__).resolve().parents[3] / "brand.json").read_text(encoding="utf-8"))
INK, LIGHT = _BRAND["colors"]["primary"], "6CB4EE"


def _rgb(h):
    return RGBColor.from_string(h)


def _shape(slide, kind, x, y, w, h, fill, line, lw=1.5, name=None):
    s = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill:
        s.fill.solid(); s.fill.fore_color.rgb = _rgb(fill)
    else:
        s.fill.background()
    if line:
        s.line.color.rgb = _rgb(line); s.line.width = Pt(lw)
    else:
        s.line.fill.background()
    s.shadow.inherit = False
    if name:
        s.name = name
    return s


def label(slide, text, x, y, w, h=0.25, size=11, color=INK, bold=False, align="center", italic=False):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}[align]
    r = p.add_run(); r.text = text
    r.font.size, r.font.bold, r.font.italic = Pt(size), bold, italic
    r.font.color.rgb = _rgb(color)
    return tb


def _inside_text(shape, text, color, size=10):
    tf = shape.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = text
    r.font.size, r.font.bold = Pt(size), True
    r.font.color.rgb = _rgb(color)


def protein(slide, x, y, w=1.1, h=0.42, text=None, state="protein"):
    fill, line = SCI[state]
    s = _shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill, line, name="Protein")
    s.adjustments[0] = 0.5
    if text:
        _inside_text(s, text, line)
    return s


def crosslink(slide, x, y1, y2, show_label=True):
    """Vertical S-S bond between two proteins at horizontal position x."""
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x), Inches(y1), Inches(x), Inches(y2))
    c.line.color.rgb = _rgb(SCI["crosslink"][1]); c.line.width = Pt(3)
    if show_label:
        label(slide, "S–S", x + 0.06, (y1 + y2) / 2 - 0.1, 0.45, 0.2, size=9, color=SCI["crosslink"][1], bold=True, align="left")
    return c


def molecule(slide, x, y, d=0.32, kind="protective", text=None):
    fill, line = SCI[kind]
    s = _shape(slide, MSO_SHAPE.OVAL, x, y, d, d, fill, line, name=LEGEND_NAMES.get(kind, kind))
    if text:
        label(slide, text, x - 0.3, y + d + 0.03, d + 0.6, 0.22, size=9, color=line, bold=True)
    return s


def prodrug(slide, x, y, d=0.28, text=None):
    """Active core (circle) carrying a promoiety (square tag)."""
    fill, line = SCI["drug"]
    core = _shape(slide, MSO_SHAPE.OVAL, x, y, d, d, fill, line, name="Prodrug core")
    tag = _shape(slide, MSO_SHAPE.RECTANGLE, x + d - 0.03, y + d * 0.3, d * 0.45, d * 0.4, SCI["prodrug"][0], line, name="Promoiety")
    if text:
        label(slide, text, x - 0.3, y + d + 0.03, d + 0.75, 0.22, size=9, color=line, bold=True)
    return core, tag


def enzyme(slide, x, y, d=0.55, text="Enzyme"):
    fill, line = SCI["enzyme"]
    s = _shape(slide, MSO_SHAPE.PIE, x, y, d, d, fill, line, name="Enzyme")
    try:
        s.adjustments[0], s.adjustments[1] = 35, 325
    except Exception:
        pass
    if text:
        label(slide, text, x - 0.3, y + d + 0.04, d + 0.6, 0.22, size=10, color=line, bold=True)
    return s


def panel(slide, x, y, w, h, title=None, kind="tissue"):
    """Rounded background panel for a compartment (tissue) or condition (inactive = aged/control)."""
    fill, line = SCI[kind] if kind in SCI else ("FFFFFF", "C9CED6")
    s = _shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill, line, lw=1, name="Panel")
    s.adjustments[0] = 0.08
    if title:
        label(slide, title, x + 0.05, y + 0.08, w - 0.1, 0.25, size=10, color=line, bold=True)
    return s


def organ(slide, x, y, diseased=False):
    """Organ/tissue cross-section: healthy = wide oval; stiff/diseased = thin gray oval."""
    fill, line = (SCI["inactive"] if diseased else (SCI["tissue"][0], SCI["protein"][1]))
    w = 0.26 if diseased else 0.5
    return _shape(slide, MSO_SHAPE.OVAL, x, y, w, 1.2, fill, line, lw=2, name="Diseased" if diseased else "Healthy")


def _arrowhead(conn, head="triangle"):
    ln = conn.line._get_or_add_ln()
    tail = etree.SubElement(ln, qn("a:tailEnd"))
    tail.set("type", head); tail.set("w", "med"); tail.set("len", "med")


def arrow(slide, x1, y1, x2, y2, kind="activate"):
    """kind: activate (navy solid) | convert (dashed purple) | light (light blue) | inhibit (red, bar end) | reversible."""
    if kind == "reversible":
        arrow(slide, x1, y1 - 0.07, x2, y2 - 0.07, "activate")
        return arrow(slide, x2, y2 + 0.07, x1, y1 + 0.07, "activate")
    color = {"activate": INK, "convert": SCI["drug"][1], "light": LIGHT, "inhibit": SCI["crosslink"][1]}[kind]
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = _rgb(color); c.line.width = Pt(2)
    if kind == "convert":
        from pptx.enum.dml import MSO_LINE_DASH_STYLE
        c.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    if kind == "inhibit":
        # flat bar across the end (horizontal or vertical arrows)
        if abs(x2 - x1) >= abs(y2 - y1):
            _shape(slide, MSO_SHAPE.RECTANGLE, x2 - 0.025, y2 - 0.14, 0.05, 0.28, color, None)
        else:
            _shape(slide, MSO_SHAPE.RECTANGLE, x2 - 0.14, y2 - 0.025, 0.28, 0.05, color, None)
    else:
        _arrowhead(c)
    return c


def step(slide, n, x, y, d=0.32, color=INK):
    s = _shape(slide, MSO_SHAPE.OVAL, x, y, d, d, color, None, name=f"Step {n}")
    _inside_text(s, str(n), "FFFFFF", size=12)
    return s


def callout_box(slide, text, x, y, w, h, fill="E8F3F8", color="1F2937", size=13):
    s = _shape(slide, MSO_SHAPE.RECTANGLE, x, y, w, h, fill, None)
    tf = s.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = Inches(0.2)
    r = tf.paragraphs[0].add_run(); r.text = text
    r.font.size = Pt(size); r.font.color.rgb = _rgb(color)
    return s


def legend(slide, kinds, x, y, per_row=4, col_w=2.25):
    """Swatch + name for each semantic kind used in the figure."""
    for i, k in enumerate(kinds):
        cx, cy = x + (i % per_row) * col_w, y + (i // per_row) * 0.32
        fill, line = SCI[k]
        if k == "crosslink":
            c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(cx), Inches(cy + 0.11), Inches(cx + 0.3), Inches(cy + 0.11))
            c.line.color.rgb = _rgb(line); c.line.width = Pt(3)
        else:
            _shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, cx, cy, 0.3, 0.22, fill, line, lw=1.25)
        label(slide, LEGEND_NAMES[k], cx + 0.38, cy, col_w - 0.4, 0.22, size=10, align="left")
