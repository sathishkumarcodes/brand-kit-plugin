---
name: claims-check
description: >
  This skill should be used when the user asks to review, check, approve or proof company material:
  "check this deck", "is this on brand", "review our press release", "can we say this", "claims check",
  "compliance review", "check before I send to investors", or before any deck, document, post or
  web copy is shared outside the company. It flags risky scientific and investor claims, unqualified data,
  off-brand styling and leftover placeholders, and proposes compliant rewrites.
metadata:
  version: "0.1.0"
---

# Brand and claims check

Review company material for claims that could mislead investors, regulators or patients, and for brand
consistency. This is an editorial review, not legal advice; say so once in the report.

## Workflow

1. **Run the screen.**
   `python3 <plugin-root>/skills/claims-check/scripts/brand_audit.py <file>` (pptx, docx, pdf, txt, md, html).
   For pasted text, write it to a .txt file first. `<plugin-root>` is two directories above this skill folder.
2. **Read the whole piece yourself.** The script only catches patterns. Also judge:
   - Is every efficacy number tied to its model (e.g. mouse, ex vivo human tissue, cell line), n and duration?
   - Are comparisons fair (same model, same endpoint) and the ratios right?
   - Does the stage read as preclinical? Any implied human efficacy or safety?
   - Competitor statements accurate and neutral?
   - Market sizes and deal values sourced?
   - Forward-looking statements disclaimer present on investor/external decks?
   - Brand: "the company" in text, logo used correctly, Arial/Calibri, palette colors, footer present.
3. **Check facts** against `brand-rules/references/boilerplate.md`. Anything not there and not sourced in the
   user's material is "unverified".
4. **Report** (in chat for short pieces; as a document when long): a table ordered by severity with
   location, the exact text, why it's a problem, and a suggested rewrite. Then a short list of brand fixes
   and placeholders. End with a one-line verdict: Ready / Ready after fixes / Needs rework.
5. **Offer to apply the fixes.** When accepted, edit the file in its own format (decks with python-pptx,
   documents with python-docx), keeping everything else unchanged, and re-run the screen.

## Severity

- **High:** unsupported efficacy/safety/"first"/"cure"/"proven" claims, outcome promises ("will restore"),
  implied approval, missing disclaimer on investor material, wrong numbers.
- **Medium:** efficacy number without model/duration, hype words, unsourced market or deal figures,
  placeholders and unconfirmed contact details.
- **Low:** name style (compact or misspelled company name), off-brand fonts/colors, minor wording.

## Approved rewrites

| Avoid | Use |
| --- | --- |
| "will reverse the disease" | "is designed to reverse" / "aims to reverse" |
| "the first drug that repairs …" | "a new approach that targets …" (or source and scope the claim) |
| "safe", "no side effects" | "well tolerated in preclinical studies" |
| "far superior to X in all cases" | "outperformed X in each head-to-head preclinical test (model, endpoint)" |
| "62% improvement" (alone) | "62% of healthy tissue elasticity in mice after 8 weeks" |
| "cures fibrosis" | "is being developed to treat fibrosis" |

See `references/claims-guide.md` for the reasoning and more examples.
