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

#cap = cv2.VideoCapture('http://192.168.123.175:8080/?action=stream&.mjpg')
cap = cv2.VideoCapture('test.mp4')

roadMask = cv2.imread('/Users/rob/CarTracking/roadMask_1.jpg')
roadMask = cv2.cvtColor(roadMask,cv2.COLOR_BGR2GRAY)
roadMask = cv2.rotate(roadMask,cv2.ROTATE_180)

tracker = cv2.Tracker_create("MEDIANFLOW")
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
        bbox = (x,y,w,h)
        #only look at big boxes
        if h > 5 and w > 5:

            #start tracking if whole box in window
            if x > 5 and x+w < width -5:

                ok = tracker.init(i, bbox)
                cv2.rectangle(i, (x, y), (x + w, y + h), (0, 255, 0), 1)
                print('in frame')
                while True:
                    # Read a new frame
                    ret, frame = cap.read()
                    frame =  cv2.rotate(frame,cv2.ROTATE_180)
                    # Update tracker
                    print("checking")
                    ok, bbox = tracker.update(frame)
                    print("checked")

                    # Draw bounding box
                    if ok:
                        p1 = (int(bbox[0]), int(bbox[1]))
                        p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                        cv2.rectangle(frame, p1, p2, (0, 0, 255))
                        cv2.imshow("Tracking", frame)
                        print("ok")
                    if not ok:
                        print("not ok")
                        break
                    # Display result



        else:
            if tracking:
                #finish tracking
                tracking = False


    cv2.imshow('colour', i)
    cv2.imshow('thresh',thresh)

    if cv2.waitKey(1) == 27:
        exit(0)


