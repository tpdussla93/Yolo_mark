import cv2
import sys
import glob
import os
import numpy as np
from shutil import copyfile
import math
import random

class LabelRect:
    def __init__(self, clsId, absX, absY, absW, absH):
        self.clsId = int(clsId)
        self.absX = int(absX)
        self.absY = int(absY)
        self.absW = int(absW)
        self.absH = int(absH)

    def setXYWH(self, absX, absY, absW, absH):
        self.absX = int(absX)
        self.absY = int(absY)
        self.absW = int(absW)
        self.absH = int(absH)

class LabelQuad:
    def __init__(self, clsId, absX1, absY1, absX2, absY2, absX3, absY3, absX4, absY4):
        self.clsId = int(clsId)
        self.absX1 = int(absX1)
        self.absX2 = int(absX2)
        self.absX3 = int(absX3)
        self.absX4 = int(absX4)
        self.absY1 = int(absY1)
        self.absY2 = int(absY2)
        self.absY3 = int(absY3)
        self.absY4 = int(absY4)

    def setPoints(self, absX1, absY1, absX2, absY2, absX3, absY3, absX4, absY4):
        self.absX1 = int(absX1)
        self.absX2 = int(absX2)
        self.absX3 = int(absX3)
        self.absX4 = int(absX4)
        self.absY1 = int(absY1)
        self.absY2 = int(absY2)
        self.absY3 = int(absY3)
        self.absY4 = int(absY4)
        
class LabeledImage:
    def __init__(self, imgFileName):
        self.imgFileName = imgFileName
        self.imgName = imgFileName[:imgFileName.rfind('.')]
        self.labelRectFileName = self.imgName + ".txt"
        self.labelQuadFileName = self.imgName + "_quadrangle.txt"
        self.img = cv2.imread(imgFileName, cv2.IMREAD_COLOR)
        if self.img is None:
            raise Exception("imread Error!")

        with open(self.labelRectFileName, "r") as lRect:
            lines = lRect.readlines()
            self.labelRects = []
            for line in lines:
                splited = line.split()
                clsId = splited[0]
                splited[1] = float(splited[1])
                splited[2] = float(splited[2])
                splited[3] = float(splited[3])
                splited[4] = float(splited[4])
                absX = int((splited[1] - splited[3]/2)*self.img.shape[1])
                absY = int((splited[2] - splited[4]/2)*self.img.shape[0])
                absW = int(splited[3]*self.img.shape[1])
                absH = int(splited[4]*self.img.shape[0])
                label = LabelRect(clsId, absX, absY, absW, absH)
                self.labelRects.append(label)
        with open(self.labelQuadFileName, "r") as lQuad:
            lines = lQuad.readlines()
            self.labelQuads = []
            for line in lines:
                splited = line.split()
                (height, width, _) = self.img.shape
                clsId = splited[0]
                absX1 = float(splited[1])*width
                absY1 = float(splited[2])*height
                absX2 = float(splited[3])*width
                absY2 = float(splited[4])*height
                absX3 = float(splited[5])*width
                absY3 = float(splited[6])*height
                absX4 = float(splited[7])*width
                absY4 = float(splited[8])*height
                label = LabelQuad(clsId, absX1, absY1, absX2, absY2, absX3, absY3, absX4, absY4)
                self.labelQuads.append(label)

    def addRandNoise(self, mean = 0, stddev = 20):
        noise = np.zeros(self.img.shape, dtype='int16')
        cv2.randn(noise, (mean, mean, mean), (stddev, stddev, stddev))
        tmp = self.img.astype('int16')
        cv2.addWeighted(tmp, 1, noise, 1, 0, tmp)
        tmp = np.clip(tmp, 0, 255)
        self.img = np.uint8(tmp)

    def rotateRnd(self, limit):
        angle = random.random()*limit*2 - limit
        self.rotate(angle)
        
    def rotate(self, angle):
        (h, w) = self.img.shape[:2]
        (cX, cY) = (w/2, h/2)
        M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
        self.img = cv2.warpAffine(self.img, M, (w,h))

        rad = -math.pi*angle/180
        delIdx = []
        for i in range(len(self.labelQuads)):
            lQuad = self.labelQuads[i]
            lRect = self.labelRects[i]
            x1 = (lQuad.absX1 - cX)*math.cos(rad) - (lQuad.absY1 - cY)*math.sin(rad) + cX
            y1 = (lQuad.absX1 - cX)*math.sin(rad) + (lQuad.absY1 - cY)*math.cos(rad) + cY
            x2 = (lQuad.absX2 - cX)*math.cos(rad) - (lQuad.absY2 - cY)*math.sin(rad) + cX
            y2 = (lQuad.absX2 - cX)*math.sin(rad) + (lQuad.absY2 - cY)*math.cos(rad) + cY
            x3 = (lQuad.absX3 - cX)*math.cos(rad) - (lQuad.absY3 - cY)*math.sin(rad) + cX
            y3 = (lQuad.absX3 - cX)*math.sin(rad) + (lQuad.absY3 - cY)*math.cos(rad) + cY
            x4 = (lQuad.absX4 - cX)*math.cos(rad) - (lQuad.absY4 - cY)*math.sin(rad) + cX
            y4 = (lQuad.absX4 - cX)*math.sin(rad) + (lQuad.absY4 - cY)*math.cos(rad) + cY
            leftTopX = min([x1,x2,x3,x4])
            leftTopY = min([y1,y2,y3,y4])
            rightBottomX = max([x1,x2,x3,x4])
            rightBottomY = max([y1,y2,y3,y4])

            # check if points went out the image
            if leftTopX < 0 or leftTopY < 0:
                delIdx.append(i)
                continue
            if rightBottomX > w or rightBottomY > h:
                delIdx.append(i)
                continue

            lQuad.setPoints(x1,y1,x2,y2,x3,y3,x4,y4)            
            lRect.setXYWH(leftTopX, leftTopY, rightBottomX - leftTopX, rightBottomY - leftTopY) 

        # remove points which are out of the image
        delIdx.reverse()
        for i in delIdx:
            del self.labelQuads[i]
            del self.labelRects[i]

    def toFile(self, idx):
        imgFileName = self.imgName + "_" + str(idx) + ".jpg"
        labelRectFileName = self.imgName + "_" + str(idx) + ".txt"
        labelQuadFileName = self.imgName + "_" + str(idx) + "_quadrangle.txt"

        cv2.imwrite(imgFileName, self.img)
        with open(labelRectFileName, "w") as f:
            for lRect in self.labelRects:
                relW = lRect.absW / self.img.shape[1]
                relH = lRect.absH / self.img.shape[0]
                relX = (lRect.absX + lRect.absW/2) / self.img.shape[1]
                relY = (lRect.absY + lRect.absH/2) / self.img.shape[0]
                f.write("%d %f %f %f %f\n" % (lRect.clsId, relX, relY, relW, relH))
        with open(labelQuadFileName, "w") as f:
            for lQuad in self.labelQuads:
                f.write("%d %f %f %f %f %f %f %f %f\n" % (lQuad.clsId, lQuad.absX1 / self.img.shape[1], lQuad.absY1 / self.img.shape[0],
                                                                    lQuad.absX2 / self.img.shape[1], lQuad.absY2 / self.img.shape[0],
                                                                    lQuad.absX3 / self.img.shape[1], lQuad.absY3 / self.img.shape[0],
                                                                    lQuad.absX4 / self.img.shape[1], lQuad.absY4 / self.img.shape[0]))

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
    for i in range(augmentRatio - 1):
        labeledImage = LabeledImage(imgName)
        labeledImage.addRandNoise(0, 20)
        labeledImage.rotateRnd(10)
        labeledImage.toFile(i)
    print(imgName + " has been augmented!")