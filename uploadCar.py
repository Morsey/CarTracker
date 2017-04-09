import pysftp
import os
virgin = 1
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None
srv = pysftp.Connection(host="home84386385.1and1-data.host",username="u35045545",password="D0nF4s4az6Wt",cnopts=cnopts)
srv.cd("/kunden/homepages/0/d84386385/htdocs/www.robmorse.com/cars")
while True:

    newTime =  os.path.getmtime("/Users/rob/PycharmProjects/CarTracker/car.jpg")
    if virgin:
        oldTime = newTime
        virgin =0
    if oldTime != newTime:
        #have a new file, upload it
        print("uploading")
        srv.put("car.jpg","cars/car.jpg")
        #os.system("scp car.jpg -p 'D0nF4s4az6Wtu35045545@home84386385.1and1-data.host/kunden/homepages/0/d84386385/htdocs/www.robmorse.com/cars/car.jpg' ")
        oldTime = newTime
    #/kunden/homepages/0/d84386385/htdocs/www.robmorse.com/cars