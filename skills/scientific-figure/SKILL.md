---
name: scientific-figure
description: >
  This skill should be used when the user asks for a scientific illustration or figure in the house style:
  "mechanism of action diagram", "MoA slide", "pathway figure", "draw how our drug works",
  "disease mechanism diagram", "prodrug activation", "study design schematic", or any biology,
  chemistry or pharmacology diagram for decks, papers, posters or grants.
metadata:
  version: "0.1.0"
---

# Scientific figures

Draw figures as native, editable PowerPoint shapes with `scripts/lb_sci.py` on a `title-only` slide from the
`branded-deck` helper. `references/recipes.md` gives worked examples for common figures.

## Principles

1. Flat 2D shapes, 1.5 pt outline in a darker shade of the fill. No 3D, gradients, glow, shadows or clip art.
2. Color always means the same thing (table below). Never use color decoratively in a figure.
3. Read left to right (or top to bottom). Number steps with primary-color circles when there are more than three.
4. Use only the five arrow types below; add a legend when more than three colors appear.
5. Labels Calibri 10-12 pt, sentence case, outside shapes where possible; key labels bold in the shape's color.
6. Never paste screenshots of figures from papers; redraw and cite the source under the figure.

## Semantic palette (`SCI` in lb_sci.py)

| Element | Fill | Line | Helper |
| --- | --- | --- | --- |
| Target protein | #D6E6F5 | #2475B8 | `protein()` |
| Cross-link / damage | — | #E31E24 (3 pt) | `crosslink()` |
| Protective molecule | #DCEFE2 | #2E7D4F | `molecule(kind="protective")` |
| Active drug | #ECE6FA | #8E6BD8 | `molecule(kind="drug")` |
| Prodrug | core + #B9A6EA tag | #8E6BD8 | `prodrug()` |
| Activating enzyme | #FFF1CC | #F2A900 | `enzyme()` |
| Tissue / compartment | #E8F3F8 | #4A90A4 | `panel()`, `organ()` |
| Diseased / inactive / control | #EEF0F3 | #9CA3AF | `panel(kind="inactive")`, `organ(diseased=True)`, `protein(state="inactive")` |

## Arrows (`arrow(slide, x1, y1, x2, y2, kind)`)

`activate` primary-color solid → leads to · `inhibit` red with a flat bar → blocks · `convert` dashed purple → metabolized
into · `reversible` paired arrows · `light` light blue → light path (optics only). 2 pt, straight lines only.

## Build

```python
import sys
sys.path.insert(0, "<plugin-root>/skills/branded-deck/scripts")
sys.path.insert(0, "<plugin-root>/skills/scientific-figure/scripts")
from lb_deck import new_deck, add_slide, save
from lb_sci import *
prs = new_deck()
s = add_slide(prs, "title-only", title="ACM-101 Mechanism of Action")
for i, h in enumerate(["Oral dose", "Absorbed as prodrug", "Enzyme releases drug", "Cross-links broken"]):
    x = 0.45 + i * 2.4; step(s, i + 1, x, 1.15); label(s, h, x + 0.42, 1.18, 1.9, size=13, bold=True, align="left")
    panel(s, x, 1.65, 1.95, 2.3)
# ... prodrug(), enzyme(), arrow(..., "convert"), protein(), crosslink() inside the panels
callout_box(s, "One-sentence explanation of the figure.", 0.45, 4.15, 9.1, 0.95)
legend(s, ["protein", "crosslink", "drug", "prodrug", "enzyme"], 0.45, 4.6)   # or the callout, not both
save(prs, "Figure_MoA.pptx")
```
`<plugin-root>` is two directories above this skill folder. Coordinates are inches; the content area is
x 0.45-9.55, y 1.2-5.25.

Recipes for common figures (disease mechanism, MoA, study design, PK): `references/recipes.md`.

## Export

- In decks: keep as shapes. For papers/posters: export the slide to PNG at ≥300 dpi
  (`soffice --convert-to pdf` then `pdftoppm -png -r 300`) or SVG.
- Data panels: label species, n, duration and statistics in the caption.

## Check

Render and look: arrows point the right way, labels don't overlap shapes, legend matches colors used.
Ask the user to confirm the biology if the mechanism isn't in their material.
