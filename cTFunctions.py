import cv2
import math
import cTDefinitions
import time

#get the tallest contour from a list
def tallestContour(c):
    (x, y, w, h) = cv2.boundingRect(c)
    return h

#return the number of seconds from a datetime
def secondsTime(dt):
    return  dt.second + dt.microsecond / 1000000

#return the centre of a bounding box
def centre(bbox):
    return int(bbox[0] + bbox[2] /2), int(bbox[1] + bbox[3] /2)

#calculate the distance between two points
def pixelsMoved(oC,nC):
    return math.sqrt(math.pow(math.fabs(oC[0] - nC[0]),2) +  math.pow(math.fabs(oC[1] - nC[1]),2))

#calculate up or down 
def upordown(oC,nC):
    if nC[0] - oC[0] < 0:
        return "down"
    else:
        return "up"

#get a frame from a source
def getFrame(cap,SOURCE):
    ok, i = cap.read()
    if SOURCE == cTDefinitions.SOURCE_VIDEO:
        time.sleep(0.1)
    return ok, i
