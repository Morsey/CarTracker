import cv2
import urllib.request
import numpy as np
import time
from datetime import datetime



def tallestContour(c):
    (x, y, w, h) = cv2.boundingRect(c)
    return h;
def msTime():
    dt = datetime.now()
    return dt.microsecond

fgbg = cv2.createBackgroundSubtractorMOG2()
kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(2,2))

stream = urllib.request.urlopen('http://192.168.123.175:8080/?action=stream')

cap = cv2.VideoCapture('http://192.168.123.175:8080/?action=stream&.mjpg')


bytes = bytes()

tracking = False
oldx = 0
oldTime =msTime()
while True:

    ret, i = cap.read()
    newTime = msTime()
    height,width = i.shape[:2]
    i =  cv2.rotate(i,cv2.ROTATE_180)
    gr = cv2.cvtColor(i,cv2.COLOR_BGR2GRAY)

    #remove region of image outside of road area
    #roadRaw = cv2.bitwise_and(i, roadMask)

    fgmask = fgbg.apply(gr)
    fgmask = cv2.morphologyEx(fgmask,cv2.MORPH_OPEN,kernel)
   # fgmask = cv2.morphologyEx(fgmask,cv2.MORPH_CLOSE,kernel)


    ret, thresh= cv2.threshold(fgmask,127,255,0)

    #get countours
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    #sortedContours = sorted(contours,key=cv2.contourArea,reverse=True)
    sortedContours = sorted(contours,key=tallestContour,reverse=True)

    if sortedContours:
        #We have a box
        (x, y, w, h) = cv2.boundingRect(sortedContours[0])
        #only look at big boxes
        if h > 10 and w > 20:
            cv2.rectangle(i, (x, y), (x + w, y + h), (0, 255, 0), 1)

            #start tracking if whole box in window
            if x > 5 and x+w < width -5:
                print('in frame')
                if tracking:
                    #measure difference
                    deltax = x - oldx
                    deltat = newTime - oldTime
                    speed = (deltax * 0.05 / (deltat/1000000) )* 2.2
                    print(deltax, "  " , deltat, "  ", speed)
                    oldx = x
                    oldTime = newTime
                else:
                    oldx = x
                    oldTime = newTime
                    tracking = True


        else:
            if tracking:
                #finish tracking
                tracking = False






    cv2.imshow('colour', i)
    cv2.imshow('thresh',thresh)

    if cv2.waitKey(1) == 27:
        exit(0)


