import cv2
import urllib.request
import numpy as np

def tallestContour(c):
    (x, y, w, h) = cv2.boundingRect(c)
    return h;


fgbg = cv2.createBackgroundSubtractorMOG2()
kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(2,2))

stream = urllib.request.urlopen('http://192.168.123.175:8080/?action=stream')

roadMask = cv2.imread('/Users/rob/CarTracking/roadMask_1.jpg')
roadMask = cv2.cvtColor(roadMask,cv2.COLOR_BGR2GRAY)
roadMask = cv2.rotate(roadMask,cv2.ROTATE_180)

bytes = bytes()

oldx = 320
oldtime = 0
while True:
    bytes += stream.read(1024)
    a = bytes.find(b'\xff\xd8')
    b = bytes.find(b'\xff\xd9')
    if a != -1 and b != -1:
        jpg = bytes[a:b+2]
        bytes = bytes[b+2:]

        i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

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
            if h > 10 and w > 10:
                cv2.rectangle(i, (x, y), (x + w, y + h), (0, 255, 0), 1)

                # only act on downhill

                diff = x - oldx
                print(diff)
                oldx = x



        cv2.imshow('colour', i)
        cv2.imshow('thresh',thresh)

        if cv2.waitKey(1) == 27:
            exit(0)


