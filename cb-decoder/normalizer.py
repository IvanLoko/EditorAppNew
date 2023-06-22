import cv2
import numpy as np
import matplotlib.pyplot as plt

import os
import glob
import pathlib
import warnings

def crop_images(bin_img, epsArea=0.5):
    contours, _ = cv2.findContours(bin_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rects = list(map(cv2.boundingRect, contours))

    rects.sort(key=lambda x: x[2] * x[3], reverse=True)
    
    rects = rects[:2]
    
    if len(rects) < 2:
        return rects
    
    if abs(rects[0][2] * rects[0][3] - rects[1][2] * rects[1][3]) < (rects[0][2] * rects[0][3]) * epsArea:
        return rects
    
    return rects[:1]

def splitter(filename, save=False, margin=5):
    file = pathlib.Path(filename).stem

    image = cv2.imread(filename)
    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, tresh = cv2.threshold(img, 0,255,cv2.THRESH_OTSU)
    tresh = cv2.bitwise_not(tresh)

    kernel = np.ones((45, 45))
    dilate_tresh = cv2.dilate(tresh, kernel, 5)

    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (size, size))
    # closed_cropped_tresh = cv2.morphologyEx(cropped_tresh_lines, cv2.MORPH_CLOSE, kernel)

    boxes = crop_images(dilate_tresh)

    cropped_imgs = []
    for i, box in enumerate(boxes):
        x, y, w, h = box
        cropped_img = image[y-margin:y+h+margin, x-margin:x+w+margin].copy()
        cropped_imgs.append(cropped_img)

        if save:
            cv2.imwrite(f'./cb/{file}-{i}.jpg', cropped_img)
    
    return cropped_imgs

if __name__ == "__main__":
    path = './cb/forbidden/*'
    for file in glob.glob(path):
        if os.path.isfile(file):
            print(file)
            splitter(file, save=True)