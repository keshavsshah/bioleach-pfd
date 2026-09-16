# Cost Basis

Capital and operating cost for the flowsheet, and the price sources behind the revenue
figure. Reproduced by `capex.py`, `opex.py`, `acid_cost.py` and `levers.py` in this folder; revenue by `revenue_floor.py`.

**Quantities come from the closed mass balance and are not estimates. Prices are
estimates**, exposed as named constants at the top of each script so a reader can
substitute a quotation and re-run. The cost *structure* is therefore considerably more
robust than the totals.

## Capital

Class 5 factored estimate: purchased equipment cost from power-law scaling of each item in
`C-equipment-list/equipment.csv`, a Lang factor of 4.05 for a solid-fluid processing plant, and
20 % contingency.

| | |
|---|---|
| Purchased equipment | ≈ $24M |
| Total fixed capital | **≈ $118M** |
| Accuracy | −50 % / +100 % |

The three largest items are the production fermenters, the batch leach train and the
water-recovery evaporator.

## Operating cost

| Input | Quantity/yr | $M/yr |
|---|---|---|
| Glucose syrup | 38,760 t | 15.5 – 25.2 |
| Sodium hydroxide | 10,737 t | 4.3 – 6.4 |
| Trisodium phosphate | 2,852 t | 2.0 – 2.9 |
| Ferrous sulfate heptahydrate | 2,821 t | 0.4 – 0.7 |
| Power | ~14.4 GWh | 1.0 – 1.4 |
| Steam | ~95,000 t | 1.0 – 1.9 |
| Labour and maintenance | — | 8.7 |
| **Total** | | **32.9 – 47.2** |

## Revenue

| Stream | Basis | $M/yr |
|---|---|---|
| Cobalt | 643 t contained Co at $15–21/lb [24], [26] | 21.2 – 29.7 |
| Nickel | 1,412 t contained Ni at $15,000/t [25] | 21.2 |
| Lithium | 1,831 t Li₃PO₄ at $2.07–3.90/kg [27] | 3.8 – 7.1 |
| **Floor** | | **46.2 – 58.1** |

This is a **floor**. Battery-grade sulfates sell above contained-metal value because the
buyer is paying for conversion, and those salt assessments are published only under
subscription [28]. No price agency assesses Li₃PO₄ at all; the figure used is a single
literature source [27], and the compound trades thinly because recyclers generally treat it
as an intermediate to Li₂CO₃ rather than a product. Sodium gluconate from the dryer is
carried at zero credit.

## Why the route costs more

Glucose alone is 53 % of operating cost, and the reason is structural. Gluconic acid is
monoprotic and heavy and is bought as food-grade sugar; sulfuric acid is diprotic, light,
and made from a waste sulfur stream.

| Acid | $ per kilo-equivalent of acidity |
|---|---|
| Sulfuric (diprotic) | 4.90 – 7.36 |
| Gluconic (from glucose) | 80.07 – 130.12 |

**Eleven to twenty-seven times more per equivalent**, before the fermenter, the air
compression and the evaporation that a dilute broth additionally requires. Against
conventional hydrometallurgical refining at roughly $1,500–1,800 per tonne of black mass,
this flowsheet runs $3,300–4,700 per tonne.

## What narrows the gap

| Change | Effect on operating cost |
|---|---|
| Corn stover hydrolysate in place of glucose syrup | −$14.5M/yr |
| Bipolar-membrane electrodialysis returning 70 % of gluconate | −$14.2M/yr |
| Broth titre 150 → 250 g/L | −$0.2M/yr |
| All three | $38.5M → $19.7M |

Applied together these move the margin from $8–20M to $27–38M. The carbon source is the
dominant lever and is the feedstock Alipanah et al. already assume [4]. Broth titre is
worth almost nothing in operating terms: a higher titre buys smaller equipment, not cheaper
operation.
