import cv2
import numpy as np
import time
import math
from datetime import datetime
import cTDefinitions
import cTFunctions as cT

SOURCE = cTDefinitions.SOURCE_LOCAL

HAVE_DISPLAY = False

if SOURCE == cTDefinitions.SOURCE_VIDEO:
    cap = cv2.VideoCapture('test.mp4')
elif SOURCE == cTDefinitions.SOURCE_HTTP:
    cap = cv2.VideoCapture('http://192.168.123.153:8080/?action=stream&.mjpg')
elif SOURCE == cTDefinitions.SOURCE_LOCAL:
    cap = cv2.VideoCapture(0)
    cap.set(3, 320)
    cap.set(4, 240)
else:
    print("Error: Unknown Source")
    exit(1)

# define image processing functions
fgbg = cv2.createBackgroundSubtractorMOG2()

kernel2x2R = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
kernel10x10E = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))

logfile = open("log.csv", "a")

if HAVE_DISPLAY:
    # create viewing windows
    cv2.namedWindow('colour')
    cv2.namedWindow('box')
    cv2.moveWindow('colour', 0, 0)
    cv2.moveWindow('box', 320, 280)
frameNo = 0

while True:
    if cv2.waitKey(1) == 27:
        exit(0)
    # Capture a frame
    ok, frame = cT.getFrame(cap, SOURCE)

    frameNo = frameNo + 1
    # print(frameNo)
    if not ok:
        break
    frame = cv2.rotate(frame, cv2.ROTATE_180)

    if HAVE_DISPLAY:
        cv2.imshow('colour', frame)

    image_height, image_width = frame.shape[:2]
    gr = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # get changes
    fgmask = fgbg.apply(gr)

    # clean up by openening image - remove noise
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel2x2R)
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_CLOSE, kernel10x10E)

    ret, thresh = cv2.threshold(fgmask, 254, 255, 0)

    # get countours
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE,
                                                cv2.CHAIN_APPROX_SIMPLE)
    if HAVE_DISPLAY:
        cv2.drawContours(frame, contours, -1, (255, 0, 0), 1)
        cv2.imshow('box', frame)

    sortedContours = sorted(contours, key=cv2.contourArea, reverse=True)
    # sortedContours = sorted(contours, key=cT.tallestContour, reverse=True)

    # if no contours restart capture
    if not sortedContours:
        continue

    # We have a box
    (x, y, w, h) = cv2.boundingRect(sortedContours[0])
    bbox = (x, y, w, h)

    # only look at big boxes
    if w < 10 or h < 10:
        continue

    # start tracking if whole box in window
    if not (x > 2 and x + w < image_width - 2):
        continue

    # initialise tracker using grayscale image
    tracker = cv2.Tracker_create("MEDIANFLOW")
    ok = tracker.init(gr, bbox)

    if HAVE_DISPLAY:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
        cv2.imshow('box', frame)

    if not ok:
        continue

    oldbbox = bbox
    oldtime = datetime.now()
    trackNo = 0

    # start tracking the found object
    while True:
        trackNo = trackNo + 1

        # Read a new frame
        ok, frame = cT.getFrame(cap, SOURCE)
        if not ok:
            break
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        gr = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        newtime = datetime.now()
        if HAVE_DISPLAY:
            cv2.imshow('colour', frame)

        # Update tracker
        ok, bbox = tracker.update(gr)
        if not ok:
            break

        (x, y, w, h) = bbox
        x = int(x)
        y = int(y)
        w = int(w)
        h = int(h)

        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 1)
        if HAVE_DISPLAY:
            cv2.imshow('colour', frame)

        deltaT = cT.secondsTime(newtime) - cT.secondsTime(oldtime)
        oldtime = newtime

        # if close to the end of the frame, drop out
        if x < 2 or y < 2 or x > (image_width - w - 2) or \
                (y > image_height - h - 2):
            break

        # check big enough object still
        if x < 8 or y < 8:
            break

        # draw distance moved from last frame
        oldC = cT.centre(oldbbox)
        newC = cT.centre(bbox)
        

        #cv2.line(frame, oldC, newC, (0, 255, 0),2)
        oldbbox = bbox

        # find distance moved
        deltaS = cT.pixelsMoved(oldC, newC)

        # check distance moved is big enough in pixels
        if deltaS < 2:
            break

        #convert to meters
        deltaS = deltaS * cTDefinitions.PIXEL_DISTANCE

        # calculate speed (1 pixel ~0.05m)
        velocity = int((deltaS / deltaT) * cTDefinitions.MPS_MPH_CONVERSION)

        # store first and last details for overview
        if trackNo == 1:
            firstImage = frame.copy()
            firstTime = oldtime
            firstCentre = newC
        lastImage = frame.copy()
        lastTime = oldtime
        lastCentre = newC
        lastVelocity = velocity

        speedText = str(velocity) + "mph"
        cv2.putText(frame, speedText, (20, 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)
        if HAVE_DISPLAY:
            cv2.imshow('colour', frame)

        cv2.imwrite("car.jpg", frame)
        cv2.waitKey(1)

    # save summary image if we have been tracking more than 2 pictures
    if trackNo < 4:
        continue

    deltaT = cT.secondsTime(lastTime) - cT.secondsTime(firstTime)

    if deltaT < 0.01:
        continue

    deltaS = cT.pixelsMoved(firstCentre, lastCentre) * cTDefinitions.PIXEL_DISTANCE


    direction = cT.upordown(firstCentre,lastCentre)
	
    if deltaS < 2:
        continue

    #calculate average velocity
    velocity = int((deltaS / deltaT) * cTDefinitions.MPS_MPH_CONVERSION)


    #construct summary image
    summaryImage = np.concatenate((firstImage, lastImage), axis=1)
    cv2.rectangle(summaryImage, (0, 0), (image_width * 2, 50), (0, 0, 0), -1)

    timeString = str(firstTime)
    cv2.putText(summaryImage, timeString, (20, 15), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)

    timeString = str(lastTime)
    cv2.putText(summaryImage, timeString, (20 + image_width, 15), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)

    summaryText = "Speed: {0} Distance: {1:.2f}m Time: {2:.2f}s".format(velocity, deltaS, deltaT) + " " + direction
    cv2.putText(summaryImage, summaryText, (20, 30), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)

    if HAVE_DISPLAY:
        cv2.imshow("last summary", summaryImage)

    #save summary images
    timestr = "trackedCars/" + time.strftime("%Y%m%d-%H%M%S") + "-" + str(velocity) + "-" + direction + ".png"
    cv2.imwrite(timestr, summaryImage)
    cv2.imwrite('summary.jpg', summaryImage)

    #output to log file
    logText = "{0},{1:.2f},{2:.2f}".format(velocity, deltaS, deltaT)
    logText = logText + time.strftime(",%Y,%m,%d,%H,%M,%S,")+direction + "\n"
    logfile.write(logText)
    
    logfile.flush()


    trackNo = 0

    if cv2.waitKey(1) == 27:
        exit(0)
