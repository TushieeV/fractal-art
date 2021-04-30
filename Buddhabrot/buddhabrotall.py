from PIL import Image, ImageDraw
from buddhabrotRGB import *
import math
import multiprocessing

def combineImg(red, green, blue, name):
    combined = Image.merge('RGB', (red.getchannel('R'), green.getchannel('G'), blue.getchannel('B')))
    combined.save(name + ".bmp")

if __name__ == '__main__':

    name = input("Enter name: ")
    p = float(input("Enter power: "))
    imgType = input("Enter image type: ")

    r_min = int(input("Enter minimum threshold: "))
    r_max = int(input("Enter maximum threshold: "))

    ratio = int(input("Enter threshold factor: "))

    w = 1350
    h = 900

    if len(imgType) == 3:

        manager = multiprocessing.Manager()
        ret = manager.list()
        jobs = []
        

        j1 = multiprocessing.Process(target=iter_multi, args=(w, h, r_min, r_max, p, 'R', ret))
        jobs.append(j1)
        j1.start()
        j2 = multiprocessing.Process(target=iter_multi, args=(w, h, int(r_min/ratio), int(r_max/ratio), p, 'G', ret))
        jobs.append(j2)
        j2.start()
        j3 = multiprocessing.Process(target=iter_multi, args=(w, h, int(r_min/ratio**2), int(r_max/ratio**2), p, 'B', ret))
        jobs.append(j3)
        j3.start()
        
        for proc in jobs:
            proc.join()

        combineImg(ret[2], ret[1], ret[0], name)
    
    elif imgType == 'R':

        # r_min = 1k, r_max = 5k, time: 2m 40secs
        red = iter_multi(w, h, r_min, r_max, p, 'R', None)
        red.save(name + ".bmp")
        
    elif imgType == 'G':

        green = iter_multi(w, h, r_min, r_max, p, 'G', None)
        green.save(name + ".bmp")

    else:

        blue = iter_multi(w, h, r_min, r_max, p, 'B', None)
        blue.save(name + ".bmp")