"""Annual operating cost, and the margin against the revenue floor.

!! REAGENT AND UTILITY PRICES BELOW ARE ESTIMATES, NOT CITED VALUES. !!
They are ordinary industrial ranges, exposed in PRICES so they can be replaced.
Consumption quantities ARE from the closed mass balance and are not estimates.
Revenue comes from revenue_floor.py, which uses published USGS benchmarks.

Run: python3 I-cost-estimate/opex.py
"""
import io, contextlib, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "G-mass-balance"))

buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    import mass_balance as m

HOURS = 8000                      # operating hours per year

# ---- estimated unit prices (low, high) in $/t unless noted -----------------
PRICES = {
    "glucose syrup (dry basis)": (400, 650),
    "ferrous sulphate heptahydrate": (150, 250),
    "sodium hydroxide": (400, 600),
    "trisodium phosphate": (700, 1000),
    "power ($/kWh)": (0.07, 0.10),
    "steam ($/t)": (10, 20),
}

s = m.streams
qty = {
    "glucose syrup (dry basis)":     s["S-201"]["glucose"] * HOURS / 1000,
    "ferrous sulphate heptahydrate": s["S-301"]["total"]   * HOURS / 1000,
    "trisodium phosphate":           s["S-514"]["total"]   * HOURS / 1000,
    "sodium hydroxide": sum(s[n]["total"] for n in ("S-406","S-410","S-502","S-507")
                            if n in s) * HOURS / 1000,
}

# ---- utilities, derived from the balance ----------------------------------
air_kw   = 24_053/3600 * 70_000 / 0.70 / 1000      # blower: Q*dp/eta
mvr_kw   = m.equipment["E-501"]["value"] * 30       # 30 kWh per t evaporated
misc_kw  = 500                                      # agitators, pumps, SX
qty["power ($/kWh)"] = (air_kw + mvr_kw + misc_kw) * HOURS
qty["steam ($/t)"]   = (m.equipment["D-601"]["value"] * 1.3          # dryer
                        + m.equipment["E-301"]["value"] / 1000 * 1.6 # preheat
                        ) * HOURS

lo_tot = hi_tot = 0.0
print(f"{'input':<34}{'quantity/yr':>16}{'$M low':>10}{'$M high':>10}")
print("-" * 70)
for k, (plo, phi) in PRICES.items():
    q = qty[k]
    lo, hi = q * plo, q * phi
    lo_tot += lo; hi_tot += hi
    unit = "kWh" if "kWh" in k else "t"
    print(f"{k:<34}{q:>13,.0f} {unit:<3}{lo/1e6:>9.1f}{hi/1e6:>10.1f}")

LABOUR, MAINT_PCT, TFC = 4.0e6, 0.04, 118e6
fixed = LABOUR + MAINT_PCT * TFC
print("-" * 70)
print(f"{'variable subtotal':<34}{'':>16}{lo_tot/1e6:>10.1f}{hi_tot/1e6:>10.1f}")
print(f"{'labour + maintenance (4 % of TFC)':<34}{'':>16}{fixed/1e6:>10.1f}{fixed/1e6:>10.1f}")
lo_tot += fixed; hi_tot += fixed
print(f"{'TOTAL OPERATING COST':<34}{'':>16}{lo_tot/1e6:>10.1f}{hi_tot/1e6:>10.1f}")

REV_LO, REV_HI = 46.2e6, 58.1e6          # revenue_floor.py, cited USGS basis
print(f"\nRevenue floor (cited): ${REV_LO/1e6:.1f}M - ${REV_HI/1e6:.1f}M")
print(f"Gross margin: best case ${(REV_HI-lo_tot)/1e6:+.1f}M   "
      f"worst case ${(REV_LO-hi_tot)/1e6:+.1f}M")

feed_t = m.FEED_KGH * HOURS / 1000
print(f"\nPer tonne of black mass ({feed_t:,.0f} t/yr):")
print(f"  operating cost  ${lo_tot/feed_t:,.0f} - ${hi_tot/feed_t:,.0f}/t")
print(f"  revenue floor   ${REV_LO/feed_t:,.0f} - ${REV_HI/feed_t:,.0f}/t")

glu_share = qty["glucose syrup (dry basis)"] * PRICES["glucose syrup (dry basis)"][1] / hi_tot
print(f"\nGlucose alone is {glu_share:.0%} of the high-case operating cost.")

assert lo_tot < hi_tot and REV_LO < REV_HI
assert abs(feed_t - 10_000) < 1, "feed basis should be 10,000 t/yr"
