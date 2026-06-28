#!/usr/bin/env python3
"""Growth piece #3 — FORM axis: VECTOR (SVG), not raster. Pure text output, no
numpy. Flat colour, hard edges, scalable — the opposite of the soft accumulated
raster. Same representational subject (sun over layered hills) in a riso/earth
palette with negative-space sky, so the *form* change is the clear move.
"""
import math

W, H = 1200, 820
HORIZON = 0.60


def hill_path(y_frac, amp, wobble, phase, seed):
    """A smooth flat-topped hill band as an SVG path filled down to the bottom."""
    pts = []
    n = 14
    for i in range(n + 1):
        x = W * i / n
        # gentle layered sine ridge (deterministic, hard-edged flat fill)
        y = H * y_frac - amp * (math.sin(i * wobble + phase) + 0.5 * math.sin(i * wobble * 2.3 + seed))
        pts.append((x, y))
    d = f"M0,{H} L0,{pts[0][1]:.1f} "
    # smooth-ish via quadratic segments between points
    for i in range(1, len(pts)):
        x0, y0 = pts[i - 1]; x1, y1 = pts[i]
        mx = (x0 + x1) / 2
        d += f"Q{x0:.1f},{y0:.1f} {mx:.1f},{(y0 + y1) / 2:.1f} "
    d += f"L{W},{pts[-1][1]:.1f} L{W},{H} Z"
    return d


def main():
    # riso / earth palette, far -> near
    bands = [
        (0.50, 18, "#c9b79c"),   # pale dune
        (0.58, 30, "#b08968"),   # clay
        (0.68, 44, "#8c6a4a"),   # terracotta-brown
        (0.80, 60, "#5b4632"),   # deep umber
    ]
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}">']
    # paper sky (flat, with a single warm band near horizon — negative space above)
    svg.append(f'<rect width="{W}" height="{H}" fill="#f2e6cf"/>')
    svg.append(f'<rect width="{W}" y="{H*HORIZON*0.78:.0f}" height="{H*HORIZON*0.32:.0f}" fill="#f6d9a8"/>')
    # flat sun disc (hard edge), off-centre (rule of thirds)
    svg.append(f'<circle cx="{W*0.70:.0f}" cy="{H*0.30:.0f}" r="58" fill="#e9a06a"/>')
    # hill bands
    for i, (yf, amp, col) in enumerate(bands):
        svg.append(f'<path d="{hill_path(yf, amp, 0.55 + 0.12*i, i*1.7, i*3+1)}" fill="{col}"/>')
    svg.append('</svg>')
    open("vector_hills.svg", "w").write("\n".join(svg))
    print("wrote vector_hills.svg")


if __name__ == "__main__":
    main()
