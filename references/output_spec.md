# Output specification

Three deliverables, every time: figure + Markdown table + SI text string.

## 1. Annotated figure

Build with `scripts/plot_nmr.py spec.json`. Layout (mimics a MestReNova
print-out so it's familiar to chemists):

- Wide spectrum trace across the bottom 60% of the canvas.
- **Top of each peak**: its δ value, vertical text.
- **Bottom of each peak**: the relative integral (normalised so a clean 1H
  signal = 1.00), vertical text in green.
- **Annotation boxes** above the trace, staggered over two rows with thin
  leader lines to the peak. Each box: `atom#  (multiplicity)` + short
  assignment. Box color encodes confidence: green=high, amber=medium ⚠,
  red=low ⚠⚠.
- **Impurity/solvent peaks**: labeled at top in red with a `*`, and a
  footnote in the subtitle (e.g. `* = CH₂Cl₂ 5.30, H₂O 1.66, TMS 0.00`).
- **Structure inset** in a corner: embed the user's numbered structure image
  if they gave one (set `structure_image`); else draw from 2D coordinates
  (`structure` block) with red atom numbers and colored heteroatom labels.
- **Confidence tinting on the structure** (required): each atom that carries an
  assigned proton is filled with a colored halo by confidence — green/amber/red
  for high/medium/low — plus a small high/med/low legend. This is automatic in
  `plot_nmr.py`: it reads every multiplet's `atoms` list and `conf`, and when an
  atom appears in several signals it keeps the LOWEST confidence. Make sure the
  `atoms` field of each multiplet uses the same numbering as the `structure`
  block so the halos land on the right atoms. (Only the drawn `structure` path
  is tinted; an embedded `structure_image` photo cannot be recolored.)

Building the `spec.json`:
- `spectrum`: point to an `.npz` (ppm,y) or `.csv` saved by
  `bruker_read.py --npz/--csv`.
- `multiplets`: one entry per signal —
  `{"ppm":, "mult":"dd", "J":"8.7,4.3", "nH":1, "atoms":"5",
    "assign":"indole H-7", "conf":"high", "integ":"1.18"}`.
- `impurities`: `[{"ppm":5.30,"label":"CH2Cl2"}, …]`.
- `out`: output PNG path.

If the sandbox font lacks CJK glyphs, keep figure text in ASCII/English
(assignments like "indole H-7", "CH2OH") — the Chinese goes in the chat table,
not baked into the PNG, to avoid tofu boxes.

Re-open the saved PNG (Read it) to verify legibility before presenting.

The annotation boxes auto-pack into as many rows as needed and each gets its
own leader line, so crowded regions (e.g. a DMSO aliphatic envelope) stay
readable — you do not need to thin out or merge labels to avoid overlap.

Structure inset sits small in the TOP-RIGHT corner by default so it never
collides with the peak labels or annotation boxes (override its position/size
with `structure_box`: [x, y, w, h] in figure fractions). Keep it compact —
the spectrum and its labels are the focus.

Structure inset: pass `structure_image` with the path to the user's uploaded
structure file to embed it exactly (preferred). If only an inline/unnumbered
drawing exists, either request the file, or omit the inset and rely on the
box labels, or supply a `structure` block of 2D coordinates to draw a skeleton.

## 2. Markdown assignment table

Exact columns (keep this order). Sort high→low δ. Confidence in the user's
language (高/中/低) with ⚠ flags.

```
| δ (ppm) | 裂分 (J/Hz) | 积分 | 原子号 | 归属 | 置信度 | 依据 |
|---|---|---|---|---|---|---|
| 8.26 | s (br) | 1H | 10 | 吲哚 N–H | 高 | CDCl₃ 中吲哚 NH 特征宽峰 |
| 7.29 | dd (8.7, 4.3) | 1H | 5 | 吲哚 H-7 | 高 | ⁴J(H–F)=4.3 诊断 |
| 7.59 | m | 1H | 9 | 吲哚 H-4 | 中 ⚠ | 落在芳香重叠区 |
| …  |
```

After the table: state the integration checksum ("各区间积分合计 = N H，与
分子式 … 吻合"), then group the ⚠ rows and give the concrete experiment that
resolves each (COSY / HSQC / D₂O), and reassure which high-confidence signals
already establish the structure.

## 3. SI text string

Plain text, manuscript-ready, English/IUPAC notation regardless of table
language:

```
¹H NMR (500 MHz, CDCl₃) δ 8.26 (s, 1H), 7.61–7.56 (m, 1H), 7.58 (s, 1H),
7.51 (dt, J = 7.8, 1.4 Hz, 1H), 7.44–7.38 (m, 1H), 7.29 (dd, J = 8.7, 4.3 Hz,
1H), 7.19 (d, J = 2.5 Hz, 1H), 6.98–6.90 (m, 2H), 4.42 (t, J = 6.5 Hz, 1H),
4.22 (t, J = 8.7 Hz, 1H), 4.14 (t, J = 8.3 Hz, 1H), 1.75 (s, 1H).
```

Rules: highest δ first; J to one decimal; standard multiplicity codes
(s, d, t, q, p, dd, dt, td, ddd, m, br s); ranges for multiplets as
"7.61–7.56 (m, 1H)"; sum of nH must equal the molecular formula. For ¹³C:
`¹³C NMR (126 MHz, CDCl₃) δ 160.5, 142.1, …` (with C–F doublets noted as
`(d, J = 245 Hz)` where resolved).
