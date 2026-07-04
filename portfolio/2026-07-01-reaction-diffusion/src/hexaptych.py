"""
Gray-Scott HEXAPTYCH — the capstone. All six explorations composed into one canvas: six panels
of the same 40-line reaction, each a different way of varying the control or reading the state.
Left→right, top→bottom: worms · atlas · iris / aniso · fronts · chrono. One organism, six lives.
A single coherent artwork and the index image for the piece.
"""
import os
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
PW, PH, STEPS = 300, 220, 9000          # per-panel sim res / steps (kept small; 6 sims)
dt = 1.0
WARM = np.array([[0.03,0.02,0.05],[0.24,0.06,0.22],[0.62,0.10,0.34],[0.92,0.45,0.20],[0.99,0.93,0.80]])


def d2x(Z): return np.roll(Z,1,1)+np.roll(Z,-1,1)-2*Z
def d2y(Z): return np.roll(Z,1,0)+np.roll(Z,-1,0)-2*Z
def lap(Z):
    return (-Z + 0.20*(np.roll(Z,1,0)+np.roll(Z,-1,0)+np.roll(Z,1,1)+np.roll(Z,-1,1))
            + 0.05*(np.roll(np.roll(Z,1,0),1,1)+np.roll(np.roll(Z,1,0),-1,1)
                    + np.roll(np.roll(Z,-1,0),1,1)+np.roll(np.roll(Z,-1,0),-1,1)))


def seedUV(rs):
    rng = np.random.default_rng(rs)
    U = np.ones((PH,PW)); V = np.zeros((PH,PW))
    s = rng.random((PH,PW))>0.65; V[s]=0.25; U[s]=0.5
    return U,V


def ramp(v, stops=WARM):
    v = v-v.min(); v/=(v.max() or 1.0); v=np.power(v,0.85)
    t=v*(len(stops)-1); i0=np.clip(t.astype(int),0,len(stops)-2); f=(t-i0)[...,None]
    return np.clip(stops[i0]+(stops[i0+1]-stops[i0])*f,0,1)


def panel_iso(F,k,rs):
    U,V=seedUV(rs)
    for _ in range(STEPS):
        uvv=U*V*V; U+=(0.16*lap(U)-uvv+F*(1-U))*dt; V+=(0.08*lap(V)+uvv-(F+k)*V)*dt
    return ramp(V)

def panel_field(Ff,kf,rs,readout="fill"):
    U,V=seedUV(rs)
    snaps={}
    for step in range(STEPS):
        uvv=U*V*V; U+=(0.16*lap(U)-uvv+Ff*(1-U))*dt; V+=(0.08*lap(V)+uvv-(Ff+kf)*V)*dt
        if readout=="chrono" and step in (1700,4000,STEPS-1):
            s=V.copy(); s-=s.min(); s/=(s.max() or 1.0); snaps[step]=np.power(s,0.8)
    if readout=="fill": return ramp(V)
    if readout=="edge":
        e=np.sqrt(d2x(V)**2+d2y(V)**2) if False else np.sqrt((np.roll(V,-1,1)-np.roll(V,1,1))**2+(np.roll(V,-1,0)-np.roll(V,1,0))**2)
        e/=(e.max() or 1.0); e=np.power(e,0.6)[...,None]
        v=V-V.min(); v/=(v.max() or 1.0)
        body=np.stack([0.14*v+0.02,0.05*v+0.01,0.16*v+0.03],-1)
        return np.clip(body+e*(np.array([0.30,0.95,0.90])-body)+ (e**3)*np.array([0.35,0.05,0.0]),0,1)
    if readout=="chrono":
        ks=sorted(snaps); e,m,l=(snaps[ks[0]],snaps[ks[1]],snaps[ks[2]])
        img=(e[...,None]*np.array([0.95,0.15,0.55])+m[...,None]*np.array([0.98,0.65,0.15])+l[...,None]*np.array([0.20,0.85,0.95]))*0.62
        return np.clip(img,0,1)

def panel_aniso(rs):
    U,V=seedUV(rs)
    for _ in range(STEPS):
        uvv=U*V*V
        U+=(0.20*d2x(U)+0.11*d2y(U)-uvv+0.037*(1-U))*dt
        V+=(0.05*d2x(V)+0.11*d2y(V)+uvv-(0.037+0.062)*V)*dt
    return ramp(V)

# field builders
yy,xx=np.mgrid[0:PH,0:PW]
Fx=np.broadcast_to(np.linspace(0.022,0.050,PW)[None,:],(PH,PW)).copy()
ky=np.broadcast_to(np.linspace(0.058,0.065,PH)[:,None],(PH,PW)).copy()
r=np.sqrt(((xx-PW/2)/(PW/2))**2+((yy-PH/2)/(PH/2))**2)
Frad=np.clip(0.020+0.030*r,0.020,0.052); k062=np.full((PH,PW),0.062)

print("rendering 6 panels…")
panels=[
    panel_iso(0.037,0.062,7),                 # worms
    panel_field(Fx,ky,3,"fill"),              # atlas
    panel_field(Frad,k062,11,"fill"),         # iris
    panel_aniso(5),                           # aniso
    panel_field(Fx,ky,3,"edge"),              # fronts
    panel_field(Fx,ky,3,"chrono"),            # chrono
]

# tile 2 rows x 3 cols with gutters on near-black ground
G=6; ground=np.array([0.02,0.02,0.03])
canvas=np.ones((2*PH+3*G, 3*PW+4*G, 3))*ground
for i,p in enumerate(panels):
    rr,cc=divmod(i,3)
    y0=G+rr*(PH+G); x0=G+cc*(PW+G)
    canvas[y0:y0+PH, x0:x0+PW]=p
S=2
canvas=np.repeat(np.repeat(canvas,S,0),S,1)
write_png(os.path.join(OUT,"hexaptych.png"),(canvas*255).astype(np.uint8))
write_png("/private/tmp/claude-501/-Users-beckyconning-conceptmodel/fafc4c16-3002-4c19-994d-3bed032b12f5/scratchpad/rd_hex_prev.png",
          (canvas[::3,::3]*255).astype(np.uint8))
print(f"wrote hexaptych.png ({canvas.shape[1]}x{canvas.shape[0]})")
