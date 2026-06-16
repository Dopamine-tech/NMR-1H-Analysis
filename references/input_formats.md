# Input formats — detection and parsing

Detect by what files/extensions are present, then parse accordingly.

## Contents
- Bruker dataset (folder or zip)
- JCAMP-DX (.dx / .jdx)
- MestReNova export (peaks / multiplets text)
- Spectrum image / PDF only

---

## Bruker dataset (richest — prefer it)

A Bruker experiment is a folder (often zipped) named by EXPNO (e.g. `10/`)
containing `acqus`, `acqu`, `fid`, `pulseprogram`, and `pdata/1/` with the
processed spectrum. If given a zip, `unzip` it first.

Key files:
- `acqus` — acquisition params. `##$NUC1=<1H>`, `##$SOLVENT=<CDCl3>`,
  `##$BF1=` (basic field → MHz), `##$SFO1=`, `##$PULPROG=<zg30>`, `##$NS=`.
- `pdata/1/procs` — processing params needed to build the ppm axis:
  `##$SF=` (spectrometer freq), `##$SW_p=` (sweep width Hz), `##$OFFSET=`
  (ppm of first point), `##$SI=` (points), `##$NC_proc=` (intensity scale
  exponent), `##$BYTORDP=` (0=little, 1=big endian).
- `pdata/1/1r` — real processed spectrum, int32. This is the data to plot.
- `pdata/1/peaklist.xml` — operator's picked peaks (δ + intensity).
- `pdata/1/intrng` — operator's integration ranges (hi lo per line).
- `pdata/1/title` — sample name (often blank).

ppm axis: `ppm[i] = OFFSET - i * (SW_p/SF) / SI`, i = 0..SI-1 (descends).

Use `scripts/bruker_read.py <…/pdata/1>` — it prints metadata, the operator
peaklist and intrng, and with `--integrate "hi-lo,hi-lo,…" --ref hi-lo`
returns relative integrals normalised to the ref window. The script needs
only numpy (no nmrglue / no internet).

If `1r` is missing, the `fid` (raw, complex int32, params in `acqus`) can be
processed (zero-fill, EM apodization, FT, phase) — but in practice a saved
`1r` almost always exists; reprocessing is rarely needed.

## JCAMP-DX (.dx / .jdx)

Plain text. Headers are `##KEY=value` lines: `##.OBSERVE FREQUENCY=`,
`##$SOLVENT=`, `##XUNITS=`, `##YUNITS=`, `##FIRSTX=`, `##LASTX=`,
`##NPOINTS=`, `##XFACTOR=`, `##YFACTOR=`. Data follows `##XYDATA=(X++(Y..Y))`
in compressed ASDF (SQZ/DIF/DUP) encoding. Parse with the `jcamp` or
`nmrglue` package if available; otherwise decode the ASDF block manually
(beware DIF differencing). X is usually in Hz or ppm; convert with the
observe frequency. Then proceed exactly as for Bruker from Step 3 on.

## MestReNova export (peaks / multiplets)

The operator may paste or export the multiplet-analysis table, e.g.
`8.26 (s, 1H); 7.51 (dt, J = 7.8, 1.4 Hz, 1H); …`, or a peaks list, or the
boxed labels from an annotated print-out. These δ/J/integration values are
**measured and trustworthy** — adopt them.

CRITICAL: the *assignment labels* MestReNova auto-generates from a predicted
structure are frequently wrong. Common failures seen in the wild:
- N–H (broad, ~8 ppm in CDCl3) labeled as an aromatic CH, and a real aromatic
  H mislabeled as the NH.
- The diaryl/benzylic methine (CH) and its CH2 swapped.
- Overlapping aromatic H's assigned to the wrong ring.
Re-derive every label yourself from the evidence (Step 5) and tell the user
which auto-labels you corrected.

## Spectrum image / PDF only

No raw data. Read δ and apparent multiplicity by eye (the peak labels are
usually printed on top; integrals on the bottom). You CANNOT re-integrate or
verify J precisely — state this limitation and cap most confidences at
medium. Still do the proton checksum from the printed integrals if legible.
