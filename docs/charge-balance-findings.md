# Charge-balance finding — the leach liquor cannot exist as modelled

> Found 2026-09-12 while setting up Sheet 6 (the E-501 concentrate came out at 340 g/L Na). Hub: [[Bioleaching-MOC]] · Balance: [[Mass Balance]] · Drawing: [[bioleach_PFD_v2.html]]

**Cations dissolved in R-301 at 10 % pulp:** Co 2.8 · Ni 6.3 · Mn 2.2 · Li 6.1 · Al 2.4 · Cu 0.6 · Fe³⁺ 3.8 = **≈ 24 keq/h**
**Anions available:** gluconate 0.85 · sulfate (FeSO₄) 2.5 = **≈ 3.4 keq/h** → 7× deficit (~2 eq/L needed vs 0.3 eq/L available).

- Every dissolved metal cation needs a counter-anion; 75 mM gluconic acid supplies ~0.075 eq/L.
- INL at 2.5 % pulp has the same shape (~0.37 eq/L needed vs ~0.13 available) — so their broth must carry more acid than the 75 mM gluconate headline (keto-gluconates, acetate; biolixiviant pH ≈ 2.2), or metals were not all free ions. Our 10 % target multiplies the gap 4×; this is consistent with INL's recovery falling off above 2.5 %.
- Downstream symptoms: NaOH doses on Sheets 4–5 and the 578 kg/h Na in the brine; PHREEQC run had no `charge` keyword so its Fe results are indicative only.

## Options (2026-09-12, under discussion)
- **A.** Scale acid with pulp: ~0.3 M gluconate at 10 % (INL's ratio). Fermentation ×4; needs a Na sink (sodium gluconate by-product, or lime where sulfate exists).
- **B.** Drop to INL's 2.5 % pulp. Everything liquid ×4; evaporator ~43 t/h. Defensible; TEA much worse — that *is* the finding.
- **C.** Gluconate + supplementary H₂SO₄. Sulfate matrix, lime/gypsum viable, small fermenter; weakens the organic-acid claim.
- **First fix regardless:** charge-balance assert in `mass_balance.py`.

## Update — acid scaled with pulp (Option A trial), 2026-09-12
- `mass_balance.py` now uses **300 mM** gluconate (INL ratio). Budget: cations 24.9 keq/h vs anions 5.9 keq/h → ratio 0.24; **1,758 mM** would balance. So proportional scaling reproduces INL's imbalance, it does not remove it — INL's own liquor must carry ~3× more acid than its gluconate headline, or hold metals as neutral species.
- `thermo_speciation.py` measures the imbalance independently: cation excess **1.70 eq/L**, ~1.8 M gluconate for electroneutrality; forcing balance (PHREEQC `charge`) does not converge — I > 3 M, outside the Davies model. The liquor cannot exist as a dilute solution.
- Side effects of the 4× acid: fermenters ~240 m³ each, glucose 640 kg/h, broth 8.3 m³/h supplies most of the leach water (S-104 → 3.7 t/h), NaOH 521 kg/h, brine Na 639 kg/h; Fe–gluconate chelation becomes material at log K ≥ 8.
- **Still open:** which of A (with a sodium sink / gluconate by-product), B (2.5 % pulp), or C (supplementary H₂SO₄) the whitepaper adopts. Keshav to decide; discussion notes in the session of 2026-09-12.

## Sensitivity (2026-09-13) — see [[sensitivity_pulp.png]]
- Pulp density does not touch the charge ratio (0.24 at every pulp when acid scales with pulp). It only sizes the water side (R-301, evaporator, make-up).
- Closing the budget at 10 % pulp needs ~6× the scaled acid (1.8 M gluconate): fermenters ~1,430 m³ each, glucose 3.8 t/h, NaOH 1.6 t/h, brine Na 1.0 t/h — and the broth water alone exceeds the 10 % pulp basis above ~1.5×.
- Consequence for the options: **A** at full charge balance is a glucose-to-sodium-gluconate plant with a battery side-stream; **B** changes nothing about the deficit; **C** is the only route that closes the budget without the fermenter growing 6×.

## Decision — Option A, gluconate carries the anion budget (Keshav, 2026-09-13)
- `GA_BALANCE=1` (default) solves `GA_MM` for electroneutrality: **1,332 mM at 7 % pulp ≈ 4.34 t/h gluconic acid** (fixed by the metals dissolved, independent of pulp). Charge ratio 0.99.
- Broth strength raised to **250 g/L** (`BROTH_GA_GL`, industrial fed-batch G. oxydans; INL lab broth 80 g/L — citation still owed). At 80 g/L the broth alone exceeds the liquor at any pulp above ~2.5 %.
- Pulp lowered **10 % → 7 %**: the highest pulp at which a 250 g/L broth fits in the liquor (make-up water S-104 stays positive, 3.6 t/h). Model now raises a hard error if the broth exceeds the liquor.
- Sodium gluconate as a saleable by-product: rejected. Food/pharma grade needs a purification plant (ppm Co/Ni kills it); technical grade (~$0.6–0.9/kg) barely returns the glucose + NaOH that made it. Recycling the anion is the real lever (see below).
- Consequences in the balance: R-202 **500 m³** each · glucose **4.2 t/h** (~34 kt/yr) · K-201 12,500 m³/h · NaOH **1.65 t/h** (1.2 t/h of it neutralising gluconate at T-402) · brine Na **1,090 kg/h** + **4.3 t/h gluconate** · products 2,980 / 6,149 / 1,651 t/yr · Co to product 78 %.

### New blocker uncovered — Li recovery does not close on Option A
- S-512 (barren liquor, ~23 t/h) is already **~204 g/L sodium gluconate**. Concentrating it 13× to 25 g/L Li puts the salt at ~2,600 g/L against ~590 g/L solubility. `mass_balance.py` now prints a WARNING and `key_metrics()["li_conc_feasible"] = False`; the E-501 duty shown (21.6 t/h) is arithmetic, not a design.
- Options for Keshav: **(i) recycle the barren raffinate to R-301** as regenerated lixiviant (cation-exchange SX returns 2 H⁺ per M²⁺, re-protonating gluconate) and bleed a slip-stream to Li recovery — shrinks the fermenter to make-up and gives the bleed a purpose; **(ii) Li₃PO₄ precipitation** directly at ~2 g/L Li (solubility 0.39 g/L) instead of evaporation + Li₂CO₃; **(iii) biological gluconate destruction** ahead of E-501 (gluconate ThOD ≈ 0.9 g O₂/g, easily degraded). Claude's recommendation: (i), with (ii) as the Li product route if the bleed is still dilute.

### Thermo re-run on the Option A liquor ([[thermo_results.txt]])
- At pH 2.5 only a few % of the 1 M gluconate is deprotonated (pKa 3.86) → PHREEQC still shows 1.0 eq/L cation excess. The balanced liquor must sit at **pH ~4.5–5**; leach pH becomes a design variable, not INL's 2.5.
- At that pH goethite is complete (Fe 0.2 % dissolved from pH 3) and gibbsite takes 91 % of Al by pH 4.5 — Fe/Al removal moves into R-301 and the residue; Co/Ni/Cu/Mn stay 100 % dissolved to pH 8 (gluconate chelation). Fe(III) oxidant mostly solid above pH 3 — questions the FeSO₄ reductant chemistry at leach pH.

## Recycle option (i) checked — does not return acid (2026-09-13, late) — [[recycle_loop_check.py]]
- Every metal equivalent removed downstream (hydroxide or pH-controlled SX) converts one gluconate equivalent to **sodium** gluconate. The raffinate therefore comes back at pH 6.5 with no free acid; fermenter duty is unchanged (~4.3–5.0 t/h). Recycle ≤ 65 % (Na-gluconate solubility), Li 5.5 g/L in the bleed, and the loop's water does not fit the 7 % pulp basis unless the fermenter medium is made from the salty recycle.
- Ways to actually close the acid loop: **bipolar-membrane electrodialysis (BMED)** on the bleed/raffinate → gluconic acid back to R-301 + NaOH back to T-402/SX (electricity ~2–3 kWh/kg acid; used industrially for organic-acid recovery); or accept the fermenter at full duty and treat the recycle as a water/Li lever only. Li product route: Li₃PO₄ at ~2–5 g/L, or evaporate the bleed only to the Na-gluconate limit.
- Side finding: NaOH had been over-counted (one per gluconate). Fixed with pH-set-point accounting: NaOH 844 kg/h, brine Na 627 kg/h. PLS pH on Option A ≈ 4.8 with a 15 % acid margin (`GA_EXCESS`).

## Closure (2026-09-13): Li₃PO₄, fermenter at full duty
- Keshav: recover lithium as **Li₃PO₄** from the barren liquor (no evaporation ahead of it); E-501 becomes a water-recovery evaporator to the Na-gluconate solubility limit. Raffinate recycle and BMED recorded as alternatives (Index note ㉘), not adopted. Basis is now fully consistent end to end: gluconate-balanced leach at 7 % pulp, pH-set-point NaOH, Li₃PO₄ 1,821 t/yr. Sheet 6 can start.

---

# 2026-09-13 — The 250 g/L broth titer does not survive a literature check

**This is the most consequential finding since the charge-balance work,
and it moves the flowsheet, not just a note.**

## What the literature actually supports

The Option A basis assumes a 250 g/L gluconic acid broth from *G. oxydans*.
A dedicated literature sweep could not verify **any** peer-reviewed report at that
titer. The defensible range for *G. oxydans* gluconic acid is **≈120–150 g/L**.
Titers above 250 g/L in this genus belong to the **ketogluconates** (2-KGA / 5-KGA),
which are a different product, not gluconic acid.

Supporting: Y. Zhang, Y. Zheng and W. Fan, "The versatility of *Gluconobacter oxydans*,"
*World J. Microbiol. Biotechnol.*, vol. 38, art. 134, 2022, doi: 10.1007/s11274-022-03310-8.

## Why it matters — the titer sets the pulp density

Pulp density was set at 7 % as "the maximum that fits the broth". That ceiling is a
direct function of the titer, so lowering the titer lowers the pulp density, and every
volume in the plant inflates:

| Broth titer | Max pulp | R-202 fermenter | R-301 leach | E-501 evaporator |
|---|---|---|---|---|
| 250 g/L (current, unsupported) | 7.0 % | 575 m³ | 318 m³ | 9.1 t/h |
| **150 g/L (literature high)** | **4.2 %** | **962 m³** | **483 m³** | **20.9 t/h** |
| 120 g/L (literature typical) | 3.3 % | infeasible — the water check fails | | |

**The evaporator duty more than doubles.** E-501 was already the largest energy user
after fermenter air, so this lands squarely on the weakest part of the energy case.
The fermenter at 962 m³ also exceeds the scale of real citric/gluconic acid plants
(commonly quoted at 100–300 m³), so it becomes a multi-train unit.

At 120 g/L the balance **raises SystemExit** — the broth required carries more water
than the leach liquor can hold. The water check added on 2026-09-13 is what caught this.

## Options, none of them free

1. **Re-base at 150 g/L and 4.2 % pulp.** Honest and defensible. Costs a much larger
   evaporator and fermenter train, and the energy case weakens.
2. **Concentrate the broth before leaching.** Moves the evaporation upstream rather than
   removing it; needs its own energy accounting.
3. **Keep 250 g/L as an explicit stretch assumption**, state plainly that it is unsupported
   by current literature, and carry option 1 as the base case with 250 g/L as sensitivity.
4. **Find a real source at 250 g/L.** Not located so far.

**Recommendation: option 3 — base case at 150 g/L, with 250 g/L shown as the upside.**
It is the only framing that survives a reviewer who checks the titer, and it turns a
hidden weakness into a stated sensitivity.

**Decision required from Keshav before the Index and PFD are re-cited**, because the
sizing tables on Sheets 2, 3 and 5 all move with it.

---

# 2026-09-13 — Second sourcing casualty: the 97 % crystalliser yield

Literature check found a real measured figure that contradicts the assumption.
O. Zhang et al., "Semi-batch evaporative crystallization and drying of cobalt
sulphate hydrates," *Hydrometallurgy*, vol. 208, art. 105821, 2022, reports a
single-pass yield near **86 %**, not 97 %.

In this flowsheet that is a **direct recovery loss**, because `CRYST_YIELD` sends
(1 − yield) to the purge streams S-518 / S-519 and out to Sheet 6:

| Per-pass yield | Co to product | Ni to product |
|---|---|---|
| 0.97 (current) | 78.1 % | 76.3 % |
| 0.90 | 70.8 % | ~69 % |
| 0.86 (literature) | 67.7 % | ~66 % |

**Ten points of cobalt recovery ride on this single unsourced number.**

## A code/comment inconsistency found while testing

`mass_balance.py` line 69 comments that the mother liquor is *"recycled to the
crystalliser feed"*. **The model does not do that** — it purges it. If the comment
describes the intent, the model understates recovery and the fix is to recycle the
purge with a small bleed. If the model is right, the comment is wrong and should go.
**Either way the two disagree and one of them must change.** Recycling with a bleed is
normal industrial practice and would recover most of the difference, which makes this
worth resolving before re-basing recovery downward.

## Status

Not changed. This and the broth titer both need Keshav's decision, and they interact:
both move Co/Ni recovery and the Area 500 purge load.
