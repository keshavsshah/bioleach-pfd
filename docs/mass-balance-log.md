# Mass Balance — Python

> Per-stream mass balance **and equipment sizing** for the black-mass bioleach PFD, grown one block at a time with the drawing.
> Created 2026-09-07 · updated 2026-09-12. Hub: [[Bioleaching-MOC]] · Drawing: [[bioleach_PFD_v2.html]] · Index: [[bioleach_PFD_index.html]] · Tables: [[Stream Table]]

- Script: [[mass_balance.py]]
  - `python3 mass_balance.py` → all streams (kg/h per component), headline numbers, equipment sizes; asserts fail if the balance breaks.
  - `python3 mass_balance.py --html N` → the Sizing + Streams table rows for Index block N (1, 2, 3). Paste into `bioleach_PFD_index.html`; never retype numbers.
- Thermodynamics companion: [[thermo_speciation.py]] · [[minteq.v4.dat]] · [[thermo_results.txt]]
- Basis: 10,000 t/yr · 8,000 h/yr · 1,250 kg/h · 10 % pulp in R-301 (INL demonstrated 2.5 %) · leach recovery Co 86 / Ni 84 / Li 100 / Mn 100 %, downstream losses applied per unit · fermentation route (*G. oxydans* gluconate + FeSO₄).
- Structure: basis constants → Block 1 → Block 3 (Area 200 first, because broth water sets S-104) → Block 2 → `equipment` sizing → output.
- Why Python over MATLAB (2026-09-07): no MATLAB on this Mac; the balance is linear splits per unit, and a dataframe is both the calculation and the whitepaper table. Port to `.m` later only if a MATLAB artifact is wanted for portfolio reasons.

## Block log
- Block 1 (2026-09-07): S-101 black mass 1,250 kg/h → V-101; S-102 vent (no net flow).
- Block 2 (2026-09-08): S-103 metered solids; S-104 make-up water; S-105 feed slurry.
- Block 3 (2026-09-12): Area 200 — 166 kg/h gluconate → 2.07 m³/h broth at 80 g/L → 160 kg/h glucose; 0.5 vvm air; raffinate return (80 %, placeholder) with 15 % bleed. **S-104 corrected 11,250 → 9,372 kg/h** (broth water counts toward pulp density). Sizing section added; R-201A = 50 L is a 1 % inoculum into R-201B (Keshav's call).

## Thermodynamics — [[thermo_speciation.py]]
- PHREEQC via `phreeqpython` (scratch venv: `pip install phreeqpython pandas`), database [[minteq.v4.dat]] (USGS, kept in this folder) plus gluconate species added in the script (pKa 3.86; 1:1 carboxylate complexes Co/Ni/Cu/Al/Mn/Fe(III) — 25 °C constants, sources in the `LOGK` dict). Output: [[thermo_results.txt]].
- Reads the PLS composition from `mass_balance.py` (S-309), pins pe = 15 (Fe as Fe(III)), titrates with NaOH and lets goethite / gibbsite / Cu(OH)₂ / Co(OH)₂ / Ni(OH)₂ precipitate (amount 0 → precipitate-only).
- Results (2026-09-12): (a) Fe(III)–gluconate holds <0.1 % of Fe below pH 4.5 — chelation does not block Fe removal in the pH 3.5–5 window (only matters if log K ≥ 10); (b) no solubility ceiling on Cu (tenorite SI −2.6) or Al (gibbsite SI −0.5) at pH 3 → Cu 80 / Al 60 are kinetic, literature values stand; (c) goethite pH 3–5.5, gibbsite 5.5–6.5, Co/Ni stay dissolved to pH 8 → Sheet 4 Fe/Al removal setpoint ≈ pH 5.5; Cu needs cementation/sulfide.
- Caveats: I ≈ 1.7 M (beyond Davies); 25 °C gluconate constants; minteq polynuclear Fe species make ferrihydrite read undersaturated — goethite used as the control phase; equilibrium only.
- Debugging lessons kept for next time: `phreeqc.dat` lacks Co/Ni; bundled `wateq4f_PWN.dat` would not load; default pe 4 silently reduces Fe(III) → Fe(II) on titration; `equalize()` default gives 10 mol of each phase to *dissolve* — pass `in_phase=[0,…]`.

## Literature (Cu / Al leach fractions, 2026-09-12 Consensus search)
- Lerchbammer et al. 2025, *Case Stud. Chem. Environ. Eng.*, DOI 10.1016/j.cscee.2025.101271 — gluconic acid + H₂O₂: 100 % Li/Ni/Co/Mn, **Al 51.9 %, Fe 9.7 %, Cu 0.3 %**.
- Porvali et al. 2020, *Sep. Purif. Technol.*, DOI 10.1016/j.seppur.2019.116305 — metallic Cu reduces Fe³⁺; Fe²⁺ reduces LiCoO₂; Cu in typical cells suffices as reductant.
- Partinen et al. 2024, *Miner. Eng.*, DOI 10.1016/j.mineng.2024.108828 — Cu the dominant in-situ reductant at 30 °C (needs ≥0.4 g/L Fe); Al takes over ≥50 °C.
- Bahaloo-Horeh et al. 2017, *Waste Manag.*, DOI 10.1016/j.wasman.2016.10.034 — *A. niger* organic acids: **100 % Cu, 75 % Al**.
- Horeh et al. 2016, *J. Power Sources*, DOI 10.1016/j.jpowsour.2016.04.104 — 100 % Cu, 65 % Al.
- Rasoulnia et al. 2021, *J. Hazard. Mater.*, DOI 10.1016/j.jhazmat.2021.125564 — gluconate pH 3 on NiMH: Cu 24 %, Fe 90 %.
- Casas et al. 2006, *Can. Metall. Q.*, DOI 10.1179/cmq.2006.45.3.243 — Fe³⁺ dissolution of metallic Cu, 25–65 °C, surface-reaction controlled.
- Alipanah et al. 2023, *Resour. Conserv. Recycl.*, DOI 10.1016/j.resconrec.2023.107293 — INL RSM + thermodynamic modeling; precedent for the speciation approach.
- Tran et al. 2026, ECS Meeting Abstracts, DOI 10.1149/ma2026-01562723mtgabs — *G. oxydans* black-mass bioleach: Cu, Al, Fe impurities remain in the leachate.
- Basis chosen: **Cu 80 %, Al 60 %** (sensitivity Cu 0.3–100 %). Cu-as-reductant credit (would halve FeSO₄) left OFF: INL's 4.1 kg/kg ratio was measured on Cu-bearing black mass.

## Placeholders to close
- S-203/S-204 raffinate return + bleed — set by Area 400 when drawn.
- Broth titer 80 g/L and 24 h cycle — INL gives 75 mM at the leach, not the fermenter titer; check against *G. oxydans* literature.
- Block 4 (2026-09-12): Area 300 — FeSO₄·7H₂O 353 kg/h dry (4.1 kg/kg Co); leach fractions Co 86 / Ni 84 / Li 100 / Mn 100, **Cu 50 / Al 60 placeholders**; CO₂ off-gas placeholder (30 % Li as carbonate); belt filter 30 % cake moisture, 2 m³/t wash, 95 % displacement. PLS Co 83.6 kg/h; residue Co 14.1; wash filtrate Co 2.3 (recycles to T-101). Sizing: R-301 4 × 180 m³ batch (50 h cycle), T-303 surge 100 m³, F-301 ~8 m², E-301 ~375 kW.
- Block 5 (2026-09-12): Area 400 — cementation (Fe powder 1.3× stoich, 99 % Cu → 19.3 kg/h cement Cu; adds 17 kg/h Fe²⁺), air oxidation + **NaOH** (not lime — sulfate too low, Ca would poison D2EHPA) to pH 5.5 → goethite 137 + gibbsite 63 kg/h dry, occlusion Co/Ni 2 % placeholder; D2EHPA SX 2E/1S/2St at pH 3.0, 98 % Mn, 2 % Co co-extraction placeholder, H₂SO₄ strip → MnSO₄ liquor 597 kg/h at 100 g/L. Purified liquor to Sheet 5: Co 80.3 · Ni 180 · Li 42.5 kg/h. Sheets renumbered to 6 (5 = Co/Ni/Li products, 6 = effluent).
- Block 6 (2026-09-12): Area 500 — Cyanex 272 Co SX (99 %, 1 % Ni co-ext), Versatic 10 Ni SX (98 %), H₂SO₄ strips at 100 g/L, evaporative crystallisers 97 %/pass with purges S-518/519, MVR evaporator to 25 g/L Li (10.7 t/h water), Li₂CO₃ at 90 °C 90 %. **Products: CoSO₄·7H₂O 2,943 t/yr · NiSO₄·6H₂O 6,074 t/yr · Li₂CO₃ 1,631 t/yr; overall Co 77 % / Ni 75 % / Li 88 %.** Water: condensate S-517 12 t/h returned (Sheet 2's return is now condensate, not raffinate); brine bleed S-516 1.8 t/h with 578 kg/h Na → Sheet 6.
- Re-basis (2026-09-12, Option A trial): `GA_MM = 75 × PULP/0.025` → **300 mM**. Gluconate demand 662 kg/h, broth 8.3 m³/h, glucose 640 kg/h, fermenters ~240 m³ each; S-104 make-up falls to 3,662 kg/h (broth is most of the leach water); NaOH 434 + 87 kg/h; brine Na 639 kg/h; evaporator 11.3 t/h. Products essentially unchanged (2,947 / 6,080 / 1,633 t/yr). **Acid budget printed by the script: cations 24.9 keq/h vs anions 5.9 keq/h (ratio 0.24); 1,758 mM gluconate would balance.** PHREEQC agrees (1.70 eq/L excess, ~1.8 M) and cannot converge a forced balance — the liquor is not a dilute solution at that point.
- Thermo re-run on 300 mM: goethite Fe removal 50 % at pH 3.0, 80 % at 3.5, 97 % at 4.5; **Fe–gluconate chelation matters at log K ≥ 8 with 4× gluconate** (92–100 % bound) — the constant to measure. Q1 loop now tolerates non-convergence.

## Sensitivity — [[sensitivity_pulp.py]] → [[sensitivity_pulp.png]] (2026-09-13)
- `mass_balance.py` takes `PULP` and `GA_SCALE` env overrides and a `--json` flag (`key_metrics()`); the sweep runs it as a subprocess.
- **Pulp 2.5 → 10 % at INL's acid ratio:** only the water side moves — R-301 705 → 183 m³ each, evaporator 49 → 11 t/h, S-104 40 → 3.7 t/h. Fermenters (~250 m³), glucose (~660 kg/h), NaOH (~880 kg/h) and the **charge ratio (0.24–0.25) are flat**: acid demand is set by the solids, not the pulp.
- **Acid multiple 1–6× at 10 %:** charge ratio 0.24 → 0.92 at 6× (1.8 M); R-202 238 → 1,430 m³ each; glucose 640 → 3,840 kg/h; NaOH 867 → 1,566 kg/h; brine Na 639 → 1,041 kg/h. **S-104 goes negative above ~1.5×** — the broth alone brings more water than a 10 % pulp basis allows, so at higher acid the pulp basis must fall or the broth must be more concentrated.
- Reading: pulp density is a *water/CapEx* lever; charge balance is an *acid* lever, and the two are coupled only through the broth water. Neither proportional scaling nor pulp reduction closes the acid budget; only more acid per tonne (A at ~6×, or C) does.

## Option A re-basis (2026-09-13)
- Keshav chose **Option A** (gluconate supplies the whole anion budget). `GA_BALANCE=1` default; `GA_MM` solved for electroneutrality up front (before Block 3) since the fermenter is sized from it. `PULP` default 0.07, `BROTH_GA_GL` 250 (env-overridable). Hard error if broth > liquor. K-201 / R-201A/B now sized from R-202 working volume, not the old fixed 50 m³.
- New flags: `LI_CONC_FEASIBLE`, `NA_GLUC_GL` — E-501 cannot reach 25 g/L Li because S-512 is ~204 g/L Na-gluconate. Decision pending (recycle raffinate / Li₃PO₄ / gluconate destruction) — see [[Charge Balance Finding]].
- `sensitivity_pulp.py` pins `GA_BALANCE=0` so the sweeps keep the INL-shape basis they were plotted on.
- Index tables regenerated (blocks 1–6); notes 6, 9, 10, 11, 12, 17, 19, 21, 27, 28, 30 and the design-basis grid rewritten. [[thermo_results.txt]] re-run on the Option A liquor (see finding note for the pH result).

## Recycle-loop check + NaOH accounting fix (2026-09-13, late)
- Keshav chose to recycle the barren raffinate (S-512) to R-301. Before restructuring the balance, [[recycle_loop_check.py]] ran the proton/sodium budget of the loop with the gluconate buffer (pKa 3.86) at each unit's pH set-point. **Result: the raffinate returns at pH 6.5 as sodium gluconate with ~0 free acid** — it covers 0 % of the leach's proton demand, so fresh gluconic acid stays ~4.3 t/h. Na-gluconate solubility (~590 g/L → Na ≤ 62 g/L) forces a bleed ≥ 7.8 m³/h (recycle ≤ 65 %); Li in the bleed 5.5 g/L; broth + recycle water exceed the 7 % pulp liquor. Recycle buys water and Li concentration, not acid. A true acid loop needs bipolar-membrane electrodialysis to split Na-gluconate back into gluconic acid + NaOH.
- **Bookkeeping fix in `mass_balance.py`:** T-402 and the SX units had counted one NaOH per gluconate; the leach already deprotonates the gluconate that balances the metals. Base demand is now `naoh_to_hold(pH, …)` = what it takes to hold the set-point (`PH_FEAL` 5.5, `PH_MN_SX` 4.2, `PH_CO_SX` 5.5, `PH_NI_SX` 6.5) in the buffer. NaOH 1,650 → **844 kg/h**; brine Na 1,090 → **627 kg/h**.
- `GA_EXCESS = 1.15`: exact charge balance means zero free acid and an undefined pH, so the leach carries a 15 % gluconic-acid surplus → PLS pH ≈ 4.8, GA 1,532 mM, 5.0 t/h, glucose 4.8 t/h, R-202 575 m³ each, K-201 14,400 m³/h, S-104 make-up 1.7 t/h (T-101 ~43 % solids — pumpability flag).

## Li₃PO₄ route (2026-09-13, late) — Keshav's call
- Block 6 rewired: S-512 → **T-501 Li₃PO₄ precipitation** (Na₃PO₄ 10 % excess, 60 °C, 95 % yield; solubility 0.39 g/L so no evaporation needed at 1.9 g/L Li) → F-501 → S-515 Li₃PO₄ 228 kg/h (**1,821 t/yr**, 94 % of feed Li) · S-520 filtrate → **E-501 water-recovery evaporator** (to 500 g/L Na-gluconate; 9.1 t/h condensate) → S-516 brine 13.7 t/h to Sheet 6. Condensate return S-517 ≈ 10.4 t/h. New constants `LI_PPT_YIELD` 0.95, `PO4_EXCESS` 1.1, `NAGLUC_CONC_GL` 500; `LI_CONC_GL`/feasibility flag removed. Na₃PO₄ lumped in the `organics` column (placeholder — add a `PO4` column when Sheet 6 needs it).
- Sheet 5 redrawn (T-501 → F-501 → E-501 column); routing table + Index block 6 equipment and notes ㉗–㉚ updated; screenshot-checked. TEA must re-price lithium as phosphate, not carbonate.

## Area 600 / Sheet 6 balance (2026-09-13, end of day)
- `PO4` column added to every stream (Na₃PO₄ no longer lumped in organics). Block 7 in `mass_balance.py`: T-601 equalises brine + purges + SC-301 blowdown (S-601, 13.9 t/h) → D-601 dryer → S-602 exhaust 7.8 t/h H₂O + **S-603 crude sodium-gluconate salt 6.1 t/h (49 kt/yr; Na-gluconate 5.5 t/h)**. Bunkers X-601/602/603 for residue, Fe/Al cake, biomass (3/3/7 days). COD-if-treated 4.4 t/h O₂ printed for comparison. Na closure assert (NaOH + Na₃PO₄ in = salt Na out) and D-601 balance assert pass.
- **Water closure:** condensate 10.4 t/h → medium 8.3 + S-104 1.7 + surplus 0.5; fresh water **6.9 t/h** (medium top-up 5.8 + wash 1.6 − surplus); condensing the dryer exhaust (7.8 t/h) would make the plant water-neutral. Water out: product hydrates 1.0, cakes 0.7, salt 0.3, dryer exhaust 7.8 t/h.
- Index: Block 7 section added (equipment, generated sizing/streams, notes ㉛–㉝); PO₄ column in Blocks 6–7 tables. `html_rows(7)` works. **Sheet 6 drawing not started** — balance is complete for all seven blocks.

## 2026-09-13 (session 2) — Sheet 6 drawn, PFD complete

Area 600 was the last undrawn sheet. It is now on the page, so all six sheets
of the PFD exist and every stream in `mass_balance.py` appears somewhere on a drawing.

**Sheet 6 layout.** Two lanes.
- *Liquid effluent* — four off-sheet inlets (S-516 E-501 brine, S-518 Co crystalliser
  purge, S-519 Ni crystalliser purge, S-304 SC-301 scrubber blowdown) collect on a
  header into **T-601** (agitated, 8 h). S-601 goes to **D-601**, the crude-salt
  dryer. S-603 leaves as crude sodium gluconate salt at 5 % moisture; S-602 is the
  humid exhaust, drawn with a **dashed optional condenser** since condensing it
  (~7.8 t/h H₂O) makes the plant water-neutral.
- *Solid residues and by-product* — S-308 → X-601 (leach residue bunker, 3 d),
  S-408 → X-602 (Fe/Al cake bunker, 3 d), S-210 → X-603 (spent-biomass skip, 7 d),
  and S-403 cement copper to a drum for smelter sale.

**Corrections made while drawing.**
- Sheet 5 heading still said Li₂CO₃; now reads Li₃PO₄.
- Routing table: S-210 and S-304 pointed at Sheet 5; both now point at Sheet 6.
  S-601 / S-602 / S-603 added to the routing table.
- PFD eyebrow said "Sheets 1–5 of 6"; now "Sheets 1–6 of 6".
- Index Block 7 heading dropped "sheet not yet drawn".
- SC-301 blowdown destination in the Index corrected to Sheet 6 (S-304 → T-601).
- **Note ⑪ is no longer a placeholder.** It had said the 80 % / 15 % condensate
  split was provisional "until Sheet 6 closes the water balance". Sheet 6 closes it:
  condensate ~10.4 t/h covers the S-104 make-up and most of the medium, leaving
  ~6.9 t/h net fresh water, and the D-601 exhaust would cover that if condensed.

Balance re-run after all edits: clean, every assert passes.

**What is still open (not a drawing problem).**
- TEA has not been re-priced on the Li₃PO₄ product or the Na-gluconate by-product.
- The 49 kt/yr of crude salt at ~$0.6–0.9/kg is comparable to metal revenue. That
  needs an honest market check before it is booked as a credit.
- BMED remains the only real route to a closed acid loop; not modelled.
- Fluoride in the leach residue is still not modelled.

## Related scripts
- [[mass_balance.py]] — every stream and sizing
- [[li_upgrade.py]] — screening for on-site Li₃PO₄ → Li₂CO₃ / LiOH·H₂O conversion
- [[recycle_loop_check.py]] — proton/Na budget of raffinate recycle
- [[thermo_speciation.py]] — PHREEQC speciation

## 2026-09-13 (session 7) — Re-based at 150 g/L; crystalliser recycle fixed

Six decisions taken. Model, Index tables and Index prose all moved together.

**1. Broth titer 250 → 150 g/L, pulp 7 % → 4.2 %.** The 250 g/L basis had no
literature support; 150 g/L is the documented high for *G. oxydans* [9]. 250 g/L
survives only as an upside case (`BROTH_GA_GL=250 PULP=0.07`).

**2. Crystalliser mother liquor now recycles.** The model used to purge (1 − yield).
It now recycles with a 5 % bleed, and per-pass yield is set to the measured 86 % [14]
instead of the unsourced 97 %. Because the *bleed* sets the loss, overall recovery is
99.2 % — better than the old 97 %, so **recovery went up, not down**:

| | before | after |
|---|---|---|
| Co to product | 78.1 % | **80.3 %** |
| Ni to product | 76.3 % | **78.4 %** |
| Li to product | 93.6 % | **94.1 %** |

A self-check was added: a literal stage-by-stage recycle simulation must converge to the
closed form `y/(y+(1−y)b)`, or the run fails.

**3–5.** pKa held at 3.86 by decision, with the Merck/Ullmann 3.70 recorded next to it.
Cyanex 272 window corrected to the measured 5.3 / 7.0 [12]. Li₃PO₄ conversion dropped.

**What the re-base costs**

| | 250 g/L @ 7 % | 150 g/L @ 4.2 % |
|---|---|---|
| R-202 fermenter | 575 m³ each | **962 m³ each** |
| R-301 leach | 318 m³ each | **483 m³ each** |
| E-501 evaporator | 9.1 t/h | **20.9 t/h** |
| Condensate returned | 10.4 t/h | 22.2 t/h |
| Gluconate in liquor | 1,530 mM | 896 mM |

The evaporator more than doubles and the fermenter now exceeds normal industrial scale
(100–300 m³), so R-202 is a multi-train unit. One thing improved: T-101 is no longer a
43 % solids paste, which retires the pumpability flag.

**6. Prices — see [[Product Pricing — Cited Basis]].** Salt assessments are paywalled and
no agency assesses Li₃PO₄ at all, so revenue is quoted as a **floor of $46.2–58.1M/yr** on
contained metal at USGS benchmarks. Lithium is ~10 % of revenue, not the 25 % the void TEA
implied. Cobalt is ~49 % and carries the price risk.
