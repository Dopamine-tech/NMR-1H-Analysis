# nmr-analysis

**A Claude Agent Skill that reads raw NMR data + a chemical structure and returns a fully annotated spectrum, a confidence‑scored assignment table, and a copy‑paste SI string.**

给 Claude 用的 NMR 解谱技能：丢进**原始谱图数据 + 分子结构**，自动产出**标注好的谱图、带置信度的归属表、可直接入稿的 SI 文字**，并把结果存进以化合物命名的文件夹。![image-20260616172622496](C:\Users\OMEN\Documents\nmr-analysis\references\image-20260616172622496.png)

![image-20260616172502742](C:\Users\OMEN\Documents\nmr-analysis\references\image-20260616172502742.png)

---

## What it does / 它能做什么

You hand Claude an NMR dataset and a structure; the skill works through a chemist's
checklist and returns three deliverables every time:

1. **Annotated spectrum (PNG)** — peak δ on top, **integration‑coverage brackets**
   below (showing the exact ppm window integrated), multiplet boxes (atom # +
   multiplicity), solvent/impurity peaks in grey, and the **numbered structure
   embedded with each assigned atom tinted by confidence** (green/amber/red).
2. **Assignment table (Markdown)** — `δ | multiplicity (J) | integration | atom |
   assignment | confidence | basis`, with ⚠ flags on uncertain rows.
3. **SI string** — `¹H NMR (500 MHz, CDCl₃) δ …`, manuscript‑ready.

It is built to be **honest**: it states up front whether the spectrum even matches
the structure, flags impure samples instead of force‑fitting impurity peaks onto
the molecule, and recommends the specific experiment (COSY/HSQC/D₂O/LC‑MS) that
would resolve each uncertainty.

### Highlights

- **Inputs:** Bruker dataset (`.zip` or folder with `fid` + `pdata`), JCAMP‑DX
  (`.dx`/`.jdx`), MestReNova peak/multiplet exports, or a spectrum image/PDF.
- **Nuclei:** ¹H, ¹³C, with COSY/HSQC support.
- **Step 0 sanity check** — *does this spectrum match this formula?* with a
  high/medium/low verdict, before any peak‑by‑peak work.
- **Phase & reference calibration** — verifies phasing, calibrates δ to TMS or the
  residual solvent peak.
- **Integrate every peak** — aromatic *and* aliphatic, shown as coverage brackets.
- **Impurity identification** — a bundled 12‑solvent common‑impurity table
  (J&K/Gottlieb‑style) + a lookup tool that pins specific substances by their
  multi‑peak fingerprint (e.g. `4.12 q + 2.05 s + 1.26 t → ethyl acetate`, not a
  vague "grease").
- **Salt‑form aware** — recognises HCl/TFA salts (extra N⁺–H, shifted N‑CH₃) so it
  doesn't mis‑call them as impurities.
- **Honest confidence + independent review** — a falsification pass (Step 9) that,
  for messy spectra, checks sample integrity, coupling notation (ⁿJ bond counting),
  and over‑confident rows.
- **Outputs land in `<compound>_<date>_Claude/`**, saved next to the original data
  when a matching folder is found.

---

## Repository layout / 仓库结构

```
nmr-analysis/
├── SKILL.md                     # the skill itself (instructions Claude follows)
├── scripts/
│   ├── bruker_read.py           # read Bruker pdata, phase/ref check, calibrate, integrate
│   ├── plot_nmr.py              # render the annotated figure
│   └── impurity_lookup.py       # common-impurity lookup / fingerprint identification
└── references/
    ├── input_formats.md         # parsing Bruker / JCAMP-DX / MestReNova / image
    ├── assignment_guide.md      # diagnostic shifts & couplings, solvent/impurity & salt notes, 2D cheat sheet
    ├── output_spec.md           # exact figure layout, table columns, SI-string rules
    ├── review_checklist.md      # the Step 9 falsification checklist
    └── impurities.csv           # common NMR impurity ¹H shifts, 12 solvents
```

---

## Installation / 安装

The scripts need **Python 3** with **numpy** and **matplotlib** (no internet
required — the impurity table is bundled):

```bash
pip install numpy matplotlib
```

Then install the skill into whichever Claude product you use:

### Option A — Claude Code

Skills live in a `skills/` folder under `.claude/`. Copy the `nmr-analysis`
directory there:

```bash
# clone this repo
git clone https://github.com/<you>/nmr-analysis.git

# install globally for your user …
mkdir -p ~/.claude/skills
cp -r nmr-analysis ~/.claude/skills/nmr-analysis

# … or per-project (inside a repo you're working in)
mkdir -p .claude/skills
cp -r nmr-analysis .claude/skills/nmr-analysis
```

Restart Claude Code. The skill auto‑triggers on phrases like *"assign these peaks"*,
*"解一下这个氢谱"*, *"做个归属表"*, or you can mention it by name.

### Option B — Claude Desktop（Desktop App）

Use the packaged **`nmr-analysis.skill`** file (a zip of this folder):

1. Open **Settings → Capabilities → Skills**.
2. Choose **Install skill** and select `nmr-analysis.skill`.
   *(In a Cowork chat you can also drop the `.skill` file in and click **Save skill**.)*

To build the `.skill` from source yourself, just zip the folder:

```bash
cd nmr-analysis && zip -r ../nmr-analysis.skill . -x '*/__pycache__/*'
```

### Option C — use the scripts standalone（不装技能，直接用脚本）

The Python tools work on their own:

```bash
# read a Bruker dataset, check phase, integrate windows (ref-normalised)
python scripts/bruker_read.py path/to/EXPNO/pdata/1 --phasecheck \
       --integrate "8.33-8.19,7.62-7.55,4.46-4.39" --ref "4.46-4.39"

# look up / fingerprint an impurity peak
python scripts/impurity_lookup.py --solvent CDCl3 --identify "4.12,2.05,1.26,0.88"

# render an annotated figure from a spec JSON (see references/output_spec.md)
python scripts/plot_nmr.py spec.json
```

---

## Usage / 用法

Once installed, just give Claude the data and the structure:

> *"解一下这个氢谱，结构在这张图里。"* （附上 Bruker `.zip` 和结构图）
>
> *"Assign the ¹H NMR for this compound."* (attach the data + structure)

Claude will run the full workflow and hand back the figure, the Markdown table,
and the SI string — saved into a `<compound>_<date>_Claude/` folder. If no compound
name is given, it asks. If the spectrum doesn't match the structure, it tells you.

---

## Notes & limitations / 说明与局限

- A picture/PDF of a spectrum can be read for δ and apparent multiplicity, but it
  **cannot be re‑integrated** — confidence is capped accordingly.
- Multiplicity labels from auto multiplet‑analysis software are often wrong on
  overlapping/second‑order aromatic systems; the skill re‑derives them.
- Enantiomers give identical ¹H spectra — the skill can't assign R/S; use chiral
  HPLC / optical rotation / NOE for configuration.
- The bundled impurity table is a curated subset of the common‑NMR‑impurity
  reference (Gottlieb/Fulmer/J&K). Verify unusual species independently.

---

## License / 许可

MIT — see `LICENSE`. Built as a Claude Agent Skill.
Contributions and issues welcome.
