---
name: nmr-analysis
description: >-
  Interpret and assign NMR spectra from raw instrument data plus a molecular
  structure, and produce a fully annotated spectrum figure, a δ/multiplicity/
  integration/assignment table (with a confidence column), and an SI-style
  text string. Handles ¹H, ¹³C, and 2D (COSY/HSQC) support. Accepts Bruker
  datasets (zip or folder with fid + pdata), JCAMP-DX (.dx/.jdx), MestReNova
  peak/multiplet exports, or a spectrum image/PDF. Use this whenever the user
  hands over NMR data together with a chemical structure and wants peak
  assignment, an annotated/labeled spectrum, a 归属表/assignment table, an
  integration check, or an "¹H NMR (…) δ …" SI string — even casual phrasings
  like 解NMR、归属、解析谱图、做归属表、assign the peaks, or interpret this spectrum.
  Always deliver BOTH a Markdown table and a plain-text SI string.
---

# NMR analysis

## What this does and why

The user has run an NMR experiment and has a proposed structure. They want to
know which signal belongs to which atom, with honest uncertainty, plus
publication-ready outputs. The value you add over a chemist eyeballing the
print-out is: reading the *real* processed data (so δ and integrals are exact,
not guessed from a screenshot), reasoning from diagnostic couplings rather than
shift alone, and being explicit about what is solid vs. what needs a 2D
experiment to confirm.

Work through the steps below in order. The hard part is never the plotting — it
is the **assignment reasoning** and **honest confidence calibration**. Spend
your effort there.

## Deliverables (always produce all three)

1. **Annotated spectrum figure** (PNG) — peak δ labels on top, integrals on the
   bottom, multiplet boxes (atom number + multiplicity + δ) with leader lines,
   and the numbered molecular structure embedded in a corner. **Every compound
   peak — aromatic AND aliphatic, no exceptions — gets an integral shown as a
   coverage bracket** beneath it (the bracket spans the exact ppm window that
   was integrated, with the value below it), so the reader sees both the number
   and where it came from. Do not leave crowded aliphatic peaks un-integrated.
   **Resolve multiplets to the finest level the data supports** — if a region
   separates into distinct sub-peaks (different centroids / integrals /
   lineshapes, as a MestReNova multiplet analysis would split it), report EACH
   as its own row (own δ, multiplicity, J, integral, assignment), never one lazy
   broad ‘m, nH’. A ‘7.4–7.1, m, 7H’ lump that actually shows a 5H multiplet +
   an isolated 1H + a 1H triplet must be written as three separate signals.
   Only group protons that are genuinely overlapping/unresolvable, and say so.
   **All solvent/impurity peaks are marked in light grey** (never as compound
   signals). **On that
   structure, every atom carrying an assigned proton MUST be tinted by its
   assignment confidence** (green = high, amber = medium, red = low), with a
   small legend — so the reader sees at a glance which parts of the molecule are
   solidly assigned and which are tentative. `plot_nmr.py` does this
   automatically from each multiplet's `atoms` + `conf` fields. See
   `references/output_spec.md` for the exact layout.
2. **Assignment table as a saved Markdown FILE** (`<sample>_1H_assignment.md`)
   — not just printed in chat. Columns: δ (ppm) | multiplicity (J/Hz) |
   integration | atom number(s) | assignment | **confidence** | basis. The
   confidence column and ⚠ flags for uncertain rows are mandatory. Put the SI
   string and the impurity/notes section in the SAME .md file so the user has
   one self-contained document.
3. **Plain-text SI string** — e.g.
   `¹H NMR (500 MHz, CDCl₃) δ 8.26 (s, 1H), 7.51 (dt, J = 7.8, 1.4 Hz, 1H), …`

### Output folder — name, date, and WHERE to save it

Put every file for one job inside ONE folder named **`<compound>_<date>_Claude`**
(e.g. `ZQL-5DC4-R_2026-06-16_Claude`). Get the date with `date +%Y-%m-%d`. The
compound name comes from the user, the structure label, or the data; **if no
name is found anywhere, pause and ASK the user** (AskUserQuestion) before
writing files. Sanitise the name for the filesystem (no spaces/slashes).

**Where to put that folder** — prefer saving it next to the original data:
1. Read the sample identity from the Bruker data — `acqus` has an `##ORIGIN`/
   path line like `D:/data/.../<SAMPLE>-<date>-root/<expno>/acqus`; the upload
   filename may also carry it.
2. If a connected/working folder is mounted, search it for the folder matching
   that sample (e.g. `find <workspace> -iname '*<SAMPLE>*'`). If found, create
   the `<compound>_<date>_Claude` result folder INSIDE that matched data folder
   so results sit with their raw data.
3. **If no matching folder is found (or nothing is mounted), default to the
   working/output directory.** Never fail for lack of a match — just fall back.

All deliverables — the figure PNG(s) and the `.md` — go into that one folder,
and you present the files from it.

Save ALL THREE to the outputs folder — the figure PNG AND the `.md` document —
then present both files to the user (present_files). Also paste the table and
SI string into the chat reply for convenience, but the `.md` FILE is a required
deliverable, never skip it: the user has explicitly asked for the assignment
table as a Markdown document every time, in addition to the in-chat text.

## Step 0 — Does the spectrum match the structure? (do this FIRST, state a verdict)

Before any peak-by-peak work, step back and judge the WHOLE picture: could this
spectrum plausibly belong to the proposed molecule/formula at all? This upfront
sanity check guards against confirmation bias in the detailed assignment that
follows. Look at: does the total integral roughly match the expected proton
count; are the expected diagnostic signals present (NH/OH, the right number of
aromatic H, key functional-group shifts like OCH₂, aldehyde, etc.); are there
major peaks that should NOT be there for this structure; does the solvent fit.

Output a one-line **符合性判断 / Match verdict** with an explicit confidence
(高/中/低) and the one or two facts driving it — e.g. ‘谱图与 C₉H₇NO 一致（高）：
芳香 4H + 环氧 ABX 3H = 7H 吻合，无多余主峰’, or ‘部分符合（中）：主体吻合但 10.1
出现额外可交换峰，疑为盐型或杂质，待 Step 9 审查’. If the count is wrong, a
diagnostic is missing, or there are unexplained major peaks, say so and drop the
confidence — do not paper over it. Put this verdict at the TOP of the .md and
the chat reply, before the table.

## Step 1 — Read the structure and build expectations

Before touching the data, establish the **compound name** (from the user, the structure label, or the data filename) — you'll need it for the output folder `<compound>_<date>`; if it's nowhere to be found, ask the user with AskUserQuestion. Then understand the molecule. If the user supplied a
numbered structure image, **adopt their atom numbering exactly** — every label
in your outputs must match their drawing. If they gave a SMILES or name instead,
derive the structure and pick a clear numbering (and show it).

Produce, for yourself:
- The molecular formula and the **expected proton count** (and carbon count for
  ¹³C). This is your checksum later.
- A list of distinct proton environments with rough predicted δ ranges and the
  multiplicity you'd expect from neighbors (n+1 rule, plus heteronuclear
  couplings like ³J/⁴J to ¹⁹F or ³¹P). Note diastereotopic CH₂ groups — they
  are often two separate dd's, a classic trap.

If the user pasted the structure only inline (in chat) rather than as an
uploaded image file, the plotting script cannot embed it — ask them to attach
the structure as an image file (png/jpg) so it can be dropped into the figure
corner verbatim. If they prefer not to, you can still deliver the figure with
group/atom labels on the annotation boxes and skip the inset (say so), or draw
a clean numbered skeleton from 2D coordinates via the `structure` block.

See `references/assignment_guide.md` for diagnostic shift/coupling patterns.

## Step 2 — Ingest the spectrum data

Detect the input format and parse it. Details and parsing code live in
`references/input_formats.md`. Quick routing:

- **Bruker dataset** (a folder/zip containing `acqus`, `fid`, `pdata/1/…`):
  this is the richest input. Use `scripts/bruker_read.py` to get the real ppm
  axis + intensities, the acquisition metadata (frequency, solvent, nucleus),
  and any peak list / integration ranges the operator already saved
  (`pdata/1/peaklist.xml`, `pdata/1/intrng`). Prefer the processed spectrum
  (`pdata/1/1r`); only reprocess the `fid` if no `1r` exists.
- **JCAMP-DX** (`.dx`/`.jdx`): parse the XY data block; metadata is in the
  `##` headers.
- **MestReNova export** (peaks/multiplets text or table): the operator has
  often *already* done the multiplet analysis (δ, multiplicity, J, integral).
  Treat those numbers as accurate measured values — but re-examine the
  *assignment* labels critically (auto-assignment frequently mislabels NH,
  swaps CH/CH₂, etc.).
- **Image/PDF only**: read δ and apparent multiplicity visually. You cannot
  re-integrate — say so, and lower confidence accordingly.

Always record: nucleus, field (MHz), solvent. These set the residual-solvent
peaks and are required for the SI string.

### Phase & reference calibration (do this before quantifying or assigning)

A spectrum must be correctly phased and referenced before its δ values mean
anything. Processed Bruker `1r` data is normally already phased by the
operator, but verify it and fix the reference:
- **Phase / baseline check**: run `bruker_read.py <pdata> --phasecheck`. Peaks
  should be absorptive (all pointing up) on a flat baseline; if it flags
  REVIEW (dispersive lobes, rolling baseline), note it — the integrals and
  even peak positions are unreliable until re-phased.
- **δ-axis reference (calibrate to TMS or the deuterated solvent)**: the axis
  must be pinned so that **TMS = 0.00 ppm**, or — when no TMS — the **residual
  deuterated-solvent peak sits at its tabulated value** (CDCl₃ 7.26, DMSO-d₆
  2.50, CD₃OD 3.31, D₂O 4.79, acetone-d₆ 2.05, C₆D₆ 7.16, CD₂Cl₂ 5.32 …).
  Check where TMS / the residual solvent actually falls; if it is off by Δ,
  recalibrate the whole axis with `--calibrate "obs:target"` (e.g.
  `--calibrate 0.04:0.00` to pull TMS to 0, or `--calibrate 7.29:7.26` for
  CDCl₃). Re-save the npz/csv from the calibrated axis and note the shift
  applied. Every downstream δ — table, SI string, figure — uses the calibrated
  axis.

## Step 3 — Quantify and run the proton checksum

For ¹H, integrate each multiplet region (use the operator's `intrng` ranges if
present, else define windows around each cluster) and **normalize to a clean
1H reference** (a CH or a well-isolated aromatic H). Then add up all
compound-belonging integrals and check the total against the expected proton
count from Step 1.

A matching total (e.g. "regions sum to 13 H = C₁₇H₁₃FN₂O") is strong evidence
the structure and spectrum agree, and you should state it explicitly. A
mismatch is a red flag worth investigating (missing/extra peak, wrong
structure, overlapping impurity) before assigning.

`scripts/bruker_read.py --integrate` does this for Bruker data.

## Step 4 — Identify solvent and impurity peaks (look them up — don't guess)

Before assigning, subtract the "not the compound" peaks so you don't
mis-assign them. For EACH peak you suspect is solvent/impurity, run it through
the lookup against the J&K common-impurity table (12 solvents):

    python3 scripts/impurity_lookup.py --solvent <CDCl3|DMSO|CD3OD|...> --ppm <d1,d2,...>

It returns candidate impurities (name, group, multiplicity, |Δ|) from
`references/impurities.csv`. **Identify the SPECIFIC substance, never a vague
tag**: when one shift has several candidates, confirm identity from the
substance's WHOLE fingerprint of peaks using
`impurity_lookup.py --solvent <s> --identify "<all non-compound δ's>"`, which
ranks substances by how many of their characteristic peaks are present (e.g.
4.12 q + 2.05 s + 1.26 t together ⇒ **ethyl acetate**, not ‘grease’; 1.26 br +
0.88 alone ⇒ a hydrocarbon, label it n-hexane/pump-oil as the data warrant).
Rules:
- A confident match → label every peak of that substance in light grey with
  its **specific name or common abbreviation**, exactly like a solvent peak
  (e.g. ‘4.12 EtOAc*’, ‘2.05 EtOAc*’, ‘1.26 EtOAc*’; ‘3.48 Et₂O*’; ‘0.88
  hexane*’) — do NOT write the generic word ‘grease’ if a real compound fits
  the peaks. Exclude all of them from compound integrals.
- **Unknown impurity** (no table match, and not part of the structure) → do NOT
  clutter the figure with it, but DO flag and discuss it in the .md (δ, rough
  size, and a guess at what it might be / what to do).
- Quick reference values also live in `references/assignment_guide.md`.
- **Account for EVERY visible peak.** No peak — however obviously solvent, even
  a big residual-water hump — may be left unlabeled. Walk the whole trace; each
  peak is either an assigned compound signal (with an integration bracket) or a
  named impurity (grey label sitting ON its peak). If you can see it, you label
  it. `plot_nmr.py` now places each impurity name directly above its own peak
  so nothing looks unhandled.

## Step 5 — Assign, reasoning from evidence

Map each compound peak to atom number(s). Lead with the **most diagnostic**
signals (the ones with fingerprint couplings or unambiguous shifts), then place
the rest. Use, in roughly this priority:

1. Heteronuclear and characteristic couplings — e.g. ³J/⁴J(H–F) pins
   fluoroaromatic positions; indole H-2 as a d (J ≈ 2.5 Hz, ⁴J to NH); a clean
   meta-only singlet in a 1,3-disubstituted ring.
2. Chemical shift windows (heteroatom-adjacent, aromatic, aliphatic).
3. Integration (1H vs 2H clusters; diastereotopic CH₂).
4. Multiplicity / coupling network (and 2D if available — COSY connects
   coupling partners, HSQC ties H to its carbon and instantly distinguishes
   CH/CH₂/CH₃).

When the operator's software pre-assigned the peaks, **do not copy its labels
blindly**. Re-derive them; note and correct common auto-assignment errors
(N–H mislabeled as an aromatic CH, methine/methylene swapped, etc.) and tell
the user what you changed and why.

## Step 6 — Score confidence honestly

Every row gets a confidence level. This is the heart of the skill — a
confident-but-wrong assignment is worse than a flagged uncertain one.

- **高 / High** — a fingerprint signal with little room for doubt (diagnostic
  coupling, isolated shift, exchangeable proton confirmed). No flag.
- **中 / Medium ⚠** — chemically reasonable but sits in a crowded/overlapping
  region, or relies on shift alone, or could swap with a neighbor.
- **低 / Low ⚠⚠** — counter-intuitive shift, or an assignment forced to make the
  count work, or only inferable with data you don't have.

For every ⚠ row, name the specific experiment that would resolve it (usually a
short, concrete recommendation): COSY to untangle an overlapping aromatic
cluster, HSQC to settle CH vs CH₂, a D₂O shake to confirm an OH/NH. Close by
noting which high-confidence signals already suffice to support the structure,
so the user knows the ⚠ items affect *precise labeling*, not the identity.

## Step 7 — Build the outputs

1. Generate the figure with `scripts/plot_nmr.py` — pass it the parsed spectrum
   and a JSON list of multiplets (δ, multiplicity, J, nH, atom labels,
   assignment, confidence) plus impurities. If the user supplied a structure
   image, embed it directly; otherwise the script can draw from supplied 2D
   atom coordinates, or you draw a clean numbered skeleton. See
   `references/output_spec.md`.
2. Write the Markdown table (with the confidence column) and SAVE it as
   `<sample>_1H_assignment.md` in the outputs folder — this file is a
   mandatory deliverable, do not leave the table only in the chat.
3. Write the SI string. Group multiplets from low to high field per convention
   (highest δ first), report J to one decimal, and keep multiplicity codes
   standard (s, d, t, q, dd, dt, ddd, m, br). Total H in the string must equal
   the formula.

## Step 8 — Verify before delivering

- Re-add the integrals in the final table; confirm the total matches the
  formula and flag any discrepancy.
- Re-read the figure you generated (open the PNG) to confirm labels are legible
  and not overlapping, the structure numbering matches the table, and impurity
  peaks are marked.
- Sanity-check J values: coupling partners must share the same J (a ³J that
  appears on one peak must appear on its partner).
- Confirm BOTH files exist in the outputs folder (the annotated PNG and the
  `*_1H_assignment.md`) and that both were presented to the user.

## Step 9 — Independent review / audit (do not skip on messy spectra)

A finished-looking table is the most dangerous moment: it invites you to stop
thinking. Before delivering, run a dedicated review pass whose job is to
*falsify* the draft, following `references/review_checklist.md`.

For a clean, small molecule a careful self-review is enough. For a messy,
crowded, or high-stakes spectrum (overlap, mixtures, many stereocentres),
run it as a TRULY INDEPENDENT review: spawn a reviewer subagent (Task tool)
and hand it only the parsed data (δ / integrals / J / solvent / field), the
structure, and your draft table — instruct it to challenge every row and to
check sample integrity first (is this even one compound?). It starts from the
data instead of your conclusion, so it catches anchoring mistakes a self-check
misses. Reconcile its findings with yours, correct the table, and adjust
confidence levels honestly.

Record the outcome in a **审查结果 / Review** section appended to the `.md`:
each check's result, discrepancies found and fixed, and residual risks with
the concrete experiment that resolves them. Crucially, if the review finds the
sample is impure or a mixture, say so up front — it changes what the data can
support.

## Output language

Default to the user's working language for the table and prose (they have been
writing in Chinese — use 高/中/低 and Chinese assignment text), and keep the SI
string in standard English/IUPAC notation, since that is what goes into a
manuscript. Follow the user's lead if they ask otherwise.

## Reference files

- `references/input_formats.md` — parsing Bruker / JCAMP-DX / MestReNova /
  image, with code.
- `references/assignment_guide.md` — diagnostic shifts & couplings, residual
  solvent / impurity table, 2D-experiment cheat sheet.
- `references/output_spec.md` — exact figure layout, table columns, SI-string
  rules.
- `references/review_checklist.md` — the Step 9 falsification checklist.
- `references/impurities.csv` + `scripts/impurity_lookup.py` — J&K common
  ¹H impurity shifts (12 solvents) and a lookup tool for Step 4.
- `scripts/bruker_read.py` — read Bruker pdata, build ppm axis, integrate.
- `scripts/plot_nmr.py` — render the annotated figure.
