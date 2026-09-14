"""voxelspace.py: front-to-back voxel-space terrain renderer (after the 1992 demoscene column caster), numpy only.

Turns any 2D field into a landscape with a horizon: height map + optional water level + slope light + distance fog.
Born in portfolio/2026-09-14-one-nights-build (the flood, the dry spire), where the height was log2 of real
Mandelbrot escape counts and the water was an iteration limit.

    import numpy as np
    from voxelspace import render
    img = render(heights, water=None, size=(1200, 700), camera=(x, y, height), horizon=0.33)
    Image.fromarray(img).save('out.png')

Heights are in the same units as camera height; exaggerate small ranges (a flat frame of water with a sliver of
land means the range is too small against the camera). Coordinates outside the map are open "floor" at
floor_height (defaults to the map minimum), so the horizon stays straight. Heights are sampled bilinearly by
default (bilinear=False gives the blocky classic voxel look used by the-flood and the-descent).
"""
import numpy as np

SKY_TOP = np.array([214, 222, 224])
SKY_LOW = np.array([241, 234, 221])
WATER = np.array([112, 132, 143])
LAND_LOW = np.array([124, 130, 104])
LAND_HIGH = np.array([206, 194, 164])


def render(heights, water=None, size=(1200, 700), camera=None, horizon=0.33, focal=180.0, fov=1.25,
           depth=(2.0, 900.0), steps=(160, 420), fog_distance=900.0, slope_light=0.12, seed=0,
           sky=(SKY_TOP, SKY_LOW), water_colour=WATER, land=(LAND_LOW, LAND_HIGH), floor_height=None,
           bilinear=True):
    """Render heights (2D array, rows = y forward, cols = x) to an RGB uint8 array of shape (H, W, 3)."""
    heights = np.asarray(heights, dtype=np.float64)
    ny, nx = heights.shape
    W, H = size
    floor = heights.min() if floor_height is None else floor_height
    if camera is None:
        camera = (nx / 2.0, -0.08 * ny, heights.max() + 0.6 * (heights.max() - heights.min()))
    cam_x, cam_y, cam_h = camera
    hy = int(H * horizon)
    lo, hi = heights.min(), heights.max()
    span = max(hi - lo, 1e-9)

    rows = np.arange(H)[:, None]
    t = np.clip(rows / (hy + 40), 0, 1)
    img = (sky[0] * (1 - t) + sky[1] * t)[:, None, :] * np.ones((1, W, 1))
    ybuf = np.full(W, H)
    cols = np.arange(W)
    near, far = depth
    # geometric depth spacing: fine steps near the camera (where one step spans many screen rows), coarse far away
    zs = np.geomspace(near, far, steps[0] + steps[1])
    rng = np.random.default_rng(seed)

    for z in zs:
        px = cam_x + (cols - W / 2) / W * z * fov
        py = cam_y + z
        inside = (px >= 0) & (px < nx - 2) & (0 <= py < ny - 1)
        if bilinear:
            # smooth sampling removes the stair-steps close to the camera
            fx = np.clip(px, 0, nx - 2.001)
            fy = float(np.clip(py, 0, ny - 1.001))
            ix, iy = fx.astype(int), int(fy)
            ax, ay = fx - ix, fy - iy
            row0 = heights[iy, ix] * (1 - ax) + heights[iy, ix + 1] * ax
            row1 = heights[iy + 1, ix] * (1 - ax) + heights[iy + 1, ix + 1] * ax
            h = np.where(inside, row0 * (1 - ay) + row1 * ay, floor)
            nxt = heights[iy, ix + 1] * (1 - ax) + heights[iy, ix + 2] * ax
            hx = np.where(inside, nxt * (1 - ay) + (heights[iy + 1, ix + 1] * (1 - ax) + heights[iy + 1, ix + 2] * ax) * ay, floor)
        else:
            ix = np.clip(px.astype(int), 0, nx - 2)
            iy = int(np.clip(py, 0, ny - 2))
            h = np.where(inside, heights[iy, ix], floor)
            hx = np.where(inside, heights[iy, ix + 1], floor)
        surf = h if water is None else np.maximum(h, water)
        y = (hy + (cam_h - surf) / z * focal).astype(int)
        tone = np.clip((h - lo) / span, 0, 1)
        shade = np.clip(1.0 + (h - hx) * slope_light, 0.70, 1.25)
        colour = (land[0][None, :] * (1 - tone[:, None]) + land[1][None, :] * tone[:, None]) * shade[:, None]
        if water is not None:
            ripple = 0.975 + 0.012 * np.sin(z * 0.55) + 0.01 * rng.standard_normal(W)
            colour = np.where((h < water)[:, None], water_colour[None, :] * ripple[:, None], colour)
        fog = np.clip(z / fog_distance, 0, 0.9) ** 1.1
        colour = colour * (1 - fog) + sky[1][None, :] * fog
        draw = y < ybuf
        if not draw.any():
            continue
        mask = (rows >= y[None, :]) & (rows < ybuf[None, :]) & draw[None, :]
        img[mask] = np.broadcast_to(colour[None, :, :], (H, W, 3))[mask]
        ybuf = np.where(draw, np.minimum(ybuf, y), ybuf)
    return np.clip(img, 0, 255).astype(np.uint8)


if __name__ == '__main__':
    # smoke test: a sine-hill field with a water level; writes voxelspace-demo.png next to this file
    from PIL import Image
    yy, xx = np.mgrid[0:300, 0:300]
    field = 40 * np.sin(xx / 23.0) * np.cos(yy / 31.0) + 25 * np.sin((xx + yy) / 57.0)
    out = render(field, water=5.0, size=(900, 520), camera=(150, -20, 95), focal=160)
    Image.fromarray(out).save(__file__.replace('voxelspace.py', 'voxelspace-demo.png'))
    print('ok', out.shape)
