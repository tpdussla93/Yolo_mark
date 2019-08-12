import cv2
import sys
import glob
import os
import numpy as np
from shutil import copyfile

argc = len(sys.argv)
if argc < 3:
    print("Usage: dataAugment.py <img path> <augment ratio>")
    exit()
imgPath = sys.argv[1]
augmentRatio = int(sys.argv[2])

if augmentRatio < 1:
    print("augment ratio have to be an integer number bigger than 1")
    exit()
if imgPath[-1] == '/':
    imgPath = imgPath[:-1]

imgList = glob.glob(imgPath + "/*.jpg")

for imgName in imgList:
    imgNameWithoutExt = imgName[:imgName.rfind('.')]
    labelTxtName = imgNameWithoutExt + ".txt"
    labelQuadTxtName = imgNameWithoutExt + "_quadrangle.txt"

    img = cv2.imread(imgName, cv2.IMREAD_COLOR)
    noise = np.zeros(img.shape, dtype='int16')
    for i in range(augmentRatio - 1):
        cv2.randn(noise, (0,0,0), (20,20,20))
        tmp = img.astype('int16')
        cv2.addWeighted(tmp, 1, noise, 1, 0, tmp)
        tmp = np.clip(tmp, 0, 255)
        tmp = np.uint8(tmp)
        fileNameWithoutExt = imgNameWithoutExt + "_" + str(i)
        cv2.imwrite(fileNameWithoutExt + ".jpg", tmp)
        copyfile(labelTxtName, fileNameWithoutExt + ".txt")
        copyfile(labelQuadTxtName,fileNameWithoutExt + "_quadrangle.txt")