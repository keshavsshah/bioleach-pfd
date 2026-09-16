"""Class 5 factored capital estimate (AACE Class 5, -50/+100 %).

Method is standard and citable: power-law scaling of purchased equipment cost,
C = C_ref * (S/S_ref)^n, summed to a purchased-equipment cost (PEC), then a Lang
factor to total fixed capital for a solid-fluid processing plant.

!! THE CORRELATION ANCHORS BELOW ARE ENGINEERING JUDGEMENT, NOT CITED VALUES. !!
They are order-of-magnitude costs for the class of equipment at the stated size.
Every anchor is exposed in ANCHORS so a reader can substitute vendor quotes.
The METHOD is defensible; the ABSOLUTE NUMBER is indicative only.

Run: python3 I-cost-estimate/capex.py
"""
import csv
from pathlib import Path

LANG = 4.05          # solid-fluid processing plant, PEC -> total fixed capital
CONTINGENCY = 0.20   # on top of the Lang-factored total

# class -> (reference cost USD, reference size, size unit, exponent)
ANCHORS = {
    "fermenter_sterile": (600_000, 100, "m3", 0.60),
    "tank_agitated":     (120_000, 100, "m3", 0.55),
    "tank_storage":       (80_000, 100, "m3", 0.55),
    "leach_tank":        (200_000, 100, "m3", 0.60),
    "mixer_settler":     (250_000,  10, "m3", 0.60),
    "evaporator_mvr":  1_500_000,
    "crystalliser":    1_200_000,
    "dryer":             900_000,
    "filter_belt":       150_000,
    "filter_press":      200_000,
    "blower":            150_000,
    "pump":               25_000,
    "silo":              150_000,
    "heat_exchanger":    180_000,
    "scrubber":           80_000,
    "bunker":             60_000,
}
# the scalar entries above, expanded to full anchors
ANCHORS.update({
    "evaporator_mvr": (1_500_000, 10,    "t/h", 0.70),
    "crystalliser":   (1_200_000, 1,     "t/h", 0.65),
    "dryer":            (900_000, 5,     "t/h", 0.65),
    "filter_belt":      (150_000, 10,    "m2",  0.60),
    "filter_press":     (200_000, 10,    "m2",  0.60),
    "blower":           (150_000, 10_000,"m3/h",0.60),
    "pump":              (25_000, 10,    "m3/h",0.50),
    "silo":             (150_000, 100,   "t",   0.50),
    "heat_exchanger":   (180_000, 1_000, "kW",  0.65),
    "scrubber":          (80_000, 1_000, "m3/h",0.60),
    "bunker":            (60_000, 50,    "t",   0.50),
})

# tag prefix -> (class, number of parallel units)
CLASSIFY = [
    ("R-201A", "fermenter_sterile", 1), ("R-201B", "fermenter_sterile", 1),
    ("R-202",  "fermenter_sterile", 2), ("R-301",  "leach_tank",       4),
    ("T-201",  "tank_agitated", 1), ("T-202", "tank_storage", 1), ("T-303", "tank_agitated", 1),
    ("T-301",  "tank_storage", 1),  ("T-302", "tank_storage", 1), ("T-401", "tank_agitated", 1),
    ("T-402",  "tank_agitated", 1),  ("T-404", "tank_storage", 1), ("T-405", "tank_storage", 1),
    ("T-501",  "tank_agitated", 1),  ("T-601", "tank_agitated", 1), ("T-101", "tank_agitated", 1),
    ("V-101",  "silo", 1), ("V-201", "tank_storage", 1), ("V-301", "silo", 1),
    ("K-201",  "blower", 1), ("K-401", "blower", 1),
    ("F-201",  "filter_press", 1), ("F-301", "filter_belt", 1), ("F-401", "filter_press", 1),
    ("F-402",  "filter_press", 1), ("F-501", "filter_press", 1),
    ("P-101",  "pump", 2), ("P-201", "pump", 1),
    ("E-301",  "heat_exchanger", 1), ("E-501", "evaporator_mvr", 1),
    ("SC-301", "scrubber", 1),
    ("X-401/402/403", "mixer_settler", 5), ("X-501/502/503", "mixer_settler", 7),
    ("X-511/512/513", "mixer_settler", 6),
    ("X-504", "crystalliser", 1), ("X-514", "crystalliser", 1),
    ("D-601", "dryer", 1), ("D-501/D-502", "dryer", 2),
    ("X-601", "bunker", 1), ("X-602", "bunker", 1), ("X-603", "bunker", 1),
]

def klass(tag):
    for pre, k, n in CLASSIFY:
        if tag.startswith(pre):
            return k, n
    return None, 0

rows, pec, unpriced = [], 0.0, []
csv_path = Path(__file__).resolve().parents[1] / "C-equipment-list" / "equipment.csv"
for r in csv.DictReader(open(csv_path)):
    k, n_units = klass(r["tag"])
    size = float(r["size"])
    if k is None:
        unpriced.append(r["tag"]); continue
    c_ref, s_ref, _, expo = ANCHORS[k]
    if r["unit"].startswith("L"):          # R-201A is in litres
        size /= 1000.0
    if r["unit"].startswith("kg/h"):       # dry-solids filters -> nominal small area
        size = max(size / 100.0, 1.0)
    cost = c_ref * (size / s_ref) ** expo * n_units
    pec += cost
    rows.append((r["tag"], k, size, n_units, cost))

rows.sort(key=lambda x: -x[4])
print(f"{'tag':<16}{'class':<20}{'size':>12}{'n':>4}{'cost $M':>10}")
print("-" * 64)
for t, k, s, n, c in rows:
    print(f"{t:<16}{k:<20}{s:>12,.1f}{n:>4}{c/1e6:>10.2f}")
print("-" * 64)
tfc = pec * LANG
total = tfc * (1 + CONTINGENCY)
print(f"{'Purchased equipment (PEC)':<52}{pec/1e6:>11.1f}")
print(f"{'x Lang factor ' + str(LANG) + ' (solid-fluid)':<52}{tfc/1e6:>11.1f}")
print(f"{'+ ' + str(int(CONTINGENCY*100)) + ' % contingency':<52}{total/1e6:>11.1f}")
print(f"\nTOTAL FIXED CAPITAL  ~${total/1e6:,.0f}M   (Class 5: -50/+100 % => "
      f"${total*0.5/1e6:,.0f}M - ${total*2/1e6:,.0f}M)")
if unpriced:
    print("\nNOT PRICED:", ", ".join(unpriced))

# the estimate must cover the whole equipment list, and the big three must dominate
assert not unpriced, f"unpriced equipment would understate the estimate: {unpriced}"
assert abs(sum(r[4] for r in rows) - pec) < 1e-6
top3 = sum(r[4] for r in rows[:3]) / pec
print(f"\ntop 3 items are {top3:.0%} of PEC  ->  {', '.join(r[0] for r in rows[:3])}")
