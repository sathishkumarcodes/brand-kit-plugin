#!/usr/bin/env python3
"""Render branded graphics (brand from brand.json) to PNG (or PDF for business cards) with headless Chromium.

Examples:
  python3 make_graphic.py post-announcement --size square --headline "Acme Bio joins X" --sub "One line" --out a.png
  python3 make_graphic.py post-milestone --size landscape --number "40%" --text "..." --source "Source: ..." --out m.png
  python3 make_graphic.py post-quote --quote "..." --name "Name, PhD" --role "Title, Org" --out q.png
  python3 make_graphic.py post-hiring --role-title "Senior Scientist" --details "Team · Boston, MA · Full-time" --out h.png
  python3 make_graphic.py post-event --event "BIO 2027" --when "May 2-6, 2027" --where "Booth 123" --out e.png
  python3 make_graphic.py linkedin-company --headline "Science that holds together" --sub "..." --out li.png
  python3 make_graphic.py linkedin-personal --headline "Our mission" --sub "..." --out lp.png
  python3 make_graphic.py x-header --headline "Science that holds together" --out x.png
  python3 make_graphic.py background --style dark|light|glow [--name "Jane Doe, PhD" --title "CEO"] --out bg.png
  python3 make_graphic.py business-card --name "..." --title "..." --email "..." --phone "..." --out card.pdf
  python3 make_graphic.py email-signature --name "..." --title "..." --email "..." --phone "..." --out sig.html

Batch from a people file (JSON list of {name, title, email, phone, city?}; see people.example.json):
  python3 make_graphic.py business-card   --people people.json --out-dir cards/
  python3 make_graphic.py email-signature --people people.json --out-dir signatures/
  python3 make_graphic.py background --style light --people people.json --out-dir backgrounds/   (name plates)

Use --html-only to write the HTML instead of rendering (for review or hand edits).
"""
import argparse
import base64
import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets"
LOGO = (ASSETS / "logos" / "logo_full_color.png").as_uri()
LOGO_W = (ASSETS / "logos" / "logo_reversed.png").as_uri()
CORNER = (ASSETS / "logos" / "corner_accent_bottom_right.png").as_uri()
import json as _json
BRAND = _json.loads((ROOT / "brand.json").read_text(encoding="utf-8"))
_C, _T = BRAND["colors"], BRAND["tints"]
_h = lambda k: "#" + _C[k]
PRIMARY, ACCENT, HIGHLIGHT, SECONDARY, POSITIVE, TEXT, MUTED, PALE, LIGHTBG, TINTBLUE = (
    _h("primary"), _h("accent"), _h("highlight"), _h("secondary"), _h("positive"), _h("text"), _h("muted"),
    _h("on_dark"), _h("background"), "#" + _T["accent"])
SITE, CITY, TAGLINE, NAME = BRAND["website"], BRAND["city"], BRAND["tagline"], BRAND["name"]
FONT = "Calibri, Carlito, 'Segoe UI', Arial, sans-serif"

SIZES = {"square": (1080, 1080), "landscape": (1200, 627), "portrait": (1080, 1350)}


def e(s):
    return html.escape(s or "")


def page(w, h, bg, body, unit="px"):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{w}{unit};height:{h}{unit};overflow:hidden}}
body{{font-family:{FONT};position:relative;background:{bg};-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.a{{position:absolute}}
.pill{{display:inline-block;border-radius:999px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#fff}}
</style></head><body>{body}</body></html>"""


def rings(cx, cy, n, step, color, op, width=2):
    return "".join(
        f'<div class="a" style="left:{cx-r}px;top:{cy-r}px;width:{2*r}px;height:{2*r}px;border:{width}px solid {color};border-radius:50%;opacity:{op}"></div>'
        for r in range(step, step * (n + 1), step))


def diag(h, width):
    return f'''<svg class="a" style="right:0;top:0" width="{width}" height="{h}" viewBox="0 0 100 100" preserveAspectRatio="none">
<polygon points="100,8 100,100 18,100" fill="{ACCENT}"/><polygon points="62,0 74,0 100,62 100,90" fill="{HIGHLIGHT}"/></svg>'''


def corner(w, h, size):
    return f'<img class="a" src="{CORNER}" style="right:0;bottom:0;width:{size}px">'


def post(kind, a):
    W, H = SIZES[a.size]
    k = W / 1080  # scale
    pad = int(64 * k) if a.size != "landscape" else 54
    fs = lambda v: int(v * (k if a.size != "landscape" else 0.72))
    logo_w = fs(150)
    if kind == "announcement":
        body = rings(W - int(180 * k), H - int(200 * k), 8, int(55 * k), SECONDARY, 0.25) + f'''
<img class="a" src="{LOGO_W}" style="left:{pad}px;top:{pad}px;width:{logo_w}px">
<div class="a" style="left:{pad}px;top:{int(H*0.27)}px;width:{int(W*0.82)}px">
 <span class="pill" style="background:{HIGHLIGHT};font-size:{fs(20)}px;padding:{fs(8)}px {fs(20)}px">{e(a.label or "Announcement")}</span>
 <div style="color:#fff;font-weight:700;font-size:{fs(64)}px;line-height:1.12;margin-top:{fs(28)}px">{e(a.headline)}</div>
 <div style="color:{PALE};font-size:{fs(30)}px;line-height:1.35;margin-top:{fs(26)}px">{e(a.sub)}</div>
</div>
<div class="a" style="left:{pad}px;bottom:{pad}px;color:{PALE};font-weight:700;font-size:{fs(24)}px">{e(SITE)}</div>'''
        return page(W, H, PRIMARY, body)
    if kind == "milestone":
        body = corner(W, H, int(W * 0.34)) + f'''
<img class="a" src="{LOGO}" style="left:{pad}px;top:{pad}px;width:{logo_w}px">
<div class="a" style="left:{pad}px;top:{int(H*0.22)}px;width:{int(W*0.75)}px">
 <span class="pill" style="background:{SECONDARY};font-size:{fs(20)}px;padding:{fs(8)}px {fs(20)}px">{e(a.label or "Milestone")}</span>
 <div style="color:{PRIMARY};font-weight:700;font-size:{fs(190)}px;line-height:1;margin-top:{fs(20)}px">{e(a.number)}</div>
 <div style="color:{TEXT};font-size:{fs(36)}px;line-height:1.3;margin-top:{fs(22)}px">{e(a.text)}</div>
</div>
<div class="a" style="left:{pad}px;bottom:{pad}px;color:{MUTED};font-style:italic;font-size:{fs(18)}px">{e(a.source)}</div>'''
        return page(W, H, LIGHTBG, body)
    if kind == "quote":
        body = f'''
<div class="a" style="left:{pad-6}px;top:{pad-40}px;color:{HIGHLIGHT};font-family:Georgia,serif;font-weight:700;font-size:{fs(230)}px;line-height:1">&ldquo;</div>
<div class="a" style="left:{pad}px;top:{int(H*0.26)}px;width:{int(W*0.84)}px;color:{PRIMARY};font-style:italic;font-size:{fs(50)}px;line-height:1.3">{e(a.quote)}</div>
<div class="a" style="left:{pad}px;bottom:{int(H*0.2)}px">
 <div style="width:{fs(70)}px;height:{max(4,fs(7))}px;background:{HIGHLIGHT};margin-bottom:{fs(18)}px"></div>
 <div style="color:{PRIMARY};font-weight:700;font-size:{fs(30)}px">{e(a.name)}</div>
 <div style="color:{SECONDARY};font-size:{fs(26)}px">{e(a.role)}</div>
</div>
<img class="a" src="{LOGO}" style="right:{pad}px;bottom:{pad}px;width:{logo_w}px">'''
        return page(W, H, TINTBLUE, body)
    if kind == "hiring":
        body = rings(W - int(150 * k), int(130 * k), 8, int(55 * k), SECONDARY, 0.25) + f'''
<img class="a" src="{LOGO_W}" style="left:{pad}px;top:{pad}px;width:{logo_w}px">
<div class="a" style="left:{pad}px;top:{int(H*0.28)}px;width:{int(W*0.82)}px">
 <div style="color:#fff;font-weight:700;font-size:{fs(84)}px">{e(a.headline or "We're hiring")}</div>
 <div style="width:{fs(80)}px;height:{max(5,fs(8))}px;background:{HIGHLIGHT};margin:{fs(18)}px 0 {fs(26)}px"></div>
 <div style="color:{PALE};font-weight:700;font-size:{fs(44)}px">{e(a.role_title)}</div>
 <div style="color:{PALE};font-size:{fs(28)}px;margin-top:{fs(12)}px">{e(a.details)}</div>
</div>
<span class="a pill" style="left:{pad}px;bottom:{pad}px;background:{HIGHLIGHT};font-size:{fs(22)}px;padding:{fs(12)}px {fs(30)}px">{e(a.cta or ("Apply at " + SITE))}</span>'''
        return page(W, H, PRIMARY, body)
    if kind == "event":
        body = corner(W, H, int(W * 0.34)) + f'''
<img class="a" src="{LOGO}" style="left:{pad}px;top:{pad}px;width:{logo_w}px">
<div class="a" style="left:{pad}px;top:{int(H*0.26)}px;width:{int(W*0.8)}px">
 <span class="pill" style="background:{PRIMARY};font-size:{fs(20)}px;padding:{fs(8)}px {fs(20)}px">{e(a.label or "Meet us at")}</span>
 <div style="color:{PRIMARY};font-weight:700;font-size:{fs(70)}px;line-height:1.1;margin-top:{fs(26)}px">{e(a.event)}</div>
 <div style="color:{SECONDARY};font-size:{fs(34)}px;line-height:1.4;margin-top:{fs(26)}px">{e(a.when)}<br>{e(a.where)}</div>
</div>'''
        return page(W, H, "#FFFFFF", body)
    raise SystemExit(f"unknown post type {kind}")


def banner(kind, a):
    if kind == "linkedin-company":
        W, H = 1128, 191
        body = rings(1000, 95, 6, 40, SECONDARY, 0.25) + f'''
<div class="a" style="left:60px;top:40px;color:#fff;font-size:36px;font-weight:700">{e(a.headline)}</div>
<div class="a" style="left:62px;top:94px;color:{PALE};font-size:20px">{e(a.sub)}</div>
<div class="a" style="left:62px;top:134px;width:50px;height:4px;background:{HIGHLIGHT}"></div>'''
        return W, H, page(W, H, PRIMARY, body)
    if kind == "linkedin-personal":
        W, H = 1584, 396
        body = diag(H, 500) + f'''
<div class="a" style="right:440px;top:105px;text-align:right">
 <div style="color:{PRIMARY};font-size:48px;font-weight:700">{e(a.headline)}</div>
 <div style="color:{SECONDARY};font-size:26px;margin-top:8px">{e(a.sub)}</div></div>
<img class="a" src="{LOGO}" style="right:445px;top:250px;width:110px">'''
        return W, H, page(W, H, LIGHTBG, body)
    if kind == "x-header":
        W, H = 1500, 500
        body = rings(1250, 300, 9, 55, SECONDARY, 0.22) + f'''
<img class="a" src="{LOGO_W}" style="left:90px;top:130px;width:200px">
<div class="a" style="left:330px;top:150px;color:#fff;font-size:54px;font-weight:700">{e(a.headline)}</div>
<div class="a" style="left:332px;top:228px;color:{PALE};font-size:26px">{e(a.sub or (NAME + " · " + SITE))}</div>'''
        return W, H, page(W, H, PRIMARY, body)
    raise SystemExit(kind)


def background(a):
    W, H = 1920, 1080
    plate = ""
    if a.name:
        plate = f'''<div class="a" style="left:70px;bottom:70px;background:{PRIMARY};padding:22px 34px;border-left:8px solid {HIGHLIGHT}">
<div style="color:#fff;font-size:40px;font-weight:700">{e(a.name)}</div><div style="color:{PALE};font-size:28px">{e(a.title)}</div></div>'''
    if a.style == "dark":
        return W, H, page(W, H, PRIMARY, rings(1700, 820, 9, 90, SECONDARY, 0.22) + f'<img class="a" src="{LOGO_W}" style="right:70px;top:60px;width:210px">' + plate)
    if a.style == "light":
        return W, H, page(W, H, LIGHTBG, diag(H, 560) + f'<img class="a" src="{LOGO}" style="left:70px;top:60px;width:210px">' + plate)
    if a.style == "glow":
        bg = f"radial-gradient(circle at 78% 60%,{ACCENT}66 0%,{PRIMARY} 50%,{PRIMARY} 100%)"
        body = rings(1520, 650, 12, 60, PALE, 0.10, 1) + rings(1520, 650, 4, 180, HIGHLIGHT, 0.25) + \
            f'<img class="a" src="{LOGO_W}" style="left:70px;top:60px;width:200px">'
        if not a.name:
            body += f'<div class="a" style="left:74px;bottom:70px;color:{PALE};font-size:30px;letter-spacing:6px">{e(TAGLINE.upper().rstrip("."))}</div>'
        return W, H, page(W, H, bg, body + plate)
    raise SystemExit("style must be dark, light or glow")


def card(a):
    """Two-page PDF: front (contact) and back (brand). 3.75 x 2.25 in incl. 0.125 in bleed."""
    W, H = 3.75, 2.25
    front = f'''<section style="width:{W}in;height:{H}in;position:relative;background:#fff;page-break-after:always;overflow:hidden">
<img class="a" src="{CORNER}" style="right:0;bottom:0;width:1.2in">
<img class="a" src="{LOGO}" style="left:2.72in;top:0.36in;width:0.66in">
<div class="a" style="left:0.36in;top:0.38in;width:2.3in;color:{PRIMARY};font-weight:700;font-size:12pt">{e(a.name)}</div>
<div class="a" style="left:0.36in;top:0.62in;width:2.3in;color:{SECONDARY};font-size:8pt">{e(a.title)}</div>
<div class="a" style="left:0.37in;top:0.9in;width:0.3in;height:0.025in;background:{HIGHLIGHT}"></div>
<div class="a" style="left:0.36in;top:1.02in;width:2.2in;color:{TEXT};font-size:7.5pt;line-height:1.45">
{e(a.email)}<br>{e(a.phone)}<br><b style="color:{PRIMARY}">{e(SITE)}</b><br>{e(a.city or CITY)}</div></section>'''
    back = f'''<section style="width:{W}in;height:{H}in;position:relative;background:{PRIMARY};overflow:hidden">
<img class="a" src="{LOGO_W}" style="left:1.32in;top:0.5in;width:1.11in">
<div class="a" style="left:1.725in;top:1.42in;width:0.3in;height:0.025in;background:{HIGHLIGHT}"></div>
<div class="a" style="left:0.4in;top:1.52in;width:2.95in;text-align:center;color:{PALE};font-style:italic;font-size:9pt">{e(a.tagline or TAGLINE.rstrip("."))}</div></section>'''
    doc = page(W, H * 2, "#fff", front + back, unit="in").replace("height:4.5in;overflow:hidden", "height:auto")
    return W, H, doc


def signature(a):
    logo = base64.b64encode((ASSETS / "logos" / "logo_full_color.png").read_bytes()).decode()
    src = a.logo_url or f"data:image/png;base64,{logo}"
    return f'''<table cellpadding="0" cellspacing="0" border="0" style="font-family:Calibri,Arial,sans-serif;color:{TEXT};font-size:13px;line-height:1.4;">
 <tr><td style="padding-right:16px;border-right:2px solid {HIGHLIGHT};vertical-align:middle;">
   <a href="https://{e(SITE)}"><img src="{src}" width="90" height="60" alt="{e(NAME)}" style="display:block;border:0;"></a></td>
  <td style="padding-left:16px;vertical-align:middle;">
   <div style="font-size:16px;font-weight:bold;color:{PRIMARY};">{e(a.name)}</div>
   <div style="font-size:13px;color:{SECONDARY};padding-bottom:6px;">{e(a.title)} &nbsp;|&nbsp; {e(NAME)}</div>
   <div><span style="color:{MUTED};">E</span>&nbsp; <a href="mailto:{e(a.email)}" style="color:{TEXT};text-decoration:none;">{e(a.email)}</a></div>
   <div><span style="color:{MUTED};">M</span>&nbsp; {e(a.phone)}</div>
   <div><span style="color:{MUTED};">W</span>&nbsp; <a href="https://{e(SITE)}" style="color:{ACCENT};font-weight:bold;text-decoration:none;">{e(SITE)}</a> &nbsp;&middot;&nbsp; {e(a.city or CITY)}</div></td></tr>
 <tr><td colspan="2" style="padding-top:10px;font-size:10px;color:#9CA3AF;max-width:480px;">This email and any attachments are confidential and intended only for the addressee. If you received it in error, please notify the sender and delete it.</td></tr>
</table>'''


def render(doc, out, W, H, pdf=False, unit="px"):
    out = Path(out).resolve()
    hp = out.with_suffix(".render.html")
    hp.write_text(doc, encoding="utf-8")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        if pdf:
            pg = b.new_page()
            pg.goto(hp.as_uri()); pg.wait_for_timeout(300)
            pg.pdf(path=str(out), width=f"{W}in", height=f"{H}in", print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        else:
            pg = b.new_page(viewport={"width": W, "height": H})
            pg.goto(hp.as_uri()); pg.wait_for_timeout(300)
            pg.screenshot(path=str(out))
        b.close()
    hp.unlink()
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("type")
    ap.add_argument("--out")
    ap.add_argument("--people", help="JSON file: list of {name, title, email, phone, city?}")
    ap.add_argument("--out-dir", help="folder for batch output with --people")
    ap.add_argument("--size", default="square", choices=list(SIZES))
    for f in ("headline", "sub", "label", "number", "text", "source", "quote", "name", "role", "role-title", "details", "cta",
              "event", "when", "where", "style", "title", "email", "phone", "city", "tagline", "logo-url"):
        ap.add_argument("--" + f)
    ap.add_argument("--html-only", action="store_true")
    a = ap.parse_args()
    if a.people:
        return batch(a)
    if not a.out:
        ap.error("--out is required (or use --people with --out-dir)")
    t = a.type
    if t.startswith("post-"):
        W, H = SIZES[a.size]
        doc, pdf = post(t[5:], a), False
    elif t in ("linkedin-company", "linkedin-personal", "x-header"):
        W, H, doc = banner(t, a); pdf = False
    elif t == "background":
        a.style = a.style or "dark"
        W, H, doc = background(a); pdf = False
    elif t == "business-card":
        W, H, doc = card(a); pdf = True
    elif t == "email-signature":
        Path(a.out).write_text(signature(a), encoding="utf-8"); print(a.out); return
    else:
        sys.exit(f"unknown type {t}")
    if a.html_only:
        Path(a.out).write_text(doc, encoding="utf-8"); print(a.out); return
    print(render(doc, a.out, W, H, pdf=pdf))


def slug(name):
    import re
    return re.sub(r"[^A-Za-z0-9]+", "_", name.split(",")[0]).strip("_")


def batch(a):
    """Render one file per person in a people JSON file."""
    import copy, json
    people = json.loads(Path(a.people).read_text(encoding="utf-8"))
    out_dir = Path(a.out_dir or ".")
    out_dir.mkdir(parents=True, exist_ok=True)
    ext = {"business-card": "pdf", "email-signature": "html", "background": "png"}.get(a.type)
    if not ext:
        sys.exit("--people works with business-card, email-signature and background")
    prefix = {"business-card": "Card", "email-signature": "Signature", "background": "Background"}[a.type]
    pages = []
    for person in people:
        b = copy.copy(a)
        for k in ("name", "title", "email", "phone", "city", "tagline", "logo_url"):
            if person.get(k) is not None:
                setattr(b, k, person[k])
        b.out = str(out_dir / f"{prefix}_{slug(b.name)}.{ext}")
        if a.type == "email-signature":
            html_snip = signature(b)
            Path(b.out).write_text(html_snip, encoding="utf-8")
            pages.append(f"<h3 style='font-family:Arial;color:{PRIMARY}'>{e(b.name)}</h3>{html_snip}<hr style='margin:24px 0;border:0;border-top:1px solid #ddd'>")
        elif a.type == "business-card":
            W, H, doc = card(b); render(doc, b.out, W, H, pdf=True)
        else:
            b.style = a.style or "light"
            W, H, doc = background(b); render(doc, b.out, W, H)
        print(b.out)
    if pages:
        idx = out_dir / "All_Signatures.html"
        idx.write_text("<!doctype html><meta charset='utf-8'><title>Signatures</title><body style='padding:32px'>"
                       "<p style='font-family:Arial;color:#6B7280'>Click inside a signature, select it, copy, and paste into your email client's signature settings.</p>"
                       + "".join(pages) + "</body>", encoding="utf-8")
        print(idx)


if __name__ == "__main__":
    main()
