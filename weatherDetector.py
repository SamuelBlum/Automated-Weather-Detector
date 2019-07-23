from __future__ import print_function
from PIL import Image
import numpy as np
import argparse
import cv2
import matplotlib.pyplot as plt

def adjust_gamma(image, gamma=1.0):

    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
	  for i in np.arange(0, 256)]).astype("uint8")
    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)

def adjust_color(image):

    x = []
    # get histogram for each channel
    for i in cv2.split(image):
            hist, bins = np.histogram(i, 256, (0, 256))
            # discard colors at each end of the histogram which are used by only 0.05% 
            tmp = np.where(hist > hist.sum() * 0.00001)[0]
            i_min = tmp.min()
            i_max = tmp.max()
            # stretch hist
            tmp = (i.astype(np.int32) - i_min) / (i_max - i_min) * 255
            tmp = np.clip(tmp, 0, 255)
            x.append(tmp.astype(np.uint8))
    return np.dstack(x)

def main(args):

    nightlevel = 0
    hazelevel = 0

    image = args.input

    im = Image.open(image)
    im_original_original = cv2.imread(image)
        
    im_grey = im.convert('LA') # convert to grayscale
    width, height = im.size

    total = 0
    for i in range(0, width):
       for j in range(0, height):
            total += im_grey.getpixel((i,j))[0]

    mean = total / (width * height)

    # Detect Night
    if mean < 100:
         nightlevel = 100 / mean

    # Detect Haze
    if mean > 100:
         hazelevel = 25.5 - 255 / mean

    # Detect underwater level
    if nightlevel > 0:
         im_enhanced = adjust_gamma(im_original_original,gamma=(2))
    if hazelevel > 0:
         im_enhanced = adjust_gamma(im_original_original,gamma=(1/hazelevel))

    print("night level is " + str(nightlevel))
    print("haze level is " + str(hazelevel))
    print(mean)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--input', type=str)

    args = parser.parse_args()
    main(args)
