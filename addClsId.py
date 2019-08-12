import glob
import os
import sys

argc = len(sys.argv)
if argc < 3:
    print("Usage: python addClsId.py <img path> <num to add>")
    exit()

imgPath = sys.argv[1]
numAdd = int(sys.argv[2])

if imgPath[-1] == '/':
    imgPath = imgPath[:-1]

txtList = glob.glob(imgPath + "/*.txt")

for filename in txtList:
    origin = open(filename, 'r')
    tmp = open(filename + "_tmp", 'w')
    lines = origin.readlines()
    for line in lines:
        splited = line.split()
        clsId = numAdd + int(splited[0])
        splited[0] = str(clsId)
        merged = " ".join(splited)
        tmp.write(merged + '\n')
    origin.close()
    tmp.close()
    
for filename in txtList:
    os.remove(filename)
    os.rename(filename + "_tmp", filename)