# Black-Mass Bioleaching Refinery

Conceptual process design for a **10,000 t/yr spent lithium-ion black-mass refinery**
built on a *Gluconobacter oxydans* gluconic-acid biolixiviant, rather than the mineral
acids used in conventional hydrometallurgy.

This repository holds the engineering: a six-sheet process flow diagram, a mass balance
that closes across all seven blocks, PHREEQC speciation of the leach liquor, and a
design basis in which every load-bearing number is either cited or explicitly marked
as unsourced.

---

## Results at the current basis

| | |
|---|---|
| Feed | 10,000 t/yr black mass (Ni 18 %, Co 8 %, Mn 5 %, Li 3.5 %, Cu 2 %, Al 3 %) |
| Biolixiviant | gluconic acid, 150 g/L fed-batch broth, 4.2 % pulp |
| **Cobalt to product** | **80.3 %** — 3,065 t/yr CoSO₄·7H₂O |
| **Nickel to product** | **78.4 %** — 6,324 t/yr NiSO₄·6H₂O |
| **Lithium to product** | **94.1 %** — 1,831 t/yr Li₃PO₄ |
| Liquid discharge | **none** — the only bleed is dried to a crude sodium-gluconate salt |
| Fresh water | 6.9 t/h, and the dryer exhaust would cover even that if condensed |
| Revenue floor | $46.2M – $58.1M/yr (contained metal at USGS benchmarks) |

Recoveries are quoted **metal in feed to bagged product**, so they carry every loss
through leaching, iron removal, solvent extraction, crystallisation and filtration.
Leach-extraction figures quoted elsewhere in the literature are measured at a much
earlier boundary and are not comparable.

## Repository map

This repository **is the appendix** to the write-up. `docs/appendix-index.md` maps every
appendix section to the file that holds it.

```
src/   -- balance and chemistry: quantities, not estimates
       mass_balance.py       every stream and equipment size; the single source of truth
       thermo_speciation.py  PHREEQC speciation of the leach liquor
       export_tables.py      writes the stream/equipment CSVs in data/streams/
       sensitivity_pulp.py   pulp-density sweep
       recycle_loop_check.py proton and sodium budget for raffinate recycle

       -- economics: the METHOD is standard, the PRICES are estimates
       capex.py              Class 5 factored capital estimate
       opex.py               annual operating cost against the revenue floor
       acid_cost.py          gluconic vs sulphuric, per equivalent of acidity
       levers.py             what would close the cost gap
       revenue_floor.py      revenue on cited prices only
       li_upgrade.py         Li3PO4 conversion screening (header marks its prices void)

pfd/   bioleach_PFD_v2.html      six-sheet process flow diagram
       bioleach_PFD_index.html   equipment, sizing, stream tables, notes, references
data/  minteq.v4.dat             PHREEQC thermodynamic database (USGS)
       thermo_results.txt        speciation output
       streams/*.csv             machine-readable stream and equipment tables
docs/  appendix-index.md         what the paper's appendix letters point at
       charge-balance-findings.md  the findings that changed the flowsheet
       mass-balance-log.md       block-by-block build log
       product-pricing.md        prices, and why most of them cannot be cited
       waste-streams.md, software-build-order.md
```

**Every script in `src/` that prints a dollar sign carries estimated prices**, named as
constants at the top of the file so they can be replaced with quotes. Quantities always
come from the balance. The cost *structure* is therefore much more robust than the
totals — see `docs/appendix-index.md`.

## Running it

```bash
pip install -r requirements.txt
python3 src/mass_balance.py            # full balance; every assert must pass
python3 src/mass_balance.py --html 3   # regenerate the Index tables for one block
python3 src/export_tables.py           # refresh data/streams/*.csv
```

The balance is self-checking. It asserts elemental closure across every unit, a
sodium balance over the whole plant, the crystalliser recycle algebra, and that the
fermenter broth never carries more water than the leach liquor can hold. **If an
assumption is edited into an infeasible combination, the run fails rather than
quietly producing a wrong answer.** The 120 g/L broth case fails exactly this way.

Two environment variables switch the basis:

```bash
BROTH_GA_GL=250 PULP=0.07 python3 src/mass_balance.py   # the retired upside case
GA_BALANCE=0 python3 src/mass_balance.py                # pre-charge-balance basis
```

## What the design actually turns on

Three findings shaped the flowsheet more than anything else, and each is written up in
`docs/charge-balance-findings.md`:

1. **The leach does not charge-balance on the published acid dose.** Scaling the source
   paper's gluconate concentration to this pulp density leaves a four-fold anion deficit.
   Gluconate is now solved for electroneutrality instead, which is what sets the broth
   requirement and therefore the size of the whole fermentation section.
2. **Raffinate recycle returns no acid.** Every equivalent of metal removed downstream
   converts gluconic acid to sodium gluconate, so the raffinate comes back at pH 6.5 with
   essentially no free acid. A true closed acid loop needs bipolar-membrane electrodialysis.
3. **The broth titre sets the pulp density, and 250 g/L is not supported.** The literature
   high for *G. oxydans* gluconic acid is about 150 g/L. Re-basing there roughly doubles the
   evaporator duty and pushes the fermenters past normal industrial scale.

## Honesty about the numbers

`pfd/bioleach_PFD_index.html` carries a section headed *numbers that are not sourced*.
It lists, among others, the iron(III)–gluconate stability constant, the Li₃PO₄ solubility,
and the 2 % co-precipitation loss. **No agency assesses a Li₃PO₄ price**, so revenue is
quoted as a floor on contained metal rather than on product sales. Ordinary engineering
practice — tank residence times, pump sparing, silo hold-up — is deliberately uncited.

See `REFERENCES.md` for the bibliography in IEEE format.

## Economics, in one line

Approximately **$118M** fixed capital and **$33–47M/yr** operating cost against a
**$46–58M/yr** revenue floor. Glucose is 53 % of operating cost, because gluconic acid
costs **eleven to twenty-seven times more per equivalent of acidity** than sulphuric:
it is monoprotic, heavy, and bought as food-grade sugar, where sulphuric is diprotic,
light, and made from a waste stream. Switching to corn stover hydrolysate and recycling
the acid by electrodialysis would remove roughly $29M/yr of that. The route is **not yet
cheaper than conventional hydrometallurgy; it is already cleaner.**

## Status

Design is complete and internally consistent: six sheets drawn, balance closed, basis
cited, costs estimated. Not built, not piloted, and not independently reviewed.

## Licence

MIT, see `LICENSE`. The PHREEQC database in `data/` is USGS work and carries its own terms.
