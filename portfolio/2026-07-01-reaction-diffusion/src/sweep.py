"""Quick (F,k) reconnaissance: simulate a small grid for each pair, report V-coverage.
Coverage in a healthy 0.15-0.55 band = living, connected structure (not dead, not saturated)."""
import numpy as np
GW, GH, STEPS = 130, 130, 5000
Du, Dv, dt = 0.16, 0.08, 1.0
rng = np.random.default_rng(7)

def lap(Z):
    return (-Z + 0.20*(np.roll(Z,1,0)+np.roll(Z,-1,0)+np.roll(Z,1,1)+np.roll(Z,-1,1))
            + 0.05*(np.roll(np.roll(Z,1,0),1,1)+np.roll(np.roll(Z,1,0),-1,1)
                    + np.roll(np.roll(Z,-1,0),1,1)+np.roll(np.roll(Z,-1,0),-1,1)))

for F in (0.014, 0.022, 0.030, 0.037, 0.046, 0.054, 0.062):
    row = []
    for k in (0.050, 0.055, 0.060, 0.062, 0.065):
        U = np.ones((GH, GW)); V = np.zeros((GH, GW))
        s = rng.random((GH, GW)) > 0.65; V[s] = 0.25; U[s] = 0.5
        for _ in range(STEPS):
            uvv = U*V*V
            U += (Du*lap(U) - uvv + F*(1-U))*dt
            V += (Dv*lap(V) + uvv - (F+k)*V)*dt
        cov = float((V > 0.2).mean())
        tag = "··" if cov < 0.03 else ("██" if cov > 0.6 else f"{cov:.2f}")
        row.append(f"k={k}:{tag}")
    print(f"F={F:.3f}  " + "  ".join(row))
