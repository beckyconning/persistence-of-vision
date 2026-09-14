# the-descent: 32 zoom steps (x1.18 each, 1e40 to 1.7e42) into the Misiurewicz point M(23,2), each step's escape
# counts rendered as a voxel landscape with tools/voxelspace.py. No caption: the land keeps unfolding toward the
# viewer because the set is self-similar there; the descent never arrives anywhere.
import sys
import numpy as np
from PIL import Image
sys.path.insert(0, '/home/april/persistence-of-vision/tools')
from voxelspace import render

D = '/tmp/claude-1000/-home-april/7aec8f25-c3b5-4b49-8020-6b43fff59a7d/scratchpad/agreement/'
F, N = 32, 200
fields = np.fromfile(D + 'descent.bin', dtype=np.float32).reshape(F, N, N).astype(np.float64)
fields[fields < 0] = fields.max()
logs = np.log2(fields)
lo, hi = np.percentile(logs, 1), np.percentile(logs, 99.5)
frames = []
for k in range(F):
    lo, hi = np.percentile(logs[k], 1), np.percentile(logs[k], 99.5)   # per-step: the self-similar land re-forms
    h = np.clip((logs[k] - lo) / (hi - lo), 0, 1.2)
    h = (1.0 - h) * 60.0                      # the slowest escapes (the filaments) rise
    img = render(h, water=46.0, size=(960, 540), camera=(100.0, -35.0, 230.0), horizon=0.10, focal=110.0,
                 depth=(2.0, 420.0), steps=(120, 300), fog_distance=460.0, seed=k)
    frames.append(Image.fromarray(img).quantize(colors=64, method=Image.Quantize.MEDIANCUT))
durations = [140] * F
durations[-1] = 1400
frames[0].save(D + 'the-descent.gif', save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=True)
lo, hi = np.percentile(logs[16], 1), np.percentile(logs[16], 99.5)
Image.fromarray(render((1.0 - np.clip((logs[16] - lo) / (hi - lo), 0, 1.2)) * 60.0, water=46.0, size=(960, 540),
                       camera=(100.0, -35.0, 230.0), horizon=0.10, focal=110.0, depth=(2.0, 420.0), steps=(120, 300),
                       fog_distance=460.0)).save(D + 'the-descent-16.png')
print('frames', F)
