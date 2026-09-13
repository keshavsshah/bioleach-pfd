"""Proton / sodium budget of a barren-raffinate recycle loop (Option A, 2026-09-13).
Question: if S-512 returns to R-301, how much fresh gluconic acid does the fermenter still have to make,
how much Na enters per pass, and what bleed does Na-gluconate solubility force? Uses mass_balance.py metals.
Gluconate is a 1 M buffer (pKa 3.86): Gluc- fraction f(pH) = 1/(1+10^(pKa-pH)). Electroneutrality: Gluc- = sum(z*M) + Na - 2*SO4.
"""
import mass_balance as mb
PKA = 3.86
f = lambda pH: 1 / (1 + 10 ** (PKA - pH))
st = mb.streams; MW = mb.MW; Z = mb.Z
kmol = lambda s, m: st[s][m] / MW[m]
liq_m3 = st["S-309"]["total"] / 1000                        # PLS volume basis, m3/h
G = st["S-309"]["GA"] / mb.GA_MW                              # kmol gluconate circulating
so4_eq = 2 * st["S-309"]["SO4"] / 96.06
metal_eq = sum(Z[m] * kmol("S-309", m) for m in Z) + 3 * st["S-309"]["Fe"] / 55.85
GA_EXCESS = 1.15   # mass_balance.py balances exactly (zero free acid -> pH undefined). A real leach needs surplus acid; assume 15 %.
G = max(G, GA_EXCESS * (metal_eq - so4_eq))
import math
def pH_of(anion): return PKA + math.log10(max(anion, 1e-6) / max(G - anion, 1e-6))
print(f"Loop liquor {liq_m3:.1f} m3/h · gluconate {G:.1f} kmol/h ({G/liq_m3:.2f} M) · metal cations {metal_eq:.1f} keq/h · sulfate {so4_eq:.1f} keq/h")

# --- pH the PLS can actually sit at (all gluconate needed as anion) ---
gluc_anion = metal_eq - so4_eq
pH_pls = pH_of(gluc_anion)
print(f"PLS pH forced by charge balance: {pH_pls:.2f} (Gluc- {gluc_anion:.1f} of {G:.1f} kmol)")

# --- walk the downstream units at their pH set-points; NaOH = what it takes to hold the set-point ---
units = [("T-401 cementation (Cu out, Fe2+ in)", None, {"Cu": -kmol("S-401","Cu")*0.99}, {"Fe2": +kmol("S-401","Cu")*0.99}),
         ("T-402 Fe/Al hydroxide, pH 5.5", 5.5, {"Fe": -3*st["S-404"]["Fe"]/55.85, "Al": -3*kmol("S-404","Al")}, {}),
         ("X-401 Mn SX (D2EHPA), pH 4.2", 4.2, {"Mn": -2*kmol("S-409","Mn")*0.98}, {}),
         ("X-501 Co SX (Cyanex 272), pH 5.5", 5.5, {"Co": -2*kmol("S-501","Co")*0.99}, {}),
         ("X-511 Ni SX (Versatic 10), pH 6.5", 6.5, {"Ni": -2*kmol("S-501","Ni")*0.98}, {})]
cat_eq = metal_eq; na = 0.0; print("\nunit                                  cations keq  Na added kmol  pH after")
for name, pH_set, d_eq, _ in units:
    cat_eq += sum(d_eq.values()) + (2*kmol("S-401","Cu")*0.99 if "cementation" in name else 0)   # Fe2+ replaces Cu2+
    if pH_set is None:
        pH = pH_of(cat_eq + na - so4_eq); print(f"{name:38s}{cat_eq:9.1f}{0:14.1f}{pH:10.2f}"); continue
    need = G * f(pH_set) - (cat_eq + na - so4_eq)              # extra anion needed to reach set-point -> Na+
    add = max(need, 0.0); na += add
    print(f"{name:38s}{cat_eq:9.1f}{add:14.1f}{pH_set:10.2f}")
print(f"\nNa added per pass: {na:.1f} kmol/h = {na*23:,.0f} kg/h (mass_balance.py single-pass basis: {mb.streams['S-516']['Na']:,.0f} kg/h)")
hgluc_back = G - (cat_eq + na - so4_eq)
print(f"Raffinate returning to R-301: Gluc- {G-hgluc_back:.1f} kmol as Na-gluconate, free acid HGluc {hgluc_back:.1f} kmol -> covers {hgluc_back/metal_eq*100:.0f} % of the leach's proton demand")
print(f"Fresh gluconic acid still required from R-202: {(metal_eq - so4_eq - hgluc_back)*mb.GA_MW:,.0f} kg/h (single-pass basis {mb.ga_kgh:,.0f} kg/h)")

# --- bleed forced by Na-gluconate solubility ---
NAGLUC_SOL_GL = 590.0; na_max_gl = NAGLUC_SOL_GL * 23 / 218.1
bleed_m3 = na * 23 / na_max_gl
li = st["S-309"]["Li"]
print(f"\nNa-gluconate solubility ~{NAGLUC_SOL_GL:.0f} g/L -> Na <= {na_max_gl:.0f} g/L -> minimum bleed {bleed_m3:.1f} m3/h of {liq_m3:.1f} (recycle {1-bleed_m3/liq_m3:.0%})")
print(f"Li in that bleed: {li/bleed_m3:.1f} g/L (Li2CO3 precipitation wants >= 15-25 g/L; Li3PO4 works at ~2 g/L)")
print(f"Water check at {mb.PULP:.0%} pulp: broth {mb.broth_h2o/1000:.1f} + recycle {(liq_m3-bleed_m3):.1f} m3/h vs liquor allowed {mb.liquor_kgh/1000:.1f} m3/h")
