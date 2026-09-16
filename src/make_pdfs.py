"""Render the two HTML deliverables to PDF using headless Chrome.

The print stylesheets live in the HTML itself, so the PDFs paginate correctly:
one landscape page per PFD sheet, A4 portrait with one block per page for the Index.

Run: python3 src/make_pdfs.py
"""
import shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
]
chrome = next((c for c in CHROME_CANDIDATES if c and Path(c).exists()), None)
if not chrome:
    sys.exit("No Chrome/Chromium found. Install one, or open the HTML and print to PDF.")

JOBS = [("pfd/bioleach_PFD_v2.html",    "pfd/bioleach_PFD.pdf"),
        ("pfd/bioleach_PFD_index.html", "pfd/bioleach_PFD_index.pdf")]

for src, out in JOBS:
    src_p, out_p = ROOT / src, ROOT / out
    if not src_p.exists():
        sys.exit(f"missing {src_p}")
    subprocess.run(
        [chrome, "--headless", "--disable-gpu", "--no-sandbox",
         "--no-pdf-header-footer", "--virtual-time-budget=10000",
         f"--print-to-pdf={out_p}", src_p.as_uri()],
        check=True, capture_output=True, timeout=180)
    size = out_p.stat().st_size
    print(f"{out:<34}{size/1024:>8,.0f} KB")
    # a PDF that is a few hundred bytes means Chrome rendered a blank page
    assert out_p.read_bytes()[:4] == b"%PDF", f"{out} is not a PDF"
    assert size > 20_000, f"{out} is suspiciously small - did the page render?"
print("\nboth PDFs written to pfd/")
