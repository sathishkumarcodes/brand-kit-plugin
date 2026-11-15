---
name: brand-rules
description: >
  This skill should be used whenever anything is made for or about the company defined in this plugin's
  brand.json: "make a deck for us", "write our press release", "draft our company description", "use our
  brand", "on-brand", "our colors / logo / fonts", "write a bio", or any document, slide, graphic, figure or
  copy that carries the company name. It holds the core identity (colors, fonts, logo rules, voice, approved
  copy and facts) that every other skill in this plugin builds on.
metadata:
  version: "1.0.0"
---

# Brand rules

The company's identity lives in `brand.json` at the plugin root (two levels above this skill). Read it first:
`name`, `legal_name`, `tagline`, `website`, `city`, `footer`, `fonts`, `colors` (by role) and `tints`.
The sample brand shipped with this plugin is **Acme Bio, a fictional company**.

For a specific format, also load the matching skill:

| Output | Skill |
| --- | --- |
| Slide deck, pitch, board or conference slides | `branded-deck` |
| Letter, report, memo, proposal, SOP, brief (Word) | `branded-document` |
| Social post, LinkedIn/X banner, Zoom/Teams background, business card, email signature | `brand-graphics` |
| Pathway, mechanism or data figure | `scientific-figure` |
| Reviewing any draft before it goes out | `claims-check` |

Brand files live in `assets/`: `logos/` (full color, reversed, corner accents), `templates/` (PowerPoint
.potx, letterhead and document .dotx), `icons/` (41 icons; see `icons/INDEX.md`), `images/`.
Always use these files. Never redraw, retype or approximate the logo.

## Color roles

| Role (`colors.*`) | Used for |
| --- | --- |
| `primary` | Titles, footers, dark panels, table headers |
| `accent` | Primary accent, the highlighted chart series, links |
| `highlight` | Logo accent, emphasis bars, risks, calls to action |
| `secondary` | Subheadings, labels, section numbers |
| `positive` | Good results, "do" |
| `milestone` | Milestones, highlights, stars on timelines |
| `extra` | Extra chart series |
| `text`, `muted` | Body text, captions and sources |
| `on_dark` | Secondary text on dark backgrounds |
| `reference`, `comparator` | Control bars and competitor bars in charts |

`tints.*` are pale fills for cards and panels only, never text. White text only on `primary`, `accent`,
`highlight`, `positive` or `secondary` fills.

Fonts: `fonts.heading` for titles, `fonts.body` for everything else. Flat fills only: no gradients, 3D, glow
or drop shadows. Logo: full color on light backgrounds, reversed on dark; clear space equal to the height of
a capital letter in the wordmark; never stretch, rotate or recolor.

Full specification: `references/brand-guide.md`. Approved copy and facts: `references/boilerplate.md`.

## Voice

- Plain, specific, confident, never hype. Lead with the result and its number.
- Name the model and duration for every efficacy number. Describe programs by their real stage.
- Prefer "is designed to", "aims to", "is expected to" over "will". No "cure", "proven", "safe",
  "breakthrough", "first-in-class" or "only" unless the user confirms it is substantiated.
- Before anything leaves the company, run the `claims-check` skill.

## Never invent

- Contact details: if an email, phone or street address is not provided, use an obvious placeholder
  (e.g. `name@example.com`, `+1 (555) 010-01xx`) and tell the user it needs replacing.
- Data, dates, people or quotes not in the user's material or `references/boilerplate.md`.

## Finish every job

1. Render the output and look at it (logo placement, footer, overflow, contrast).
2. Run `claims-check` on text that will be seen outside the company.
3. In the reply, list any placeholders left and any claim that could not be verified.
