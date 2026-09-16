# Appendix Index

The write-up is the front page and the summary. **This repository is the appendix.**

Appendices A and B are also provided as **PDFs** (`pfd/*.pdf`) for attaching to the paper;
the HTML sources sit beside them and stay the editable originals. Regenerate with
`python3 src/make_pdfs.py`.
Anything a reader wants to check, reproduce or argue with lives here.

Sections are lettered so the paper can cite them as "Appendix C" without needing the
tables reproduced inline.

| | Appendix section | Where it lives |
|---|---|---|
| **A** | Process flow diagram, six sheets | **`pfd/bioleach_PFD.pdf`** (HTML source alongside) |
| **B** | Design basis and assumptions | **`pfd/bioleach_PFD_index.pdf`**, top section |
| **C** | Equipment list with sizing basis | `data/streams/equipment.csv`, and per block in the Index |
| **D** | Stream tables, Blocks 1–7 | `data/streams/streams.csv`, and per block in the Index |
| **E** | Numbered process notes ①–㉝ | `pfd/bioleach_PFD_index.html`, per block |
| **F** | Thermodynamic speciation | `src/thermo_speciation.py`, `data/thermo_results.txt` |
| **G** | Mass balance model and self-checks | `src/mass_balance.py` |
| **H** | Design findings that changed the flowsheet | `docs/charge-balance-findings.md` |
| **I** | Block-by-block build log | `docs/mass-balance-log.md` |
| **J** | Capital and operating cost estimate | `src/capex.py`, `src/opex.py`, `src/levers.py`, `src/acid_cost.py` |
| **K** | Product pricing and its limits | `docs/product-pricing.md`, `src/revenue_floor.py` |
| **L** | Waste streams and effluent | `docs/waste-streams.md` |
| **M** | Numbers that are **not** sourced | `pfd/bioleach_PFD_index.html`, end of the References section |
| **N** | References, [1]–[28] | `REFERENCES.md` |

## Two classes of number, and the difference matters

**Rigorous.** Everything produced by `mass_balance.py` — every stream, every equipment
size, every recovery. These come from a balance that closes, with asserts on elemental
closure, the sodium balance, the crystalliser recycle algebra, and the broth-water
constraint. Quantities are not estimates.

**Estimated.** Everything in Appendix J and K that carries a dollar sign. Equipment cost
anchors, reagent and utility prices, the Lang factor. The *method* is standard and citable;
the *absolute numbers* are Class 5, minus 50 / plus 100 per cent. Every price is exposed as
a named constant at the top of its script so a reader can substitute a quote and re-run.

The consumption quantities those costs multiply are from the rigorous set. So the cost
*structure* — that glucose is 53 % of operating cost, that gluconic acid runs eleven to
twenty-seven times sulphuric per equivalent of acidity — is far more robust than the
totals. That structure is the paper's economic argument, and it survives a large error
in any individual price.

## Not in this repository

The Google Doc write-up, the project management notes, the retired techno-economic
analysis (withdrawn as unsourced), and the market and strategy material. Those are
working documents, not part of the record a reader should check the design against.
