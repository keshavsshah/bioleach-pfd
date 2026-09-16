"""Black-mass bioleach mass balance: one row per PFD stream, plus equipment sizing.

Basis: 10,000 t/yr black mass, 8,000 h/yr. Gluconate is solved for electroneutrality of the
leach liquor (896 mM at a 150 g/L broth, 4.2 % pulp). Every block asserts closure; an
infeasible basis raises SystemExit rather than producing a plausible wrong answer.

Run:  python3 G-mass-balance/mass_balance.py           full balance and equipment list
      python3 G-mass-balance/mass_balance.py --html N  Index tables for block N
See B-design-basis/ for the basis and I-cost-estimate/ for the economics.
"""
import os, json
import pandas as pd

# ---- basis -----------------------------------------------------------------
FEED_TPY = 10_000
HOURS = 8_000
FEED_KGH = FEED_TPY * 1000 / HOURS          # 1,250 kg/h
# Gluconate supplies the whole anion budget: a charge-balanced leach liquor with no mineral acid.
# GA_BALANCE=1 solves GA_MM for electroneutrality; GA_BALANCE=0 restores the INL pulp-scaled basis (sensitivity runs).
GA_BALANCE = os.environ.get("GA_BALANCE", "1") == "1"
PULP = float(os.environ.get("PULP", 0.042 if GA_BALANCE else 0.10))   # 4.2 % = max that fits a 150 g/L broth   # kg solid / kg slurry in R-301. The ceiling is set by the broth, not chosen:
#   pulp at which a 250 g/L broth can carry the required gluconate without negative make-up water (see water check below).
GRADE = dict(Ni=.18, Co=.08, Mn=.05, Li=.035, Cu=.02, Al=.03)   # wt fraction of black mass
GRADE["other"] = 1 - sum(GRADE.values())     # graphite, binder, oxide O — 0.605
LEACH_REC = dict(Co=.86, Ni=.84, Li=1.0, Mn=1.0)                # INL 2022, leach step only

# Area 200 — biolixiviant
INL_PULP, INL_GA_MM = 0.025, 75          # INL demonstrated condition
GA_SCALE = float(os.environ.get("GA_SCALE", 1.0))   # extra acid multiple on top of the pulp scaling (sensitivity runs)
GA_MM_INL = INL_GA_MM * PULP / INL_PULP * GA_SCALE   # reference-shape basis: acid scaled with pulp density
GA_MW, GLU_MW = 196.16, 180.16
# Broth strength: the reference lab broth is ~80 g/L. A charge-balanced leach needs a concentrated broth;
# from ~300 g/L glucose (industrial gluconic-acid fermentation; placeholder to cite). Env BROTH_GA_GL overrides.
BROTH_GA_GL = float(os.environ.get("BROTH_GA_GL", 150.0 if GA_BALANCE else 80.0))
# 150 g/L is the highest titre reported for G. oxydans gluconic acid.
# Higher titres can be explored with e.g. BROTH_GA_GL=200 PULP=0.055.
GLU_YIELD = 0.95           # mol GA / mol glucose
CELLS_WET_KGH = 40.0       # spent biomass, wet cake, per hour of broth
AIR_VVM = 0.5              # sparge rate on the working volume, one fermenter running at a time
RECYCLE_FRAC = 0.80        # share of medium water supplied by returned raffinate (placeholder until Area 400)
BLEED_FRAC = 0.15          # share of returned raffinate bled to effluent (sulfate / Na control)

# Area 300 — leach
FESO4_PER_CO = 4.1         # kg FeSO4.7H2O per kg Co recovered (INL 3.75-4.51)
# Cu/Al are not reported in the reference work. From the literature:
#   Cu: gluconic acid alone 0.3 % (Lerchbammer 2025, H2O2 system) but with Fe3+ present metallic Cu is consumed as a
#       reductant (Porvali 2020; Partinen 2024) and organic-acid bioleaching reaches 100 % Cu (Bahaloo-Horeh 2017).
#       -> 0.80 for an Fe(II)/Fe(III) system at 55 C. Sensitivity: 0.3-1.0.
#   Al: 51.9 % (Lerchbammer 2025), 65-75 % (Horeh 2016; Bahaloo-Horeh 2017) -> 0.60.
# thermo_speciation.py: no solubility ceiling on Cu or Al at leach pH 2.5-3.0 (tenorite SI -2.6, gibbsite SI -0.5),
# so both fractions are kinetic, not thermodynamic -> literature values stand. Gibbsite saturates above pH ~3.2.
LEACH_FRAC = dict(Co=.86, Ni=.84, Li=1.0, Mn=1.0, Cu=.80, Al=.60, other=0.0)
CU_REDUCTANT_CREDIT = False  # sensitivity only: metallic Cu gives 2 e-/atom via Fe3+ (Porvali 2020). OFF by default because
                             # INL's 4.1 kg/kg ratio was measured on real black mass that already contained Cu (double count).
LI_AS_CARBONATE = 0.30     # share of Li present as Li2CO3 -> CO2 on acid contact (placeholder)
CAKE_MOISTURE = 0.30       # wt fraction liquid in filter cake
WASH_RATIO = 2.0           # m3 wash water per t dry residue
WASH_EFF = 0.95            # fraction of PLS displaced from the cake by the wash
LEACH_T = 55

# Area 400 - impurity removal: cementation, NaOH neutralisation, D2EHPA SX for Mn
CEM_CU_REMOVAL = 0.99      # Cu2+ + Fe -> Cu + Fe2+
CEM_FE_EXCESS = 1.3        # Fe powder dosed vs stoichiometric; excess reports to the cement cake
FE_AL_PH = 5.5             # thermo_speciation.py: goethite complete by 5.5, gibbsite mostly, Co/Ni still dissolved
OCCLUSION = dict(Co=.02, Ni=.02)      # placeholder: Co/Ni lost into the goethite/gibbsite cake
FE_AL_CAKE_MOISTURE = 0.60
MN_SX_EXTRACTION = 0.98    # D2EHPA, 2 stages, pH 3.0
MN_SX_CO_COEXTRACT = 0.02  # placeholder Co loss to the Mn circuit
MN_STRIP_GL = 100.0        # g/L Mn in strip liquor (MnSO4 product)

# Area 500 — products (Co SX Cyanex 272, Ni SX Versatic 10, crystallisers, Li3PO4, water-recovery evaporator)
CO_SX_EXT, CO_SX_NI_COEXT, CO_STRIP_GL = 0.99, 0.01, 100.0
NI_SX_EXT, NI_STRIP_GL = 0.98, 100.0
COSO4_7H2O, NISO4_6H2O, LI2CO3 = 281.1, 262.8, 73.89
CRYST_YIELD = 0.86                    # per pass, measured; Zhang et al., Hydrometallurgy 208 (2022) 105821
CRYST_BLEED = 0.05                    # fraction of mother liquor bled to Sheet 6; the rest recycles to the feed
# Overall recovery with mother-liquor recycle. Steady state on combined feed C = F + (1-y)(1-b)C gives
# P/F = y / (y + (1-y)b) -- so the BLEED, not the per-pass yield, sets how much metal is lost.
CRYST_REC = CRYST_YIELD / (CRYST_YIELD + (1 - CRYST_YIELD) * CRYST_BLEED)
# Li is recovered as Li3PO4 directly from the barren liquor (~1.9 g/L Li). Li3PO4 solubility ~0.39 g/L
# (= 0.07 g/L Li), so no evaporation is needed ahead of the precipitation; E-501 becomes a water-recovery evaporator.
LI_PPT_YIELD = 0.95                   # Li3PO4 with Na3PO4, 10 % excess, 60 C (residual ~0.1 g/L Li)
PO4_EXCESS = 1.10
NAGLUC_CONC_GL = 500.0                # E-501 concentrates the Li-free barren to ~500 g/L Na-gluconate (solubility ~590 at 25 C)
BRINE_BLEED = 1.0                     # all of the Na-gluconate brine leaves to Sheet 6 (no salty return to the fermenter)

SOLIDS = list(GRADE)
LIQ = ["H2O", "GA", "glucose", "organics", "Fe", "SO4", "Na", "Ca", "PO4"]
GAS = ["air", "CO2"]
COLS = SOLIDS + LIQ + GAS
streams = {}

def stream(no, frm, to, phase, T=25, **comp):
    """comp: kg/h of each component; total is derived."""
    row = dict(frm=frm, to=to, phase=phase, T=T, **{c: comp.get(c, 0.0) for c in COLS})
    row["total"] = sum(row[c] for c in COLS)
    streams[no] = row
    return row

# ---- Block 1: receiving ----------------------------------------------------
solids = {s: FEED_KGH * f for s, f in GRADE.items()}
stream("S-101", "OSBL", "V-101", "dry solid", **solids)
stream("S-102", "V-101 vent", "F-101", "gas+dust")            # no net mass flow (fines return)

# ---- Acid budget: gluconate required for electroneutrality ----
# Cations set by feed x leach fractions (+ Fe(III) from FeSO4); anions = gluconate + sulfate from FeSO4. Solved before Block 3
# because the fermenter is sized from it. Fixed by feed chemistry, so the kg/h of gluconate is independent of pulp density.
Z = dict(Co=2, Ni=2, Mn=2, Li=1, Cu=2, Al=3)
MW = dict(Co=58.93, Ni=58.69, Mn=54.94, Li=6.94, Cu=63.55, Al=26.98)
_feso4 = FESO4_PER_CO * solids["Co"] * LEACH_FRAC["Co"]
_fe_in, _so4_in, _hyd = _feso4 * 55.85/278.0, _feso4 * 96.06/278.0, _feso4 * 126.1/278.0
cation_keq = sum(solids[m] * LEACH_FRAC[m] / MW[m] * Z[m] for m in Z) + _fe_in / 55.85 * 3
_liq_m3h = (FEED_KGH * (1 - PULP) / PULP + _hyd) / 1000
ga_mm_for_balance = (cation_keq - _so4_in / 96.06 * 2) / _liq_m3h * 1000
GA_EXCESS = float(os.environ.get("GA_EXCESS", 1.15))   # free gluconic acid left after leaching (15 %): exact balance = zero acidity, pH undefined
GA_MM = ga_mm_for_balance * GA_EXCESS if GA_BALANCE else GA_MM_INL
# Gluconate is a ~1 M buffer (pKa 3.86). Downstream base demand = what it takes to hold each unit's pH set-point, not
# "one NaOH per gluconate": the leach has already deprotonated the gluconate that balances the metals.
PKA_GA = 3.86   # sources also report 3.70; the spread is the gluconic acid /
                # glucono-delta-lactone equilibrium. Worth <2 % on base demand either way.
def gluc_anion_frac(pH): return 1 / (1 + 10 ** (PKA_GA - pH))
def naoh_to_hold(pH, ga_kgh_, cation_eq, so4_kgh_, na_kgh_):
    """kg/h NaOH so that Gluc- = G*f(pH) balances (cations + Na - 2 SO4). Returns 0 if the liquor is already above the set-point."""
    need = ga_kgh_ / GA_MW * gluc_anion_frac(pH) - (cation_eq + na_kgh_ / 23 - 2 * so4_kgh_ / 96.06)
    return max(need, 0.0) * 40.0
PH_FEAL, PH_MN_SX, PH_CO_SX, PH_NI_SX = 5.5, 4.2, 5.5, 6.5   # set-points; Mn SX at 4.2 is the lowest pH the buffered PLS can reach

# ---- Block 3: biolixiviant fermentation (computed first — it sets S-104) ----
liquor_kgh = FEED_KGH * (1 - PULP) / PULP                     # 11,250 kg/h liquid in R-301 at 10 % pulp
ga_kgh = liquor_kgh / 1000 * GA_MM / 1000 * GA_MW              # ~165 kg/h gluconic acid demand
broth_m3h = ga_kgh / BROTH_GA_GL                               # ~2.1 m3/h broth dosed at R-301
glucose_kgh = ga_kgh / GA_MW * GLU_MW / GLU_YIELD              # ~160 kg/h glucose fed
broth_kgh = broth_m3h * 1000                                   # density ~1.0
broth_h2o = broth_kgh - ga_kgh - 5 - CELLS_WET_KGH*0.25 - 10   # water after GA, residual glucose, cells, misc organics
medium_h2o = broth_h2o + CELLS_WET_KGH*0.75                    # water charged with the medium (cells leave wet)
R202_WORK_M3 = broth_m3h * 24                                   # working volume of the running fermenter (24 h batch)
air_kgh = AIR_VVM * R202_WORK_M3 * 60 * 1.2                     # 0.5 vvm on the working volume -> m3/h x 1.2 kg/m3
o2_used = ga_kgh / GA_MW * 0.5 * 32                            # glucose + 1/2 O2 -> gluconic acid

raff_to_T201 = RECYCLE_FRAC * medium_h2o
raff_return = raff_to_T201 / (1 - BLEED_FRAC)
stream("S-201", "V-201", "T-201", "liquid (syrup)", glucose=glucose_kgh, H2O=glucose_kgh*0.4)
stream("S-203", "Sh 5 condensate", "tee", "liquid", H2O=raff_return)                        # placeholder: Sheet 6 closes the water balance
stream("S-204", "tee", "Sh 1 make-up (S-104)", "liquid", H2O=raff_return*BLEED_FRAC)
stream("S-202", "T-201", "R-201/202", "liquid", T=30, H2O=medium_h2o + glucose_kgh*0.4, glucose=glucose_kgh, organics=10)   # salts lumped in organics
stream("S-205", "K-201/F-202", "R-201/202", "gas", air=air_kgh)
stream("S-206", "R-201/202", "atm", "gas", T=30, air=air_kgh - o2_used)
stream("S-207", "R-201A", "R-201B", "broth", T=30, H2O=0.5*1000*0.9, GA=0.5*80)               # 0.5 m3 per batch, shown per batch
stream("S-208", "R-201B", "R-202 A/B", "broth", T=30, H2O=5*1000*0.9, GA=5*80)               # 5 m3 per batch, shown per batch
stream("S-209", "R-202 A/B", "F-201", "broth", T=30, H2O=broth_h2o + CELLS_WET_KGH*0.75, GA=ga_kgh, glucose=5, organics=10 + CELLS_WET_KGH*0.25)
stream("S-210", "F-201", "Sh 5 effluent", "wet cake", T=30, H2O=CELLS_WET_KGH*0.75, organics=CELLS_WET_KGH*0.25)
stream("S-211", "F-201", "T-202", "liquid", T=30, H2O=broth_h2o, GA=ga_kgh, glucose=5, organics=10)
stream("S-212", "P-201", "R-301", "liquid", T=30, H2O=broth_h2o, GA=ga_kgh, glucose=5, organics=10)

# ---- Block 2: metering + slurry make-up (water corrected for broth dosed at R-301) ----
water_kgh = liquor_kgh - broth_h2o                             # make-up water: pulp density is held in R-301, not T-101
if water_kgh < 0:
    _pmax = 1 / (1 + broth_h2o / FEED_KGH)   # broth alone would exceed the liquor the pulp allows
    raise SystemExit(f"Infeasible basis at PULP={PULP:.3f}: broth {broth_h2o:,.0f} kg/h > liquor {liquor_kgh:,.0f} kg/h. "
                     f"Max pulp at {BROTH_GA_GL:.0f} g/L broth is {_pmax:.3f}; raise BROTH_GA_GL or lower PULP.")
stream("S-103", "W-101", "T-101", "dry solid", **solids)
stream("S-104", "Sh3/4 recycle + fresh", "T-101", "liquid", H2O=water_kgh)
stream("S-105", "P-101", "R-301", "slurry", H2O=water_kgh, **solids)

# ---- Block 4: Area 300 batch leach + S/L separation ------------------------------
co_rec = solids["Co"] * LEACH_FRAC["Co"]
feso4_gross = FESO4_PER_CO * co_rec                            # ~350 kg/h FeSO4.7H2O, dry (INL ratio, no Cu credit)
cu_e = solids["Cu"] * LEACH_FRAC["Cu"] / 63.55 * 2               # kmol e-/h from Cu -> Cu2+
fe_credit = cu_e * 55.85 if CU_REDUCTANT_CREDIT else 0.0         # kg/h Fe2+ equivalent supplied by Cu (1 e- per Fe)
feso4 = max(feso4_gross - fe_credit * 278.0 / 55.85, 0.0)
fe_in, so4_in, hyd_h2o = feso4 * 55.85/278.0, feso4 * 96.06/278.0, feso4 * 126.1/278.0
stream("S-301", "V-301/W-301", "R-301", "dry solid", Fe=fe_in, SO4=so4_in, H2O=hyd_h2o)
s105, s212 = streams["S-105"], streams["S-212"]
stream("S-302", "E-301 tee", "R-301", "slurry", T=LEACH_T, **{c: s105[c] + s212[c] for c in COLS})
dissolved = {m: solids[m] * LEACH_FRAC[m] for m in SOLIDS}
residue   = {m: solids[m] - dissolved[m] for m in SOLIDS}
co2 = solids["Li"] * LI_AS_CARBONATE / 6.94 / 2 * 44.0
stream("S-303", "R-301", "SC-301", "gas", T=LEACH_T, CO2=co2)
stream("S-304", "SC-301", "Sh 5 effluent", "liquid", H2O=50, CO2=co2)     # blowdown, placeholder 50 kg/h
liq = {c: s105[c] + s212[c] for c in LIQ}; liq["H2O"] += hyd_h2o; liq["Fe"] += fe_in; liq["SO4"] += so4_in
liq_total = sum(liq.values()) + sum(dissolved.values())
leached = {**residue, **liq}
for m, v in dissolved.items(): leached[m] = leached.get(m, 0) + v      # dissolved metals ride with the liquid
leached["other"] -= co2; residue["other"] -= co2                        # carbonate leaves as CO2
stream("S-305", "R-301", "T-303", "slurry", T=LEACH_T, **leached)
stream("S-306", "P-303", "F-301", "slurry", T=LEACH_T, **leached)
dry_res = sum(residue.values())
cake_liq = dry_res * CAKE_MOISTURE / (1 - CAKE_MOISTURE)
wash_h2o = WASH_RATIO * dry_res
stream("S-307", "process water", "F-301", "liquid", H2O=wash_h2o)
frac_liq = lambda c: (liq.get(c, 0) + dissolved.get(c, 0)) / liq_total   # composition of the leach liquor
pls_kgh = liq_total - cake_liq
stream("S-309", "F-301 strong", "T-301", "liquid", T=45, **{c: pls_kgh * frac_liq(c) for c in COLS if frac_liq(c)})
displaced = cake_liq * WASH_EFF
wash_filt = {c: displaced * frac_liq(c) for c in COLS if frac_liq(c)}; wash_filt["H2O"] = wash_filt.get("H2O", 0) + wash_h2o - displaced
stream("S-311", "F-301 wash", "T-302", "liquid", T=40, **wash_filt)
cake = {**residue}; 
for c in COLS:
    if frac_liq(c): cake[c] = cake.get(c, 0) + (cake_liq - displaced) * frac_liq(c)
cake["H2O"] = cake.get("H2O", 0) + displaced   # wash water left in the pores
stream("S-308", "F-301", "Sh 6 residue bunker X-601", "wet cake", T=40, **cake)
stream("S-310", "P-301", "Sh 4 (Fe removal)", "liquid", T=45, **{c: streams["S-309"][c] for c in COLS})
stream("S-312", "P-302", "Sh 1 T-101 (S-104)", "liquid", T=40, **{c: streams["S-311"][c] for c in COLS})

# ---- Acid / charge budget of the leach liquor ------------------------
anion_keq = ga_kgh / GA_MW + so4_in / 96.06 * 2       # cation_keq, ga_mm_for_balance computed up front (before Block 3)
liq_m3h = liq_total / 1000
charge_ratio = anion_keq / cation_keq

# ---- Block 5: Area 400 impurity removal (Cu -> Fe/Al -> Mn) -------------------------
pls = {c: streams["S-310"][c] for c in COLS}
stream("S-401", "Sh 3 PLS", "T-401", "liquid", T=45, **pls)
cu_rem = pls["Cu"] * CEM_CU_REMOVAL
fe_stoich = cu_rem / 63.55 * 55.85
fe_powder = fe_stoich * CEM_FE_EXCESS
stream("S-402", "V-401/W-401", "T-401", "dry solid", Fe=fe_powder)
cem_cake = dict(Cu=cu_rem, Fe=fe_powder - fe_stoich, H2O=(cu_rem + fe_powder - fe_stoich) * 0.25)
after_cem = dict(pls); after_cem["Cu"] -= cu_rem; after_cem["Fe"] += fe_stoich; after_cem["H2O"] -= cem_cake["H2O"]
stream("S-403", "F-401", "Cu cement product", "wet cake", **cem_cake)
stream("S-404", "F-401", "T-402", "liquid", T=45, **after_cem)
# Fe(II) -> Fe(III) with air, then NaOH to pH 5.5: goethite + gibbsite; gluconate deprotonated on the way
fe_kmol, al_kmol, ga_kmol = after_cem["Fe"] / 55.85, after_cem["Al"] / 26.98, after_cem["GA"] / GA_MW
o2 = fe_kmol / 4 * 32
stream("S-405", "K-401", "T-402", "gas", air=o2 / 0.233 * 2.0)                      # 2x stoichiometric air
cat_eq_402 = sum(after_cem[m] / MW[m] * Z[m] for m in Z if m not in ("Fe", "Al")) + 0.0   # Fe, Al leave as hydroxides
naoh = naoh_to_hold(PH_FEAL, after_cem["GA"], cat_eq_402, after_cem["SO4"], after_cem["Na"]) * 1.05
stream("S-406", "NaOH 50 %", "T-402", "liquid", Na=naoh * 23 / 40, H2O=naoh + naoh * 0)  # 50 % w/w: equal mass water
goethite, gibbsite = fe_kmol * 88.85, al_kmol * 78.0
occ = {m: after_cem[m] * f for m, f in OCCLUSION.items()}
dry_cake = goethite + gibbsite + sum(occ.values())
cake_h2o = dry_cake * FE_AL_CAKE_MOISTURE / (1 - FE_AL_CAKE_MOISTURE)
liq2 = dict(after_cem); liq2["Fe"] = 0.0; liq2["Al"] = 0.0
for m, v in occ.items(): liq2[m] -= v
liq2["Na"] += naoh * 23 / 40; liq2["H2O"] += naoh - cake_h2o + fe_kmol * 18 * 1  # hydroxide water bookkeeping (approx.)
stream("S-407", "T-402", "F-402", "slurry", T=50, **{**liq2, "other": dry_cake, "H2O": liq2["H2O"] + cake_h2o})
stream("S-408", "F-402", "Sh 6 Fe/Al cake", "wet cake", other=dry_cake, H2O=cake_h2o, **{m: 0 for m in ()})
streams["S-408"].update({"Co": occ["Co"], "Ni": occ["Ni"]}); streams["S-408"]["other"] = goethite + gibbsite
streams["S-408"]["total"] = sum(streams["S-408"][c] for c in COLS)
stream("S-409", "F-402", "X-401 Mn SX", "liquid", T=45, **liq2)
# D2EHPA SX: Mn extracted, Co co-extraction placeholder, NaOH for pH 3.0 control, H2SO4 strip -> MnSO4 liquor
mn_ext = liq2["Mn"] * MN_SX_EXTRACTION
co_ext = liq2["Co"] * MN_SX_CO_COEXTRACT
cat_eq_401 = sum(liq2[m] / MW[m] * Z[m] for m in Z) - mn_ext / 54.94 * 2 - co_ext / 58.93 * 2
naoh_sx = naoh_to_hold(PH_MN_SX, liq2["GA"], cat_eq_401, liq2["SO4"], liq2["Na"])
stream("S-410", "NaOH 50 %", "X-401", "liquid", Na=naoh_sx * 23 / 40, H2O=naoh_sx)
h2so4 = (mn_ext / 54.94) * 98.08
strip_h2o = mn_ext / MN_STRIP_GL * 1000 - mn_ext - h2so4 * 96.06 / 98.08
stream("S-412", "H2SO4 98 %", "X-403", "liquid", SO4=h2so4 * 96.06 / 98.08, H2O=h2so4 * 0.02)
stream("S-413", "X-403 strip", "T-404 MnSO4 product", "liquid", Mn=mn_ext, Co=co_ext, SO4=h2so4 * 96.06 / 98.08, H2O=strip_h2o)
raff = dict(liq2); raff["Mn"] -= mn_ext; raff["Co"] -= co_ext; raff["Na"] += naoh_sx * 23 / 40; raff["H2O"] += naoh_sx
stream("S-414", "X-401 raffinate", "T-405 -> Sh 5", "liquid", T=40, **raff)
org_m3h = streams["S-409"]["total"] / 1000            # O/A = 1, 20 % D2EHPA in kerosene, internal loop
stream("S-411", "X-401 -> X-403 (organic loop)", "internal", "organic", organics=org_m3h * 800)

# ---- Block 6: Area 500 products ------------------------------------------------------
pur = {c: streams["S-414"][c] for c in COLS}
stream("S-501", "Sh 4 purified liquor", "X-501", "liquid", T=40, **pur)
co_x = pur["Co"] * CO_SX_EXT; ni_co = pur["Ni"] * CO_SX_NI_COEXT
cat_eq_501 = sum(pur[m] / MW[m] * Z[m] for m in Z) - co_x / 58.93 * 2 - ni_co / 58.69 * 2
naoh_co = naoh_to_hold(PH_CO_SX, pur["GA"], cat_eq_501, pur["SO4"], pur["Na"])   # Cyanex 272 releases 2 H+ per Co; buffer + NaOH hold pH
stream("S-502", "NaOH 50 %", "X-501", "liquid", Na=naoh_co * 23 / 40, H2O=naoh_co)
h2so4_co = co_x / 58.93 * 98.08
stream("S-503", "H2SO4 98 %", "X-503 strip", "liquid", SO4=h2so4_co * 96.06 / 98.08, H2O=h2so4_co * 0.02)
co_strip_h2o = co_x / CO_STRIP_GL * 1000 - co_x - h2so4_co * 96.06 / 98.08
stream("S-504", "X-503", "X-504 crystalliser", "liquid", Co=co_x, Ni=ni_co, SO4=h2so4_co * 96.06 / 98.08, H2O=co_strip_h2o)
coso4 = co_x * CRYST_REC / 58.93 * COSO4_7H2O
stream("S-505", "X-504/C-501/D-501", "CoSO4.7H2O product", "solid", Co=co_x * CRYST_REC, SO4=co_x * CRYST_REC / 58.93 * 96.06, H2O=co_x * CRYST_REC / 58.93 * 7 * 18.02)
stream("S-506", "X-504 evaporator", "condensate header", "liquid", H2O=co_strip_h2o - co_x * CRYST_REC / 58.93 * 7 * 18.02 - 30)   # mother-liquor purge 30 kg/h
stream("S-518", "X-504 mother-liquor purge", "Sh 6", "liquid", Co=co_x * (1 - CRYST_REC), Ni=ni_co, SO4=h2so4_co * 96.06 / 98.08 - co_x * CRYST_REC / 58.93 * 96.06, H2O=30)
raff1 = dict(pur); raff1["Co"] -= co_x; raff1["Ni"] -= ni_co; raff1["Na"] += naoh_co * 23 / 40; raff1["H2O"] += naoh_co
ni_x = raff1["Ni"] * NI_SX_EXT
cat_eq_511 = sum(raff1[m] / MW[m] * Z[m] for m in Z) - ni_x / 58.69 * 2
naoh_ni = naoh_to_hold(PH_NI_SX, raff1["GA"], cat_eq_511, raff1["SO4"], raff1["Na"])
stream("S-507", "NaOH 50 %", "X-511", "liquid", Na=naoh_ni * 23 / 40, H2O=naoh_ni)
h2so4_ni = ni_x / 58.69 * 98.08
stream("S-508", "H2SO4 98 %", "X-513 strip", "liquid", SO4=h2so4_ni * 96.06 / 98.08, H2O=h2so4_ni * 0.02)
ni_strip_h2o = ni_x / NI_STRIP_GL * 1000 - ni_x - h2so4_ni * 96.06 / 98.08
stream("S-509", "X-513", "X-514 crystalliser", "liquid", Ni=ni_x, SO4=h2so4_ni * 96.06 / 98.08, H2O=ni_strip_h2o)
stream("S-510", "X-514/C-502/D-502", "NiSO4.6H2O product", "solid", Ni=ni_x * CRYST_REC, SO4=ni_x * CRYST_REC / 58.69 * 96.06, H2O=ni_x * CRYST_REC / 58.69 * 6 * 18.02)
stream("S-511", "X-514 evaporator", "condensate header", "liquid", H2O=ni_strip_h2o - ni_x * CRYST_REC / 58.69 * 6 * 18.02 - 60)
stream("S-519", "X-514 mother-liquor purge", "Sh 6", "liquid", Ni=ni_x * (1 - CRYST_REC), SO4=h2so4_ni * 96.06 / 98.08 - ni_x * CRYST_REC / 58.69 * 96.06, H2O=60)
raff2 = dict(raff1); raff2["Ni"] -= ni_x; raff2["Na"] += naoh_ni * 23 / 40; raff2["H2O"] += naoh_ni
stream("S-512", "X-511 raffinate", "T-501 Li3PO4 precipitation", "liquid", T=40, **raff2)
li_ppt = raff2["Li"] * LI_PPT_YIELD
na3po4 = li_ppt / 6.94 / 3 * 163.94 * PO4_EXCESS                      # kg/h Na3PO4 (anhydrous basis)
li3po4 = li_ppt / 6.94 / 3 * 115.79
stream("S-514", "Na3PO4", "T-501", "dry solid", Na=na3po4 * 69 / 163.94, PO4=na3po4 * 94.97 / 163.94)
stream("S-515", "F-501", "Li3PO4 product", "solid", Li=li_ppt, PO4=li3po4 - li_ppt, H2O=li3po4 * 0.15)   # 15 % cake moisture (water from the filtrate)
filt = dict(raff2); filt["Li"] -= li_ppt; filt["Na"] += na3po4 * 3 * 23 / 163.94
filt["PO4"] += na3po4 * (PO4_EXCESS - 1) / PO4_EXCESS * 94.97 / 163.94        # excess phosphate stays in solution
filt["H2O"] -= li3po4 * 0.15
stream("S-520", "F-501 filtrate", "E-501 evaporator", "liquid", T=40, **filt)
# E-501: water recovery only — concentrate the Li-free barren to NAGLUC_CONC_GL sodium gluconate
nagluc_kgh = filt["GA"] / GA_MW * 218.1
brine_m3h = nagluc_kgh / NAGLUC_CONC_GL
brine_kgh = brine_m3h * 1000 * 1.25                                        # ~1.25 kg/L at 500 g/L
evap_h2o = streams["S-520"]["total"] - brine_kgh
assert 0 < evap_h2o < filt["H2O"], "E-501: concentration target not reachable"
stream("S-513", "E-501", "condensate header", "liquid", T=60, H2O=evap_h2o)
brine = dict(filt); brine["H2O"] -= evap_h2o
NA_GLUC_GL = raff2["GA"] / GA_MW * 218.1 / (streams["S-512"]["total"] / 1000)   # g/L sodium gluconate in S-512, as-is
stream("S-516", "E-501 brine", "Sh 6 effluent (bleed)", "liquid", T=60, **brine)
cond_total = streams["S-506"]["H2O"] + streams["S-511"]["H2O"] + evap_h2o

# ---- Block 7 (Sheet 6): Area 600 - effluent and by-product ----
# Liquids: the brine (S-516), crystalliser purges (S-518/519) and the SC-301 scrubber blowdown (S-304) are equalised in
# T-601 and dried in D-601 to a crude sodium-gluconate salt — the whole sodium/phosphate/gluconate bleed leaves as one
# saleable-or-disposable solid instead of a 14 t/h liquid effluent (no liquid discharge; technical grade at best,
# note the ppm Co/Ni). Solids (leach residue S-308, Fe/Al cake S-408, spent biomass S-210, Cu cement S-403) go to bunkers.
CRUDE_SALT_MOISTURE = 0.05
eff = {c: streams["S-516"][c] + streams["S-518"][c] + streams["S-519"][c] + streams["S-304"][c] for c in COLS}
stream("S-601", "T-601 equalisation", "D-601 dryer", "liquid", T=50, **eff)
salt_dry = sum(v for c, v in eff.items() if c != "H2O" and c not in GAS) + eff["CO2"]   # scrubber CO2 leaves as carbonate (counted as CO2 mass; scrubber NaOH not tracked)
salt_h2o = salt_dry * CRUDE_SALT_MOISTURE / (1 - CRUDE_SALT_MOISTURE)
dryer_h2o = eff["H2O"] - salt_h2o
stream("S-602", "D-601 exhaust", "atmosphere (humid air)", "gas", T=90, H2O=dryer_h2o)
salt = {c: v for c, v in eff.items() if c != "H2O" and c not in GAS}; salt["H2O"] = salt_h2o; salt["other"] = salt.get("other", 0) + eff["CO2"]
stream("S-603", "D-601", "crude Na-gluconate salt, OSBL", "solid", T=40, **salt)
nagluc_product = eff["GA"] / GA_MW * 218.1
cod_kgh = eff["GA"] * 0.90 + eff["organics"] * 1.2 + eff["glucose"] * 1.07       # ThOD: gluconate 0.90, glucose 1.07, biomass ~1.2 g O2/g
# --- plant water closure ---
cond_to_medium = cond_total - streams["S-204"]["H2O"]                                  # condensate share of the fermenter medium (S-203)
medium_fresh = max(streams["S-203"]["H2O"] - cond_to_medium, 0)                        # medium water the condensate cannot cover
cond_surplus = max(streams["S-204"]["H2O"] - water_kgh, 0)                             # condensate left after S-104 (displaces fresh wash water)
fresh_water_in = streams["S-307"]["total"] + medium_fresh + max(water_kgh - streams["S-204"]["H2O"], 0) - cond_surplus
water_out = {k: streams[k]["H2O"] for k in ("S-403","S-505","S-510","S-515","S-413","S-408","S-308","S-210","S-602","S-603")}
key_water = dict(cond_total=cond_total, medium_fresh=medium_fresh, fresh_water_in=fresh_water_in, dryer_h2o=dryer_h2o)
stream("S-517", "condensate header", "Sh 2 (S-203) + Sh 1/3 make-up", "liquid", T=45, H2O=cond_total)

# ---- equipment sizing (residence time x flow; hold-ups from the streams above) -----
RHO_SLURRY = 1.08   # t/m3, 10 % graphite/oxide slurry
equipment = {}
def size(tag, service, basis, value, unit):
    equipment[tag] = dict(service=service, basis=basis, value=value, unit=unit)

size("V-101", "Black mass receiving silo", "48 h hold-up", FEED_KGH * 48 / 1000, "t")
size("T-101", "Slurry make-up tank", "2 h at S-105", streams["S-105"]["total"] / 1000 / RHO_SLURRY * 2, "m3")
size("P-101 A/B", "Feed slurry pump", "S-105 volumetric", streams["S-105"]["total"] / 1000 / RHO_SLURRY, "m3/h")
size("V-201", "Glucose syrup storage", "7 d of S-201 as 70 % syrup", glucose_kgh / 0.7 / 1000 / 1.35 * 24 * 7, "m3")
size("T-201", "Medium make-up", "1 batch of S-202", streams["S-202"]["total"] / 1000 * 24, "m3/batch")
size("R-201A", "Pre-seed fermenter", "1/100 of R-201B (1 % inoculum)", R202_WORK_M3 / 100 * 10, "L")
size("R-201B", "Seed fermenter", "1/10 of R-202 working", R202_WORK_M3 / 10, "m3")
size("R-202 A/B", "Production fermenter", "24 h of broth, x1.2 headspace", broth_m3h * 24 * 1.2, "m3 each")
size("K-201", "Sterile air blower", f"{AIR_VVM} vvm on R-202 working volume", AIR_VVM * R202_WORK_M3 * 60, "m3/h")
size("F-201", "Cell removal", "S-209 volumetric", streams["S-209"]["total"] / 1000, "m3/h")
size("T-202", "Biolixiviant hold", "12 h at S-211", streams["S-211"]["total"] / 1000 * 12, "m3")
size("P-201", "Biolixiviant dose pump", "S-212 volumetric", streams["S-212"]["total"] / 1000, "m3/h")
slurry_m3h = streams["S-302"]["total"] / 1000 / RHO_SLURRY
size("V-301", "FeSO4.7H2O silo", "7 d of S-301", feso4 * 24 * 7 / 1000, "t")
size("E-301", "Slurry preheater", "S-302 x 3.5 kJ/kgK x (55-25)", streams["S-302"]["total"] * 3.5 * (LEACH_T - 25) / 3600, "kW")
size("R-301 A-D", "Batch leach tank", "12.5 h fill at S-302, x1.2 headspace", slurry_m3h * 12.5 * 1.2, "m3 each")
size("T-303", "Leached-slurry surge", "8 h at S-305 (drain 150 m3 in 7.5 h vs filter 12 m3/h)", slurry_m3h * 8, "m3")
size("F-301", "Belt filter", "dry residue / 100 kg/m2.h", dry_res / 100, "m2")
size("T-301", "PLS tank", "4 h at S-309", streams["S-309"]["total"] / 1000 * 4, "m3")
size("T-302", "Wash-filtrate tank", "4 h at S-311", streams["S-311"]["total"] / 1000 * 4, "m3")
size("SC-301", "Vent scrubber", "S-303 + displacement air", co2 / 1.8 * 5, "m3/h gas")
pls_m3h = streams["S-401"]["total"] / 1000
size("T-401", "Cementation reactor", "1 h at S-401", pls_m3h * 1, "m3")
size("F-401", "Cement Cu filter", "S-403 dry solids", cu_rem + fe_powder - fe_stoich, "kg/h dry")
size("T-402", "Fe/Al oxidation + neutralisation", "2 h at S-404, x1.2", pls_m3h * 2 * 1.2, "m3")
size("K-401", "Oxidation air blower", "S-405 at 1.2 kg/m3", streams["S-405"]["air"] / 1.2, "m3/h")
size("F-402", "Fe/Al cake filter press", "dry cake at 15 kg/m2.h", dry_cake / 15, "m2")
size("X-401/402/403", "D2EHPA mixer-settlers (2E + 1S + 2St)", "10 min mixer at O/A 1, S-409 + organic", 2 * org_m3h * 10 / 60, "m3 mixer each")
size("T-404", "MnSO4 strip liquor tank", "24 h at S-413", streams["S-413"]["total"] / 1000 * 24, "m3")
size("T-405", "Purified liquor tank", "4 h at S-414", streams["S-414"]["total"] / 1000 * 4, "m3")
q5 = streams["S-501"]["total"] / 1000
size("X-501/502/503", "Co SX mixer-settlers (3E + 2S + 2St)", "10 min mixer at O/A 1", 2 * q5 * 10 / 60, "m3 mixer each")
size("X-504", "CoSO4 crystalliser (evaporative)", "water evaporated", streams["S-506"]["H2O"] / 1000, "t/h H2O")
size("X-511/512/513", "Ni SX mixer-settlers (3E + 1S + 2St)", "10 min mixer at O/A 1", 2 * q5 * 10 / 60, "m3 mixer each")
size("X-514", "NiSO4 crystalliser (evaporative)", "water evaporated", streams["S-511"]["H2O"] / 1000, "t/h H2O")
size("T-501", "Li3PO4 precipitation", "1 h at barren flow, 60 C", streams["S-512"]["total"] / 1000 * 1, "m3")
size("F-501", "Li3PO4 filter", "cake at 15 % moisture", li3po4, "kg/h dry")
size("T-601", "Effluent equalisation tank", "8 h of combined liquid effluent", streams["S-601"]["total"] / 1000 * 8, "m3")
size("D-601", "Crude-salt dryer (steam-tube / spray)", "water evaporated from the brine", dryer_h2o / 1000, "t/h H2O")
size("X-601", "Leach residue bunker", "3 days of wet cake", streams["S-308"]["total"] * 72 / 1000, "t")
size("X-602", "Fe/Al cake bunker", "3 days of wet cake", streams["S-408"]["total"] * 72 / 1000, "t")
size("X-603", "Spent-biomass skip", "7 days of wet cake", streams["S-210"]["total"] * 168 / 1000, "t")
size("E-501", "Barren evaporator (MVR), water recovery", f"to {NAGLUC_CONC_GL:.0f} g/L Na-gluconate", evap_h2o / 1000, "t/h H2O")
size("D-501/D-502", "Product dryers", "CoSO4 + NiSO4 crystals", (coso4 + streams["S-510"]["total"]) , "kg/h")

# ---- output ----------------------------------------------------------------
ORDER = ["S-101","S-102","S-103","S-104","S-105"] + [f"S-2{n:02d}" for n in range(1,13)] + [f"S-3{n:02d}" for n in range(1,13)] + [f"S-4{n:02d}" for n in range(1,15) if f"S-4{n:02d}" in streams] + [f"S-5{n:02d}" for n in range(1,21)] + ["S-601","S-602","S-603"]

def table():
    df = pd.DataFrame(streams).T.loc[ORDER]
    return df[["frm", "to", "phase", "T", "total"] + COLS]

def html_rows(block):
    """Stream + equipment rows for one Index block, ready to paste."""
    blocks = {1: ["S-101","S-102"], 2: ["S-103","S-104","S-105"], 3: [f"S-2{n:02d}" for n in range(1,13)], 4: [f"S-3{n:02d}" for n in range(1,13)], 5: [f"S-4{n:02d}" for n in range(1,15) if f"S-4{n:02d}" in streams], 6: [f"S-5{n:02d}" for n in range(1,21)], 7: ["S-601","S-602","S-603"]}
    eq = {1: ["V-101"], 2: ["T-101","P-101 A/B"], 3: ["V-201","T-201","R-201A","R-201B","R-202 A/B","K-201","F-201","T-202","P-201"], 4: ["V-301","E-301","R-301 A-D","T-303","F-301","T-301","T-302","SC-301"], 5: ["T-401","F-401","T-402","K-401","F-402","X-401/402/403","T-404","T-405"], 6: ["X-501/502/503","X-504","X-511/512/513","X-514","E-501","T-501","D-501/D-502"], 7: ["T-601","D-601","X-601","X-602","X-603"]}
    fmt = lambda v: "0" if abs(v) < 0.05 else f"{v:,.0f}" if v >= 100 else f"{v:,.1f}"
    out = ["<!-- equipment -->"]
    for t in eq[block]:
        e = equipment[t]
        out.append(f'<tr><td class="t">{t}</td><td>{e["service"]}</td><td class="num">{fmt(e["value"])} {e["unit"]}</td><td>{e["basis"]}</td></tr>')
    out.append("<!-- streams -->")
    cols = SOLIDS if block < 3 else (LIQ + GAS if block == 3 else SOLIDS + ["H2O","Fe","SO4","GA"] + (["Na"] if block >= 5 else []) + (["PO4"] if block >= 6 else []))
    for no in blocks[block]:
        r = streams[no]
        cells = "".join(f'<td class="num">{fmt(r[c])}</td>' for c in cols)
        out.append(f'<tr><td class="t">{no}</td><td>{r["frm"]} → {r["to"]}</td><td>{r["phase"]}</td><td class="num">{fmt(r["total"])}</td>{cells}<td class="num">{r["T"]}</td></tr>')
    return "\n".join(out)

def key_metrics():
    """One flat dict per basis — what sensitivity_pulp.py sweeps."""
    return dict(pulp=PULP, ga_mM=GA_MM, charge_ratio=charge_ratio, ga_mM_balance=ga_mm_for_balance,
                r202_m3=equipment["R-202 A/B"]["value"], glucose_kgh=glucose_kgh, broth_m3h=broth_m3h,
                r301_m3=equipment["R-301 A-D"]["value"], naoh_kgh=naoh + naoh_sx + naoh_co + naoh_ni,
                brine_na_kgh=brine["Na"], evap_tph=evap_h2o / 1000, s104_kgh=water_kgh, na_gluc_gl_s512=NA_GLUC_GL, brine_ga_kgh=brine["GA"], li3po4_tpy=li3po4 * HOURS / 1000, na3po4_kgh=na3po4,
                co_product_kgh=co_x * CRYST_REC, coso4_tpy=coso4 * HOURS / 1000)

if __name__ == "__main__":
    import sys
    if "--json" in sys.argv:
        print(json.dumps(key_metrics())); sys.exit()
    if "--html" in sys.argv:
        b = int(sys.argv[sys.argv.index("--html") + 1])
        print(html_rows(b)); sys.exit()
    df = table()
    assert abs(df.loc["S-101", "total"] - FEED_KGH) < 1e-6
    assert abs(sum(GRADE.values()) - 1) < 1e-9
    r301_liquid = df.loc["S-105", "H2O"] + df.loc["S-212", "H2O"]
    assert abs(FEED_KGH / (FEED_KGH + r301_liquid) - PULP) < 1e-3, "pulp density in R-301 off basis"
    assert abs(df.loc["S-209","total"] - df.loc["S-210","total"] - df.loc["S-211","total"]) < 1e-6, "F-201 balance"
    for m in ["Co","Ni","Li","Mn"]:   # metal in = residue + PLS + wash filtrate
        assert abs(df.loc["S-101",m] - df.loc["S-308",m] - df.loc["S-309",m] - df.loc["S-311",m]) < 1e-6, f"{m} balance across F-301"
    assert abs(df.loc["S-302","total"] + df.loc["S-301","total"] - df.loc["S-305","total"] - df.loc["S-303","total"]) < 1e-6, "R-301 balance"
    for m in ["Co","Ni","Li","Mn","Cu"]:   # Area 400: in = cement cake + Fe/Al cake + MnSO4 + raffinate
        assert abs(df.loc["S-401",m] - df.loc["S-403",m] - df.loc["S-408",m] - df.loc["S-413",m] - df.loc["S-414",m]) < 1e-6, f"{m} balance across Area 400"
    for m in ["Co","Ni","Li"]:   # Area 500: in = products + brine
        assert abs(df.loc["S-501",m] - df.loc["S-505",m] - df.loc["S-510",m] - df.loc["S-515",m] - df.loc["S-516",m] - df.loc["S-518",m] - df.loc["S-519",m]) < 1e-6, f"{m} balance across Area 500"
    assert abs(df.loc["S-520","H2O"] - evap_h2o - brine["H2O"]) < 1e-6, "E-501 water balance"

    # crystalliser mother-liquor recycle: derive the overall recovery from a literal stage-by-stage
    # simulation and check it against the closed form CRYST_REC = y/(y+(1-y)b). If the algebra above is
    # ever edited wrongly, this fails loudly instead of silently shifting Co/Ni recovery.
    _y, _b = CRYST_YIELD, CRYST_BLEED
    _fresh, _recycle, _prod, _bled = 1.0, 0.0, 0.0, 0.0
    for _ in range(2000):
        _c = _fresh + _recycle           # combined feed to the crystalliser
        _p = _y * _c                     # crystals out this pass
        _m = _c - _p                     # mother liquor
        _prod += _p; _bled += _b * _m
        _recycle = (1 - _b) * _m
        _fresh = 0.0                     # unit pulse of fresh feed, then follow the recycle to extinction
    assert abs(_prod + _bled - 1.0) < 1e-9, "crystalliser recycle does not close on total mass"
    assert abs(_prod - CRYST_REC) < 1e-9, (
        f"crystalliser recycle: simulated recovery {_prod:.6f} != closed form {CRYST_REC:.6f}")
    assert abs(df.loc["S-601","total"] - df.loc["S-602","total"] - df.loc["S-603","total"]) < 1e-6, "D-601 balance"
    na_in = sum(df.loc[k,"Na"] for k in ("S-406","S-514","S-502","S-507") if k in df.index) + naoh_sx * 23 / 40
    assert abs(df.loc["S-603","Na"] - na_in) < 1.0, f"Na closure: in {na_in:.0f} vs out {df.loc['S-603','Na']:.0f}"
    pd.set_option("display.width", 220)
    print(df.round(1).to_string())
    print(f"\nGA demand {ga_kgh:.0f} kg/h · broth {broth_m3h:.2f} m3/h · glucose {glucose_kgh:.0f} kg/h · O2 used {o2_used:.1f} kg/h")
    print(f"S-104 water {water_kgh:,.0f} kg/h (was 11,250 before broth water was counted)")
    print(f"FeSO4.7H2O gross {feso4_gross:.0f} kg/h, Cu reductant credit {fe_credit:.1f} kg Fe/h -> dosed {feso4:.0f} kg/h")
    print(f"FeSO4.7H2O {feso4:.0f} kg/h · Co to PLS {df.loc['S-310','Co']:.1f} · Co in residue {df.loc['S-308','Co']:.1f} · Co in wash filtrate {df.loc['S-312','Co']:.2f} kg/h")
    print(f"Area 400: Fe powder {fe_powder:.1f} · NaOH {naoh:.0f}+{naoh_sx:.0f} kg/h · goethite {goethite:.0f} + gibbsite {gibbsite:.0f} kg/h dry · MnSO4 liquor {streams['S-413']['total']:.0f} kg/h · Co to Sh 5 {raff['Co']:.1f} kg/h (loss {occ['Co']+co_ext:.1f})")
    print(f"Li3PO4 {li3po4:,.0f} kg/h ({li3po4*HOURS/1000:,.0f} t/yr) · Na3PO4 {na3po4:,.0f} kg/h · Li to product {li_ppt/(FEED_KGH*GRADE['Li'])*100:.1f}%")
    print(f"Area 600: effluent {streams['S-601']['total']:,.0f} kg/h -> crude salt {streams['S-603']['total']:,.0f} kg/h (Na-gluconate {nagluc_product:,.0f}, Na {salt['Na']:,.0f}, PO4 {salt['PO4']:,.0f}, SO4 {salt['SO4']:,.0f}) · dryer {dryer_h2o/1000:.1f} t/h H2O · COD if sent to WWTP instead {cod_kgh/1000:.1f} t/h O2")
    print(f"Water closure: condensate {cond_total:,.0f} kg/h -> medium {cond_to_medium:,.0f} + S-104 {water_kgh:,.0f} + surplus {cond_surplus:,.0f} · fresh water {fresh_water_in:,.0f} kg/h (medium top-up {medium_fresh:,.0f} + wash {streams['S-307']['total']:,.0f} - surplus) · dryer exhaust {dryer_h2o:,.0f} kg/h would cover it if condensed · water out: products {sum(water_out[k] for k in ('S-403','S-505','S-510','S-515','S-413')):,.0f} · cakes {sum(water_out[k] for k in ('S-408','S-308','S-210')):,.0f} · dryer exhaust {dryer_h2o:,.0f} · salt {salt_h2o:,.0f}")
    print(f"Products: CoSO4.7H2O {coso4:.0f} kg/h ({coso4*HOURS/1000:,.0f} t/yr) · NiSO4.6H2O {streams['S-510']['total']:.0f} kg/h ({streams['S-510']['total']*HOURS/1000:,.0f} t/yr) · Li3PO4 {li3po4:.0f} kg/h ({li3po4*HOURS/1000:,.0f} t/yr)")
    print(f"Overall recovery to product: Co {co_x*CRYST_REC/solids['Co']:.1%} · Ni {ni_x*CRYST_REC/solids['Ni']:.1%} · Li {li_ppt/solids['Li']:.1%}")
    print(f"Water: condensate {cond_total:,.0f} kg/h returned · brine bleed {streams['S-516']['total']:,.0f} kg/h (Na {brine['Na']:.0f}) · evaporator duty {evap_h2o:,.0f} kg/h")
    print(f"\nAcid budget in R-301: cations {cation_keq:.1f} keq/h vs anions {anion_keq:.1f} keq/h (gluconate {GA_MM:.0f} mM + sulfate) -> ratio {charge_ratio:.2f}")
    print(f"  gluconate for strict charge balance: {ga_mm_for_balance:,.0f} mM; pulp-scaled reference basis would be {GA_MM_INL:,.0f} mM ({ga_mm_for_balance/GA_MM_INL:.1f}x short). Mode: {'charge-balanced' if GA_BALANCE else 'reference-shape'}.")
    if charge_ratio < 0.9: print("  WARNING: leach liquor is not charge-balanced as modelled — see B-design-basis/design-basis.md")
    print("\nEquipment")
    for t, e in equipment.items():
        print(f"  {t:10s} {e['service']:28s} {e['value']:9,.1f} {e['unit']:9s} ← {e['basis']}")
