"""Sensitivity: what narrows the operating-cost gap to mineral-acid hydrometallurgy.

Baseline is opex.py. Each lever is applied to the same closed mass balance;
only the price or the recycle fraction changes. Prices are estimates (see opex.py).

Run: python3 I-cost-estimate/levers.py
"""
import io, contextlib, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "G-mass-balance"))
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    import mass_balance as m

HOURS = 8000
s = m.streams
glucose_tpy = s["S-201"]["glucose"] * HOURS / 1000
other_reagents = (s["S-301"]["total"] + s["S-514"]["total"]
                  + sum(s[n]["total"] for n in ("S-406","S-410","S-502","S-507") if n in s)
                  ) * HOURS / 1000
mvr_kwh = m.equipment["E-501"]["value"] * 30 * HOURS
steam_t = m.equipment["D-601"]["value"] * 1.3 * HOURS

P_GLU_SYRUP, P_GLU_STOVER = 525, 150      # $/t, mid-case syrup vs stover hydrolysate
P_KWH, P_STEAM, FIXED = 0.085, 15, 8.72e6  # labour + maintenance from opex.py

def total(glu_price, glu_tpy, mvr, steam):
    return (glu_tpy*glu_price + other_reagents*450 + mvr*P_KWH + steam*P_STEAM
            + 600*HOURS*P_KWH + FIXED)      # 600 kW air+misc

base = total(P_GLU_SYRUP, glucose_tpy, mvr_kwh, steam_t)
print(f"{'case':<46}{'opex $M/yr':>12}{'vs base':>10}")
print("-" * 70)
print(f"{'baseline (glucose syrup, once-through)':<46}{base/1e6:>12.1f}{'':>10}")

cases = [
 ("carbon source: corn stover hydrolysate",
  total(P_GLU_STOVER, glucose_tpy, mvr_kwh, steam_t)),
 ("BMED acid recycle, 70 % of gluconate returned",
  total(P_GLU_SYRUP, glucose_tpy*0.30, mvr_kwh, steam_t)),
 ("titre 150 -> 250 g/L (smaller evaporator, 9.1 t/h)",
  total(P_GLU_SYRUP, glucose_tpy, 9.1*30*HOURS, steam_t)),
 ("all three together",
  total(P_GLU_STOVER, glucose_tpy*0.30, 9.1*30*HOURS, steam_t)),
]
for name, v in cases:
    print(f"{name:<46}{v/1e6:>12.1f}{(v-base)/1e6:>+10.1f}")

REV_LO, REV_HI = 46.2e6, 58.1e6
best = cases[-1][1]
print("-" * 70)
print(f"Revenue floor ${REV_LO/1e6:.1f}M-${REV_HI/1e6:.1f}M.")
print(f"Baseline margin  ${(REV_LO-base)/1e6:+.1f}M to ${(REV_HI-base)/1e6:+.1f}M")
print(f"All-levers margin ${(REV_LO-best)/1e6:+.1f}M to ${(REV_HI-best)/1e6:+.1f}M")

assert best < base, "levers must reduce cost"
assert cases[0][1] < base and cases[1][1] < base
