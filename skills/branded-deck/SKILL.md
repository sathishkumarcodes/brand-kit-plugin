---
name: branded-deck
description: >
  This skill should be used when the user asks for a company presentation or slides: "make a deck for us",
  "investor deck", "board update slides", "conference talk", "turn this into slides", "pitch deck",
  "add a slide in our template", or any company PowerPoint. It builds editable .pptx files on the
  corporate template with python-pptx.
metadata:
  version: "0.1.0"
---

# Branded deck

Build every deck on the corporate template (`assets/templates/Brand_Corporate_Template.potx`)
using the helper library `scripts/lb_deck.py`. Load `brand-rules` first for voice, copy and facts.

## Workflow

1. **Gather content first.** Read the user's material. Draft the storyline as a list of slide titles, each one a
   takeaway sentence ("ACM-101 Reduced Fibrosis in Mice", not "Results"). Ask only if the audience or purpose is
   unclear and it changes the deck.
2. **Plan the structure.**
   - Cover → (external/investor decks) Forward-Looking Statements → Agenda → numbered section pages
     (01, 02 …) between topics → content → Closing.
   - Pick a layout per slide from the table in `references/layouts.md`. Use Title Only plus helpers for
     stat cards, banners, icons, timelines and diagrams.
3. **Build with the helper.**
   ```python
   import sys; sys.path.insert(0, "<plugin-root>/skills/branded-deck/scripts")
   from lb_deck import *
   prs = new_deck()                       # template with sample slides removed
   add_slide(prs, "cover", title="…", subtitle="…", tagline="Audience | Month YYYY")
   add_disclaimer(prs)                    # investor / external decks
   add_slide(prs, "agenda", title="Agenda", body=["…", "…"])
   add_slide(prs, "section-number", number="01", title="The Problem", body="One line")
   add_slide(prs, "content-subheading", title="Takeaway", subheading="Context", body=["Point", ("Sub-point", 1)])
   add_slide(prs, "chart", title="…", chart=dict(kind="column", categories=[…], series={"Name": […]},
             colors=[REFERENCE, ACCENT, COMPARATOR], number_format='0.0"%"', title="Measure (units)"),
             takeaway_head="62% of healthy", takeaway=["…"], source="Source: model, n, duration")
   add_slide(prs, "table", title="…", subheading="…", table=[header, *rows], source="Source: …")
   s = add_slide(prs, "title-only", title="…"); stat_cards(s, [("10M+", "Patients")…]); banner(s, "Takeaway")
   add_slide(prs, "closing", title="Thank You", body="Name | Title")
   save(prs, "<Company>_Deck_<Topic>_<YYYY-MM>.pptx")
   ```
   `<plugin-root>` is two directories above this skill folder. Run `python3 scripts/lb_deck.py --layouts` to list
   every layout and its fields. Pass `notes="…"` to any `add_slide` for speaker notes.
4. **Custom visuals** on `title-only` slides: `add_text`, `add_box` (brand tints in `TINT`, colors from brand.json), `stat_cards`,
   `banner`, `add_icon(slide, category, name, x, y)` (names in `assets/icons/INDEX.md`), `add_picture_fill`,
   `add_table(slide, rows, left=, top=, width=, col_widths=, numeric_cols=, total_row=)`,
   `add_chart(slide, kind=column|bar|line|doughnut|stacked, …, left=, top=, width=, height=)`.
   Content area: x 0.45-9.55 in, y 1.2-5.25 in. For mechanism or pathway figures use `scientific-figure`.
5. **Check.** Convert to PDF and render pages to images (LibreOffice `soffice --headless --convert-to pdf`,
   then `pdftoppm -jpeg -r 60`) and look at every slide: text overflow, overlaps, empty placeholders, chart
   labels. Fix and re-render. Then run the `claims-check` skill on the deck.

## Rules

- Never rebuild the master by hand or paste from old decks; always `new_deck()`.
- One message per slide; at most six bullets, two levels.
- Every number on a slide carries its source line (model, n, duration for data).
- Charts are native and editable; tables use `add_table` (primary-color header, zebra rows).
- Photos: `assets/images/sample_photo.png` or user-supplied; placed with `photo=` (cropped to fill), never stretched.
- Team slides: ask the user for headshots; crop them round (1:1) before placing.
- Fade transitions are added automatically; don't add other animations unless asked.
- If the user asks for Google Slides, build the .pptx and tell them to import it (File → Import slides).

Detailed layout fields, slide recipes and a full example: `references/layouts.md`.
