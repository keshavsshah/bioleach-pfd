"""Revenue floor on CITED prices only. USGS MCS 2026 for Co/Ni contained metal;
a peer-reviewed LFP-recycling TEA for Li3PO4. No paywalled salt assessments used."""
LB_T = 2204.62
MW = dict(CoSO4_7H2O=281.09, Co=58.93, NiSO4_6H2O=262.84, Ni=58.69, Li3PO4=115.79)
PROD = dict(CoSO4_7H2O=3065.0, NiSO4_6H2O=6324.0, Li3PO4=1831.0)   # t/yr, closed balance

co_t = PROD["CoSO4_7H2O"] * MW["Co"] / MW["CoSO4_7H2O"]
ni_t = PROD["NiSO4_6H2O"] * MW["Ni"] / MW["NiSO4_6H2O"]

# USGS MCS 2026, CY2025 annual averages
CO_LME, CO_SPOT = 15.0 * LB_T, 21.0 * LB_T      # $/t Co
NI_LME = 15_000.0                                # $/t Ni
LI3PO4_LO, LI3PO4_HI = 2_070.0, 3_900.0          # $/t salt, Materials 19(4) 674 (2026)

def band(lo, hi): return f"${lo/1e6:,.1f}M - ${hi/1e6:,.1f}M"

co = (co_t * CO_LME, co_t * CO_SPOT)
ni = (ni_t * NI_LME, ni_t * NI_LME)
li = (PROD["Li3PO4"] * LI3PO4_LO, PROD["Li3PO4"] * LI3PO4_HI)
tot = tuple(sum(x) for x in zip(co, ni, li))

print(f"Contained metal: Co {co_t:,.0f} t/yr | Ni {ni_t:,.0f} t/yr\n")
print(f"{'stream':<26}{'revenue band':>24}{'share of midpoint':>20}")
print("-" * 70)
mid_tot = sum(tot) / 2
for name, v in (("Cobalt (as contained Co)", co), ("Nickel (as contained Ni)", ni), ("Lithium (as Li3PO4)", li)):
    print(f"{name:<26}{band(*v):>24}{(v[0]+v[1])/2/mid_tot:>19.0%}")
print("-" * 70)
print(f"{'TOTAL (floor)':<26}{band(*tot):>24}")

# self-check: contained metal can never exceed the salt it came from
assert co_t < PROD["CoSO4_7H2O"] and ni_t < PROD["NiSO4_6H2O"]
assert abs(co_t / PROD["CoSO4_7H2O"] - 0.2097) < 1e-3, "Co fraction in the heptahydrate"
assert abs(ni_t / PROD["NiSO4_6H2O"] - 0.2233) < 1e-3, "Ni fraction in the hexahydrate"
assert tot[0] < tot[1], "band must be ordered"
print("\nchecks pass")
