# Run the scripts directly

[← Back to README](../README.md)

The plugin is mostly used through Claude, but every tool also runs on its own.

## Requirements

Python 3.10+, `python-pptx`, `python-docx`, `Pillow`, `lxml` and `playwright` (with Chromium). LibreOffice
and poppler are optional, for rendering previews.

```bash
pip install python-pptx python-docx pillow lxml playwright
python3 -m playwright install chromium
```

## Commands

```bash
# Decks and documents
python3 examples/build_sample_deck.py                       # outputs/Acme_Sample_Deck.pptx
python3 examples/build_sample_documents.py                  # outputs/Acme_Sample_Letter.docx, ..._Report.docx
python3 skills/branded-deck/scripts/lb_deck.py --layouts    # list layouts and their fields

# Graphics
python3 skills/brand-graphics/scripts/make_graphic.py post-milestone --size square \
  --number "62%" --text "of healthy tissue elasticity after 8 weeks in mice" \
  --source "Fictional data" --out post.png
python3 skills/brand-graphics/scripts/make_graphic.py background --style glow \
  --name "Jane Doe, PhD" --title "CEO" --out zoom.png
python3 skills/brand-graphics/scripts/make_graphic.py business-card \
  --people people.example.json --out-dir cards/
python3 skills/brand-graphics/scripts/make_graphic.py --help   # every type and option

# Claims check
python3 skills/claims-check/scripts/brand_audit.py examples/sample_draft_press_release.txt
```

## A minimal deck in Python

```python
import sys; sys.path.insert(0, "skills/branded-deck/scripts")
from lb_deck import *

prs = new_deck()
add_slide(prs, "cover", title="Breaking Cross-Links", subtitle="ACM-101 investor update", tagline="Q4 2026")
add_disclaimer(prs)
s = add_slide(prs, "title-only", title="Three Milestones Reached This Quarter")
stat_cards(s, [("62%", "Tissue elasticity restored in mice"), ("8 wk", "Oral dosing"), ("Q4", "IND-enabling studies start")])
banner(s, "On track for first-in-human studies in 2027")
add_slide(prs, "chart", title="ACM-101 Reduced Fibrosis in Mice",
          chart=dict(kind="column", categories=["Healthy", "ACM-101", "Vehicle"],
                     series={"% of healthy": [100, 62, 21]}, colors=[REFERENCE, ACCENT, COMPARATOR],
                     number_format='0"%"'),
          takeaway_head="62% of healthy", takeaway=["vs 21% with vehicle", "8-week oral dosing"],
          source="Source: fictional sample data.")
add_slide(prs, "closing", title="Thank You", body="Jane Doe, PhD  |  CEO")
save(prs, "outputs/Investor_Update.pptx")
```

Generated files go in `outputs/`, `cards/`, `signatures/` and `backgrounds/`, which `.gitignore` keeps out
of Git.
