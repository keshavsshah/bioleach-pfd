"""VOID 2026-09-13 - the price anchors here are UNSOURCED. They came from the retired
TEA, which Keshav disregarded. Stoichiometry, tonnages and reagent ratios are sound;
every dollar figure is not. Do not cite the paybacks until a cited price basis exists.

Is on-site Li3PO4 -> Li2CO3 / LiOH.H2O conversion worth the capital?
Class 5 screening (+/-50%). Run: python3 li_upgrade.py"""
MW = dict(Li3PO4=115.79, Li2CO3=73.89, LiOHH2O=41.96, H2SO4=98.08,
          Na2CO3=105.99, CaOH2=74.09, Ca3PO42=310.18, Li=6.941)
LI_F = {k: (3 if k=="Li3PO4" else 2 if k=="Li2CO3" else 1)*MW["Li"]/MW[k]
        for k in ("Li3PO4","Li2CO3","LiOHH2O")}

FEED_TPY   = 1821.0                 # Li3PO4 from the closed balance
CONV_REC   = 0.92                   # Li recovery through conversion
P_LI2CO3   = 18_500                 # $/t battery grade (existing TEA anchor)
P_LIOH     = 19_000                 # $/t LiOH.H2O
REAGENT    = dict(H2SO4=150, Na2CO3=300, CaOH2=120)   # $/t
# bolt-on capex, shares site utilities; $/t-yr of finished product
CAPEX_RATE = dict(carbonate=8_500, hydroxide=10_500)
ADD_OPEX   = dict(carbonate=2.5e6, hydroxide=2.0e6)   # $/yr utilities+labour+maint

li_t   = FEED_TPY * LI_F["Li3PO4"]
li_rec = li_t * CONV_REC
kmol   = FEED_TPY * 1000 / MW["Li3PO4"]

def case(name, price, prod_t, reagents, capex_rate, opex):
    rev   = prod_t * price
    rgt   = sum(t * REAGENT[k] for k, t in reagents.items())
    capex = prod_t * capex_rate
    return dict(name=name, prod_t=prod_t, rev=rev, rgt=rgt,
                capex=capex, opex=opex, net=rev - rgt - opex)

carb = case("Li2CO3  (H2SO4 -> Na2CO3)", P_LI2CO3, li_rec/LI_F["Li2CO3"],
            {"H2SO4": 1.5*kmol*MW["H2SO4"]/1000, "Na2CO3": 1.5*kmol*MW["Na2CO3"]/1000},
            CAPEX_RATE["carbonate"], ADD_OPEX["carbonate"])
hyd  = case("LiOH.H2O (lime causticisation)", P_LIOH, li_rec/LI_F["LiOHH2O"],
            {"CaOH2": 1.5*kmol*MW["CaOH2"]/1000},
            CAPEX_RATE["hydroxide"], ADD_OPEX["hydroxide"])

print(f"Li3PO4 {FEED_TPY:,.0f} t/yr = {li_t:.0f} t Li; {li_rec:.0f} t Li recovered at {CONV_REC:.0%}\n")
print(f"{'discount':>9} | {'Li3PO4 $/t':>10} | {'sell as-is':>11} | "
      f"{'Li2CO3 payback':>14} | {'LiOH payback':>12}")
print("-"*72)
for disc in (0.15, 0.30, 0.45, 0.60):
    p_li3po4 = P_LI2CO3 / LI_F["Li2CO3"] * LI_F["Li3PO4"] * (1 - disc)
    base = FEED_TPY * p_li3po4
    row = [f"{disc:>8.0%}", f"{p_li3po4:>10,.0f}", f"${base/1e6:>10.2f}M"]
    for c in (carb, hyd):
        gain = c["net"] - base
        row.append(f"{c['capex']/gain:>13.1f}y" if gain > 0 else f"{'never':>14}")
    print(" | ".join(row))

print()
for c in (carb, hyd):
    print(f"{c['name']}: {c['prod_t']:,.0f} t/yr | rev ${c['rev']/1e6:.2f}M | "
          f"reagents ${c['rgt']/1e6:.2f}M | opex ${c['opex']/1e6:.2f}M | "
          f"capex ${c['capex']/1e6:.1f}M")

# self-check: lithium is conserved through every conversion
for c in (carb, hyd):
    k = "Li2CO3" if "Li2CO3" in c["name"] else "LiOHH2O"
    assert abs(c["prod_t"] * LI_F[k] - li_rec) < 1e-6, c["name"]
assert li_t < FEED_TPY, "Li content cannot exceed the salt mass"
print("\nchecks pass")
