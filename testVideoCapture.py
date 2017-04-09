import cv2
import urllib.request
import numpy as np


cap = cv2.VideoCapture('http://192.168.123.175:8080/?action=stream&.mjpg')
while True:
    ret, frame = cap.read()
    cv2.imshow('ff',frame)

    if cv2.waitKey(1) == 27:
        exit(0)