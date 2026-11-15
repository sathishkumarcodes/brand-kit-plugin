# Use it for your own brand

[← Back to README](../README.md)

The whole kit reads its brand from one file, `brand.json`. Change that, swap the logos, re-skin the Office
templates with one script, and every output is yours.

## Steps

1. **Keep a copy of the sample config** as the "from" brand:
   ```bash
   cp brand.json brand.sample.json
   ```
2. **Edit `brand.json`:** name, legal name, wordmark, tagline, website, city, footer, program name, fonts
   and colors by role (see the [reference](#brandjson-reference) below).
3. **Replace the logos** in `assets/logos/`. Keep the same file names and a 3:2 canvas for the main logos.
   Replace the cover art and corner accents too if you like. Keep copies of the sample files for the next
   step.
4. **Re-skin the Office templates** from the sample brand to yours:
   ```bash
   python3 scripts/rebrand_templates.py --from brand.sample.json --to brand.json \
       --in assets/templates/*.potx assets/templates/*.dotx --out assets/templates/
   ```
   It updates the theme colors, maps every hard-coded color by role, swaps logos and accents (matched by
   content, resized to the original dimensions), replaces the company name, footer, website, city and
   tagline, and rewrites the document metadata. Options: `--strip-slides` removes sample slides,
   `--layout-prefix` renames layouts.
5. **Replace the copy** in `skills/brand-rules/references/boilerplate.md` with your approved descriptions,
   key facts and claims to avoid. Adjust `brand-guide.md` if your rules differ.
6. **Tune the claims rules** in `skills/claims-check/scripts/brand_audit.py` for your field. The defaults
   suit preclinical and clinical biotech.
7. **Check the result:**
   ```bash
   python3 examples/build_sample_deck.py
   python3 examples/build_sample_documents.py
   ```
   Open the files in `outputs/` and look at every page.

## brand.json reference

| Key | Example | Used for |
| --- | --- | --- |
| `name` | `Acme Bio` | Running text, footers, signatures |
| `legal_name` | `Acme Bio, Inc.` | Letter footers, disclaimers, signature blocks |
| `wordmark` | `ACME BIO` | Logo-style text; the claims check flags it in running text |
| `tagline` | `Science that holds together.` | Covers, banners, signatures |
| `website`, `city` | `acmebio.example`, `Boston, Massachusetts` | Cards, signatures, letterhead |
| `footer` | `Acme Bio  \|  Confidential` | Slide and document footers |
| `program` | `ACM-101` | Sample content and examples |
| `fonts.heading`, `fonts.body` | `Arial`, `Calibri` | Every output; the claims check flags other fonts |
| `colors.*` | see below | Every output, by role |
| `tints.*` | `accent`, `peach`, `green`, `pink`, `gray`, `amber` | Card and callout backgrounds |
| `assets.*` | logo, reversed logo, corner accents, cover art | Paths used by the tools |

### Color roles

| Role | Sample | Meaning |
| --- | --- | --- |
| `primary` | `#12403C` | Titles, dark backgrounds, table headers |
| `accent` | `#2A9D8F` | Your result, links, highlights in charts |
| `highlight` | `#F06449` | Small accents, rules, call-to-action marks |
| `secondary` | `#5B7FA6` | Second data series, subheads |
| `positive` | `#3A7D44` | Good outcomes, "done" |
| `milestone` | `#E9B44C` | Milestones and stars on timelines |
| `extra` | `#7B5EA7` | Additional series |
| `text`, `muted`, `on_dark` | `#1F2933`, `#667370`, `#CFE6E2` | Body text, captions, text on dark backgrounds |
| `rule`, `border`, `zebra`, `background` | light neutrals | Lines, table borders, alternate rows, page backgrounds |
| `reference`, `comparator` | `#C8D3D1`, `#D2B48C` | "Healthy / baseline" and "competitor / vehicle" bars in charts |
