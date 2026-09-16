# Product Pricing — Cited Basis

> Companion script: [[revenue_floor.py]]. Physical basis: [[mass_balance.py]].

## What can actually be cited, and what cannot

| Product | Direct price assessment? | Status |
|---|---|---|
| CoSO₄·7H₂O (20.5 % Co) | Yes — Fastmarkets MB-CO-0017 | **Paywalled.** Series confirmed live; the number is not public. |
| NiSO₄·6H₂O (22 % Ni) | Yes — SMM daily index | **Paywalled.** Only a stale Sep-2025 figure was retrievable. |
| Li₃PO₄ | **No agency assesses it.** SMM assesses lithium *dihydrogen* phosphate (LiH₂PO₄), a different compound. | No market price exists to cite. |
| Cobalt metal, Class 1 nickel | Yes — USGS, free and authoritative | **Citable.** |

**So the salt prices the old TEA quoted cannot be sourced without a subscription.**
Rather than invent them, price on **contained metal at USGS benchmarks**, which is
free, citable, dated, and gives a defensible **floor**.

## The floor

Contained metal from the closed balance: **Co 643 t/yr · Ni 1,412 t/yr · Li₃PO₄ 1,831 t/yr.**

| Stream | Basis | Revenue | Share |
|---|---|---|---|
| Cobalt | contained Co at LME cash $15/lb → US spot $21/lb (CY2025 avg) | $21.2M – $29.7M | 49 % |
| Nickel | contained Ni at LME cash $15,000/t (CY2025 avg) | $21.2M | 41 % |
| Lithium | Li₃PO₄ at $2.07–3.90/kg | $3.8M – $7.1M | 10 % |
| **Total floor** | | **$46.2M – $58.1M/yr** | |

## Three things this table is honest about

1. **It is a floor, not a forecast.** Battery-grade sulphates sell *above* contained-metal
   value, because the buyer is paying for conversion. That premium is exactly what sits
   behind the Fastmarkets paywall. Real revenue is above this band; how far above is the
   one number a subscription would buy.
2. **Lithium collapsed from the retired TEA.** The void TEA implied ~$22M of lithium on an
   assumed $12,300/t. The only peer-reviewed figure for Li₃PO₄ is $2.07–3.90/kg, three to
   six times lower. **Lithium is ~10 % of revenue, not 25 %.** The phosphate route is still
   right on recovery grounds (94.1 % Li), but it does not carry the business case.
3. **Cobalt price risk is now the dominant exposure.** Co is ~49 % of the floor and its
   price moved +81 % year-on-year to Dec 2025 on the DRC export ban and quota regime.
   Nickel moved the other way, down a fourth straight year on surplus. A single-point
   revenue figure would hide both.

## Prices used, with sources

- Cobalt, CY2025 avg: US spot cathode **$21/lb**, LME cash **$15/lb** — USGS MCS 2026, Cobalt, pp. 70–71.
- Cobalt, Dec 2025 monthly: US spot **$28.23/lb**, LME cash **$23.31/lb** (+81 % y/y) — USGS Mineral Industry Surveys.
- Nickel, CY2025 avg: LME cash **$15,000/t ($6.90/lb)** — USGS MCS 2026, Nickel.
- Li₃PO₄: **$2.07–3.90/kg** — Z. Wang et al., *Materials*, vol. 19, no. 4, Art. no. 674, Feb. 2026, doi 10.3390/ma19040674. Bibliographic details confirmed via Crossref 2026-09-13. **Single-source, and it is a review** — the figures are quoted from its own sources, not assessed.
- Battery-grade Li₂CO₃ context: ¥117,000/t (~$16,734/t) at 31 Dec 2025, ¥141,000/t at 9 Jan 2026 — S&P Global. Lithium swung roughly 2× inside 18 months.

## What would improve this

A Fastmarkets or SMM subscription converts the floor into an actual revenue line by
supplying the two salt assessments. Short of that, the floor is the honest number and
the conversion premium should be stated as unquantified rather than guessed.

## Second search for a Li₃PO₄ price: none found

A dedicated second sweep (EverBatt, DLE project technical reports, SMM / Asian Metal /
Baiinfo / Mysteel for 磷酸锂, EU LCA-TEA studies, payability papers) found **no independent
corroboration**. Three things worth recording:

1. **There is no market for the compound.** Twenty peer-reviewed recycling papers treat
   Li₃PO₄ as an intermediate on the way to Li₂CO₃; almost none sells it. SMM assesses
   lithium *dihydrogen* phosphate (LiH₂PO₄), a different chemical. That absence is
   itself the finding, and it is why no agency publishes a price.
2. **A false corroboration was caught.** *Molecules* 30, 2587 (2025) carries $2.63 and
   $4.46/kg figures that look like a match. On direct check they price **FePO₄**, not
   Li₃PO₄. Phosphate-compound prices in this literature are easily conflated and must be
   checked against the exact chemical identity, not the keyword.
3. **Two leads stay open, unresolved rather than negative:** the EverBatt Excel workbook
   (Argonne blocks non-browser fetches; download it directly and read the material-price
   tab) and Vision Lithium's March 2023 NI 43-101 (scanned PDF, needs OCR).

**Framing for the whitepaper:** the $2.07–3.90/kg range is a single-source literature
figure from a review, not an established market price. Quote it with that caveat and do
not average it with anything. Lithium is ~10 % of the revenue floor, so the paper's
economics do not turn on it — the process story (94.1 % Li recovery) does not depend on
the price at all.

**Note on a closed decision.** The Li₃PO₄→LiOH conversion was dropped when Li₃PO₄ was
assumed at $12,300/t (a ~30 % discount to carbonate). At $2–4/kg the discount is ~75 %,
and since the conversion uplift equals the discount, that case is now strongly economic
rather than marginal. Not reopened; recorded so the reason for the decision is visible.
