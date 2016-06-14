import numpy as np
print("Creating reference image...")
sz = 256
img = np.ndarray(shape=(6,sz,sz,3),dtype=np.float)
for y in range(0, sz / 2):
    for x in range(0, sz / 2):
        r = (float(x)/float(sz / 2))
        g = (float(y)/float(sz / 2))
        r = r if r != 0.0 else -10000.0
        g = g if g != 0.0 else -10000.0
        img[0][y][x] = [r, g, 0]
        img[0][y][x + (sz / 2)] = [r * 2.0, g * 2.0, 0]
        img[0][y + (sz / 2)][x] = [r * 4.0, g * 4.0, 0]
        img[0][y + (sz / 2)][x + (sz / 2)] = [r * 8.0, g * 8.0, 0]
import hdr
print("Creating spheremap...")
spheremap = hdr.createspheremap(img)
#print("Creating sphere...")
#sphere = hdr.spheremap2sphere(spheremap)
#print("Saving...")
#hdr.saveArray("test2.hdr", sphere)
print("Done!")