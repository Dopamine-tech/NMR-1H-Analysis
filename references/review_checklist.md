# Review / audit checklist (Step 9)

The goal of this pass is to *falsify* the draft assignment before delivery —
actively look for what could be wrong, not to re-confirm what you already
believe. For a messy or high-stakes spectrum, run it as an INDEPENDENT review:
spawn a fresh reviewer subagent and give it only (a) the parsed data
(δ / integrals / J / metadata), (b) the structure, and (c) the draft table —
ask it to challenge each row. Then reconcile. A second pair of eyes that starts
from the data, not from your conclusion, catches anchoring errors.

Run every check; report the outcome of each in the review section.

## 1. Sample integrity (do this FIRST — it can invalidate everything else)
- Is there evidence of MORE THAN ONE species? Tell-tales: a second
  exchangeable/NH-type peak of similar size, doubled peaks at ~constant ratio
  (diastereomers/rotamers), or an aromatic/aliphatic integral total that
  exceeds the single-molecule count. If so, say so — a clean one-structure assignment is not valid for a mixture.
- BEFORE declaring an impurity/mixture, rule out benign causes — above all a **salt form**. A protonated-amine N⁺–H (HCl/TFA salt) is an 'extra' ~1H exchangeable peak (often 9–11 ppm in DMSO) that BELONGS to the molecule, and it comes with the amine α-protons shifted downfield (e.g. N(CH₃)₂ at ~2.6–3.0 instead of ~2.0). Count the salt's added proton(s) in the formula total. Rotamers and ¹³C/¹⁹F satellites are other benign doublings. Confirm with a D₂O shake / LC-MS before concluding the sample is impure. If so, say so — a clean one-structure
  assignment is not valid for a mixture, and confidence must drop.
- Normalise to a CLEAN, isolated 1H signal (a sharp aromatic dd, a methine),
  NOT a broad NH/OH (which reads low) and NOT a peak overlapping solvent.
  Re-check the proton total against the formula with that reference.

## 2. Proton accounting
- Every compound peak assigned exactly once; none orphaned, none double-counted.
- Σ integrals of compound peaks = formula H (state it).
- Every impurity/solvent peak named with a reason and excluded.

## 3. Shift plausibility
- Each δ within the expected window for its group; flag anything >~0.3 ppm
  outside the typical range and justify or re-assign.

## 4. Coupling consistency
- Coupling partners share an identical J (a ³J on one peak appears on its
  partner). Multiplicity matches the neighbour count.
- Heteronuclear couplings (H–F, H–P) attributed to the right nucleus — not an
  invented extra ¹H partner.

## 4b. Coupling notation (nJ) is correctly labelled
The left superscript n in ⁿJ is the NUMBER OF BONDS between the two coupling
nuclei — count the bonds on the shortest path, and a double bond still counts
as ONE bond (bond order changes the size of J, never the n). Check each J:
- On a fluoro-aromatic ring: **ortho H–F = ³J ≈ 8–10 Hz** (path H–C–C–F = 3
  bonds, even though one ring bond is double), **meta H–F = ⁴J ≈ 5–8 Hz**,
  **para H–F = ⁵J ≈ 2 Hz**; **ortho H–H = ³J ≈ 8 Hz**, **meta H–H = ⁴J ≈ 2–3
  Hz**. A common slip is mislabelling the large ortho H–F as ⁴J — it is ³J.
- Make sure the nucleus pair in parentheses is right: a ~9 Hz splitting with no
  ¹H partner on the adjacent carbon is ³J(H–F), not an invented H–H.
- An apparent triplet from a ring H next to F is usually ³J(H–H)≈³J(H–F): two
  different partners with coincidentally equal J — label it as such, not as one
  symmetric coupling.

## 5. Symmetry & equivalence
- Symmetric groups (para-/mono-substituted phenyl, N(CH₃)₂, equivalent CH₂)
  integrate to the right multiple. Diastereotopic CH₂ splits accounted for.

## 6. Diagnostic re-derivation
- Independently re-derive the high-confidence fingerprints (NH; ortho-F
  shielded ring H; AA'BB'; indole H-2 d; epoxide ABX …). If a "high" row has no
  fingerprint, it isn't high.

## 7. Internal contradiction & honest confidence
- No atom assigned to two incompatible shifts.
- Nothing in a crowded/overlapped region marked "high". Anything resting on
  shift alone is at most "medium".

## 8. Figure ↔ table parity
- Atom numbers, integrals, multiplicities, impurity marks and confidence halos
  in the figure all match the final table and the structure numbering.

## 8b. Multiplets resolved as finely as the data allows
Did you split every region into the distinct sub-multiplets the data shows,
or did you lazily lump a broad ‘m, nH’? Re-examine each multi-proton ‘m’: if
the peaks resolve into separate centroids with their own integrals (e.g.
phenyl 5H + an isolated 1H + a 1H triplet under one envelope), each must be a
separate row. Integrate every visible sub-peak. Lumping is only acceptable for
true overlap that cannot be resolved at this field — state that explicitly.

## 9. Alternative hypotheses
- For each medium/low row, is a different assignment more likely? Could a
  "compound" peak actually be an impurity (or vice versa)? Name the experiment
  (COSY/HSQC/HMBC/D₂O/VT) that would settle each residual doubt.

## Output
Append a **审查结果 / Review** section to the `.md`: list each check's outcome,
every discrepancy found and correction made, and the residual risks with the
specific experiment that resolves them. If sample-integrity (check 1) failed,
lead with that.
