"""Wave interference — a ripple tank. Several point sources each emit cos(k·r − φ); summed, their
crests and troughs reinforce and cancel into interference fringes (the physics behind the double-slit
bands and Newton's rings). Amplitude mapped to a cool-deep→bright ramp; nodal lines (destructive
cancellation) read as dark filaments threading the bright antinodal zones."""
import os, math
import numpy as np
from pnglib import write_png
OUT = os.path.join(os.path.dirname(__file__), "..", "images")
W=H=1200
xs=np.linspace(-1,1,W); X,Y=np.meshgrid(xs,xs)
k=42.0
# sources on a gentle ring + one off-centre, slightly detuned phases
srcs=[(0.6*math.cos(a),0.6*math.sin(a),i*0.5) for i,a in enumerate(np.linspace(0,2*math.pi,5,endpoint=False))]
srcs.append((0.0,0.0,0.0))
field=np.zeros((H,W))
for (sx,sy,ph) in srcs:
    r=np.sqrt((X-sx)**2+(Y-sy)**2)
    field+=np.cos(k*r-ph)/np.sqrt(1+8*r)   # amplitude falls with distance
field/=np.max(np.abs(field))
# map: deep blue trough → black node → warm crest
a=(field*0.5+0.5)  # 0..1
stops=np.array([[0.05,0.10,0.30],[0.02,0.02,0.05],[0.55,0.20,0.15],[1.0,0.85,0.55]])
t=a*(len(stops)-1); i0=np.clip(t.astype(int),0,len(stops)-2); f=(t-i0)[...,None]
img=stops[i0]+(stops[i0+1]-stops[i0])*f
# emphasise nodal (|field|~0) darkness
node=np.exp(-(field*field)/(2*0.02**2))[...,None]
img=img*(1-0.6*node)
np.clip(img,0,1,out=img)
write_png(os.path.join(OUT,"interference.png"),(img*255).astype(np.uint8))
write_png("/private/tmp/claude-501/-Users-beckyconning-conceptmodel/fafc4c16-3002-4c19-994d-3bed032b12f5/scratchpad/interf_prev.png",(img[::3,::3]*255).astype(np.uint8))
print(f"wrote interference.png ({W}x{H}, {len(srcs)} sources)")
