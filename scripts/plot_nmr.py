#!/usr/bin/env python3
"""Render an annotated NMR figure from a spec JSON.

  python plot_nmr.py spec.json

Spec schema (see references/output_spec.md for the full description):
{
  "title": "1H NMR (500 MHz, CDCl3)  ZQL-5ER",
  "subtitle": "* = solvent/impurity",
  "spectrum": {"npz": ".../spec.npz"}  | {"csv": ".../spec.csv"},
  "xlim": [8.6, -0.4],
  "multiplets": [
    {"ppm":8.26,"mult":"s","J":"","nH":1,"atoms":"10",
     "assign":"indole NH","conf":"high","integ":"0.97"}, ...],
  "impurities": [{"ppm":5.30,"label":"CH2Cl2"}, ...],
  "structure_image": "/path/structure.png",   # OPTIONAL: embed user's drawing
  "structure": { "atoms":{"1":[x,y],...}, "bonds":[[a,b],...],
                 "double":[[a,b],...], "triple":[[a,b],...],
                 "labels":{"10":"NH",...}, "title":"..." },  # OPTIONAL: draw
  "out": "/path/out.png"
}
Either structure_image OR structure may be given; image wins if both present.
Confidence ("high"/"medium"/"low") tints the annotation boxes.

Annotation boxes are packed into as many rows as needed so that boxes whose
peaks sit close together never overlap — each box is given a leader line down
to its own peak. This keeps crowded regions (e.g. an aliphatic envelope in
DMSO) legible instead of stacking labels on top of each other.
"""
import sys, json, re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Circle

CONF = {  # box facecolor, edgecolor
    'high':   ('#e9f7ef', '#3a9d6a'),
    'medium': ('#fdf3e0', '#d99a2b'),
    'low':    ('#fcebea', '#c0392b'),
    '':       ('#f3eefc', '#9070c0'),
}
# halo fill colour used to tint each atom on the structure by assignment confidence
HALO = {'high': '#7ed99a', 'medium': '#f4c160', 'low': '#ef8e8e'}
CONF_RANK = {'high': 2, 'medium': 1, 'low': 0}

def _atom_conf_map(multiplets):
    """Map each structure atom number that carries an assigned proton to a
    confidence level, so the structure can be tinted. When an atom appears in
    several multiplets, keep the LOWEST confidence (most conservative)."""
    m = {}
    for mp in multiplets:
        conf = mp.get('conf', '')
        if conf not in HALO:
            continue
        for tok in re.split(r'[\s,/]+', str(mp.get('atoms', ''))):
            key = re.sub(r'^[A-Za-z]+', '', tok).strip()  # 'C29'->'29'
            if not key:
                continue
            if key not in m or CONF_RANK[conf] < CONF_RANK[m[key]]:
                m[key] = conf
    return m

def _load_spectrum(s):
    if 'npz' in s:
        d = np.load(s['npz']); return d['ppm'], d['y']
    if 'csv' in s:
        a = np.loadtxt(s['csv'], delimiter=',', skiprows=1); return a[:, 0], a[:, 1]
    raise SystemExit('spectrum needs npz or csv')

def _draw_structure(ax, st, atom_conf=None):
    ax.axis('off'); ax.set_aspect('equal')
    P = {k: tuple(v) for k, v in st['atoms'].items()}
    xs = [p[0] for p in P.values()]; ys = [p[1] for p in P.values()]
    ax.set_xlim(min(xs) - 1, max(xs) + 1.2); ax.set_ylim(min(ys) - 1.3, max(ys) + 1)
    # confidence halos behind each assigned atom (drawn first, low zorder)
    atom_conf = atom_conf or {}
    for n, conf in atom_conf.items():
        if n in P and conf in HALO:
            ax.add_patch(Circle(P[n], 0.42, facecolor=HALO[conf], edgecolor='none',
                                alpha=0.85, zorder=0))
    def line(a, b, off=0, lw=1.3):
        (x1, y1), (x2, y2) = P[a], P[b]
        if off:
            dx, dy = x2 - x1, y2 - y1; n = np.hypot(dx, dy)
            px, py = -dy / n * off, dx / n * off
            ax.plot([x1 + px, x2 + px], [y1 + py, y2 + py], lw=lw, color='#111')
        else:
            ax.plot([x1, x2], [y1, y2], lw=lw, color='#111')
    for a, b in st.get('bonds', []): line(a, b)
    for a, b in st.get('double', []): line(a, b); line(a, b, off=0.12, lw=1.0)
    for a, b in st.get('triple', []):
        line(a, b); line(a, b, off=0.10, lw=1.0); line(a, b, off=-0.10, lw=1.0)
    labels = st.get('labels', {})
    for n, (x, y) in P.items():
        if n in labels:
            col = '#1560bd' if labels[n] in ('NH', 'OH', 'N', 'NH2', 'NMe2') else \
                  '#159215' if labels[n] in ('F', 'Cl', 'Br') else '#111'
            ax.text(x, y, labels[n], ha='center', va='center', fontsize=11, color=col,
                    bbox=dict(boxstyle='round,pad=0.05', fc='white', ec='none'))
    if st.get('numbers', True):
        for n, (x, y) in P.items():
            ax.text(x + 0.22, y + 0.20, str(n), fontsize=7, color='#c01010',
                    ha='center', va='center')
    if atom_conf:
        xlo, xhi = ax.get_xlim(); ylo, yhi = ax.get_ylim()
        lx = xlo + 0.04 * (xhi - xlo); ly = ylo + 0.10 * (yhi - ylo)
        for i, (lab, key) in enumerate([('high', 'high'), ('med', 'medium'), ('low', 'low')]):
            yy = ly - i * 0.07 * (yhi - ylo)
            ax.add_patch(Circle((lx, yy), 0.16, facecolor=HALO[key], edgecolor='none', alpha=0.85, zorder=2))
            ax.text(lx + 0.30, yy, lab, fontsize=6, va='center', ha='left', color='#444', zorder=2)
    if st.get('title'):
        ax.set_title(st['title'], fontsize=9, pad=2)

def _pack_rows(centers, halfwidth, gap):
    """Greedy interval packing. centers: list of ppm (any order).
    Returns dict idx->row so that boxes (center ± halfwidth) sharing a row never
    overlap. Packs left-to-right on a reversed (high->low ppm) axis."""
    order = sorted(range(len(centers)), key=lambda i: -centers[i])  # high ppm first
    rows_edge = []     # for each row, the last (lowest) ppm edge occupied
    rowof = {}
    for i in order:
        c = centers[i]; top = c + halfwidth      # higher-ppm edge of this box
        placed = False
        for r, edge in enumerate(rows_edge):
            if top <= edge - gap:                # fits to the right of last box in row r
                rows_edge[r] = c - halfwidth
                rowof[i] = r; placed = True; break
        if not placed:
            rows_edge.append(c - halfwidth)
            rowof[i] = len(rows_edge) - 1
    return rowof, len(rows_edge)

def main(spec_path):
    S = json.load(open(spec_path))
    ppm, y = _load_spectrum(S['spectrum'])
    y = y / y.max()
    xlim = S.get('xlim', [float(ppm.max()) + 0.3, float(ppm.min()) - 0.3])
    span = abs(xlim[0] - xlim[1])

    fig = plt.figure(figsize=(16, 9))
    ax = fig.add_axes([0.04, 0.09, 0.93, 0.52])
    ax.plot(ppm, y, lw=0.7, color='#111')
    ax.set_xlim(*xlim); ax.set_ylim(-0.22, 1.22)
    ax.set_xlabel('f1 (ppm)'); ax.set_yticks([])
    lo, hi = sorted(xlim)
    ax.set_xticks(np.arange(np.floor(lo), np.ceil(hi) + 0.5, 0.5)); ax.tick_params(labelsize=8)
    for sp in ['top', 'left', 'right']: ax.spines[sp].set_visible(False)

    M = S.get('multiplets', [])
    BR = '#7a5ea8'   # integration bracket colour
    yb = -0.055      # bracket baseline (just under the spectrum)
    for m in M:
        x = m['ppm']
        ax.text(x, 1.05, f"{x:.2f}", rotation=90, fontsize=6.5, ha='center', va='bottom', color='#222')
        if m.get('integ') not in (None, ''):
            # integration coverage bracket: spans the integrated ppm window, with end ticks
            rng = m.get('range')
            if not rng:
                hw = 0.012 * abs(xlim[0] - xlim[1]) / 10.0 + 0.04
                rng = [x + hw, x - hw]
            hi, lo = max(rng), min(rng)
            ax.plot([hi, lo], [yb, yb], color=BR, lw=1.0, zorder=4)
            for e in (hi, lo):
                ax.plot([e, e], [yb - 0.012, yb + 0.012], color=BR, lw=1.0, zorder=4)
            ax.text((hi + lo) / 2, yb - 0.022, str(m['integ']), rotation=90,
                    fontsize=6.3, ha='center', va='top', color='#0a7d3a', zorder=4)
    # impurities: light-grey name placed JUST ABOVE its own peak so it is clearly
    # tied to the peak (never looks "unhandled"); a short grey tick marks the apex.
    def _peak_h(px):
        i = int(np.argmin(np.abs(ppm - px)))
        w = max(2, int(len(ppm) * 0.0008))
        return float(np.max(y[max(0, i - w):i + w + 1]))
    for im in S.get('impurities', []):
        ph = min(_peak_h(im['ppm']), 1.0)
        ax.plot([im['ppm'], im['ppm']], [ph + 0.01, ph + 0.05], color='#b8b8b8', lw=0.7, zorder=2)
        ax.text(im['ppm'], ph + 0.07, f"{im['label']} {im['ppm']:.2f}*", rotation=90,
                fontsize=6.3, ha='center', va='bottom', color='#9a9a9a', zorder=2)

    # ---- annotation boxes: pack into non-overlapping rows with leader lines ----
    if M:
        centers = [m['ppm'] for m in M]
        halfwidth = span * 0.030          # ~ box half-width in ppm
        rowof, nrows = _pack_rows(centers, halfwidth, gap=span * 0.004)
        top_y, bot_y = 0.82, 0.28         # band the rows live in (stays clear of the structure corner)
        nrows = max(nrows, 1)
        ylev = [top_y - (top_y - bot_y) * (r / max(nrows - 1, 1)) for r in range(nrows)]
        fs = 6.6 if nrows <= 4 else 6.0 if nrows <= 7 else 5.3
        for i, m in enumerate(M):
            x = m['ppm']; yb = ylev[rowof[i]]
            fc, ec = CONF.get(m.get('conf', ''), CONF[''])
            ax.plot([x, x], [0.17, yb - 0.005], lw=0.45, color='#aaa', zorder=1)
            flag = ' ⚠' if m.get('conf') == 'medium' else ' ⚠⚠' if m.get('conf') == 'low' else ''
            txt = f"{m.get('atoms','')}  ({m.get('mult','')}){flag}".strip()
            if m.get('assign'):
                txt += f"\n{m['assign']}"
            ax.text(x, yb, txt, fontsize=fs, ha='center', va='bottom', color='#333', zorder=3,
                    bbox=dict(boxstyle='round,pad=0.22', fc=fc, ec=ec, lw=0.8))

    # structure: embed image or draw
    sbox = S.get('structure_box', [0.70, 0.605, 0.29, 0.34])  # top-right corner, small
    sx = fig.add_axes(sbox)
    if S.get('structure_image'):
        sx.axis('off'); sx.imshow(mpimg.imread(S['structure_image']))
    elif S.get('structure'):
        _draw_structure(sx, S['structure'], _atom_conf_map(M))
    else:
        sx.axis('off')

    if S.get('title'):
        fig.suptitle(S['title'] + ('   ' + S['subtitle'] if S.get('subtitle') else ''),
                     fontsize=11, y=0.975, x=0.28, ha='center')
    fig.savefig(S['out'], dpi=170)
    print('wrote', S['out'])

if __name__ == '__main__':
    main(sys.argv[1])
