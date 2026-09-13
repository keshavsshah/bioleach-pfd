---
aliases: [Waste Streams, Effluent Treatment, Waste Streams & Effluent Treatment]
---

# ♻️ Waste Streams & Effluent Treatment

> What actually has to be treated at the back end of the gluconic-acid bioleach, species by species.
> Created **2026-09-05** from a full read of the INL manuscript (INL/JOU-22-70203, *J. Cleaner
> Production* **382**, 135274). Hub: [[Bioleaching-MOC]] · Paper notes: [[INL 2022 Paper — Figures, Fermentation Precedent & Industry Status]] · Feeds: [[Bioleaching TEA — Guide & Progress]]

> [!warning] Sourcing
> **The paper does not do a waste inventory.** Its system boundary stops at *solubilized* metals;
> downstream separation into salable salts is explicitly out of scope. Only three waste-relevant
> numbers appear in it at all (wastewater mass, a lump waste-management cost, and lignin combustion).
> **Everything else below is standard hydrometallurgy applied to their stated conditions** — treat it
> as engineering reasoning to be verified, not as reported results.

## What the paper actually reports

| Item | Value | Where |
|---|---|---|
| **Wastewater** | **183–216 kg per kg Co recovered** | LCA inventory — the largest mass flow in the study; bioleaching + biolixiviant production combined. Treatment assumed, never modeled. |
| **Waste management cost** | **$1.08M/yr** (~3% of OpEx) | From a generic water/wastewater escalation reference, not a stream-specific estimate |
| **Lignin residue** (corn stover) | Not treated as waste — **burned** for heat/power | Reported surplus of **251 kWh per tonne** sodium gluconate |
| Iron sulfate dose | **3.75–4.51 kg per kg Co**, 10% of OpEx | LCA inventory + cost breakdown |

Leach conditions for reference: **75 mM gluconic acid, 2.5% pulp density, 55 °C, 30 h, FeSO₄ reductant.**
Recoveries **Co 86% · Ni 84% · Li 100% · Mn 100%.**

---

## 1. Iron — the dominant treatment burden

### It ends as Fe(III), not Fe(II)
Fe²⁺ is **not a spectator** — it is consumed. Its function is reducing **Co³⁺ → Co²⁺** (and Mn⁴⁺ → Mn²⁺)
in the layered oxide so those metals will dissolve; the paper's Eq. 1 has Fe²⁺ → Fe³⁺ stoichiometrically.
So the pregnant leach solution (PLS) carries **Fe³⁺**, plus whatever Fe²⁺ was dosed in excess and never reacted.

### Why the order of operations is forced
| Species | Hydrolysis / precipitation pH |
|---|---|
| Fe³⁺ | **~3 – 3.5** |
| Fe²⁺ | **~8** |
| Co²⁺, Ni²⁺ | **~8** |

You **cannot** simply neutralize the whole liquor — Fe²⁺ comes out in the same window as the products
and you lose cobalt into the iron sludge. The forced sequence is:

1. **Oxidize residual Fe²⁺ → Fe³⁺** (air sparge or H₂O₂)
2. **Precipitate all iron at low pH** as goethite / ferrihydrite / jarosite
3. **Then** recover Co/Ni

**Iron removal happens *before* metal recovery, not at the end.**

### Scale
At **3.75–4.51 kg iron sulfate per kg Co**, the iron input is the **same order of mass as the product
itself**. Output is a bulky, wet, poorly-filtering **Fe(III) hydroxide sludge** that also **occludes some
Co/Ni** on the way down — a second recovery loss on top of the 14% Co / 16% Ni left in the leach residue.

### ⚠️ The non-obvious risk: gluconate chelates Fe(III)
**Gluconic acid is used industrially *as an iron sequestrant*** — it keeps Fe soluble at pH values where it
would otherwise precipitate. **The lixiviant that makes this process work actively fights the iron removal
step.** Likely consequence: the organics must be destroyed *first* (wet-air oxidation, ozone, or biological
COD removal) before iron will drop cleanly.

> **This is the biggest engineering risk in the route and it appears nowhere in the paper.** If the
> gluconate–Fe³⁺ complex is strong at process pH, the "mild organic acid" advantage is partly paid back
> as an extra oxidation stage.

---

## 2. Everything else in the spent liquor

| Species | Source | Why it needs treatment | Likely route |
|---|---|---|---|
| **Gluconate + organics** | The lixiviant itself (75 mM), plus 2-ketogluconate, acetate, residual sugars, cell debris | **High COD** — the bulk of the 183–216 kg/kg-Co wastewater | Aerobic biological treatment. **Readily biodegradable — the genuine advantage over mineral-acid raffinate** |
| **Sulfate** | Every kg of FeSO₄ brings it; nowhere to go | Discharge-limited in most jurisdictions | Lime neutralization → **gypsum (CaSO₄·2H₂O)**, a second bulk solid waste |
| **Phosphate** | **Pikovskaya medium is phosphate-based** | Eutrophication-regulated | Chemical P removal; also precipitates metal phosphates |
| **Ammonium / N** | Growth medium | Nutrient discharge limits | Nitrification/denitrification |
| **Calcium** | Listed as an LCA input to biolixiviant production | Scaling; drives gypsum load | — |
| **Al³⁺** | Residual Al current-collector fines in black mass | **Gelatinous hydroxides blind filters and form crud in solvent extraction** | Hydrolytic precipitation with the iron |
| **Cu²⁺** | Residual Cu current-collector fines | **Poisons Co/Ni recovery** — more strongly extracted than either | Cementation or sulfide precipitation, ahead of Co/Ni |
| **Fluoride / HF** | **LiPF₆ electrolyte hydrolysis + PVDF binder** | Corrosive, discharge-limited | Lime → **CaF₂**. Severity depends on how well pretreatment washed the black mass |
| **Manganese** | 100% dissolved, low value | **If not sold, it is a waste stream** — and awkward to remove | Oxidation to MnO₂ or high-pH precipitation |

**Nutrients are easy to overlook** because they arrive as "just growth medium" — but phosphate and
ammonium removal is a real, separately-regulated duty on the fermentation side of the plant.

---

## 3. Solids and gas

- **Leach residue** — graphite (largest single solid), PVDF binder, **unleached cathode carrying ~14% of the
  Co and ~16% of the Ni**, plus Al/Cu fines. Graphite is potentially salable if cleaned.
  → This is simultaneously the **largest value loss** and a disposal question. See the TEA note: cobalt is
  **46% of revenue on 8% of feed mass**, so residue Co is worth chasing.
- **Spent *G. oxydans* biomass** — from the 0.22 µm filtration. Small, benign, digestible.
- **Off-gas** — CO₂ from fermentation; volatile electrolyte carbonates (EC/DMC) if pretreatment didn't strip them.
- **Lignin residue** — burned for energy, not landfilled (per the paper).

---

## The one-line takeaway

> **The iron dose is what converts an elegant mild-acid leach into a conventional-looking hydromet plant** —
> with an oxidation stage, a precipitation circuit, an iron sludge, and a gypsum stream. That, plus the
> **gluconate–Fe³⁺ chelation conflict**, is where to push if the TEA restarts.

## Where this feeds

- **[[Bioleaching TEA — Guide & Progress]] — Step 1 (CapEx)**, which is exactly where this stopped. The unit
  operations implied here — Fe oxidation + precipitation, residue handling, COD/nutrient treatment, gypsum —
  are all unpriced, and the paper gives **no basis** for any of them.
- **Step 0 revisit:** the model assumed 86% Co recovery. This confirms that is the paper's **optimum under
  optimized lab conditions**, not a floor — and the residue + iron-sludge occlusion both pull it down.

## Related

- [[Bioleaching-MOC]] · [[INL 2022 Paper — Figures, Fermentation Precedent & Industry Status]]
- [[Bioleaching TEA — Guide & Progress]] · [[Stream Table]] · [[Process Flow Diagram]]
- [[Q1 — Heterotroph vs Chemoautotroph Break-Even]]
