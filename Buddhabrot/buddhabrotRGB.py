from PIL import Image, ImageDraw
import math
import cmath
from scipy.special import gamma
import multiprocessing
import sys

sequence_function = lambda z_n, c, p : z_n ** p + c
#sequence_function = lambda z_n, c, p : gamma(z_n) ** p + c
#sequence_function = lambda z_n, c, p : (cmath.sin(cmath.tan(z_n))) ** p + c
#sequence_function = lambda z_n, c, p : cmath.sin(z_n.conjugate()) ** p + c 
#sequence_function = lambda z_n, c, p : cmath.sinh(z_n) ** p + c

#sequence_function = lambda z_n, c, p : 0.1 * z_n ** p + 2 * 0.1 * z_n + c

# Good ones
#sequence_function = lambda z_n, c, p : 2 * ((cmath.cos(z_n)) ** p) + c
#sequence_function = lambda z_n, c, p : 2 * ((cmath.sin(z_n)) ** p) + c


def iterate_over_bands(width, height, min_iter, max_iter, p, y_offset, arr):
    #width, height, min_iter, max_iter, p, x_start_end, y_start_end, plane = args

    plane = [[0] * height for _ in range(width)]
    
    for x in range(width):
        for y in range(int(height/4)):
            c = complex(((x * 3.) / width) - 2, (((y + y_offset) * 2.0) / height) - 1)
            z = c
            complex_sequence = set([])
            for i in range(max_iter):
                complex_sequence.add(z)
                z = sequence_function(z, c, p)
                if abs(z) > 2:
                    if len(complex_sequence) <= min_iter:
                        break
                    complex_sequence.add(z)
                    for term in complex_sequence:
                        pixel_x = math.floor(((term.real + 2) * width) / 3.)
                        pixel_y = math.floor(((term.imag + 1) * height) / 2.)
                        if 0 <= pixel_x < width and 0 <= pixel_y < height:
                            plane[int(pixel_x)][int(pixel_y)] += 1
                    break
        print("x is: " + str(x))
    arr.append(plane)

def iterate_over_quadrants(width, height, min_iter, max_iter, p, x_range, y_range, arr):

    (x_s, x_e) = x_range
    (y_s, y_e) = y_range

    plane = [[0] * height for _ in range(width)]
    
    for x in range(x_s, x_e):
        for y in range(y_s, y_e):
            c = complex(((x * 3.) / width) - 2, ((y * 2.0) / height) - 1)
            z = c
            complex_sequence = set([])
            for i in range(max_iter):
                complex_sequence.add(z)
                z = sequence_function(z, c, p)
                if abs(z) > 2:
                    if len(complex_sequence) <= min_iter:
                        break
                    complex_sequence.add(z)
                    for term in complex_sequence:
                        pixel_x = math.floor(((term.real + 2) * width) / 3.)
                        pixel_y = math.floor(((term.imag + 1) * height) / 2.)
                        if 0 <= pixel_x < width and 0 <= pixel_y < height:
                            plane[int(pixel_x)][int(pixel_y)] += 1
                    break
        print("x is: " + str(x))
    arr.append(plane)

def iter_multi(width, height, min_iter, max_iter, p, channel, arr):
    x_r_1 = (0, int(width/2))
    x_r_2 = (int(width/2), width)
    y_r_1 = (0, int(height/2))
    y_r_2 = (int(height/2), height)

    manager = multiprocessing.Manager()
    plane = manager.list()
    jobs = []

    # time: 43 secs
    '''
    j1 = multiprocessing.Process(target = iterate_over_bands, args = (width, height, min_iter, max_iter, p, 0, plane))
    jobs.append(j1)
    j1.start()

    j2 = multiprocessing.Process(target = iterate_over_bands, args = (width, height, min_iter, max_iter, p, int(height/4), plane))
    jobs.append(j2)
    j2.start()

    j3 = multiprocessing.Process(target = iterate_over_bands, args = (width, height, min_iter, max_iter, p, int(2 * height/4), plane))
    jobs.append(j3)
    j3.start()

    j4 = multiprocessing.Process(target = iterate_over_bands, args = (width, height, min_iter, max_iter, p, int(3 * height/4), plane))
    jobs.append(j4)
    j4.start()
    '''
    # time: 38 secs
    j1 = multiprocessing.Process(target=iterate_over_quadrants, args=(width, height, min_iter, max_iter, p, x_r_1, y_r_1, plane))
    jobs.append(j1)
    j1.start()

    j2 = multiprocessing.Process(target=iterate_over_quadrants, args=(width, height, min_iter, max_iter, p, x_r_2, y_r_1, plane))
    jobs.append(j2)
    j2.start()

    j3 = multiprocessing.Process(target=iterate_over_quadrants, args=(width, height, min_iter, max_iter, p, x_r_1, y_r_2, plane))
    jobs.append(j3)
    j3.start()

    j4 = multiprocessing.Process(target=iterate_over_quadrants, args=(width, height, min_iter, max_iter, p, x_r_2, y_r_2, plane))
    jobs.append(j4)
    j4.start()

    for proc in jobs:
        proc.join()

    final_plane = [[0] * height for _ in range(width)]

    minimum = final_plane[0][0]
    maximum = final_plane[0][0]

    print("Starting rendering...")

    for p in plane:
        for x in range(width):
            for y in range(height):
                final_plane[x][y] += p[x][y]
                if p[x][y] < minimum: minimum = p[x][y]
                if p[x][y] > maximum: maximum = p[x][y]

    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    for y in range(height):
        for x in range(width):
            val = int((final_plane[x][y] - minimum) * 255 / (maximum - minimum))
            if channel == 'R':
                draw.point([x, y], (val, 0, 0))
            elif channel == 'G':
                draw.point([x, y], (0, val, 0))
            else:
                draw.point([x, y], (0, 0, val))

    print ("Rendering done")

    if arr is not None: 
        arr.append(img)
        sys.exit()

    return img

def iterate_over_region(width, height, min_iter, max_iter, p, ret):

    complex_plane = [[0] * height for _ in range(width)]
    for x in range(width):
        for y in range(int(height/2)):
            c = complex(((x * 3.) / width) - 2, ((y * 2.0) / height) - 1)
            z = c
            complex_sequence = set([])
            for i in range(max_iter):
                complex_sequence.add(z)
                z = sequence_function(z, c, p)
                if abs(z) > 2:
                    if len(complex_sequence) <= min_iter:
                        break
                    complex_sequence.add(z)
                    for term in complex_sequence:
                        pixel_x = math.floor(((term.real + 2) * width) / 3.)
                        pixel_y = math.floor(((term.imag + 1) * height) / 2.)
                        if 0 <= pixel_x < width and 0 <= pixel_y < height:
                            complex_plane[int(pixel_x)][int(pixel_y)] += 1
                    break
        print("x is: " + str(x))

    for x in range(width):
        i = 0
        for y in range(int(height/2)):
            complex_plane[x][int(height/2) + y] = complex_plane[x][int(height/2) - y]
    ret.append(complex_plane)

def render_picture(width, height, result, channel):

    minimum = result[0][0]
    maximum = result[0][0]

    print ("Starting rendering")
    print ("The image size is", width, "x", height)
    for x in range(width):
        for y in range(height):
            if result[x][y] < minimum:
                minimum = result[x][y]
            if result[x][y] > maximum:
                maximum = result[x][y]
        print('Rendered x: ' + str(x))
    
    img = Image.new('RGB', (width, height))

    draw = ImageDraw.Draw(img)

    for y in range(height):
        for x in range(width):
            val = int((result[x][y] - minimum) * 255 / (maximum - minimum))
            if channel == 'R':
                draw.point([x, y], (val, 0, 0))
            elif channel == 'G':
                draw.point([x, y], (0, val, 0))
            else:
                draw.point([x, y], (0, 0, val))
            
    print ("Rendering done")
    return img
