'''
Cybergraphics Final Art Project - procedural mountain range pixel art creator

Charles Calder
December 22nd
ART 100
'''

import sys
import time
import random
import math
import numpy

from PIL import Image
from noise import perlin

##-=-=-=- TODO =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=##
    #//::moon

class Generator(object):
    '''Class for generating procedural pixel art'''

    ##-=-=-=- Class Functions -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-##

    def __init__(self, width_factor, seed=time.time(), prnt=False):
        '''Initialize random variable and generate image'''

        if width_factor <= 0:
            print("Whoops! First paramater must be greater than zero")
            exit(-1)

        ##-=-=-=- Set Random Seed -=-=-=-=-=-=-=-=-=-##
        self.rand_seed = int(seed)
        random.seed(self.rand_seed)

        ##-=-=-=- Tweakable Values -=-=-=-=-=-=-=-=-=##
        self.num_ranges     = 3             # Number of mountain ranges to be generated
        self.num_sines      = 10            # Number of sin values generated for each mountain range
        self.image_height   = 150           # Consider this the amount of "detail" in the mountains
        self.shadow_angle   = 2.5           # The angle of the shadow on the mountains

        ##-=-=-=- Constant Values -=-=-=-=-=-=-=-=-=##
        self.constant       = 30
        self.k              = 0.04
        self.color          = [random.randint(0, 150),
                               random.randint(0, 150),
                               random.randint(0, 150)]

        ##-=-=-=- Programatically Set Values -=-=-=-##
        self.image_width    = int(width_factor * self.image_height)
        self.data           = []
        self.output         = [[(30, 30, 40) for x in range(self.image_width)]
                               for y in range(self.image_height)]

        ##-=-=-=- Creation -=-=-=-=-=-=-=-=-=-=-=-=-##
        self.generate_ranges()
        self.create_mountains()
        self.create_sky()
        self.show_image()
        if prnt:
            print(self)

    def __str__(self):
        '''String representation of Generator'''
        string = "Image Width:\t" + str(self.image_width)
        string += "\nSeed:\t\t" + str(self.rand_seed)

        return string

    ##-=-=-=- Setters -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-##

    def generate_ranges(self):
        '''Generate random mountains'''
        self.data = [self.random_mountain() for r in range(self.num_ranges)]

    def random_mountain(self):
        '''Generate random sin waves for each mountain'''
        sin_vars = []
        for s in range(self.num_sines):
            sin_vars.append(self.random_sin_func())
        return sin_vars

    def random_sin_func(self):
        '''Create pseudo-random variables for a sin wave'''
        frequency   = random.uniform(1, 10)
        amplitude   = random.uniform(-self.constant/frequency, self.constant/frequency)
        phase       = random.uniform(0, 2 * math.pi)
        variables   = [amplitude, frequency, phase]
        return variables

    ##-=-=-=- Getters -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-##

    def get_height_data(self, x, m=0):
        '''Return the y of mountain given x value and which range'''
        rnge    = self.data[m]
        output  = 0
        extra   = (self.image_height / (self.num_ranges + 1) * (m + 1))
        noise   = random.randint(0, 2)

        for sine in range(self.num_sines):
            a       = rnge[sine][0]
            f       = rnge[sine][1]
            p       = rnge[sine][2]

            output += (a * math.sin(f * (self.k * x + p)))

        return output + extra + noise

    def get_derivative_height_data(self, x, m=0):
        '''Return the derivative of mountain slope given x value'''
        rnge    = self.data[m]
        output  = 0
        noise   = random.randint(0, 1)
        #//: I think this is where there's some stuff happening that is framing the mountains weirdly
        for sine in range(self.num_sines):
            a       = rnge[sine][0]
            f       = rnge[sine][1]
            p       = rnge[sine][2]

            output += ((a * f * self.k) * math.cos(f * (self.k * x + p)))

        return output

    def get_highest_point(self, x):
        highest_val = 0
        for rnge in range(self.num_ranges):
            val = self.get_height_data(x, rnge)
            if val > highest_val:
                highest_val = val
        return highest_val

    def calculate_color(self, y, m, shadow):
        '''Calculate color based on mountain number, slope, and height'''
        desaturated_color = list(self.color)
        change = int(y * 150 / self.image_height) - (shadow + (m * 50))

        desaturated_color[0] = max(desaturated_color[0] + change, 0)
        desaturated_color[1] = max(desaturated_color[1] + change, 0)
        desaturated_color[2] = max(desaturated_color[2] + change, 0)

        return tuple(desaturated_color)


    ##-=-=-=- Image Functions -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-##

    def create_mountains(self):
        '''Turn data generated from setters into pixels'''
        #img = Image.new("RGB", (self.image_width, self.image_height), "white")
        #draw = ImageDraw.Draw(img)
        color = tuple(self.color)

        for x in range(self.image_width):
            m_val       = 0
            highest_val = int(self.get_highest_point(x))

            for y in range(highest_val):
                mountain_height = self.get_height_data(x, m_val)
                if y >= mountain_height and m_val < self.num_ranges - 1:
                    m_val += 1
                dist_to_peak = (y - mountain_height) / self.shadow_angle
                if self.get_derivative_height_data(x - dist_to_peak, m_val) < 0:
                    shadow = 0
                else:
                    shadow = 20
                color = self.calculate_color(y, m_val, shadow)
                self.output[self.image_height - y - 1][x] = color

    def create_sky(self):
        '''Use perlin noise to create a cloudy sky'''
        pnf = perlin.SimplexNoise()
        pnf.randomize()
        res = 200.0
        for x in range(self.image_width):
            highest_val = int(self.get_highest_point(x))
            for y in range(self.image_height - highest_val):
                if random.random() > 0.99:
                    extra = random.randint(-55, 55)
                    color = (200 + extra, 200 + extra, 200 + extra)
                    self.output[y][x] = color
                else:
                    n = pnf.noise2(y / res * 30, x / res)
                    cloudy = int(n / 2 * 100 + 0.5)
                    if cloudy > 0:
                        color = (30 + cloudy, 30 + cloudy, 40 + cloudy)
                        self.output[y][x] = color

    def show_image(self):
        '''Turn output data into an image'''
        self.output = numpy.array(self.output, dtype=numpy.uint8)
        new_image = Image.fromarray(self.output)
        new_image.show()


##-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=##

def main():
    '''Main function!'''
    if len(sys.argv) == 1:
        print ('Whoops! Please provide a width factor (and optionally a seed value)')
        exit(-1)

    timer = time.time()
    num = int(sys.argv[1])
    if len(sys.argv) > 2:
        g = Generator(num, sys.argv[2], prnt=True)
    else:
        g = Generator(num, prnt=True)

    print (time.time() - timer)

main()
