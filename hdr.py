import numpy as np
import operator
import sys
#Clamps a number.
def clamp(x, xmin, xmax):
    return max(min(x, xmin), xmax)
#Saves an array as an HDR file.
def saveArray(filename, data):
    # https://gist.github.com/edouardp/3089602
    f = open(filename, "wb")
    f.write("#?RADIANCE\n# Made with Python & Numpy\nFORMAT=32-bit_rle_rgbe\n\n")
    f.write("-Y {0} +X {1}\n".format(data.shape[0], data.shape[1]))
    brightest = np.maximum(np.maximum(data[...,0], data[...,1]), data[...,2])
    exp = np.zeros_like(brightest)
    man = np.zeros_like(brightest)
    np.frexp(brightest, man, exp)
    scman = np.nan_to_num(man * 256.0 / brightest)
    rgbe = np.zeros((data.shape[0], data.shape[1], 4), dtype=np.uint8)
    rgbe[...,0:3] = np.minimum(np.maximum(np.around(data[...,0:3] * scman[...,None]), 0), 255)
    rgbe[...,3] =np.minimum(np.maximum(np.around(exp + 128), 0), 255)
    rgbe.flatten().tofile(f)
    f.close()
#Gets float info.
def planePosition(x):
    fx = int(x) if (x >= 0) else (int(x) - 1)
    cx = fx if (float(fx) - x == 0.0) else (fx + 1)
    lx = x - fx
    return fx, cx, lx
#Gets a planes pixel.
def planePixelColor(plane, u, v):
    return plane[int(u),int(v)] if (u >= 0 and v >= 0 and u < plane.shape[0] and v < plane.shape[1]) else [0.0, 100.0, 0.0, 1.0]
#Gets a planes mapped pixel.
def planePixelMapped(plane, u, v):
    if(u < 0):
        if(v < 0):
            return planePixelColor(plane, 0, 0)
        if(v >= plane.shape[1]):
            return planePixelColor(plane, 0, plane.shape[1] - 1)
        return planePixelColor(plane, 0, v)
    if(u >= plane.shape[0]):
        if(v < 0):
            return planePixelColor(plane, plane.shape[0] - 1, 0)
        if(v >= plane.shape[1]):
            return planePixelColor(plane, plane.shape[0] - 1, plane.shape[1] - 1)
        return planePixelColor(plane, plane.shape[0] - 1, v)
    if(v < 0):
        return planePixelColor(plane, u, 0)
    if(v >= plane.shape[1]):
        return planePixelColor(plane, u, plane.shape[1] - 1)
    return planePixelColor(plane, u, v)
#Gets the average color from a 4 color array.
def colorAverageLerp(colors, u, v):
    c1 = map(operator.add, colors[0][0], map(lambda x: u * x, map(operator.sub, colors[1][0], colors[0][0])))
    c2 = map(operator.add, colors[0][1], map(lambda x: u * x, map(operator.sub, colors[1][1], colors[0][1])))
    return map(operator.add, c1, map(lambda x: v * x, map(operator.sub, c2, c1)))
#Gets the closest pixel color from a plane of pixels.
def planePixelClosest(plane, u, v):
    fu, cu, lu = planePosition(u)
    fv, cv, lv = planePosition(v)
    clr1 = planePixelMapped(plane, fu, fv)
    clr2 = planePixelMapped(plane, fu, cv)
    clr3 = planePixelMapped(plane, cu, fv)
    clr4 = planePixelMapped(plane, cu, cv)
    clrs = [[clr1, clr2], [clr3, clr4]]
    return colorAverageLerp(clrs, lu, lv)
#Turns 0..1 UVs in -1..1 UVs.
def plane2space(u,v):
    return (u - 0.5) * 2.0, (v - 0.5) * 2.0
#Creates a pixel to UV mapping for each side of the cubemap.
def createspheremap(img):
    size = img.shape
    spheremap = np.ndarray(shape=(size[0], size[1], size[2], 2), dtype=np.float)
    for j in range(0, size[2]):
        nj = ((float(j) / size[2]) - 0.5) * 2.0
        for i in range(0, size[1]):
            ni = ((float(i) / size[1]) - 0.5) * 2.0
            for s in range(0, size[0]):
                if(s == 0):
                    x = ni
                    y = nj
                    z = -1
                    lv = np.sqrt(np.power(x,2.0)+np.power(z,2.0))
                    nv = (np.arctan2(y, lv)) / np.pi
                    nu = (np.arctan2(x, z)) / np.pi
                    spheremap[0][j][i][1] = nv
                    spheremap[0][j][i][0] = nu
    return spheremap
#Wraps a number.
def wrap(x, xmin, xmax):
    vx = x
    while(vx >= xmax):
        vx -= (xmax - xmin)
    while(vx < xmin):
        vx += (xmax - xmin)
    return vx
#Get an angle difference.
def getAngleRadDiff(x, y):
    v1 = x
    v2 = y
#    v1 = wrap(x, -np.pi, np.pi)
#    v2 = wrap(y, -np.pi, np.pi)
    vdiff = wrap(v1 - v2, -np.pi, np.pi)
    return vdiff
#Determine if an angle is facing the right way.
def getFacing(diff):
    return ((diff > (-np.pi / 2.0)) and (diff < (np.pi / 2.0)))
def getFacingAngs(ang1, ang2):
    diff = getAngleRadDiff(ang1, ang2)
    return getFacing(diff)
#Verifies a plane coord.
def isPlanic(x):
    return (x[0] >= -1.0 and x[0] <= 1.0 and x[1] >= -1.0 and x[1] <= 1.0)
#Spheretracer
def sphereTrace(img, size):
    sphere = np.ndarray(shape=(size[0], size[1], 4), dtype=np.float)
    for v in range(0, size[1]):
        #print("Rays for row %d..." % v)
        radv = (((float(v) / float(size[1])) - 0.5) * 2.0) * (np.pi / 2.0)
        for u in range(0, size[0]):
            radu = ((float(u) / float(size[0])) * 2.0 * np.pi) - np.pi
            sideuvs = np.ndarray(shape=(img.shape[0], 2), dtype=np.float)
            for s in range(0, img.shape[0]):
                sideuvs[s][1] = -2.0
                sideuvs[s][0] = -2.0
                if(s == 0):
                    diffv = getAngleRadDiff(radv, (0.0 * (np.pi / 2.0)))
                    diffu = getAngleRadDiff(radu, (3.0 * (np.pi / 2.0)))
                    if(getFacing(diffv) and getFacing(diffu)):
                        sideuvs[s][0] = np.tan(diffu)
                        sideuvs[s][1] = np.tan(diffv) * np.sqrt(np.power(sideuvs[s][0],2.0) + 1.0)
                if(s == 1):
                    diffv = getAngleRadDiff(radv, (0.0 * (np.pi / 2.0)))
                    diffu = getAngleRadDiff(radu, (1.0 * (np.pi / 2.0)))
                    if(getFacing(diffv) and getFacing(diffu)):
                        sideuvs[s][0] = np.tan(diffu)
                        sideuvs[s][1] = np.tan(diffv) * np.sqrt(np.power(sideuvs[s][0],2.0) + 1.0)
                if(s == 2):
                    diffv = getAngleRadDiff(radv, (0.0 * (np.pi / 2.0)))
                    diffu = getAngleRadDiff(radu, (0.0 * (np.pi / 2.0)))
                    if(getFacing(diffv) and getFacing(diffu)):
                        sideuvs[s][0] = np.tan(diffu)
                        sideuvs[s][1] = np.tan(diffv) * np.sqrt(np.power(sideuvs[s][0],2.0) + 1.0)
                if(s == 3):
                    diffv = getAngleRadDiff(radv, (0.0 * (np.pi / 2.0)))
                    diffu = getAngleRadDiff(radu, (2.0 * (np.pi / 2.0)))
                    if(getFacing(diffv) and getFacing(diffu)):
                        sideuvs[s][0] = np.tan(diffu)
                        sideuvs[s][1] = np.tan(diffv) * np.sqrt(np.power(sideuvs[s][0],2.0) + 1.0)
                if(s == 4):
                    diffv = getAngleRadDiff(radv, (1.0 * (np.pi / 2.0)))
                    diffu = getAngleRadDiff(radu, (0.0 * (np.pi / 2.0)))
                    if(getFacing(diffv)):
                        sideuvs[s][0] = np.cos(diffu) * np.tan(np.abs(diffv))
                        sideuvs[s][1] = np.sin(diffu) * np.tan(np.abs(diffv))
                if(s == 5):
                    diffv = getAngleRadDiff(radv, (-1.0 * (np.pi / 2.0)))
                    diffu = getAngleRadDiff(radu, (0.0 * (np.pi / 2.0)))
                    if(getFacing(diffv)):
                        sideuvs[s][0] = np.cos(diffu) * np.tan(np.abs(diffv))
                        sideuvs[s][1] = np.sin(diffu) * np.tan(np.abs(diffv))
            sind = -1
            for s in range(0, img.shape[0]):
                if(isPlanic(sideuvs[s])):
                    sind = s
                    break
            if(sind == -1):
                print("Error! Raytrace could not get valid UV pair!")
                sys.exit(1)
            if(sind != -1):
                planesv = ((sideuvs[sind][1] / 2.0) + 0.5) * float(img.shape[2])
                planesu = ((sideuvs[sind][0] / 2.0) + 0.5) * float(img.shape[1])
                clr = planePixelClosest(img[sind], planesu, planesv)
                sphere[v][u] = clr if len(clr) == 4 else [clr[0], clr[1], clr[2], 0.0]
            else:
                sphere[v][u] = np.asarray([0.0, 0.0, 0.0, 0.0], dtype=np.float)
    return sphere