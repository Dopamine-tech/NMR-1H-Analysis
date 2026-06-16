#!/usr/bin/env python3
"""Look up common-NMR-impurity candidates for a given solvent and chemical shift.

Data: references/impurities.csv (J&K Scientific common-impurity ¹H shift table,
12 solvents). Use this in Step 4 to label/justify solvent & impurity peaks, and
in Step 0/3 so impurity protons are never mistaken for compound signals.

  python impurity_lookup.py --solvent CDCl3 --ppm 1.26 [--tol 0.05]
  python impurity_lookup.py --solvent DMSO --ppm 3.33,2.50,1.15
  python impurity_lookup.py --solvent CDCl3 --list      # dump all for that solvent

Solvent keys: THF, CD2Cl2, CDCl3, toluene, C6D6, C6D5Cl, acetone, DMSO,
CD3CN, TFE, CD3OD, D2O  (aliases: CDCl3=chloroform-d; DMSO=DMSO-d6; etc.)
"""
import csv, os, argparse

ALIAS = {'cdcl3':'CDCl3','chloroform':'CDCl3','dmso':'DMSO','dmso-d6':'DMSO',
         'd2o':'D2O','cd3od':'CD3OD','meod':'CD3OD','methanol-d4':'CD3OD',
         'cd3cn':'CD3CN','acetonitrile-d3':'CD3CN','acetone':'acetone',
         'acetone-d6':'acetone','c6d6':'C6D6','benzene-d6':'C6D6',
         'cd2cl2':'CD2Cl2','thf':'THF','thf-d8':'THF','toluene':'toluene',
         'toluene-d8':'toluene','c6d5cl':'C6D5Cl','tfe':'TFE','tfe-d3':'TFE'}

def _csv_path():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, '..', 'references', 'impurities.csv')

def load():
    with open(_csv_path()) as f:
        return list(csv.DictReader(f))

def norm_solvent(s):
    return ALIAS.get(s.strip().lower(), s.strip())

def lookup(ppm, solvent, tol=0.05):
    col = norm_solvent(solvent)
    rows = load()
    if col not in rows[0]:
        raise SystemExit(f"unknown solvent '{solvent}'. Columns: "
                         + ", ".join(k for k in rows[0] if k not in ('name','proton','mult')))
    hits = []
    for r in rows:
        v = r.get(col, '-')
        for part in str(v).replace('/', ' ').split():
            try:
                d = float(part)
            except ValueError:
                continue
            if abs(d - ppm) <= tol:
                hits.append((abs(d - ppm), d, r['name'], r['proton'], r['mult']))
    hits.sort()
    return hits


def identify(observed, solvent, tol=0.03):
    """Given the list of observed peak δ's, find which named substances have
    MULTIPLE of their characteristic peaks present — so a multi-line impurity
    (e.g. ethyl acetate = 4.12 q + 2.05 s + 1.26 t) is pinned to the specific
    compound instead of a vague single-line guess. Returns substances ranked by
    how many of their peaks matched, with the matched shifts."""
    col = norm_solvent(solvent)
    rows = load()
    bysub = {}
    for r in rows:
        try:
            d = float(r.get(col, '-'))
        except ValueError:
            continue
        hit = [o for o in observed if abs(o - d) <= tol]
        if hit:
            bysub.setdefault(r['name'], []).append((d, r['proton'], min(hit)))
    ranked = sorted(bysub.items(), key=lambda kv: -len(kv[1]))
    return ranked

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--solvent', required=True)
    ap.add_argument('--ppm', help='comma-separated δ value(s) to look up')
    ap.add_argument('--tol', type=float, default=0.05)
    ap.add_argument('--list', action='store_true', help='dump all impurities for the solvent')
    ap.add_argument('--identify', help='comma δ list of all non-compound peaks; pins multi-line impurities')
    a = ap.parse_args()
    col = norm_solvent(a.solvent)
    if a.list:
        for r in load():
            print(f"  {r.get(col,'-'):>7}  {r['name']} ({r['proton']}, {r['mult']})")
    if a.identify:
        obs=[float(x) for x in a.identify.split(',')]
        print(f'Multi-peak impurity identification ({col}):')
        for name, hits in identify(obs, a.solvent):
            tag='  <-- specific (>=2 peaks)' if len(hits)>=2 else ''
            shifts=', '.join(f"{d}({pr})" for d,pr,_ in hits)
            print(f'   {name}: {len(hits)} peak(s) [{shifts}]{tag}')
    if a.ppm:
        for p in [float(x) for x in a.ppm.split(',')]:
            hits = lookup(p, a.solvent, a.tol)
            if not hits:
                print(f"δ {p} ({col}): no common-impurity match within ±{a.tol} → treat as UNKNOWN impurity (discuss in md, do not label on figure)")
            else:
                print(f"δ {p} ({col}) candidates:")
                for dd, d, name, proton, mult in hits:
                    print(f"   {d:>6}  {name} ({proton}, {mult})   |Δ|={dd:.3f}")
