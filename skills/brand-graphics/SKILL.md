---
name: brand-graphics
description: >
  This skill should be used when the user asks for branded image or print graphics: "social media post",
  "LinkedIn post graphic", "announcement graphic", "we're hiring post", "conference/event post",
  "LinkedIn banner", "X/Twitter header", "Zoom background", "Teams background", "virtual background",
  "business card", "email signature", or any branded PNG/PDF graphic.
metadata:
  version: "0.1.0"
---

# Brand graphics

Render graphics with `scripts/make_graphic.py` (HTML + headless Chromium via Playwright). Every type uses
the real logo files in `assets/logos/`. Load `brand-rules` for voice and approved facts.

## Types and sizes

| Type (`make_graphic.py <type>`) | Output | Fields |
| --- | --- | --- |
| `post-announcement` | PNG, `--size square` 1080², `landscape` 1200×627, `portrait` 1080×1350 | `--headline --sub [--label]` |
| `post-milestone` | PNG, same sizes | `--number --text --source [--label]` |
| `post-quote` | PNG | `--quote --name --role` |
| `post-hiring` | PNG | `--role-title --details [--headline --cta]` |
| `post-event` | PNG | `--event --when --where [--label]` |
| `linkedin-company` | PNG 1128×191 | `--headline --sub` |
| `linkedin-personal` | PNG 1584×396 (left 400 px kept clear for the profile photo) | `--headline --sub` |
| `x-header` | PNG 1500×500 | `--headline [--sub]` |
| `background` | PNG 1920×1080 for Zoom/Teams | `--style dark|light|glow [--name --title]` |
| `business-card` | 2-page print PDF, 3.5×2 in + 0.125 in bleed | `--name --title --email --phone [--city --tagline]` |
| `email-signature` | HTML snippet | `--name --title --email --phone [--city --logo-url]` |

Example:
```bash
python3 <plugin-root>/skills/brand-graphics/scripts/make_graphic.py post-milestone --size square \
  --number "62%" --text "of healthy tissue elasticity after 8 weeks in mice" \
  --source "Source: fictional sample data" --out Post_Milestone.png
```
`<plugin-root>` is two directories above this skill folder. Add `--html-only` to get the HTML for hand edits.

## Several people at once (people file)

When the user attaches a people file (JSON list of `{name, title, email, phone, city?}`; format in
`<plugin-root>/people.example.json`) or asks for cards, signatures or name-plate backgrounds "for everyone":
```bash
python3 make_graphic.py business-card   --people people.json --out-dir cards/
python3 make_graphic.py email-signature --people people.json --out-dir signatures/   # also writes All_Signatures.html
python3 make_graphic.py background --style light --people people.json --out-dir backgrounds/
```
Treat the people file as personal data: use it only for the job at hand, never copy its contents into the
plugin, a repository or other files, and don't repeat anyone's details beyond what the output needs.

If Playwright's browser is missing, run `python3 -m playwright install chromium` once.

## Copy rules

- Headline ≤ 10 words; supporting line ≤ 15 words. One number per milestone post, always with model and duration
  in the text and a source line.
- Use the company name and tagline from brand.json.
- Hiring: role, team, location, type; CTA "Apply at <website>" unless the user gives a link.
- Write the accompanying post caption too (≤ 3 short paragraphs, 1-3 hashtags such as #biotech #drugdevelopment).
- Never invent contact details. If email/phone are not given, use `name@example.com` / `+1 (555) 010-01xx` and flag them.

## Specific guidance

- **Backgrounds:** keep the centre and lower middle clear (that's where the person sits). Name-plate versions
  put a primary-color box with a highlight-color edge bottom left. Teams: upload under Background effects → Add new. Zoom: Settings →
  Backgrounds & effects → +.
- **Business cards:** text stays 0.25 in inside the trim; the PDF already includes bleed. Print on 16 pt matte
  or uncoated stock. Generate one PDF per person.
- **Email signature:** paste the HTML into Outlook (Settings → Mail → Signatures) or Apple Mail. Gmail drops
  embedded images: host the logo (website or public link) and pass `--logo-url`.
- **Icons in graphics:** use `assets/icons/png-white/` on dark or `png-dark/` on light backgrounds.

## Check

Open each PNG/PDF and look at it: text fits, nothing overlaps the logo, contrast is fine, numbers match the
source. Run `claims-check` on the text before posting.
