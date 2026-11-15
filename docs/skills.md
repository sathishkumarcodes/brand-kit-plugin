# The six skills in detail

[← Back to README](../README.md)

Each skill is a folder in [`skills/`](../skills) with a `SKILL.md` that tells Claude when the skill applies,
the workflow to follow and the rules, plus the references and Python tools it uses.

- [1. brand-rules](#1-brand-rules)
- [2. branded-deck](#2-branded-deck)
- [3. branded-document](#3-branded-document)
- [4. brand-graphics](#4-brand-graphics)
- [5. scientific-figure](#5-scientific-figure)
- [6. claims-check](#6-claims-check)

---

## 1. brand-rules

The foundation. Every other skill loads it first.

| Contains | Details |
| --- | --- |
| Brand guide | Colors by role, fonts, logo rules (full color on light, reversed on dark, clear space, minimum size, never stretch or recolor), layout grid, chart and table style, photography and icon rules |
| Voice | Plain, precise, confident without hype. Active voice. Numbers with their model and duration. |
| Approved copy | Tagline, one-liner, and ~50, ~100 and ~200 word company descriptions, each with when to use it |
| Key facts | The approved wording for stage, lead program, headline data and location, so numbers don't drift |
| Claims to avoid | "Cures", "will reverse", unsourced "first"/"only", "safe" / "no side effects", efficacy without model and duration |

**Ask for things like:** "What's our approved short description?", "Which color do I use for a positive
result?", "Write an About paragraph for this press release."

---

## 2. branded-deck

Builds editable PowerPoint decks on the corporate template.

**Ask for things like:** "Make a 10-slide investor update from these notes", "Turn this report into a board
deck", "Add a competitive comparison slide", "Make a one-slide summary of these results."

**The 21 layouts** (`lb_deck.py --layouts` lists them with their fields; full detail in
[layouts.md](../skills/branded-deck/references/layouts.md)):

| Group | Layouts |
| --- | --- |
| Openers | `cover`, `cover-photo`, `agenda` |
| Section pages | `section`, `section-number`, `section-light`, `photo-divider` |
| Content | `content`, `content-subheading`, `two-content`, `comparison`, `content-picture` |
| Data | `chart`, `table`, `big-number` |
| Flexible | `title-only`, `blank`, `statement` |
| Closers | `quote`, `disclaimer`, `closing` |

**What `lb_deck.py` provides:**

| Function | Does |
| --- | --- |
| `new_deck()` | Opens the template as a new deck with sample slides removed |
| `add_slide(prs, layout, notes=None, **fields)` | Adds a slide and fills its fields by name. Text fields take a string or a list of bullets (with levels and bold). Unused fields are removed, so no "Click to add text" is left behind. Adds speaker notes and a fade transition. |
| `add_chart(...)` | Native, editable PowerPoint charts: column, bar, line, doughnut, stacked. Brand colors, per-bar colors for "reference vs ours vs comparator", number formats |
| `add_table(...)` | Branded tables: header row in the primary color, zebra rows, thin borders, optional highlighted row |
| `stat_cards(...)`, `banner(...)` | Big-number cards and a takeaway banner, the most common investor slide |
| `add_text(...)`, `add_box(...)` | Brand-styled text and shapes for custom layouts |
| `add_icon(...)` | Places an icon from the library in any of its styles |
| `picture_in(...)`, `add_picture_fill(...)` | Fills a picture placeholder or box, cropping to fit without distortion |
| `add_disclaimer(prs)` | Adds the standard forward-looking-statements slide |
| `save(prs, path)` | Saves with clean metadata |

**Slide recipes** in the layout reference cover stat cards, icon grids, callouts, process flows, timelines
and roadmaps, team pages and head-to-head comparisons.

**Rules Claude follows:** action titles ("ACM-101 Reduced Fibrosis in Mice", not "Results"); one message per
slide; at most 6 bullets; sources on every data slide; a disclaimer slide in any investor or external deck;
render and inspect every slide before delivery.

---

## 3. branded-document

Builds editable Word documents on the letterhead and report templates.

**Ask for things like:** "Letter on letterhead to Dr. Alex Morgan proposing a collaboration", "Write the
quarterly board report from these notes", "Staff memo about the office move."

| Document | Template | What you get |
| --- | --- | --- |
| Letter | `Brand_Letterhead.dotx` | Logo header, address footer, date, recipient block, subject line, body, sign-off and signature block |
| Report | `Brand_Document_Template.dotx` | Cover page with title, subtitle and details, optional table of contents, running header with the document title, page numbers, confidentiality footer |
| Memo | `Brand_Document_Template.dotx` | "Memorandum" heading with To / From / CC / Date / Subject block, no cover |

**Building blocks in `lb_doc.py`:** `h1`/`h2`/`h3` headings, `p` paragraphs (with `**bold**` inline),
`bullets` and `numbered` lists (numbering restarts correctly), branded `table` (header shading, zebra rows,
right-aligned number columns, total row, caption), `image` with caption, `callout`, `quote`, `small` print,
`caption`, `page_break`, and `toc` (a real Word table of contents that updates when the file is opened).

---

## 4. brand-graphics

Renders social posts, banners, backgrounds, business cards and email signatures. Each graphic is laid out
in HTML with the brand fonts and colors, then rendered to a pixel-exact PNG or PDF with headless Chromium.

**Ask for things like:** "Square LinkedIn milestone post: 62% of healthy tissue elasticity after 8 weeks in
mice", "Hiring post for a Senior Scientist", "Zoom background with my name and title", "Business cards for
everyone in this file", "Email signatures for the team."

| Type | Sizes / format | Notes |
| --- | --- | --- |
| `post-announcement` | square 1080×1080, landscape 1200×627, portrait 1080×1350 | Headline, subline, label |
| `post-milestone` | same three sizes | One big number, its meaning, and a required source line |
| `post-quote` | same three sizes | Quote, name, role |
| `post-hiring` | same three sizes | Role, team / location / type, call to action |
| `post-event` | same three sizes | Event, dates, location or booth |
| `linkedin-company` | 1128×191 | Company page cover |
| `linkedin-personal` | 1584×396 | Personal profile banner for staff |
| `x-header` | 1500×500 | X / Twitter header |
| `background` | 1920×1080 | Styles `dark`, `light`, `glow`; optional name plate with name and title |
| `business-card` | 3.5×2 in + bleed, 2-page PDF | Front with name, title, email, phone, city and website; back with the logo and tagline |
| `email-signature` | HTML | Table-based layout that survives Outlook, Apple Mail and Gmail; hosted logo URL option |

**Batch mode:** point any person-specific type at a people file and get one file per person:

```bash
python3 make_graphic.py business-card   --people people.json --out-dir cards/
python3 make_graphic.py email-signature --people people.json --out-dir signatures/   # also writes All_Signatures.html
python3 make_graphic.py background --style light --people people.json --out-dir backgrounds/
```

`--html-only` writes the HTML instead of rendering, for hand edits.

---

## 5. scientific-figure

Draws mechanism, pathway and study-design figures as native PowerPoint shapes, in one consistent
illustration style.

**Ask for things like:** "Mechanism-of-action slide for ACM-101", "Show how the prodrug is activated",
"Study design figure: three arms, 8 weeks, two readouts."

**Semantic color:** each kind of biological element always gets the same color, in every figure, deck,
paper and poster.

| Element | Function | Fill / outline |
| --- | --- | --- |
| Target protein | `protein()` | light blue / blue |
| Cross-link or damage | `crosslink()` | light red / red |
| Protective molecule | `molecule(kind="protective")` | light green / green |
| Active drug | `molecule(kind="drug")` | light violet / violet |
| Prodrug | `prodrug()` | violet / violet |
| Activating enzyme | `enzyme()` | light amber / amber |
| Tissue or compartment | `panel()`, `organ()` | pale blue / teal |
| Diseased, inactive or control | `state="inactive"`, `organ(diseased=True)` | gray / gray |

**Arrows:** five kinds with fixed meanings: `activate`, `convert`, `light`, `inhibit` (flat head) and
`reversible`. Plus `step()` numbered circles, `label()`, `callout_box()` and an automatic `legend()`.

The [figure recipes](../skills/scientific-figure/references/recipes.md) cover disease mechanism, mechanism of
action, prodrug activation, study design and PK figures.

---

## 6. claims-check

Screens decks, documents, PDFs and plain text for risky claims and off-brand styling before they go out.

**Ask for things like:** "Check this press release before it goes out", "Review the investor deck for
anything we can't support", "Is this LinkedIn post OK to publish?"

**How it works:** `brand_audit.py` scans the file and produces a severity-ranked report. Then the skill has
Claude read the whole piece in context, confirm or dismiss each finding, catch what patterns can't, and
propose specific rewrites.

| Severity | What it catches | Example |
| --- | --- | --- |
| **HIGH** | Cure language; promised outcomes ("will restore"); unsourced "first" or "only"; safety claims; "proven" or "guaranteed" | "will cure fibrotic disease and is safe" |
| **MEDIUM** | "FDA approved" in the wrong context; hype words; overstated comparisons; fold-change claims; efficacy numbers without model and duration; placeholders and fake contact details left in | "breakthrough", "10x better", "62% improvement" with no model |
| **LOW** | Company name written in the logo style in running text | "AcmeBio" instead of "Acme Bio" |
| **Style** | Fonts not in the brand, colors not in the palette, missing forward-looking-statements disclaimer in a deck with projections | A slide in Times New Roman |

Reads `.pptx`, `.potx`, `.docx`, `.dotx`, `.pdf` and text. See the [sample report](sample-claims-report.md).
It is editorial guidance, not legal advice.
