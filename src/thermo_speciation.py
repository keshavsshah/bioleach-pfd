"""Speciation of the leach liquor (PLS) with PHREEQC via phreeqpython.

Answers three questions the mass balance cannot:
  1. How much Fe(III) does gluconate hold in solution at pH 2.5-4?  (the chelation risk for Fe removal, Sheet 4)
  2. Is there a thermodynamic ceiling on Cu / Al dissolution at leach pH?  (bounds LEACH_FRAC in mass_balance.py)
  3. Where do Fe, Al, Cu, Co, Ni precipitate as pH is raised?  (sets the Sheet 4 precipitation setpoints)

Gluconate is NOT in the PHREEQC databases, so it is added below with literature constants.
Constants are 25 C, I ~0.1; PHREEQC has no dH for them, so the 55 C runs use the 25 C values (flagged).

Run:  python3 thermo_speciation.py
"""
from pathlib import Path
from phreeqpython import PhreeqPython
import mass_balance as mb

# ---- gluconate chemistry to add ----------------------------------------------------------
# log K at 25 C.  Only carboxylate 1:1 complexes matter at leach pH; the strong hydroxy-deprotonated
# Fe(III)/Cu complexes that make gluconate an industrial sequestrant form above pH ~5-6 and are added as
# a separate Fe species so the pH window where they take over is visible.
LOGK = {
    "HGluc":     (3.86, "Sawyer 1964 (pKa)"),
    "CoGluc+":   (1.9,  "NIST 46 / Sawyer 1964"),
    "NiGluc+":   (1.8,  "NIST 46 / Sawyer 1964"),
    "CuGluc+":   (2.5,  "Pecsok & Juvet 1955; Sawyer 1964"),
    "AlGluc+2":  (2.0,  "Motekaitis & Martell 1984 (approx.)"),
    "MnGluc+":   (1.5,  "Sawyer 1964"),
    "FeGluc+2":  (3.5,  "Fe(III) 1:1 carboxylate, Bechtold 2002 / Pecsok 1955 — UNCERTAIN, swept below"),
    "FeGlucOH+": (-2.0, "Fe(III) hydroxo-gluconate, effective log K for Fe+3 + Gluc- + H2O = FeGlucOH+ + H+ (approx.)"),
}
# database: USGS minteq.v4.dat (Co, Ni, Cu, Al, Li, Mn, Fe all present) kept in this folder
GLUC_DB = """
SOLUTION_MASTER_SPECIES
    Gluc    Gluc-   0   C6H11O7   195.15
SOLUTION_SPECIES
    Gluc- = Gluc-
        log_k 0
    Gluc- + H+ = HGluc
        log_k {HGluc}
    Co+2 + Gluc- = CoGluc+
        log_k {CoGluc+}
    Ni+2 + Gluc- = NiGluc+
        log_k {NiGluc+}
    Cu+2 + Gluc- = CuGluc+
        log_k {CuGluc+}
    Al+3 + Gluc- = AlGluc+2
        log_k {AlGluc+2}
    Mn+2 + Gluc- = MnGluc+
        log_k {MnGluc+}
    Fe+3 + Gluc- = FeGluc+2
        log_k {FeGluc+2}
    Fe+3 + Gluc- + H2O = FeGlucOH+ + H+
        log_k {FeGlucOH+}
PHASES
    Fix_pH
        H+ = H+
        log_k 0
"""

def liquor_gL():
    """PLS composition (g/L) straight from the mass balance — S-309 leach liquor, ~1.0 kg/L."""
    r = mb.streams["S-309"]; vol_L = r["total"]                      # kg/h ~ L/h
    gl = lambda c: r[c] * 1000 / vol_L
    return dict(Co=gl("Co"), Ni=gl("Ni"), Mn=gl("Mn"), Li=gl("Li"), Cu=gl("Cu"), Al=gl("Al"),
                Fe=gl("Fe"), SO4=gl("SO4"), Gluc=gl("GA"))

def make_pp(fe_gluc_logk=None):
    k = {n: v for n, (v, _) in LOGK.items()}
    if fe_gluc_logk is not None: k["FeGluc+2"] = fe_gluc_logk
    pp = PhreeqPython(database="minteq.v4.dat", database_directory=Path(__file__).parent.parent / "data")
    pp.ip.run_string(GLUC_DB.format(**k))
    return pp

def solution(pp, comp, pH, temp=55, fe3_frac=1.0, balance_with=None):
    """comp in g/L; Fe split between +3 (from Co3+ reduction) and +2 (excess dose).
    balance_with='Gluc' lets PHREEQC adjust gluconate to charge-balance the liquor (the acid budget)."""
    mgL = {k: v * 1000 for k, v in comp.items()}
    gluc = mgL["Gluc"] * 195.15 / 196.16
    gluc = f"{gluc} charge" if balance_with == "Gluc" else gluc
    s = pp.add_solution({
        "units": "mg/l", "pH": pH, "temp": temp,
        "Co": mgL["Co"], "Ni": mgL["Ni"], "Mn": mgL["Mn"], "Li": mgL["Li"], "Cu": mgL["Cu"], "Al": mgL["Al"],
        "Fe(3)": mgL["Fe"] * fe3_frac, "Fe(2)": mgL["Fe"] * (1 - fe3_frac),
        "S(6)": mgL["SO4"], "Gluc": gluc,
    })
    return s

# Goethite, not ferrihydrite: at 0.1 M Fe(III) minteq holds Fe in polynuclear hydroxo species and ferrihydrite stays
# undersaturated, while goethite (the phase a 55 C Fe-removal circuit actually makes) is supersaturated from pH ~3.
PHASES_PPT = ["Goethite", "Gibbsite", "Cu(OH)2", "Co(OH)2", "Ni(OH)2"]
FE3_SPECIES = ("Fe+3", "FeOH+2", "Fe(OH)2+", "Fe(OH)3", "Fe(OH)4-", "FeSO4+", "Fe(SO4)2-", "FeHSO4+2", "Fe2(OH)2+4", "Fe3(OH)4+5", "FeGluc+2", "FeGlucOH+")

import re as _re
def charge_imbalance(s):
    """Sum of z*molality over all aqueous species (eq/kgw). PHREEQC does not enforce electroneutrality unless told."""
    tot = 0.0
    for name, m in s.species.items():
        mt = _re.search(r'([+-])(\d*)$', name)
        if mt: tot += (1 if mt.group(1) == '+' else -1) * (int(mt.group(2)) if mt.group(2) else 1) * m
    return tot

def fe3_bound(s):
    """Fraction of dissolved Fe(III) held by gluconate."""
    sp = s.species
    tot = sum(sp.get(k, 0) for k in FE3_SPECIES)
    glu = sp.get("FeGluc+2", 0) + sp.get("FeGlucOH+", 0)
    return glu / tot if tot else 0.0

def titrate(s0, pH, phases=PHASES_PPT):
    """Raise pH with NaOH from the leach liquor and let hydroxides precipitate (SI = 0)."""
    s = s0.copy(); s.change_ph(pH, "NaOH"); s.equalize(phases, [0] * len(phases), [0] * len(phases))   # in_phase 0: precipitate only (default 10 mol would DISSOLVE hydroxides)
    return s

def dissolved(s, el):
    return s.total_element(el, units="mol")

if __name__ == "__main__":
    comp = liquor_gL()
    print("PLS from mass_balance.py (g/L):", {k: round(v, 2) for k, v in comp.items()})
    pp = make_pp()
    # --- Q0: acid / charge budget. PHREEQC accepts a non-electroneutral solution silently; measure the imbalance.
    base = solution(pp, comp, 2.5)
    imb = charge_imbalance(base)                        # eq/kgw, positive = excess cations
    g_given = base.total("Gluc", units="mol")
    print(f"\n--- Q0: charge budget at pH 2.5 — cation excess {imb:.2f} eq/L; gluconate given {g_given*1000:,.0f} mM, "
          f"gluconate for electroneutrality ≈ {(g_given + imb)*1000:,.0f} mM ({(g_given+imb)/g_given:.1f}x). "
          f"Forcing balance (charge keyword) does not converge: I > 3 M is outside the Davies model — the liquor cannot exist as a dilute solution ---")
    tot0 = {el: dissolved(base, el) for el in ("Fe", "Al", "Cu", "Co", "Ni")}

    print("\n--- Q1/Q3: neutralisation of the PLS at 55 C — fraction of each metal STILL DISSOLVED after hydroxides equilibrate ---")
    print(f"{'pH':>4} {'Fe':>6} {'Al':>6} {'Cu':>6} {'Co':>6} {'Ni':>6}   {'Fe(III)-gluc':>12}")
    for pH in (2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 7.0, 8.0):
        s = titrate(base, pH)
        fr = {el: dissolved(s, el) / tot0[el] for el in tot0}
        print(f"{pH:>4} {fr['Fe']:>6.3f} {fr['Al']:>6.3f} {fr['Cu']:>6.3f} {fr['Co']:>6.3f} {fr['Ni']:>6.3f}   {fe3_bound(s):>12.2f}")
        s.forget()

    print("\n--- Q1 sensitivity: Fe(III)-gluconate log K (the uncertain constant) — Fe still dissolved at pH 3.5 and 4.5 ---")
    print(f"{'logK':>5} {'Fe diss pH3.5':>14} {'Fe diss pH4.5':>14} {'Fe-gluc pH3.5':>14}")
    for lk in (2.0, 3.5, 5.0, 6.5, 8.0, 10.0):
        try:
            pp2 = make_pp(lk); b2 = solution(pp2, comp, 2.5); t0 = dissolved(b2, "Fe")
            s35 = titrate(b2, 3.5); s45 = titrate(b2, 4.5)
            print(f"{lk:>5} {dissolved(s35,'Fe')/t0:>14.3f} {dissolved(s45,'Fe')/t0:>14.3f} {fe3_bound(s35):>14.2f}")
        except Exception:
            print(f"{lk:>5}   no convergence (ionic strength beyond the Davies model at this log K)")

    print("\n--- Q2: solubility ceiling on Cu / Al at leach pH? (saturation indices, no precipitation allowed) ---")
    for pH in (2.5, 3.0, 3.5):
        s = solution(pp, comp, pH)
        print(f"  pH {pH}: SI Gibbsite {s.si('Gibbsite'):6.2f} · Al(OH)3(am) {s.si('Al(OH)3(am)'):6.2f} · Tenorite {s.si('Tenorite'):6.2f} · Cu(OH)2 {s.si('Cu(OH)2'):6.2f} · Ferrihydrite {s.si('Ferrihydrite'):6.2f}")
        s.forget()
    assert abs(base.pH - 2.5) < 0.05
    assert imb > 0, "expected a cation excess in the as-modelled liquor"
    print("\nNotes: 25 C constants for gluconate species (no dH available); ionic strength ~1 M is beyond the Davies range — treat as indicative.")
