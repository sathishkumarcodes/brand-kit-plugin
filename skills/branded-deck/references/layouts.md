# Template layouts and fields

| Key (`add_slide`) | Template layout | Fields | Use for |
| --- | --- | --- | --- |
| `cover` | Cover | title, subtitle, tagline | Standard cover (white with blue/red art) |
| `cover-photo` | Cover Photo | photo, title, subtitle, tagline | Cover with a photo on the right half |
| `agenda` | Agenda | title, body (numbered list) | 4-6 agenda items |
| `section` | Section | title, body | Unnumbered primary-color divider |
| `section-number` | Section Number | number, title, body | Numbered primary-color divider ("01") matching the agenda |
| `section-light` | Section Light | number, title, body | Light divider for bright rooms |
| `photo-divider` | Photo Divider | photo, title, body | Story/chapter opener with a wide photo |
| `content` | Title and Content | title, body | Bullets |
| `content-subheading` | Title Subheading Content | title, subheading, body | Bullets with a teal context line |
| `two-content` | Two Content | title, left, right | Two equal columns |
| `comparison` | Comparison | title, left_head, right_head, left, right | Status quo (gray) vs your approach (accent) |
| `content-picture` | Content with Picture | title, subheading, body, photo | Text beside an image |
| `chart` | Chart | title, chart, takeaway_head, takeaway, source | Chart with a blue takeaway panel |
| `table` | Table | title, subheading, table, source | Full-width data table |
| `title-only` | Title Only | title | Custom visuals: cards, timelines, icons, figures |
| `blank` | Blank | — | Logo + footer only |
| `statement` | Statement | title, statement | Visual above, primary-color takeaway panel below (y 4.3-5.47 in) |
| `big-number` | Big Number | number, label, title, body | One hero number |
| `quote` | Quote | quote, name, role | KOL / partner / patient quote (≤30 words) |
| `disclaimer` | Disclaimer | title, body | Forward-looking statements (`add_disclaimer(prs)`) |
| `closing` | Closing | title, body | Thank-you / contact |

Text fields accept a string or a list. List items can be `"text"`, `("text", level)` or
`{"text": …, "level": 0|1, "bold": True}`. Fields left out are removed (no "Click to add" prompts).

`chart=` takes `dict(kind, categories, series, colors=None, number_format='0', title=None, show_values=True, legend=None)`.
Single-series column/bar charts can color each bar by passing one color per category (e.g. `REFERENCE`, `ACCENT`, `COMPARATOR`). Kinds: `column`, `bar`, `line`, `doughnut`, `stacked`.

`table=` takes rows (first row = header). For more control call `add_table` directly on a `title-only` slide.

## Slide recipes (title-only + helpers)

- **Stat cards:** `stat_cards(s, [("2B+", "Patients globally"), ("100%", "…"), ("$18.2B", "…")])`, then
  `banner(s, "2 billion people × $15/year = $30B opportunity")`.
- **Icon grid (2 × 3):** for each item, `add_icon(s, cat, name, x, y, 0.65)`, then `add_text` for a bold primary-color
  heading (16 pt) and a 13 pt description beside it. Finish with `banner(...)`.
- **Callouts:** `add_box(s, x, y, 4.45, 1.75, TINT["blue"|"green"|"amber"|"pink"])` + icon (idea/check-circle/
  warning/risk icons in accent/positive/milestone/highlight) + heading + text.
- **Process flow:** numbered primary-color circles (`add_box(..., rounded=True)` or `lb_sci.step`) on a gray line, step
  heading 17 pt bold primary-color, description 13 pt.
- **Timeline/roadmap:** light year bands (tints), bars in secondary/primary, milestone-color stars for
  milestones, label each milestone; finish with a blue takeaway box.
- **Team:** accent-tint cards (2.1 in wide), round headshot 1.5 in, name 14 pt bold primary-color, role 12 pt secondary, one-line bio 12 pt.
- **Head-to-head:** gray rounded label box on the left, tinted result box on the right with your result bold
  and comparator in gray beneath.

## Example: short investor update (fictional sample brand)

```python
from lb_deck import *
prs = new_deck()
add_slide(prs, "cover", title="Breaking Cross-Links", subtitle="ACM-101 investor update", tagline="Q4 2026")
add_disclaimer(prs)
add_slide(prs, "agenda", title="Agenda", body=["Highlights", "Program progress", "Financing", "Next 12 months"])
add_slide(prs, "section-number", number="01", title="Highlights", body="What changed this quarter")
s = add_slide(prs, "title-only", title="Three Milestones Reached This Quarter")
stat_cards(s, [("62%", "Tissue elasticity restored in mice"), ("8 wk", "Oral dosing"), ("Q4", "IND-enabling studies start")])
banner(s, "On track for first-in-human studies in 2027")
add_slide(prs, "chart", title="ACM-101 Reduced Fibrosis in Mice",
          chart=dict(kind="column", categories=["Healthy", "ACM-101", "Vehicle"], series={"% of healthy": [100, 62, 21]},
                     colors=[REFERENCE, ACCENT, COMPARATOR], number_format='0"%"', title="Tissue elasticity (% of healthy)"),
          takeaway_head="62% of healthy", takeaway=["vs 21% with vehicle", "8-week oral dosing"],
          source="Source: fictional sample data.")
add_slide(prs, "closing", title="Thank You", body="Jane Doe, PhD  |  CEO")
save(prs, "Acme_Deck_Investor-Update_2026-11.pptx")
```
