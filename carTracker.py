import cv2
import urllib.request
import numpy as np
import time
import math
from datetime import datetime
import pysftp
import os

FAKE = False
FAKE_SLEEP = 0.1
def tallestContour(c):
    (x, y, w, h) = cv2.boundingRect(c)
    return h;

def secondsTime(dt):
    return dt.second + dt.microsecond / 1000000

def centre(bbox):
    return int(bbox[0] + bbox[2]/2), int(bbox[1] + bbox[3]/2)

def pixelsMoved(oC,nC):
    return math.sqrt(math.pow(math.fabs(oC[0] - nC[0]),2) +  math.pow(math.fabs(oC[1] - nC[1]),2))


f = open("password")
password = f.readline()

password = str(password)
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None
srv = pysftp.Connection(host="home84386385.1and1-data.host",username="u35045545-9",password=password,cnopts=cnopts)
srv.cd("/kunden/homepages/0/d84386385/htdocs/www.robmorse.com/cars")


fgbg = cv2.createBackgroundSubtractorMOG2()
kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(2,2))

stream = urllib.request.urlopen('http://192.168.123.175:8080/?action=stream')
if FAKE:
    cap = cv2.VideoCapture('test.mp4')
else:
    cap = cv2.VideoCapture('http://192.168.123.175:8080/?action=stream&.mjpg')



tracker = cv2.Tracker_create("MEDIANFLOW")
bytes = bytes()

lastTime =0
firstTime =0

while True:

    ok, i = cap.read()
    if not ok:
        break
    if FAKE:
        time.sleep(FAKE_SLEEP)
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

        if h > 10 and w > 10:
            #start tracking if whole box in window

            if x > 5 and x+w < image_width -5:

                ok = tracker.init(i, bbox)

                cv2.rectangle(i, (x, y), (x + w, y + h), (0, 255, 0), 1)
                cv2.imshow('colour', i)
                if ok:
                    print("Have object to track")
                    oldbbox = bbox
                    oldtime = datetime.now()
                    trackNo = 0;
                    while True:
                        trackNo = trackNo+1

                        # Read a new frame
                        ret, frame = cap.read()
                        if FAKE:
                            time.sleep(FAKE_SLEEP)
                        frame =  cv2.rotate(frame,cv2.ROTATE_180)
                        # Update tracker

                        ok, bbox = tracker.update(frame)

                        newtime = datetime.now()
                        deltaT = secondsTime(newtime) - secondsTime(oldtime)
                        oldtime = newtime

                        #if close to the end of the frame, drop out
                        if bbox[0] < 5 or bbox[1] < 5 or bbox[0] > (image_width - bbox[2] -5) or (bbox[1] > image_height - bbox[3] -5):
                            print("at an edge   " ,ok, "  ", bbox)
                            ok = False

                        #check big enough object still
                        if x < 10 or y < 10:
                            print("too small")
                            ok = False

                        oldC = centre(oldbbox)
                        newC = centre(bbox)
                        cv2.line(frame, oldC, newC, (0, 255, 0))
                        oldbbox = bbox

                        # find pixels moved
                        deltaS = pixelsMoved(oldC, newC) * 0.05

                        if deltaS == 0:
                            print("no deltaS")
                            ok = False

                        # calculate speed (1 pixel ~0.05m)
                        velocity = int((deltaS / (deltaT)) * 2.2)



                        # Draw bounding box
                        if ok and deltaS > 0.2:


                            print(velocity, " ", deltaS, " ", deltaT)



                            p1 = (int(bbox[0]), int(bbox[1]))
                            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                            cv2.rectangle(frame, p1, p2, (0, 0, 255))
                            cv2.rectangle(frame,(0,0),(image_width,60),(0,0,0),-1)

                            #save first and last images, combine and save with time difference
                            if trackNo ==1:
                                firstImage = frame.copy()
                                firstTime = oldtime
                                firstCentre = newC
                            lastImage = frame.copy()
                            lastTime = oldtime
                            lastCentre = newC
                            lastVelocity = velocity


                            speedText =  str(velocity)+ "mph"
                            cv2.putText(frame,speedText,(20,20),cv2.FONT_HERSHEY_PLAIN,1,(0,0,255),1)
                            cv2.imshow('colour', frame)
                            cv2.imwrite("car.jpg",frame)
                            cv2.waitKey(1)


                        if not ok:
                            #reset tracker
                            tracker = cv2.Tracker_create("MEDIANFLOW")
                            print("Finished Tracking \n\n")

                            #save summary image if we have been tracking
                            if trackNo >0 :
                                deltaT = secondsTime(lastTime) - secondsTime(firstTime)
                                if deltaT > 0:
                                    deltaS = pixelsMoved(firstCentre, lastCentre) * 0.05
                                    if deltaS > 4:
                                        summaryImage = np.concatenate((firstImage,lastImage),axis=1)

                                        velocity = int((deltaS / (deltaT)) * 2.2)

                                        summaryText =  "Speed: {0} Distance: {1:.2f}m Time: {2:.2f}s".format(velocity,deltaS,deltaT)

                                        cv2.rectangle(summaryImage, (0, 0), (image_width*2, 50), (0, 0, 0), -1)
                                        print(summaryText)
                                        timeString = str(firstTime)
                                        cv2.putText(summaryImage, timeString, (20, 15), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)
                                        timeString = str(lastTime)
                                        cv2.putText(summaryImage, timeString, (20 + image_width, 15), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)
                                        cv2.putText(summaryImage, summaryText, (20 , 30), cv2.FONT_HERSHEY_PLAIN, 1,
                                                    (0, 0, 255), 1)

                                        cv2.imshow ("last summary", summaryImage)

                                        timestr = "trackedCars/" + str(velocity) + "-" + time.strftime("%Y%m%d-%H%M%S.jpg")
                                        cv2.imwrite(timestr,summaryImage)
                                        srv.put(timestr, "car.jpg")
                            break


    #cv2.imshow('thresh',thresh)

    if cv2.waitKey(1) == 27:
        exit(0)


