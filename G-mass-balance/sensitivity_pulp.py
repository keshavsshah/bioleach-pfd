"""Sensitivity: pulp density (water side) and acid multiple (acid side) on the black-mass bioleach balance.

Runs mass_balance.py as a subprocess with PULP / GA_SCALE overrides and plots small multiples.
Output: sensitivity_pulp.png + a table on stdout.   Run: python3 G-mass-balance/sensitivity_pulp.py
"""
import json, os, subprocess
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

def run(**env):
    e = {**os.environ, "GA_BALANCE": "0", **{k: str(v) for k, v in env.items()}}   # INL-shape basis for the sweeps
    return json.loads(subprocess.check_output(["python3", str(Path(__file__).resolve().parent / "mass_balance.py"), "--json"], env=e, text=True))

pulps = [0.025, 0.04, 0.05, 0.06, 0.08, 0.10]
scales = [1, 2, 3, 4, 5, 6]
A = [run(PULP=p) for p in pulps]                       # acid scaled with pulp (INL ratio)
B = [run(PULP=0.10, GA_SCALE=k) for k in scales]       # extra acid at 10 % pulp

print(f"{'pulp %':>7} {'GA mM':>6} {'ratio':>6} {'R-301 m3':>9} {'evap t/h':>9} {'S-104 t/h':>10} {'R-202 m3':>9} {'NaOH kg/h':>10}")
for r in A: print(f"{r['pulp']*100:>7.1f} {r['ga_mM']:>6.0f} {r['charge_ratio']:>6.2f} {r['r301_m3']:>9.0f} {r['evap_tph']:>9.1f} {r['s104_kgh']/1000:>10.2f} {r['r202_m3']:>9.0f} {r['naoh_kgh']:>10.0f}")
print(f"\n{'acid x':>7} {'GA mM':>6} {'ratio':>6} {'R-202 m3':>9} {'glucose':>8} {'broth m3/h':>10} {'NaOH kg/h':>10} {'brine Na':>9} {'S-104 t/h':>10}")
for k, r in zip(scales, B): print(f"{k:>7} {r['ga_mM']:>6.0f} {r['charge_ratio']:>6.2f} {r['r202_m3']:>9.0f} {r['glucose_kgh']:>8.0f} {r['broth_m3h']:>10.1f} {r['naoh_kgh']:>10.0f} {r['brine_na_kgh']:>9.0f} {r['s104_kgh']/1000:>10.2f}")

INK, MUTED, GRID = "#111111", "#5C616B", "#D9D6CC"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(2, 4, figsize=(11, 5.6), facecolor="#F7F5EE")
def panel(a, x, y, title, unit, xlabel, fmt="{:.0f}", ylim0=True):
    a.set_facecolor("#F7F5EE"); a.grid(True, color=GRID, lw=0.6); a.set_axisbelow(True)
    a.plot(x, y, color=INK, lw=2, marker="o", ms=5, mfc="#F7F5EE", mew=1.6)
    a.annotate(fmt.format(y[-1]), (x[-1], y[-1]), xytext=(4, 4), textcoords="offset points", fontsize=8, color=INK)
    a.annotate(fmt.format(y[0]), (x[0], y[0]), xytext=(4, -10), textcoords="offset points", fontsize=8, color=INK)
    a.set_title(f"{title}  ({unit})", fontsize=9.5, color=INK, loc="left"); a.set_xlabel(xlabel, fontsize=8.5)
    if ylim0: a.set_ylim(bottom=0)
xp = [r["pulp"] * 100 for r in A]
panel(ax[0,0], xp, [r["r301_m3"] for r in A], "R-301 batch tank", "m³ each", "pulp density, %")
panel(ax[0,1], xp, [r["evap_tph"] for r in A], "E-501 evaporation", "t/h water", "pulp density, %", "{:.1f}")
panel(ax[0,2], xp, [r["s104_kgh"]/1000 for r in A], "S-104 make-up water", "t/h", "pulp density, %", "{:.1f}")
panel(ax[0,3], xp, [r["charge_ratio"] for r in A], "Charge ratio, anions/cations", "–", "pulp density, %", "{:.2f}")
ax[0,3].axhline(1, color=MUTED, lw=1, ls="--"); ax[0,3].set_ylim(0, 1.1)
xs = scales
panel(ax[1,0], xs, [r["charge_ratio"] for r in B], "Charge ratio at 10 % pulp", "–", "acid multiple on 300 mM", "{:.2f}")
ax[1,0].axhline(1, color=MUTED, lw=1, ls="--"); ax[1,0].set_ylim(0, 1.6)
panel(ax[1,1], xs, [r["r202_m3"] for r in B], "R-202 fermenter", "m³ each", "acid multiple on 300 mM")
panel(ax[1,2], xs, [r["naoh_kgh"] for r in B], "NaOH, Sheets 4–5", "kg/h", "acid multiple on 300 mM")
panel(ax[1,3], xs, [r["brine_na_kgh"] for r in B], "Na in brine bleed", "kg/h", "acid multiple on 300 mM")
fig.suptitle("Black-mass bioleach — what pulp density moves (top) vs what the acid budget moves (bottom)", fontsize=10.5, color=INK, x=0.01, ha="left")
fig.text(0.01, 0.005, "Top row: gluconate scaled with pulp at INL's ratio (75 mM at 2.5 %) — fermenters, glucose, NaOH and the charge ratio are flat because acid demand is set by the solids. "
         "Bottom row: extra acid at 10 % pulp — charge balance needs ~6× (1.8 M), and every kg of acid returns as NaOH and sodium.", fontsize=7.5, color=MUTED, wrap=True)
fig.tight_layout(rect=(0, 0.06, 1, 0.95)); fig.savefig(Path(__file__).resolve().parent / "sensitivity_pulp.png", dpi=160, facecolor=fig.get_facecolor())
print("\nwrote sensitivity_pulp.png")
