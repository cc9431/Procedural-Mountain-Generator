'''
Procedural Moon Generator
Charles Calder
'''

import sys
import time
import random
import math
import numpy

from PIL import Image

class Moon(object):
    '''Class for generating procedural pixel art'''

    ##-=-=-=- Class Functions -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-##

    def __init__(self, num, seed=time.time(), prnt=False):
        '''Initialize random variables and generate image'''

        if num < 0:
            print("Whoops! First paramater must be greater than zero")
            exit(-1)

        ##-=-=-=- Set Random Seed -=-=-=-=-=-=-=-=-=-##
        self.rand_seed = int(seed)
        random.seed(self.rand_seed)

        ##-=-=-=- Tweakable Values -=-=-=-=-=-=-=-=-=##
        self.crater_freq    = num             	# Amount of craters in the moon's face
        self.shadow_angle   = 2.5           	# The amount of shadow covering moon

        ##-=-=-=- Constant Values -=-=-=-=-=-=-=-=-=##
        self.k              = 0.04          	# Streching factor of mountains
        #self.pnf = perlin.SimplexNoise()    	# Initialize perlin noise creator
        self.sky_color      = [30, 30, 40]  	# Set Color of sky and mountains
        self.color          = [150, 150, 150]	# Color of moon face

        ##-=-=-=- Programatically Set Values -=-=-=-##
        self.size           = 10
        self.image_width    = int(self.size * 2.5)
        self.image_height   = int(self.size * 2.5)
        self.center         = [self.image_width/2, self.image_height/2]
        self.craters        = []
        self.output         = [[tuple(self.sky_color) for x in range(self.image_width)]
                               for y in range(self.image_height)]

        ##-=-=-=- Creation -=-=-=-=-=-=-=-=-=-=-=-=-##
        self.generate_craters()
        self.create()
        if prnt:
            print(self)

    def __str__(self):
        '''String representation of Generator'''
        string = "\nSeed:\t\t" + str(self.rand_seed)
        return string

    def get(self):
        return self.output

    def length(self):
        '''Return data list length'''
        return len(self.output)

    def generate_craters(self):
        '''Calculate where craters should be and how dark they are'''
        for freq in range(self.crater_freq):

            x   = random.randint(int(self.center[0] - self.size), int(self.center[0] + self.size))
            y   = random.randint(int(self.center[1] - self.size), int(self.center[1] + self.size))
            sz  = random.randint(self.size / 5, self.size / 2)
            col = random.randint(10, 30)
            self.craters.append([[x, y], sz, col])

    def calculate_dist(self, x, y, center):
        '''Return distance between two points'''
        y_2  = math.pow(x - center[0], 2)
        x_2  = math.pow(y - center[1], 2)
        dist = int(math.sqrt(x_2 + y_2) - 0.5)
        return dist

    def in_radius(self, x, y, center, size):
        '''Return if current pixel is within radius'''
        dist = self.calculate_dist(x, y, center)
        return dist <= size

    def create(self):
        '''Create a moon'''
        for x in range(self.image_width):
            for y in range(self.image_height):
                if self.in_radius(x, y, self.center, self.size):
                    color = [val for val in self.color]
                    for crater in self.craters:
                        noisex = random.randint(1, 2)
                        noisey = random.randint(1, 2)
                        if self.in_radius(x + noisex, y + noisey, crater[0], crater[1]):
                            extra = random.randint(0, 10)
                            color = [max(col - crater[2], 0) + extra for col in color]
                else:
                    color = self.sky_color
                self.output[y][x] = tuple(color)

    def show_image(self):
        '''Turn output data into an image'''
        self.output = numpy.array(self.output, dtype=numpy.uint8)
        new_image = Image.fromarray(self.output)
        new_image.show()

def main():
    '''Main function'''
    if len(sys.argv) == 1:
        print('Whoops! Please provide a width factor (and optionally a seed value)')
        exit(-1)

    timer = time.time()
    num = int(sys.argv[1])
    if len(sys.argv) > 2:
        moon = Moon(num, sys.argv[2], prnt=True)
    else:
        moon = Moon(num, prnt=True)

    moon.show_image()
    print (time.time() - timer)
