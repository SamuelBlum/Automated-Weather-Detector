from __future__ import print_function
from PIL import Image
import numpy as np
import argparse
import cv2
import matplotlib.pyplot as plt

def main(args):

    nightlevel = 0
    hazelevel = 0

    image = args.input

    im = Image.open(image)
    im_original = cv2.imread(image)
        
    im_grey = im.convert('LA') # convert to grayscale
    width, height = im.size

    # compute average pixel intensity value
    total = 0
    for i in range(0, width):
       for j in range(0, height):
            total += im_grey.getpixel((i,j))[0]

    mean = total / (width * height)

    # Detect Night
    if mean < 100:
         nightlevel = 100 / mean

    # Automatically adjust gamma
    if nightlevel > 0:
         im_enhanced = automated_gamma_correction(im_original,gamma=(2))

    # Detect Haze
    if mean > 100:
         hazelevel = 25.5 - 255 / mean

    # Automatically adjust gamma
    if hazelevel > 0:
         im_enhanced = automated_gamma_correction(im_original,gamma=(1/hazelevel))

    # Detect underwater level
    totalred = 0
    for i in range(0, width):
       for j in range(0, height):
            totalgreen += im_original.getpixel((i,j))[1]

    # Underwater images have significant levels of green
    meanred = totalred / (width * height)

    # Apply red filter automatically for underwater
    # compute average pixel red channel intensity value
    if mean < 100:
         im_enhanced = automated_color_correction(im_original)

    print("Night level is " + str(nightlevel))
    print("Haze level is " + str(hazelevel))
    print("Underwater level is " + str(meanred))
    print(mean)

def automated_gamma_correction(image, gamma=1.0):

    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
	  for i in np.arange(0, 256)]).astype("uint8")
    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)

def automated_color_correction(image):

    x = []
    # get the histogram for each channel
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

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--input', type=str)

    args = parser.parse_args()
    main(args)
