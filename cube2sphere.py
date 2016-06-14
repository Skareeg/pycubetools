from skimage.io import imread, imsave
import numpy as np
import hdr
import sys
if(len(sys.argv) != 10):
    print("Usage:")
    print("   python cube2sphere <back.png> <front.png> <left.png> <right.png> <bottom.png> <top.png> <sizeOut> <sphereOut.png> <hdrOut.hdr>")
    sys.exit(1)
print("Reading images...")
img = []
img.append(imread(sys.argv[1]))
img.append(imread(sys.argv[2]))
img.append(imread(sys.argv[3]))
img.append(imread(sys.argv[4]))
img.append(imread(sys.argv[5]))
img.append(imread(sys.argv[6]))
print("Converting to arrays...")
imgcube = np.ndarray(shape=(6,img[0].shape[0],img[0].shape[1],4),dtype=np.uint8)
imgcube[0] = img[0]
imgcube[1] = img[1]
imgcube[2] = img[2]
imgcube[3] = img[3]
imgcube[4] = img[4]
imgcube[5] = img[5]
print("Converting to float form...")
imgfloat = imgcube.astype(np.float) / 256.0
print("Sphere tracing...")
sz = int(sys.argv[7])
imgout = hdr.sphereTrace(imgfloat, [sz, sz])
print("Converting to uint8 form...")
out = np.minimum(np.maximum(imgout * 256.0, 0.0), 255.0).astype(np.uint8)
print("Saving png...")
imsave(sys.argv[8], out)
print("Saving hdr...")
hdr.saveArray(sys.argv[9], imgout)
print("Done!")