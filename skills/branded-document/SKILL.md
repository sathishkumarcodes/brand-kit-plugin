---
name: branded-document
description: >
  This skill should be used when the user asks for a company Word document: "write a letter on letterhead",
  "official letter", "board report", "memo to staff", "proposal", "SOP", "white paper", "grant narrative",
  "one-pager in Word", or any company .docx. It builds editable Word files on the
  letterhead and document templates with python-docx.
metadata:
  version: "0.1.0"
---

# Branded document

Build Word files on the templates in `assets/templates/` with the helper `scripts/lb_doc.py`.
Load `brand-rules` first for voice, approved copy and facts.

## Pick the format

| Ask | Function | Template |
| --- | --- | --- |
| Letter, official correspondence, offer/reference letter | `new_letter(...)` | Letterhead (logo, corner accent, company footer) |
| Report, proposal, plan, SOP, white paper, brief | `new_report(title, subtitle, meta, toc)` | Document template (cover page, running header, "Page X of Y") |
| Internal memo | `new_memo(to, frm, date, subject, cc)` | Document template without cover |

If the user asks for "a document" without naming Word, and a docs/artifact type is available, follow the
host's guidance; use this skill when Word, .docx, letterhead or print is wanted.

## Build

```python
import sys; sys.path.insert(0, "<plugin-root>/skills/branded-document/scripts")
from lb_doc import *
d = new_report(title="…", subtitle="…", meta={"Prepared by": "…", "Date": "…", "Version": "1.0 Draft",
               "Distribution": "Board"}, toc=True)
h1(d, "1. Executive Summary"); p(d, "Lead with the conclusion. **Bold** with double asterisks.")
callout(d, "**Key takeaway:** …")             # light-blue box with a blue left bar
h2(d, "1.1 …"); bullets(d, ["…", ("sub-point", 1)]); numbered(d, ["…", "…"])   # numbering restarts each call
table(d, [["Col", "Col"], ["…", "…"]], col_widths=[3.5, 3.25], numeric_cols=(1,), total_row=False,
      caption="Table 1. …")
image(d, "chart.png", width_in=6.0, caption_text="Figure 1. …")
quote(d, "“…”"); small(d, "Source: …"); page_break(d)
save(d, "<Company>_<Type>_<Topic>_<YYYY-MM>.docx")
```

Letters:

```python
d = new_letter(date="November 15, 2026", recipient=["Name", "Title", "Organization", "Street", "City, ST ZIP"],
               subject="…", salutation="Dear Dr. …,", paragraphs=["…", "…"], bullet_items=None,
               signoff="Sincerely,", signer=["Name Surname", "Title", BRAND["legal_name"]])
```

`<plugin-root>` is two directories above this skill folder.

## Writing rules

- Letters: purpose in the first sentence; one idea per paragraph; close with the next step. One page where possible.
- Reports: executive summary first (conclusion + numbers), then sections numbered "1.", "1.1". Use the
  Callout style once or twice for the point a skimmer must not miss.
- Memos: Purpose · Background · Recommendation · Next steps (action — owner — date).
- Tables get a caption; data gets a source line (Small Print or Caption style).
- Dates written "November 15, 2026". Company name "the company" (legal: "the company, Inc." in signatures).
- Never invent recipients' addresses, signatures or contact details; leave clear placeholders and say so.

## Check

Convert to PDF (`soffice --headless --convert-to pdf`) and render pages (`pdftoppm -jpeg -r 60`); look at
every page for header/footer, spacing and table fit. Validate the .docx opens (python-docx reload). Run
`claims-check` on anything external. Tell the user to right-click the table of contents → Update Field if
it was included (Word also refreshes it on open).

## Styles available in both templates

Title, Subtitle, Heading1-3, Callout, Quote, SmallPrint, Caption, brand bullets (blue •, teal –), numbered
lists (bold primary-color numbers). Body: Calibri 11 pt, 1.15 spacing.
