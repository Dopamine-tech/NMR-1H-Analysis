#!/usr/bin/env python3
"""Read a Bruker NMR dataset: build the ppm axis, expose metadata, integrate.

Usage
-----
  python bruker_read.py <pdata_dir>                # dump metadata + save x/y
  python bruker_read.py <pdata_dir> --csv out.csv  # save ppm,intensity CSV
  python bruker_read.py <pdata_dir> --integrate "8.33-8.19,7.62-7.55,..." [--ref 4.46-4.39]

<pdata_dir> is the processed-data folder, e.g. .../EXPNO/pdata/1
(it must contain `procs` and `1r`). The acquisition file `acqus` is read from
two levels up for solvent / frequency / nucleus when available.

Only numpy is required. No internet, no nmrglue needed.
"""
import sys, os, re, json, argparse
import numpy as np

def _getpar(path, key):
    if not os.path.exists(path):
        return None
    for line in open(path, errors='ignore'):
        if line.startswith('##$' + key + '='):
            return line.split('=', 1)[1].strip().strip('<>')
    return None

def load(pdata_dir):
    """Return dict with ppm axis, intensity, and metadata."""
    procs = os.path.join(pdata_dir, 'procs')
    onef  = os.path.join(pdata_dir, '1r')
    SF     = float(_getpar(procs, 'SF'))
    SW_p   = float(_getpar(procs, 'SW_p'))
    OFFSET = float(_getpar(procs, 'OFFSET'))
    SI     = int(_getpar(procs, 'SI'))
    NC     = int(_getpar(procs, 'NC_proc') or 0)
    BYT    = int(_getpar(procs, 'BYTORDP') or 0)
    dt = '>i4' if BYT == 1 else '<i4'
    y = np.fromfile(onef, dtype=dt).astype(float) * (2.0 ** NC)
    ppm = OFFSET - np.arange(SI) * SW_p / SF / SI   # high ppm -> low ppm

    # acquisition metadata (two levels up: EXPNO/acqus)
    acqus = os.path.normpath(os.path.join(pdata_dir, '..', '..', 'acqus'))
    meta = {
        'nucleus': _getpar(acqus, 'NUC1'),
        'solvent': _getpar(acqus, 'SOLVENT'),
        'pulprog': _getpar(acqus, 'PULPROG'),
        'field_MHz': None,
        'SF': SF, 'SW_ppm': round(SW_p / SF, 4), 'SI': SI,
    }
    bf1 = _getpar(acqus, 'BF1')
    if bf1:
        meta['field_MHz'] = round(float(bf1))
    return {'ppm': ppm, 'y': y, 'meta': meta, 'pdata_dir': pdata_dir}

def read_peaklist(pdata_dir):
    """Operator's saved peak list (pdata/1/peaklist.xml): list of (ppm, intensity)."""
    p = os.path.join(pdata_dir, 'peaklist.xml')
    if not os.path.exists(p):
        return []
    txt = open(p, errors='ignore').read()
    return [(float(a), float(b)) for a, b in
            re.findall(r'F1="([-\d.eE+]+)"\s+intensity="([-\d.eE+]+)"', txt)]

def read_intrng(pdata_dir):
    """Operator's saved integration ranges (pdata/1/intrng): list of (hi_ppm, lo_ppm)."""
    p = os.path.join(pdata_dir, 'intrng')
    out = []
    if os.path.exists(p):
        for line in open(p, errors='ignore'):
            m = re.match(r'\s*([-\d.]+)\s+([-\d.]+)', line)
            if m:
                a, b = float(m.group(1)), float(m.group(2))
                out.append((max(a, b), min(a, b)))
    return out


SOLVENT_REF = {'CDCl3':7.26,'DMSO':2.50,'CD3OD':3.31,'D2O':4.79,'CD3CN':1.94,
               'acetone':2.05,'C6D6':7.16,'CD2Cl2':5.32,'THF':3.58,'toluene':2.08,
               'TFE':3.88,'C6D5Cl':6.96}

def phase_baseline_ok(y):
    """Crude sanity flags for a processed spectrum: peaks should be absorptive
    (dominant max >> |min|) and the baseline roughly flat. Returns (ok, note)."""
    import numpy as _np
    mx, mn = float(_np.max(y)), float(_np.min(y))
    edges = _np.concatenate([y[:len(y)//50], y[-len(y)//50:]])
    base = float(_np.median(edges)) / (mx if mx else 1.0)
    ok = (mx >= abs(mn) * 0.8) and (abs(base) < 0.05)
    note = "max/|min|=%.1f baseline~%+.3f" % (mx/abs(mn) if mn else 0, base)
    if not ok:
        note += "  <- check phase/baseline"
    return ok, note

def calibrate(ppm, obs, target):
    """Shift the whole delta axis so a reference peak at obs reads target."""
    return ppm + (target - obs), (target - obs)

def integrate(ppm, y, ranges, ref=None):
    """ranges: list of (hi,lo) ppm. ref: (hi,lo) for the 1H normaliser.
    Returns list of dicts with raw and relative integrals."""
    def _area(hi, lo):
        m = (ppm <= hi) & (ppm >= lo)
        return float((getattr(np,"trapezoid",None) or np.trapz)(y[m]))
    raw = [(_area(hi, lo), hi, lo) for hi, lo in ranges]
    refval = _area(*ref) if ref else (raw[0][0] if raw else 1.0)
    return [{'hi': hi, 'lo': lo, 'raw': a, 'rel_H': round(a / refval, 3)}
            for a, hi, lo in raw]

def _parse_ranges(s):
    out = []
    for chunk in s.split(','):
        a, b = chunk.split('-') if '-' in chunk[1:] else chunk.split('..')
        a, b = float(a), float(b)
        out.append((max(a, b), min(a, b)))
    return out

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('pdata_dir')
    ap.add_argument('--csv')
    ap.add_argument('--npz')
    ap.add_argument('--integrate', help='comma list of hi-lo ppm windows')
    ap.add_argument('--ref', help='hi-lo ppm window of a clean 1H signal')
    ap.add_argument('--phasecheck', action='store_true')
    ap.add_argument('--calibrate', help='obs:target  e.g. 0.02:0.00 (TMS) or 7.28:7.26 (CHCl3)')
    a = ap.parse_args()
    d = load(a.pdata_dir)
    print(json.dumps(d['meta'], ensure_ascii=False, indent=2))
    if a.phasecheck:
        ok, note = phase_baseline_ok(d['y'])
        print('# phase/baseline: %s  (%s)' % ('OK' if ok else 'REVIEW', note))
        sol = d['meta'].get('solvent')
        if sol in SOLVENT_REF:
            print('# expected residual %s = %s ppm; TMS = 0.00 (use --calibrate if axis is off)' % (sol, SOLVENT_REF[sol]))
    if a.calibrate:
        o, tg = [float(x) for x in a.calibrate.split(':')]
        d['ppm'], shift = calibrate(d['ppm'], o, tg)
        print('# calibrated: shifted axis by %+.4f ppm (obs %s -> %s)' % (shift, o, tg))
    pk = read_peaklist(a.pdata_dir)
    ir = read_intrng(a.pdata_dir)
    if pk:
        print(f'# operator peaklist: {len(pk)} peaks, {pk[:5]} ...')
    if ir:
        print(f'# operator intrng ranges: {ir}')
    if a.csv:
        np.savetxt(a.csv, np.c_[d['ppm'], d['y']], delimiter=',',
                   header='ppm,intensity', comments='')
        print('wrote', a.csv)
    if a.npz:
        np.savez(a.npz, ppm=d['ppm'], y=d['y'])
        print('wrote', a.npz)
    if a.integrate:
        rngs = _parse_ranges(a.integrate)
        ref = _parse_ranges(a.ref)[0] if a.ref else None
        for r in integrate(d['ppm'], d['y'], rngs, ref):
            print(f"  {r['lo']:6.2f}-{r['hi']:5.2f} ppm   rel_H={r['rel_H']:.2f}")
