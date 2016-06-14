import numpy as np
print("Creating reference image...")
sz = 128
img = np.ndarray(shape=(sz,sz,3),dtype=np.float)
for y in range(0, sz):
    for x in range(0, sz):
        img[x][y] = [0.0, 1.0, 0.0]
sz2 = sz / 2
for y in range(0, sz2):
    for x in range(0, sz2):
        c = (float(x) * float(y)) / (float(sz2) * float(sz))
        #c = float((float(x)/float(sz2)) * (float(y)/float(sz2)))
        c = c if c != 0.0 else -10000.0
        img[x][y] = [c, 0.0, 0.0]
        img[x + (sz2)][y] = [c * 2.0, 0.0, 0.0]
        img[x][y + (sz2)] = [c * 4.0, 0.0, 0.0]
        img[x + (sz2)][y + (sz2)] = [c * 8.0, 0.0, 0.0]
import hdr
print("Creating large copy image...")
sz = 256
img2 = np.ndarray(shape=(sz,sz,3),dtype=np.float)
for y in range(0, sz):
    for x in range(0, sz):
        v = float(y) / float(sz)
        u = float(x) / float(sz)
        img2[y][x] = hdr.planePixelClosest(img, v * float(img.shape[1]), u * float(img.shape[0]))
print("Saving large copy image...")
hdr.saveArray("test1.hdr", img2)
print("Done!")