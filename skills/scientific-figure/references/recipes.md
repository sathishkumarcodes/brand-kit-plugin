# Figure recipes

All coordinates in inches on a `title-only` slide (content area x 0.45-9.55, y 1.2-5.25).

## 1. Disease mechanism (healthy vs diseased)

- Two panels side by side: `panel(s, 0.45, 1.5, 4.2, 2.4, "Healthy tissue")` and
  `panel(s, 5.35, 1.5, 4.2, 2.4, "Diseased tissue", kind="inactive")`; `arrow(s, 4.75, 2.7, 5.25, 2.7)` labeled
  with the driver (e.g. "Injury", "Age").
- Healthy: `protein()` pills in a 2×2 grid with a few `molecule(kind="protective")` protective molecules.
- Diseased: the same pills joined by `crosslink()`; fewer protective molecules; a one-line caption in the
  crosslink color that states the change.
- Bottom: `callout_box` with the consequence, or a `legend`.

## 2. Mechanism of action (four steps)

Columns at x = 0.45, 2.85, 5.25, 7.65 (1.95 wide); `step()` numbers above; primary-color arrows between panels.
1. Dose: white panel with `prodrug()` molecules (add a product image if the user has one).
2. Absorption/distribution: tissue panel with several `prodrug()`.
3. Activation: `prodrug()` → `arrow(..., "convert")` → `molecule(kind="drug")`; `enzyme()` below.
4. Effect: two `protein()` with the crosslink broken (two short segments with a gap) and the active drug;
   a positive-color caption naming the outcome.

## 3. Study design schematic

Horizontal timeline (gray line); `step()` circles at dosing and readout points; tinted boxes above for arms
(drug: purple tint, vehicle: gray, comparator: tan); readouts below in secondary-color text; caption with
species, n per arm, route, dose and duration.

## 4. PK / exposure comparison

Use a native chart (`lb_deck.add_chart`, kind="column") rather than shapes: compartments on the x-axis,
active drug in the accent color, prodrug in a pale tint, units in the axis title, the target exposure as a
text callout.

## Labels and captions

- Figure caption (10 pt italic muted): "Figure n. What it shows. Species, n, duration. Source."
- Define abbreviations once.
