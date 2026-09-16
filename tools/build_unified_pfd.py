"""Build one continuous PFD from the six area sheets.

Not a tiling. Each area's drawing is placed on a single canvas in process order,
the per-sheet furniture (borders, title blocks) and the off-sheet connector
pentagons are stripped, and the streams that used to say "to Sheet 4" are drawn
as real routed lines between the areas. Dashed boxes delineate each area.

Run: python3 tools/build_unified_pfd.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "A-process-flow-diagram" / "bioleach_PFD.html"
OUT = ROOT / "A-process-flow-diagram" / "bioleach_PFD_unified.html"

SW, SH = 1100, 720                       # one area's own coordinate system
GX, GY = 260, 340                        # gutters that carry the inter-area lines
ML, MT, MB = 150, 300, 240               # margins: left, top, bottom

# area -> (column, row). Laid out so the main flow runs left to right.
PLACE = {1: (0, 0), 3: (1, 0), 4: (2, 0), 5: (3, 0), 2: (0, 1), 6: (2, 1)}
TITLES = {1: ("AREA 100", "Feed preparation"),
          2: ("AREA 200", "Biolixiviant fermentation"),
          3: ("AREA 300", "Batch leach · solid/liquid separation"),
          4: ("AREA 400", "Impurity removal · Cu → Fe/Al → Mn"),
          5: ("AREA 500", "Products · Co SX, Ni SX, Li₃PO₄"),
          6: ("AREA 600", "Effluent, by-product salt, residues")}

def org(a):
    c, r = PLACE[a]
    return ML + c * (SW + GX), MT + r * (SH + GY)

W = ML * 2 + 4 * SW + 3 * GX
H = MT + MB + 2 * SH + GY

src = SRC.read_text(encoding="utf-8")
defs = re.search(r"<defs>.*?</defs>", src, re.S).group()
syms = "".join(re.findall(r"<symbol[^>]*>.*?</symbol>", src, re.S))

def clean(body):
    """Strip per-sheet furniture and the off-sheet connector pentagons."""
    body = re.sub(r'<rect x="12" y="12" width="1076" height="696"[^>]*/>', "", body)
    body = re.sub(r'<rect x="20" y="20" width="1060" height="680"[^>]*/>', "", body)
    body = re.sub(r'<line x1="20" y1="676"[^>]*/>', "", body)
    body = re.sub(r'<text x="(?:30|1070)" y="692"[^>]*>.*?</text>', "", body)
    # pentagon + its "Sh N" / "product" label -> gone; the line stub stays and we
    # meet it with a real connector line instead.
    body = re.sub(
        r'<polygon points="(?:[\d.]+,[\d.]+\s){4}[\d.]+,[\d.]+"[^>]*/>'
        r'<text x="[\d.]+" y="[\d.]+"[^>]*>(?:Sh[^<]*|product|Sh 1·2·3)</text>', "", body)
    return body

tiles, boxes = [], []
for a in sorted(PLACE):
    m = re.search(rf'<div class="sheet" id="sheet{a}">\s*<svg[^>]*>(.*?)</svg>', src, re.S)
    x, y = org(a)
    tiles.append(f'<g transform="translate({x},{y})">{clean(m.group(1))}</g>')
    code, name = TITLES[a]
    boxes.append(
        f'<rect x="{x+8}" y="{y+8}" width="{SW-16}" height="{SH-16}" fill="none" '
        f'stroke="#111111" stroke-width="1.6" stroke-dasharray="14 9" rx="6"/>'
        f'<rect x="{x+26}" y="{y-16}" width="{26+len(code)*17+len(name)*8}" height="34" fill="#F7F5EE"/>'
        f'<text x="{x+38}" y="{y+8}" class="area">{code}</text>'
        f'<text x="{x+38+len(code)*17+14}" y="{y+8}" class="areasub">{name}</text>')

# ---- inter-area connections -------------------------------------------------
# (label, kind, [(x,y) …]) in global coordinates. kind: main | recycle | solids
def P(a, lx, ly):
    x, y = org(a); return (x + lx, y + ly)

# routing channels that keep lines out of the drawings
CH_V = {"1-3": ML + SW + GX//2, "3-4": ML + 2*SW + GX + GX//2, "4-5": ML + 3*SW + 2*GX + GX//2}
LANE = [MT + SH + 70, MT + SH + 130, MT + SH + 190, MT + SH + 250]   # horizontal lanes
BOT = MT + 2*SH + GY + 110                                            # bottom highway

def route(src, dst, *, via_x=None, via_y=None, out=0, into=0):
    """Strictly orthogonal path from src to dst.
    out/into extend a short stub before/after turning, so lines leave and meet
    the drawings square-on rather than clipping their edges."""
    pts = [src]
    a = (src[0] + out, src[1]) if out else src
    if out: pts.append(a)
    b = (dst[0] - into, dst[1]) if into else dst
    if via_y is not None and via_x is not None:
        pts += [(a[0], via_y), (via_x, via_y), (via_x, b[1])]
    elif via_x is not None:
        pts += [(via_x, a[1]), (via_x, b[1])]
    elif via_y is not None:
        pts += [(a[0], via_y), (b[0], via_y)]
    if into: pts.append(b)
    pts.append(dst)
    # drop any zero-length or duplicate points
    out_pts = [pts[0]]
    for p in pts[1:]:
        if p != out_pts[-1]: out_pts.append(p)
    return out_pts

L = lambda a, lx, ly: P(a, lx, ly)
CONNS = [
 ("S-105 feed slurry", "main",
  route(L(1,707,622), L(3,28,250), via_x=CH_V["1-3"], out=60, into=60)),
 ("S-212 biolixiviant", "main",
  route(L(2,955,585), L(3,28,320), via_x=CH_V["1-3"]-70, out=60, into=60)),
 ("S-310 PLS", "main",
  route(L(3,1062,600), L(4,24,250), via_x=CH_V["3-4"], out=60, into=60)),
 ("S-414 purified liquor", "main",
  route(L(4,1027,560), L(5,24,315), via_x=CH_V["4-5"], out=60, into=60)),
 ("S-311 wash filtrate", "recycle",
  route(L(3,1062,560), L(1,40,500), via_x=CH_V["3-4"]+70, via_y=LANE[3], out=60, into=-60)),
 ("S-308 leach residue", "solids",
  route(L(3,667,580), L(6,24,450), via_y=LANE[0], into=70)),
 ("S-304 blowdown", "solids",
  route(L(3,1027,200), L(6,24,274), via_x=CH_V["3-4"]-70, via_y=LANE[1], out=50, into=130)),
 ("S-408 Fe/Al cake", "solids",
  route(L(4,563,500), L(6,24,530), via_y=LANE[0], into=190)),
 ("S-403 cement Cu", "solids",
  route(L(4,300,830), L(6,600,530), via_y=LANE[2])),
 ("S-516 brine", "main",
  route(L(5,418,488), L(6,24,100), via_y=LANE[1], into=250)),
 ("S-518 / S-519 purges", "main",
  route(L(5,1032,488), L(6,24,158), via_y=LANE[2], into=310)),
 ("S-210 spent cells", "solids",
  route(L(2,877,620), L(6,24,610), via_y=BOT, into=370)),
 ("S-517 condensate return", "recycle",
  route(L(5,95,660), L(2,28,245), via_x=ML+70, via_y=BOT, out=-70, into=-60)),
 ("S-204 medium surplus", "recycle",
  route(L(2,197,320), L(1,40,540), via_x=ML+70, out=-60, into=-60)),
]

STYLE = {"main": 'stroke="#111111" stroke-width="2.6"',
         "recycle": 'stroke="#111111" stroke-width="2" stroke-dasharray="12 7"',
         "solids": 'stroke="#111111" stroke-width="2.2" stroke-dasharray="3 5"'}

for label, _, pts in CONNS:                       # a PFD has no diagonals
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        assert x1 == x2 or y1 == y2, f"{label}: diagonal segment ({x1},{y1})->({x2},{y2})"

lines = []
for label, kind, pts in CONNS:
    d = f"M{pts[0][0]} {pts[0][1]} " + " ".join(f"L{x} {y}" for x, y in pts[1:])
    lines.append(f'<path d="{d}" fill="none" {STYLE[kind]} marker-end="url(#arr)"/>')
    # label the run on its longest straight segment
    best, bl = None, 0
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        if y1 != y2: continue                      # horizontal runs only
        if abs(x2-x1) > bl: bl, best = abs(x2-x1), ((x1+x2)/2, y1)
    if best is None:
        (x1, y1), (x2, y2) = pts[0], pts[1]; best = ((x1+x2)/2, (y1+y2)/2)
    mx, my = best
    lines.append(f'<rect x="{mx-len(label)*4.6-8}" y="{my-22}" width="{len(label)*9.2+16}" height="26" fill="#F7F5EE"/>'
                 f'<text x="{mx}" y="{my-4}" class="slab" text-anchor="middle">{label}</text>')

svg = f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
{defs}{syms}
<rect width="{W}" height="{H}" fill="#F7F5EE"/>
<text x="{ML}" y="112" class="t1">BLACK MASS BIOLEACH — UNIFIED PROCESS FLOW DIAGRAM</text>
<text x="{ML}" y="158" class="t2">Zero-discharge refinery · 10,000 t/yr spent lithium-ion black mass · gluconic-acid biolixiviant</text>
<text x="{ML}" y="194" class="t3">All six areas on one drawing. Solid lines carry the main process flow; dashed lines are recycles; dotted lines are solids and bleeds. Equipment, sizing, stream tables and notes are in the companion PFD Index.</text>
<line x1="{ML}" y1="222" x2="{W-ML}" y2="222" stroke="#111111" stroke-width="1.6"/>
{chr(10).join(boxes)}
{chr(10).join(tiles)}
{chr(10).join(lines)}
<line x1="{ML}" y1="{H-90}" x2="{W-ML}" y2="{H-90}" stroke="#111111" stroke-width="1"/>
<text x="{ML}" y="{H-58}" class="t4">github.com/keshavsshah/bioleach-pfd</text>
<text x="{W-ML}" y="{H-58}" class="t4" text-anchor="end">Keshav Shah · unified flowsheet, areas 100–600</text>
</svg>'''

pw, ph = W / 3.4, H / 3.4
html = f'''<!doctype html><meta charset="utf-8"><title>Unified PFD</title>
<style>
@page{{size:{pw:.2f}mm {ph:.2f}mm;margin:0}}
html,body{{margin:0;padding:0;background:#F7F5EE;overflow:hidden}}
svg{{display:block;width:{pw:.2f}mm;height:{ph:.2f}mm}}
text{{font-family:"Helvetica Neue",Arial,sans-serif}}
.t1{{font:700 46px/1 "Helvetica Neue",Arial,sans-serif;fill:#111;letter-spacing:.05em}}
.t2{{font:400 24px/1 "Helvetica Neue",Arial,sans-serif;fill:#111}}
.t3{{font:400 17px/1 "Helvetica Neue",Arial,sans-serif;fill:#4A4F58}}
.t4{{font:400 16px/1 "Helvetica Neue",Arial,sans-serif;fill:#4A4F58;letter-spacing:.04em}}
.area{{font:700 24px/1 "Helvetica Neue",Arial,sans-serif;fill:#111;letter-spacing:.09em}}
.areasub{{font:400 17px/1 "Helvetica Neue",Arial,sans-serif;fill:#4A4F58}}
.slab{{font:600 17px/1 "Helvetica Neue",Arial,sans-serif;fill:#111}}
.tagf{{font-weight:700}}
</style>
{svg}'''
OUT.write_text(html, encoding="utf-8")

assert len(tiles) == 6, "all six areas must be placed"
assert "sheeth" not in html, "per-sheet headings must not survive"
print(f"{len(CONNS)} inter-area connections drawn")
print(f"canvas {W} x {H} units -> {pw:.0f} x {ph:.0f} mm")
print(f"wrote {OUT.relative_to(ROOT)}")
