"""Build the fictional Acme Bio sample deck shown in the README.

    python3 examples/build_sample_deck.py   ->  outputs/Acme_Sample_Deck.pptx
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/branded-deck/scripts"))
sys.path.insert(0, str(ROOT / "skills/scientific-figure/scripts"))
from lb_deck import *  # noqa: E402,F401
from lb_sci import *  # noqa: E402,F401

prs = new_deck()
add_slide(prs, "cover", title="Breaking Cross-Links", subtitle="ACM-101: an oral prodrug for\nfibrotic disease",
          tagline="Investor overview | 2026 (fictional sample)")
add_disclaimer(prs)
add_slide(prs, "agenda", title="Agenda", body=["The problem", "Our approach", "Evidence", "Plan and financing"])
add_slide(prs, "section-number", number="01", title="The Problem", body="Scar tissue that the body cannot clear")
s = add_slide(prs, "title-only", title="Fibrosis Affects Millions and Has Few Options")
stat_cards(s, [("10M+", "Patients (illustrative)"), ("2", "Approved drugs (illustrative)"), ("0", "That reverse scarring")])
banner(s, "A disease-modifying therapy would change the standard of care")
add_slide(prs, "chart", title="ACM-101 Reduced Fibrosis in Mice",
          chart=dict(kind="column", categories=["Healthy", "ACM-101", "Vehicle"], series={"% of healthy": [100, 62, 21]},
                     colors=[REFERENCE, ACCENT, COMPARATOR], number_format='0"%"', title="Tissue elasticity (% of healthy)"),
          takeaway_head="62% of healthy", takeaway=["vs 21% with vehicle", "8-week oral dosing in mice (fictional data)"],
          source="Source: fictional sample data for illustration")
add_slide(prs, "table", title="Program Milestones", subheading="From lead to Phase 1 in 24 months (illustrative)",
          table=[["Milestone", "Target", "Status"], ["Lead selected", "Q1 2026", "Done"],
                 ["IND-enabling toxicology", "Q4 2026", "In progress"], ["Phase 1 start", "Q2 2027", "Planned"]],
          source="Fictional sample")
s = add_slide(prs, "title-only", title="How ACM-101 Works")
for i, hd in enumerate(["Oral dose", "Absorbed as prodrug", "Enzyme releases drug", "Cross-links broken"]):
    x = 0.45 + i * 2.4
    step(s, i + 1, x, 1.15)
    label(s, hd, x + 0.42, 1.18, 1.9, size=13, bold=True, align="left")
    panel(s, x, 1.65, 1.95, 2.3)
prodrug(s, 0.9, 2.4, 0.3); prodrug(s, 1.4, 2.9, 0.3)
prodrug(s, 3.2, 2.3, 0.3); prodrug(s, 3.9, 2.7, 0.3); prodrug(s, 3.4, 3.2, 0.3)
prodrug(s, 5.45, 2.1, 0.32); arrow(s, 5.95, 2.26, 6.45, 2.26, "convert")
molecule(s, 6.55, 2.1, 0.32, "drug", "Active drug"); enzyme(s, 5.85, 2.85, 0.55)
protein(s, 7.85, 1.95, 1.0, 0.36); protein(s, 7.85, 2.75, 1.0, 0.36)
crosslink(s, 8.2, 2.31, 2.45, show_label=False); crosslink(s, 8.2, 2.62, 2.75, show_label=False)
molecule(s, 8.95, 2.35, 0.32, "drug")
for x in (2.4, 4.8, 7.2):
    arrow(s, x + 0.02, 2.8, x + 0.43, 2.8)
legend(s, ["protein", "crosslink", "drug", "prodrug", "enzyme"], 0.45, 4.3, per_row=5, col_w=1.82)
add_slide(prs, "big-number", number="24 mo", label="From lead selection to first patient",
          title="A Fast, Capital-Efficient Path", body="Fictional sample slide showing the Big Number layout.")
add_slide(prs, "photo-divider", photo=str(ROOT / "assets/images/sample_photo.png"), title="Our Approach",
          body="Break the links that hold scar tissue together")
add_slide(prs, "closing", title="Thank You", body="Jane Doe, PhD  |  CEO  |  acmebio.example")
out = ROOT / "outputs"
out.mkdir(exist_ok=True)
print(save(prs, out / "Acme_Sample_Deck.pptx"))
