# Design Basis

The quantitative basis on which the flowsheet is sized. Every figure here is reproduced
by `G-mass-balance/mass_balance.py`, which asserts closure rather than assuming it.

## Feed and product

| | |
|---|---|
| Throughput | 10,000 t/yr black mass |
| Feed grade | Ni 18 %, Co 8 %, Mn 5 %, Li 3.5 %, Cu 2 %, Al 3 % |
| Operating hours | 8,000 h/yr |
| Products | CoSO₄·7H₂O 3,065 t/yr · NiSO₄·6H₂O 6,324 t/yr · Li₃PO₄ 1,831 t/yr |
| Recovery to product | Co 80.3 % · Ni 78.4 % · Li 94.1 % |

Recoveries are quoted **metal in feed to bagged product** and carry every loss through
leaching, iron removal, solvent extraction, crystallisation and filtration. Leach
extraction figures reported in the literature are measured at a much earlier boundary
and are not directly comparable.

## The biolixiviant requirement is set by electroneutrality

The gluconate concentration is not a free parameter. Dissolved metal cations must be
charge-balanced by an anion, and with sulfate contributed only by the ferrous sulfate
dose, gluconate carries the remainder. Solving the leach for electroneutrality, with a
15 % free-acid margin so the liquor holds a finite pH, fixes the requirement at:

| | |
|---|---|
| Gluconate in leach liquor | 896 mM, ≈ 5.0 t/h gluconic acid |
| Charge ratio (anion : cation) | 1.13 |
| Leach pH | ≈ 4.8 |

This single constraint sizes the entire fermentation section, and through it the plant.

## Pulp density follows from the broth

The broth is dilute, so its water is most of the leach liquor and pulp density cannot be
set independently. At a 150 g/L broth, the highest titre reported for *G. oxydans*
gluconic acid [12], the maximum workable pulp is **4.2 %**. Raising the titre raises the
pulp ceiling and shrinks the equipment; it has almost no effect on operating cost, because
the evaporation saved is small beside the cost of the carbon source.

`mass_balance.py` refuses to run any combination where the broth carries more water than
the leach liquor can hold, so an infeasible basis fails loudly rather than producing a
plausible but wrong answer.

## Leach conditions

Taken from Alipanah et al. [4]: 55 °C, 30 h residence, ferrous sulfate at 3.75–4.51 kg
per kg of cobalt recovered. Iron is a stoichiometric reductant rather than a catalyst, so
essentially all of it reports to the pregnant liquor as Fe(III).

## Separation set-points

| Unit | Reagent | Set-point | Basis |
|---|---|---|---|
| Fe/Al precipitation | NaOH | pH 5.5 | Goethite complete from pH 3, gibbsite 91 % by pH 4.5 [19] |
| Mn extraction | D2EHPA | pH 3.0 | Mn ahead of Co; Co co-extraction climbs above ~3.5 |
| Co extraction | Cyanex 272 | pH 5.5–6.0 | pH₅₀ 5.3 Co, 7.0 Ni [15] |
| Ni extraction | Versatic 10 | pH 6.5 | Ni ahead of Li and Na |
| Li precipitation | Na₃PO₄ | 60 °C | Li₃PO₄ precipitates directly from the 1.9 g/L barren |

Base demand is computed as the quantity required to hold each set-point against the
gluconate buffer, not assumed.

## Crystallisation

Cobalt and nickel sulfate crystallise evaporatively at 86 % per pass [17], with the mother
liquor recycled to the crystalliser feed and a 5 % bleed. Because recovery follows
*y* / (*y* + (1−*y*)·*b*), the bleed rather than the per-pass yield governs the loss, giving
99.2 % overall. The model verifies this closed form against a stage-by-stage simulation.

## Water and effluent

| | |
|---|---|
| Condensate recovered | 22.2 t/h |
| Fresh water demand | 6.9 t/h |
| Combined liquid bleed | 13.9 t/h |
| Crude sodium gluconate salt | 6.1 t/h |

The plant has no liquid discharge: the combined bleed is dried to a technical-grade salt.
Condensing the dryer exhaust, ~7.8 t/h, would close the water balance entirely.

## Acid recycle

Returning raffinate to the leach recovers water but no acidity. Every equivalent of metal
removed downstream converts gluconic acid to sodium gluconate, so raffinate returns near
pH 6.5 with essentially no free acid, and sodium accumulates against the ~590 g/L
solubility of the salt [20]. A genuinely closed acid loop requires bipolar-membrane
electrodialysis to split the sodium gluconate back to gluconic acid and caustic.
`H-acid-recycle/recycle_loop_check.py` quantifies the proton and sodium budget.

## Assumptions carried without a cited value

Stated so they can be checked rather than inherited: the Fe(III)–gluconate stability
constant, the Li₃PO₄ solubility and its temperature dependence, the 2 % Co/Ni occlusion
loss in the hydroxide cake, MVR specific energy at 25–35 kWh per tonne evaporated, and the
solvent-extraction stage counts. The gluconic acid pKa is taken as 3.86; sources also
report 3.70, the spread reflecting the equilibrium with glucono-δ-lactone, and the
difference is worth under 2 % on base demand. Ordinary engineering practice — tank
residence times, pump sparing, silo hold-up — is uncited by intent.
