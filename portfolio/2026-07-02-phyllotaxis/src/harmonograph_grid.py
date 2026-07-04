"""Harmonograph atlas — 2x3 grid of frequency-ratio / phase / damping presets, each an unbroken
damped-Lissajous stroke. Same machine, six tunings: from tight roses to open drifting ribbons."""
import os, math
import numpy as np
from pnglib import write_png
OUT = os.path.join(os.path.dirname(__file__), "..", "images")
P, G, ROWS, COLS = 380, 8, 2, 3
STEPS, dt = 150000, 0.0011
# (fx1,fx2,fy1,fy2, d, seedphase)
PRESETS = [
 (2.0,3.01,3.0,2.004,0.0018,0.0),
 (3.0,2.01,2.0,4.003,0.0022,0.6),
 (5.0,3.0,3.0,5.008,0.0016,0.2),
 (2.0,2.99,2.0,3.002,0.0026,0.9),
 (4.0,5.02,5.0,4.006,0.0014,0.4),
 (3.0,4.01,4.0,3.004,0.0020,1.2),
]
t = np.arange(STEPS)*dt
canvas = np.ones((ROWS*P+(ROWS+1)*G, COLS*P+(COLS+1)*G, 3))*np.array([0.02,0.02,0.03])
cool=np.array([0.25,0.55,0.95]); warm=np.array([1.0,0.72,0.30])
for idx,(fx1,fx2,fy1,fy2,d,ph) in enumerate(PRESETS):
    ex=np.exp(-d*t)
    x=(np.sin(fx1*t+ph)+0.7*np.sin(fx2*t+math.pi/2))*ex
    y=(np.sin(fy1*t+math.pi/4)+0.7*np.sin(fy2*t))*ex
    gx=np.clip(((x/1.75*0.5+0.5)*(P-1)).astype(np.int32),0,P-1)
    gy=np.clip(((y/1.75*0.5+0.5)*(P-1)).astype(np.int32),0,P-1)
    panel=np.zeros((P,P,3)); frac=t/t[-1]
    cols=cool[None,:]+(warm-cool)[None,:]*frac[:,None]
    np.add.at(panel,(gy,gx),cols*0.6)
    panel=1.0-np.exp(-1.9*panel)
    rr,cc=divmod(idx,COLS); y0,x0=G+rr*(P+G),G+cc*(P+G)
    canvas[y0:y0+P,x0:x0+P]=np.clip(panel,0,1)
write_png(os.path.join(OUT,"harmonograph_grid.png"),(canvas*255).astype(np.uint8))
write_png("/private/tmp/claude-501/-Users-beckyconning-conceptmodel/fafc4c16-3002-4c19-994d-3bed032b12f5/scratchpad/harmo_grid_prev.png",(canvas[::3,::3]*255).astype(np.uint8))
print(f"wrote harmonograph_grid.png ({canvas.shape[1]}x{canvas.shape[0]}, 6 presets)")
