"""Write the stream table, equipment list and key metrics to data/ as CSV.

Run from anywhere:  python3 src/export_tables.py
These CSVs are the machine-readable form of the tables in pfd/bioleach_PFD_index.html.
"""
import csv, io, contextlib, sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
OUT = SRC.parent / "data" / "streams"
sys.path.insert(0, str(SRC))

buf = io.StringIO()
with contextlib.redirect_stdout(buf):          # the module prints its summary on import
    import mass_balance as m

OUT.mkdir(parents=True, exist_ok=True)

# --- streams ---------------------------------------------------------------
cols = ["total"] + m.COLS + ["T"]
with open(OUT / "streams.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["stream", "from", "to", "phase"] + cols)
    for no in m.ORDER:
        if no not in m.streams:
            continue
        r = m.streams[no]
        w.writerow([no, r["frm"], r["to"], r["phase"]] + [round(r[c], 3) for c in cols])

# --- equipment -------------------------------------------------------------
with open(OUT / "equipment.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["tag", "service", "size", "unit", "basis"])
    for tag, e in m.equipment.items():
        w.writerow([tag, e["service"], round(e["value"], 3), e["unit"], e["basis"]])

# --- headline numbers ------------------------------------------------------
rows = [
    ("black mass feed",        m.FEED_KGH,        "kg/h"),
    ("pulp density",           m.PULP,            "fraction"),
    ("broth titre",            m.BROTH_GA_GL,     "g/L gluconic acid"),
    ("gluconate in liquor",    m.GA_MM,           "mM"),
    ("crystalliser per-pass",  m.CRYST_YIELD,     "fraction"),
    ("crystalliser overall",   m.CRYST_REC,       "fraction"),
    ("gluconic acid pKa",      m.PKA_GA,          "-"),
]
with open(OUT / "key_parameters.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["parameter", "value", "unit"])
    w.writerows([(n, round(v, 4), u) for n, v, u in rows])

# the export must not silently drop streams the model defines
assert len({*m.streams} - {*m.ORDER}) == 0, "ORDER is missing streams the model built"
print(f"wrote {len(list(OUT.glob('*.csv')))} CSVs to {OUT}")
