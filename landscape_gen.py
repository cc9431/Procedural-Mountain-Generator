'''
procedural mountain range pixel art creator

Charles Calder
December 22nd 2017
'''

import sys
import time
import random
import math
import numpy
import moon

from PIL import Image
from noise import perlin

##-=-=-=- TODO =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=##
    #//:
        # I think the derivative function is where there's some stuff happening that is framing the mountains weirdly

class Generator(object):
    '''Class for generating procedural pixel art'''

    ##-=-=-=- Class Functions -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-##

    def __init__(self, width_factor, seed=time.time(), prnt=False):
        '''Initialize random variables and generate image'''

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
        self.constant       = 30            # Overall amplitude of superpositioned waves
        self.k              = 0.04          # Streching factor of mountains
        self.pnf = perlin.SimplexNoise()    # Initialize perlin noise creator
        self.sky_color      = [30, 30, 40]  # Set Color of sky and mountains
        self.color          = [random.randint(0, 150),
                               random.randint(0, 150),
                               random.randint(0, 150)]
        self.moon           = moon.Moon(15, self.rand_seed)

        ##-=-=-=- Programatically Set Values -=-=-=-##
        self.image_width    = int(width_factor * self.image_height)
        self.data           = list          # Stored variables of sine wave functions
        self.output         = [[tuple(self.sky_color) for x in range(self.image_width)]
                               for y in range(self.image_height)]
        self.moon_location = random.randint(0, self.image_width - 10)

        ##-=-=-=- Creation -=-=-=-=-=-=-=-=-=-=-=-=-##
        self.pnf.randomize()                # Randomize perlin noise
        self.generate_ranges()              # Generate variables for sine functions
        self.create_moon(self.moon_location, 2)
        self.create_scene()                 # Assign values to pixels
        self.show_image()
        if prnt:
            print(self)

    def __str__(self):
        '''String representation of Generator'''
        string = "Image Width:\t" + str(self.image_width)
        string += "\nSeed:\t\t" + str(self.rand_seed)
        string += "\nMoon Location:\t\t" + str(self.moon_location)

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

        for sine in range(self.num_sines):
            a       = rnge[sine][0]
            f       = rnge[sine][1]
            p       = rnge[sine][2]

            output += ((a * f * self.k) * math.cos(f * (self.k * x + p)))

        return output

    def get_highest_point(self, x):
        '''Return the highest mountain point for a given column'''
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

    def create_scene(self):
        '''Turn data generated from setters into pixels'''
        #img = Image.new("RGB", (self.image_width, self.image_height), "white")
        #draw = ImageDraw.Draw(img)
        color = tuple(self.color)

        for x in range(self.image_width):
            m_val       = 0
            highest_val = int(self.get_highest_point(x))

            for y in range(self.image_height):
                mountain_height = self.get_height_data(x, m_val)

                if y > highest_val:
                    color = self.create_sky(x, y)
                else:
                    if y >= mountain_height and m_val < self.num_ranges - 1:
                        m_val += 1
                    dist_to_peak = (y - mountain_height) / self.shadow_angle
                    if self.get_derivative_height_data(x - dist_to_peak, m_val) < 0:
                        shadow = 0
                    else:
                        shadow = 20
                    color = self.calculate_color(y, m_val, shadow)

                self.output[self.image_height - y - 1][x] = color

    def create_sky(self, x, y):
        '''Randomly place stars and use perlin noise for clouds'''
        res = 250.0
        curr = self.output[self.image_height - y - 1][x]
        if random.random() > 0.993 and curr == tuple(self.sky_color):
            extra = random.randint(-55, 55)
            color = (200 + extra, 200 + extra, 200 + extra)
            return color
        else:
            color = list(curr)
            noise = random.randint(0, 4)
            prln = self.pnf.noise2(y / res * 15, x / res)
            cloudy = int(prln / 2 * 100)
            if cloudy > 1:
                color = [col + cloudy + noise for col in color]
            return tuple(color)

    def create_moon(self, x, y):
        '''Paste moon into scene'''
        moon_data = self.moon.get()
        length = self.moon.length()
        for yval in range(length):
            for xval in range(length):
                if xval + x < len(self.output):
                    self.output[yval + y][xval + x] = moon_data[yval][xval]

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
