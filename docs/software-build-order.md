# Software Coupling & Build Order

**Type:** Modeling plan · **Status:** v1 · **Updated:** 2026-06-23

> How to turn [[Process Flow Diagram]] into a multistep model across tools. Each step's exported interface variables are the inputs to the next. Numbered streams (S1–S21 in [[Stream Table]]) are the hand-off points.

## Coupling table
| # | Tool | Computes | Exports (interface variables) |
|---|---|---|---|
| 1 | **Python — kinetics** | Microbial growth, Fe/S bio-oxidation, shrinking-core leach | Extraction X_i(t), residence time τ, O₂ uptake |
| 2 | **PHREEQC / OLI** | PLS speciation; Fe/Li precipitation equilibria; activities | Free-ion activities, Eh, pH, saturation indices |
| 3 | **Ansys Fluent / M-Star CFD** | Reactor hydrodynamics: kLa, solids suspension, shear | kLa, mixing time, N_js → back to Python + sizing |
| 4 | **Aspen + OLI MSE** | SX stage equilibria (Cu, Mn, Co/Ni, Ni polish) | Stage counts, raffinate purities, reagent flows |
| 5 | **PipeFlo** | Slurry/solution hydraulics: line sizing, pump duty, ΔP, NPSH | Pump kW, pipe spec, valve Cv → CapEx/OpEx |
| 6 | **SuperPro / BioSTEAM** | Global mass-energy balance, equipment sizing, TEA | Stream table, utilities, $/kg, NPV/IRR |
| 7 | **openLCA** | Life-cycle inventory & impact | CO₂eq/kg metal vs pyromet/hydromet |

## Build sequence
1. **Python** — fit growth + shrinking-core kinetics to bench data → sets S5 extraction and C-1 residence time/volume.
2. **PHREEQC/OLI** — speciate S7 (PLS) → feed spec for every separation; closes acid/Fe chemistry.
3. **Ansys / M-Star CFD** — verify kLa, solids suspension, shear in B-2 and C-1; loop kLa back to Python ([[Q2 — kLa at High Pulp Density]]).
4. **Aspen + OLI MSE** — stage counts + raffinate purities for E-2, F-1, **F-2 (Cyanex 272 Co/Ni split)**, F-3 ([[Q3 — Fe & TOC Carryover to Spec]]).
5. **PipeFlo** — size every edge (slurry/solution lines, pumps, recycle loops S21 + Fe regen).
6. **SuperPro / BioSTEAM** — global balance, equipment sizing, TEA; reconcile against [[Stream Table]] and [[Microbe & Break-Even Model]].
7. **openLCA** — cradle-to-gate CO₂eq/kg from the SuperPro inventory.

## Related
- Maps onto the nine layers in [[Modeling Roadmap]].
- [[Process Flow Diagram]] · [[Stream Table]]
