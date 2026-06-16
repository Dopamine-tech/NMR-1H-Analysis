# Assignment guide — diagnostics, solvents, 2D cheat sheet

## Diagnostic shifts & couplings (¹H, lead with these)

These "fingerprints" let you place a signal with high confidence regardless of
overlap. Use them before falling back on shift alone.

- **Exchangeable H** (OH, NH, COOH, SH): broad, shift varies with conc/solvent.
  Confirm by D₂O shake (peak disappears). Indole/pyrrole NH in CDCl₃ ~8.0–8.3
  (br s); amide NH 6–8; COOH 10–12; alcohol OH 1–5 (sharp s if dry).
- **¹⁹F coupling** pins fluoroaromatics. On a fluorobenzene/indole: ³J(H–F)
  ~8–9 Hz (H ortho to F), ⁴J ~5 Hz, ⁵J small. A ring H showing a dd with one
  J ≈ 4–9 Hz that has no ¹H partner is coupling to F. 5-fluoroindole: H-7 dd
  (J ≈ 8.7, 4.3), H-6 td (ortho to F, ~9), H-4 dd (J ≈ 9.8, 2.4).
- **Indole H-2**: d, J ≈ 2.0–2.5 Hz (⁴J to NH), ~7.0–7.3 — very diagnostic.
- **1,3-disubstituted benzene**: the H between the two substituents shows only
  meta coupling → near-singlet (J ~1.5 Hz). The H para-type in the middle is a
  t (J ~7.7). Ortho pairs are d/dt.
- **Diastereotopic CH₂** next to a stereocenter: two separate doublets-of-
  doublets (geminal ²J ~ 8–13 Hz + vicinal). Easy to mistake for two different
  protons — integration (2H total) and the shared geminal J give it away.
- **n+1 multiplicity**: an apparent t/q with one clean J usually means
  equivalent neighbors; an ABX or dd pattern means inequivalent neighbors.

Typical ¹H windows (CDCl₃): aldehyde 9–10, aromatic 6.5–8.5, vinyl 5–7,
OCH/NCH 3.3–5, allylic/benzylic CH 2.3–4, CH/CH₂/CH₃ aliphatic 0.8–2.5.

## ¹³C quick notes

No integration (intensities unreliable without inverse-gated). Assign by shift
window: C=O 160–220, aromatic/olefinic 100–160, C≡N ~118, OCH 50–90,
aliphatic 10–50; C–F shows large ¹J(C–F) ~245 Hz doublet, ortho C ~21 Hz, etc.
DEPT/HSQC distinguishes CH/CH₂/CH₃/quaternary. Count unique carbons vs formula.

## Residual solvent & common impurity peaks (¹H)

Mark these as solvent/impurity, never as structural protons.

| species | CDCl₃ | DMSO-d₆ | CD₃OD | D₂O |
|---|---|---|---|---|
| residual solvent | 7.26 | 2.50 | 3.31 | 4.79 |
| H₂O | 1.56 | 3.33 | 4.87 | 4.79 |
| TMS | 0.00 | 0.00 | 0.00 | – |
| CH₂Cl₂ | 5.30 | 5.76 | 5.49 | – |
| CHCl₃ | 7.26 | 8.32 | 7.90 | – |
| acetone | 2.17 | 2.09 | 2.15 | 2.22 |
| ethyl acetate | 4.12/2.05/1.26 | 4.03/1.99/1.17 | – | – |
| diethyl ether | 3.48/1.21 | 3.38/1.09 | – | – |
| grease (hydrocarbon) | 1.26/0.86 | – | – | – |
| silicone grease | 0.07 | 0.07 | – | – |
| n-hexane | 1.26/0.88 | – | – | – |
| DMF | 8.02/2.96/2.88 | 7.95/2.89/2.73 | – | – |

(Values from Gottlieb, Kotlyar, Nudelman, J. Org. Chem. 1997, 62, 7512 — the
standard reference. Water shifts a bit with conc.) Water can drift; in practice
a small sharp peak near 1.5–1.7 in CDCl₃ is water/OH.

## Salt forms (check before crying 'impurity')

Many isolated compounds are salts (HCl, TFA, formate…). A salt changes the
spectrum in diagnostic ways — recognising it prevents mis-calling features as
impurities or a second species:
- **Protonated amine N⁺–H**: a basic amine as its HCl/TFA salt gains an
  exchangeable N⁺–H. A tertiary ammonium R₃N⁺–H shows a broad ~1H peak that in
  DMSO-d₆ often sits ~9–11 ppm (amine basicity/solvent dependent). An 'extra'
  ~1H exchangeable peak that D₂O removes is very likely this, NOT an impurity.
- **α-protons shift downfield**: N–CH₃/N–CH₂ next to the protonated nitrogen
  move ~0.5–0.8 ppm downfield and broaden. e.g. a free-base N(CH₃)₂ singlet at
  ~2.0–2.2 becomes ~2.6–3.0 (often a broadened ~6H, sometimes a doublet from
  ³J to N⁺–H) in the HCl salt. If the expected amine methyl singlet is 'missing'
  at its free-base shift, look downfield for the protonated form.
- **Proton count**: include the salt's added proton(s) in the formula total
  (e.g. free base C₃₀H₃₀F₂N₂O = 30 H → mono-HCl salt shows 31 ¹H incl. N⁺–H).
- **TFA salt**: no extra ¹H methyl, but a ¹⁹F singlet ~ -75 ppm and a ¹³C
  quartet ~116/161; counter-ion invisible in routine ¹H beyond the N⁺–H.
- Confirm with a **D₂O shake** (exchangeables vanish) and, for stoichiometry,
  elemental analysis / ion chromatography / quantitative ¹⁹F.

## Which 2D experiment resolves which ambiguity

Recommend the *minimal* experiment that breaks the specific tie:
- **CH vs CH₂ vs CH₃** → **HSQC** (¹H–¹³C one-bond; one CH₂ carbon shows two ¹H
  cross-peaks). Settles methine/methylene swaps instantly.
- **Overlapping aromatic cluster / which ring** → **COSY** (¹H–¹H; traces the
  coupling network so each ring's spin system separates).
- **Connectivity across quaternary atoms / regiochemistry** → **HMBC**
  (2–3 bond ¹H–¹³C).
- **Through-space proximity / stereochem** → **NOESY/ROESY**.
- **OH/NH confirmation** → **D₂O shake** (cheap, immediate).
