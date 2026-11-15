# Brand guide (sample brand: Acme Bio, fictional)

Values below are the sample brand's; the source of truth is `brand.json`. Change that file (and run
`scripts/rebrand_templates.py`) to use your own brand.

## 1. Color

| Role | Sample hex | Use |
| --- | --- | --- |
| primary | #12403C | Titles, footers, dark panels, table headers |
| accent | #2A9D8F | Primary accent, highlighted chart series, links |
| highlight | #F06449 | Logo accent, emphasis bars, calls to action, risks |
| secondary | #5B7FA6 | Subheadings, labels, section numbers |
| positive | #3A7D44 | Good results |
| milestone | #E9B44C | Milestones and highlights |
| extra | #7B5EA7 | Extra chart series |
| text / muted | #1F2933 / #667370 | Body text / captions and sources |
| on_dark | #CFE6E2 | Secondary text on dark fills |

Tints (backgrounds only): accent #E3F2EF, peach #FDEBDD, green #E6F2E7, pink #FBE9E4, gray #EEF2F1, amber #FBF1DC.

Chart series order: primary, accent, secondary, milestone, highlight, extra. Control bars use `reference`,
competitor bars `comparator`. Gridlines #E5E7EB, axis labels #4B5563.

## 2. Typography

| Use | Slides | Word |
| --- | --- | --- |
| Title | Heading font 26 pt, primary | Heading font 28 pt, primary |
| Heading | Body font bold 20 pt, primary | H1 heading font 16 pt + thin rule; H2 body bold 13 pt |
| Subheading | Body font bold 16 pt, secondary | H3 body bold 11.5 pt, secondary |
| Body | Body font 14-16 pt, text color | Body font 11 pt, 1.15 spacing |
| Caption / source | Italic 9-11 pt, muted | Caption style 9 pt italic |
| Big number | Bold 40-60 pt (up to 100 pt), primary, with a secondary-color label | — |

Minimum sizes: 10 pt on slides, 8 pt in print, 9 pt in Word.

## 3. Logo

Files: `assets/logos/logo_full_color.png` (light backgrounds) and `logo_reversed.png` (dark backgrounds).
Slides: top right, about 0.72 × 0.48 in. Covers: top left, about 1.05 in wide. Clear space: the height of a
capital letter of the wordmark on all sides. Use vector masters for large print.

## 4. Graphic devices

- Short highlight-color bar (0.6 × 0.06 in) near section titles and under names in quotes.
- Thin rule under slide titles with a 1.25 in accent-color segment at the left.
- Corner accent (`corner_accent_bottom_right.png`) on light pages, cards and posts.
- Thin concentric rings in `secondary` at about 20-25% opacity on dark backgrounds.
- Fully rounded uppercase pill labels: highlight = announcement/CTA, secondary = milestone, primary = event.

## 5. Layout

16:9 slides, side margins 0.45 in, content between 1.2 in and 5.25 in, footer bar with the `footer` text and
slide number (built into the template). One message per slide; slide titles state the takeaway.

## 6. Tables and charts

Tables: primary header row with white bold text, zebra rows, thin borders, numbers right-aligned, totals bold
on gray tint, one highlighted row at most, caption or source underneath. Charts: native and editable, brand
series colors, data labels when there are fewer than 10 values, a title with units, a source line with model,
n and duration.

## 7. Icons

Tabler outline icons (24 px grid, 2 px rounded strokes) in `assets/icons`. Outline in the primary color on
light backgrounds, or white in a category-color circle. Never mix icon sets.

## 8. Accessibility

Body text contrast at least 4.5:1, never color alone (add labels or legends), alt text on images, six bullets
or fewer per slide.
