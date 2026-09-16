# Zero-Discharge Bioleaching of Spent Lithium-Ion Black Mass

### Process Design and the Cost of a Biological Lixiviant

Process design for a **10,000 t/yr spent lithium-ion black-mass refinery** using a
*Gluconobacter oxydans* gluconic-acid biolixiviant in place of mineral acid.

## ▶ Start here

**[Black Mass BioLeach Summary.pdf](Black%20Mass%20BioLeach%20Summary.pdf)** — the paper.
Read this first; it is the whole argument in eight pages, references included.

Everything else in this repository is the **appendix** to that paper: the detail a reader
might want to check, reproduce or argue with. Folders are lettered to match, so where the
paper cites "Appendix G" the reader opens `G-mass-balance/`.

## Results

| | |
|---|---|
| Feed | 10,000 t/yr black mass · Ni 18 %, Co 8 %, Mn 5 %, Li 3.5 %, Cu 2 %, Al 3 % |
| Biolixiviant | gluconic acid, 150 g/L broth, 4.2 % pulp, charge-balanced leach at pH ≈ 4.8 |
| **Cobalt to product** | **80.3 %** · 3,065 t/yr CoSO₄·7H₂O |
| **Nickel to product** | **78.4 %** · 6,324 t/yr NiSO₄·6H₂O |
| **Lithium to product** | **94.1 %** · 1,831 t/yr Li₃PO₄ |
| Liquid discharge | none — the only bleed is dried to a crude sodium-gluconate salt |
| Fresh water | 6.9 t/h; condensing the dryer exhaust would close the balance |
| Fixed capital | ≈ $118M, Class 5 |
| Operating cost | $33–47M/yr |
| Revenue floor | $46–58M/yr on contained metal at USGS benchmarks |

Recoveries are **metal in feed to bagged product** and carry every downstream loss. Leach
extraction figures in the literature are measured at a much earlier boundary and are not
comparable.

The route is not yet cheaper than conventional hydrometallurgy; it is already cleaner.
Gluconic acid costs eleven to twenty-seven times more per equivalent of acidity than
sulfuric, and glucose is 53 % of operating cost. Corn stover hydrolysate as the carbon
source and electrodialytic acid recycle would remove roughly $29M/yr of that gap.

## Appendix map

| | Folder | Contents |
|---|---|---|
| **A** | `A-process-flow-diagram/` | The **unified flowsheet** — all six areas on one drawing with the inter-area streams actually connected (1235 × 712 mm) — plus the six-sheet PDF for reading, and the HTML sources |
| **B** | `B-design-basis/` | Feed, products, the electroneutrality constraint, set-points, water closure |
| **C** | `C-equipment-list/` | Every unit with its size and sizing basis, CSV |
| **D** | `D-stream-tables/` | Every stream, Blocks 1–7, CSV; key model parameters |
| **E** | `E-process-notes/` | The PFD Index as **PDF** and HTML: equipment, sizing, streams and notes ①–㉝ per block, references |
| **F** | `F-thermodynamics/` | PHREEQC speciation of the leach liquor, the USGS database it uses, and its output |
| **G** | `G-mass-balance/` | The model itself, the CSV exporter, and the pulp-density sensitivity |
| **H** | `H-acid-recycle/` | Proton and sodium budget showing why raffinate recycle returns water but not acid |
| **I** | `I-cost-estimate/` | Capital, operating cost, revenue, acid cost per equivalent, and what narrows the gap |
| **J** | `J-unsourced-assumptions/` | Every number carried without a verified source, and every price |
| **K** | `K-references/` | The bibliography, [1]–[28], IEEE style — the numbering the paper uses |

Two forms of the same drawing. **`bioleach_PFD_unified.pdf`** is the whole plant as one continuous
flowsheet: the areas sit in process order, each inside a dashed boundary, and the streams that would
otherwise say "to Sheet 4" are drawn as real routed lines. Solid lines carry the main flow, dashed are
recycles, dotted are solids and bleeds. **`bioleach_PFD.pdf`** is the same content split one area per
page, which is easier to read at desk size.

`tools/build_unified_pfd.py` rebuilds the unified drawing from the per-sheet source. It asserts that no
connector is drawn diagonally and that none runs through another area's drawing, so a layout change that
would produce a misleading sheet fails the build instead. `tools/make_pdfs.py` regenerates the per-sheet PDFs.

## Two classes of number

**From the balance.** Every stream, equipment size and recovery. `G-mass-balance/mass_balance.py`
asserts elemental closure across every unit, a plant-wide sodium balance, the crystalliser
recycle algebra, and that the broth never carries more water than the leach liquor can hold.
An infeasible basis fails the run rather than producing a plausible wrong answer.

**Estimated.** Everything in `I-cost-estimate/` with a dollar sign. Equipment cost anchors,
reagent and utility prices and the Lang factor are named constants at the top of each script
so a reader can substitute a quotation and re-run. The cost *structure* is therefore far more
robust than the totals.

## Running it

```bash
pip install -r requirements.txt
python3 G-mass-balance/mass_balance.py            # full balance; every assert must pass
python3 G-mass-balance/mass_balance.py --html 3   # regenerate the Index tables for one block
python3 G-mass-balance/export_tables.py           # refresh the CSVs in C/ and D/
python3 I-cost-estimate/opex.py                   # operating cost against the revenue floor
python3 tools/make_pdfs.py                        # re-render both PDFs
```

The basis can be varied through environment variables, for example
`BROTH_GA_GL=200 PULP=0.055 python3 G-mass-balance/mass_balance.py`.

## Status

Design complete and internally consistent: six sheets drawn, balance closed, basis cited,
costs estimated. Not built, not piloted, not independently reviewed.

## Licence

MIT, see `LICENSE`. The PHREEQC database in `F-thermodynamics/` is USGS work under its own terms.
