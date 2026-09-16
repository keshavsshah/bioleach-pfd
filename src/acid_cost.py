"""Why the bioleach costs more: acid cost per equivalent of acidity.

This is the structural economic result. Gluconic acid is monoprotic and heavy;
sulphuric acid is diprotic and light and is made from a waste sulphur stream.
Per equivalent of acidity delivered to the leach, they are not close.

Prices are estimates (see opex.py). Stoichiometry is exact.
Run: python3 src/acid_cost.py
"""
EQ_W = {"sulphuric": 98.08 / 2,    # diprotic
        "gluconic":  196.16 / 1}   # monoprotic

# gluconic acid is bought as glucose and fermented: 1 mol glucose -> 1 mol gluconic
GLU_MW, GA_MW, GLU_YIELD = 180.16, 196.16, 0.90

PRICE = {"sulphuric ($/t)": (100, 150), "glucose ($/t)": (400, 650)}

def per_keq(price_t, eq_weight_g):
    """$ per kilo-equivalent of acidity."""
    return price_t / 1000 * eq_weight_g          # $/t * t/kg * g/eq -> $/keq

print(f"{'acid':<28}{'$/keq low':>12}{'$/keq high':>12}")
print("-" * 52)
s_lo, s_hi = (per_keq(p, EQ_W["sulphuric"]) for p in PRICE["sulphuric ($/t)"])
print(f"{'sulphuric (diprotic)':<28}{s_lo:>12.2f}{s_hi:>12.2f}")

# glucose needed per equivalent of gluconic acid
glu_per_eq = EQ_W["gluconic"] / GA_MW * GLU_MW / GLU_YIELD    # g glucose per eq
g_lo, g_hi = (per_keq(p, glu_per_eq) for p in PRICE["glucose ($/t)"])
print(f"{'gluconic (from glucose)':<28}{g_lo:>12.2f}{g_hi:>12.2f}")
print("-" * 52)
print(f"gluconic costs {g_lo/s_hi:.0f}x to {g_hi/s_lo:.0f}x more per equivalent of acidity")
print(f"\nand that is before the fermenter, the air, and the evaporator "
      f"that a {GLU_YIELD:.0%}-yield broth requires.")

assert glu_per_eq > EQ_W["gluconic"], "glucose mass must exceed the acid it makes at <100% yield"
assert g_lo > s_hi, "the whole point is that gluconic is the dearer acid"
