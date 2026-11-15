"""Build the fictional sample letter and report shown in the README -> outputs/."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/branded-document/scripts"))
from lb_doc import *  # noqa: E402,F401

out = ROOT / "outputs"
out.mkdir(exist_ok=True)
d = new_letter(date="November 15, 2026", recipient=["Dr. Alex Morgan", "Director of Research", "Example University", "100 Main Street", "Cambridge, MA 02139"],
               subject="Proposed research collaboration", salutation="Dear Dr. Morgan,",
               paragraphs=["Thank you for meeting with our team last week. We would like to propose a six-month collaboration to test ACM-101 in your tissue models.",
                           "We suggest three steps:"],
               bullet_items=["Agree the study design and endpoints by December 15", "Share compound and protocols in January", "Review interim data in April"],
               signoff="Sincerely,", signer=["Jane Doe, PhD", "Chief Executive Officer", BRAND["legal_name"]])
save(d, out / "Acme_Sample_Letter.docx")

d = new_report(title="Quarterly Board Update", subtitle="Program status and 2027 plan (fictional sample)",
               meta={"Prepared by": "Jane Doe, PhD", "Date": "November 15, 2026", "Version": "1.0 Draft"}, toc=False)
h1(d, "1. Executive Summary")
p(d, "ACM-101 remains on track for **IND-enabling toxicology in Q4 2026**. Mouse data show 62% of healthy tissue elasticity after 8 weeks of oral dosing.")
callout(d, "**Key takeaway:** the next financing milestone is the start of first-in-human studies in 2027.")
h2(d, "1.1 Highlights")
bullets(d, ["Lead candidate selected", ("Oral bioavailability confirmed in two species", 1), "Manufacturing partner contracted"])
h1(d, "2. Milestones")
table(d, [["Milestone", "Target", "Status"], ["Lead selected", "Q1 2026", "Done"], ["IND-enabling toxicology", "Q4 2026", "In progress"],
          ["Phase 1 start", "Q2 2027", "Planned"]], col_widths=[3.0, 1.75, 2.0], caption="Table 1. Program milestones (fictional).")
numbered(d, ["Approve the 2027 budget", "Confirm the Phase 1 site shortlist", "Start financing discussions"])
small(d, "All names, data and programs in this document are fictional.")
save(d, out / "Acme_Sample_Report.docx")
print("ok")
