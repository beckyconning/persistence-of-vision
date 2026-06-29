"""Elementary (Wolfram 1D) cellular automata as tall tapestries — a new axis: a complex
image grown from ONE local rule + one seed, no drawing, no LLM, fully deterministic.

Each row is one time-step; cell (t+1, x) = rule applied to the 3-cell neighbourhood at t.
Rule 110 is Turing-complete and makes structured-yet-irregular weave; rule 30 is chaotic.
Rendered with depth shading (a cell's colour tracks how long it's been alive) so the woven
structures read with light, not just black/white. Pure numpy; stdlib filter-0 PNG out.
"""
import os

import numpy as np
from pnglib import ramp, write_png


def evolve(rule: int, w: int, h: int, seed: str = "center") -> np.ndarray:
    """Run an elementary CA. Returns an (h, w) uint8 {0,1} grid, row = time-step.

    Args:
        rule: Wolfram rule number 0-255.
        w, h: grid width (cells) and height (steps).
        seed: "center" (single live cell) or "random" (random first row).

    Returns:
        (h, w) array of 0/1.
    """
    table = np.array([(rule >> k) & 1 for k in range(8)], np.uint8)  # table[neighbourhood]
    grid = np.zeros((h, w), np.uint8)
    if seed == "random":
        rng = np.linspace(0, 1, w)  # deterministic "noise" (no RNG — banned in this kit)
        grid[0] = ((np.sin(rng * 97.3) * 43758.5) % 1.0 > 0.5).astype(np.uint8)
    else:
        grid[0, w // 2] = 1
    for t in range(1, h):
        left = np.roll(grid[t - 1], 1)
        right = np.roll(grid[t - 1], -1)
        idx = (left << 2) | (grid[t - 1] << 1) | right  # 3-bit neighbourhood -> 0..7
        grid[t] = table[idx]
    return grid


def age_field(grid: np.ndarray) -> np.ndarray:
    """Per-cell 'age' = consecutive live steps up to each row, normalised 0..1 — gives the
    tapestry depth/shading instead of flat binary."""
    h, w = grid.shape
    age = np.zeros((h, w), np.float32)
    for t in range(1, h):
        age[t] = (age[t - 1] + 1.0) * grid[t]
    return np.clip(age / 18.0, 0, 1)


def render(grid: np.ndarray, stops: list) -> np.ndarray:
    """Colour a CA grid: dead cells = the first stop (ground), live cells shaded by age."""
    age = age_field(grid)
    # Floor live cells well above ground so SPARSE/short-lived rules (e.g. 90) still read;
    # age then lifts long-lived cells toward the bright stop.
    img = ramp(0.4 + 0.6 * age, stops)  # (h,w,3) float 0..1
    dead = grid == 0
    ground = np.array(stops[0])
    img[dead] = ground
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)


def upscale(img: np.ndarray, k: int) -> np.ndarray:
    """Nearest-neighbour integer upscale (crisp cells, no blur)."""
    return np.repeat(np.repeat(img, k, axis=0), k, axis=1)


def main():
    here = os.path.dirname(__file__)
    out = os.path.join(here, "..", "images")
    jobs = [
        # rule, w, h, seed, palette (dead→old), scale, filename
        (110, 360, 460, "center",
         [(0.06, 0.07, 0.11), (0.95, 0.55, 0.25), (0.98, 0.85, 0.55)], 3, "rule110.png"),
        (30, 380, 380, "center",
         [(0.04, 0.05, 0.08), (0.30, 0.55, 0.75), (0.85, 0.95, 1.0)], 3, "rule30.png"),
        (90, 384, 384, "center",  # Sierpinski
         [(0.05, 0.04, 0.07), (0.55, 0.25, 0.55), (0.95, 0.8, 0.55)], 3, "rule90.png"),
    ]
    for rule, w, h, seed, stops, k, fn in jobs:
        grid = evolve(rule, w, h, seed)
        img = upscale(render(grid, stops), k)
        write_png(os.path.join(out, fn), img)
        live = int(grid.sum())
        print(f"rule {rule}: {w}x{h} ({live} live cells) -> {fn} ({img.shape[1]}x{img.shape[0]})")


if __name__ == "__main__":
    main()
