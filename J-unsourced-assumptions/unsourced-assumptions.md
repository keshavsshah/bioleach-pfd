# Assumptions Carried Without a Cited Value

Stated so they can be checked rather than inherited. Each is used by the balance or the
cost estimate; none has a source that could be verified at publication rigour.

| Assumption | Value used | Where it acts | Note |
|---|---|---|---|
| Fe(III)–gluconate stability constant | not fixed | Fe/Al precipitation, speciation | Sawyer [16] is the reference to consult; values from 8 to 10 change whether iron precipitates cleanly or stays complexed |
| Li₃PO₄ solubility | 0.39 g/L, and its behaviour at 60 °C | Lithium precipitation | Sets whether Li₃PO₄ precipitates from the 1.9 g/L barren without evaporation |
| Co/Ni occlusion in the hydroxide cake | 2 % | Fe/Al removal | Literature suggests 2–5 %; no specific figure verified |
| MVR specific energy | 25–35 kWh per tonne evaporated | Operating cost | Order of magnitude is right; the range is vendor-typical |
| Solvent-extraction stage counts | 3 extraction / 2 scrub / 2 strip | Equipment list | Ordinary design practice, uncited by intent |
| Sterile air filtration | 0.2 µm | Fermentation | Ordinary practice |
| Industrial fermenter scale | 100–300 m³ typical | Comparison only | Not a design input |
| Gluconic acid pKa | 3.86 | Base demand | Sources also report 3.70; the spread is the equilibrium with glucono-δ-lactone. Under 2 % effect on base demand |

## Prices

Every price in `I-cost-estimate/` is an estimate, exposed as a named constant at the top
of the script that uses it. Equipment cost anchors, reagent and utility prices, and the
Lang factor are all of this kind. Consumption quantities are not: they come from the
closed balance.

Battery-grade sulfate assessments exist but are published only under subscription [28],
and no agency assesses a Li₃PO₄ price at all [27]. Revenue is therefore a floor on
contained metal at USGS benchmarks [24]–[26].

## Deliberately uncited

Tank residence times, pump sparing, silo and bunker hold-up, and similar matters of
ordinary engineering practice carry no citation. A reference for them would pad the
bibliography without adding anything a reviewer could dispute.
