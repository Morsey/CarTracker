import cv2
import urllib.request
import numpy as np
import time
import math
from datetime import datetime



def tallestContour(c):
    (x, y, w, h) = cv2.boundingRect(c)
    return h;

def sTime():
    dt = datetime.now()
    return dt.second + dt.microsecond / 1000000


def centre(bbox):
    return int(bbox[0] + bbox[2]/2), int(bbox[1] + bbox[3]/2)

def pixelsMoved(oC,nC):
    return math.sqrt(math.pow(math.fabs(oC[0] - nC[0]),2) +  math.pow(math.fabs(oC[1] - nC[1]),2))

fgbg = cv2.createBackgroundSubtractorMOG2()
kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(2,2))

stream = urllib.request.urlopen('http://192.168.123.175:8080/?action=stream')

cap = cv2.VideoCapture('http://192.168.123.175:8080/?action=stream&.mjpg')
#cap = cv2.VideoCapture('test.mp4')


tracker = cv2.Tracker_create("MEDIANFLOW")
bytes = bytes()



while True:

    ret, i = cap.read()
    image_height,image_width = i.shape[:2]

    i =  cv2.rotate(i,cv2.ROTATE_180)
    gr = cv2.cvtColor(i,cv2.COLOR_BGR2GRAY)

    #get changes
    fgmask = fgbg.apply(gr)
    fgmask = cv2.morphologyEx(fgmask,cv2.MORPH_OPEN,kernel)


    ret, thresh = cv2.threshold(fgmask,127,255,0)

    #get countours
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    #sortedContours = sorted(contours,key=cv2.contourArea,reverse=True)
    sortedContours = sorted(contours,key=tallestContour,reverse=True)

    cv2.imshow('colour', i)

    if sortedContours:
        #We have a box
        (x, y, w, h) = cv2.boundingRect(sortedContours[0])
        bbox = (x,y,w,h)
        #only look at big boxes

        if h > 20 and w > 20:
            #start tracking if whole box in window

            if x > 5 and x+w < image_width -5:

                ok = tracker.init(i, bbox)

                cv2.rectangle(i, (x, y), (x + w, y + h), (0, 255, 0), 1)
                cv2.imshow('colour', i)
                if ok:
                    print("Have object to track")
                    oldbbox = bbox
                    oldtime = sTime()
                    while True:
                        # Read a new frame
                        ret, frame = cap.read()
                        frame =  cv2.rotate(frame,cv2.ROTATE_180)
                        # Update tracker

                        ok, bbox = tracker.update(frame)

                        newtime = sTime()
                        deltaT = newtime - oldtime
                        oldtime = newtime

                        #if close to the end of the frame, drop out
                        if bbox[0] < 5 or bbox[1] < 5 or bbox[0] > (image_width - bbox[2] -5) or (bbox[1] > image_height - bbox[3] -5):
                            ok = False

                        #check big enough object still
                        if x < 20 or y < 20:
                            ok = False

                        oldC = centre(oldbbox)
                        newC = centre(bbox)
                        cv2.line(frame, oldC, newC, (0, 255, 0))
                        oldbbox = bbox

                        # find pixels moved
                        deltaS = pixelsMoved(oldC, newC) * 0.05

                        if deltaS == 0:
                            ok = False

                        # calculate speed (1 pixel ~0.05m)
                        velocity = int((deltaS / (deltaT)) * 2.2)



                        # Draw bounding box
                        if ok and deltaS > 0.2:

                            print(velocity, " ", deltaS, " ", deltaT)



                            p1 = (int(bbox[0]), int(bbox[1]))
                            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                            cv2.rectangle(frame, p1, p2, (0, 0, 255))
                            cv2.putText(frame,"test",(10,image_height-30),cv2.FONT_HERSHEY_PLAIN,1,(255,255),2)
                            cv2.imshow('colour', frame)
                            cv2.waitKey(1)


                        if not ok:
                            #reset tracker
                            tracker = cv2.Tracker_create("MEDIANFLOW")
                            print("Finished Tracking \n\n")
                            break


    #cv2.imshow('thresh',thresh)

    if cv2.waitKey(1) == 27:
        exit(0)


