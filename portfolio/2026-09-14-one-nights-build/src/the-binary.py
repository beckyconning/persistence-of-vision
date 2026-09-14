# the-binary: the shipped Mandeldive.exe (1166848 bytes) as a 1024-wide page, one byte = one pixel, byte value = ink.
import numpy as np
from PIL import Image
b = np.fromfile('Mandeldive.exe', dtype=np.uint8)
W = 1024
H = (len(b) + W - 1) // W
pad = np.zeros(W * H, np.uint8); pad[:len(b)] = b
g = pad.reshape(H, W).astype(np.float64) / 255.0
paper, ink = np.array([242, 237, 227]), np.array([34, 36, 52])
Image.fromarray((paper * (1 - g[:, :, None]) + ink * g[:, :, None]).astype(np.uint8)).save('the-binary.png')
