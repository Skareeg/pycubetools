import numpy as np
print("Creating reference image...")
sz = 128
img = np.ndarray(shape=(6,sz,sz,3),dtype=np.float)
for y in range(0, sz / 2):
    for x in range(0, sz / 2):
        c = (float(x)/float(sz / 2)) * (float(y)/float(sz / 2))
        img[0][x][y] = [c / 16.0, 0.0, 0.0]
        img[0][x + (sz / 2)][y] = [c / 8.0, 0.0, 0.0]
        img[0][x][y + (sz / 2)] = [c / 4.0, 0.0, 0.0]
        img[0][x + (sz / 2)][y + (sz / 2)] = [c / 2.0, 0.0, 0.0]
        img[1][x][y] = [c, 0.0, 0.0]
        img[1][x + (sz / 2)][y] = [c * 2.0, 0.0, 0.0]
        img[1][x][y + (sz / 2)] = [c * 4.0, 0.0, 0.0]
        img[1][x + (sz / 2)][y + (sz / 2)] = [c * 8.0, 0.0, 0.0]
        img[2][x][y] = [0.0, c / 16.0, 0.0]
        img[2][x + (sz / 2)][y] = [0.0, c / 8.0, 0.0]
        img[2][x][y + (sz / 2)] = [0.0, c / 4.0, 0.0]
        img[2][x + (sz / 2)][y + (sz / 2)] = [0.0, c / 2.0, 0.0]
        img[3][x][y] = [0.0, c, 0.0]
        img[3][x + (sz / 2)][y] = [0.0, c * 2.0, 0.0]
        img[3][x][y + (sz / 2)] = [0.0, c * 4.0, 0.0]
        img[3][x + (sz / 2)][y + (sz / 2)] = [0.0, c * 8.0, 0.0]
        img[4][x][y] = [0.0, 0.0, c / 16.0]
        img[4][x + (sz / 2)][y] = [0.0, 0.0, c / 8.0]
        img[4][x][y + (sz / 2)] = [0.0, 0.0, c / 4.0]
        img[4][x + (sz / 2)][y + (sz / 2)] = [0.0, 0.0, c / 2.0]
        img[5][x][y] = [0.0, 0.0, c]
        img[5][x + (sz / 2)][y] = [0.0, 0.0, c * 2.0]
        img[5][x][y + (sz / 2)] = [0.0, 0.0, c * 4.0]
        img[5][x + (sz / 2)][y + (sz / 2)] = [0.0, 0.0, c * 8.0]
import hdr
print("Creating latlong image from raytrace...")
sphere = hdr.sphereTrace(img, (256, 256))
print("Saving...")
hdr.saveArray("test3.hdr", sphere)
print("Done!")