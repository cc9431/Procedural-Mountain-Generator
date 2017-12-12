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
from PIL import Image, ImageDraw

##-=-=-=- TODO =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=##
    #//::moon
    #//:clouds?
    #//:random color?

class Generator(object):
    '''Class for generating procedural pixel art'''

    ##-=-=-=- Class Functions -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-##

    def __init__(self, width_factor, seed=time.time(), prnt=False):
        '''Initialize random variable and generate image'''

        if width_factor <= 0:
            print("Whoops! First paramater must be greater than zero")
            exit(-1)
        
        ##-=-=-=- Set Random Seed =-=-=-=-=-=-=-=-=-=##
        self.rand_seed = int(seed)
        random.seed(self.rand_seed)

        ##-=-=-=- Tweakable Values -=-=-=-=-=-=-=-=-=##
        self.num_ranges     = 2             # Number of mountain ranges to be generated
        self.num_sines      = 8             # Number of sin values generated for each mountain range
        self.image_height   = 100           # Consider this the amount of "detail" in the mountains
        self.shadow_angle   = 2.5           # The angle of the shadow on the mountains (2.5 seems to be best)

        ##-=-=-=- Constant Values -=-=-=-=-=-=-=-=-=##
        self.c              = 25
        self.k              = 0.05
        self.color          = [50, 50 + random.randint(0, 150), 150 + random.randint(0, 55)]
        
        ##-=-=-=- Programatically Set Values =-=-=-=##
        self.image_width    = int(width_factor * self.image_height + (0.05 * math.pi))
        self.data           = []

        ##-=-=-=- Creation -=-=-=-=-=-=-=-=-=-=-=-=-##
        self.generateRanges()
        self.createImage()
        if prnt:
            print(str(self))

    def __str__(self):
        '''String representation of Generator'''
        string = "Image Width:\t" + str(self.image_width)
        string += "\nSeed:\t\t" + str(self.rand_seed)

        return string

    ##-=-=-=- Setters -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-##

    def generateRanges(self):
        '''Generate random mountains'''
        self.data = [self.randomMountain() for r in range(self.num_ranges)]

    def randomMountain(self):
        '''Generate random sin waves for each mountain'''
        sinVars = []
        for s in range(self.num_sines):
            sinVars.append(self.randomSinFunc())
        return sinVars

    def randomSinFunc(self):
        '''Create pseudo-random variables for a sin wave'''
        frequency   = random.uniform(1, 10)
        amplitude   = random.uniform(-self.c/frequency, self.c/frequency)
        phase       = random.uniform(0, 2 * math.pi)
        variables   = [amplitude, frequency, phase]
        return variables

    ##-=-=-=- Getters -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-##

    def getHeightData(self, x, m=0):
        '''Return the y of mountain given x value and which range'''
        rnge    = self.data[m]
        output  = 0
        extra   = (self.image_height / (self.num_ranges + 1) * (m + 1))
        noise   = random.randint(0, 4)

        for sine in range(self.num_sines):
            a       = rnge[sine][0]
            f       = rnge[sine][1]
            p       = rnge[sine][2]

            output += (a * math.sin(f * (self.k * x + p)))

        return output + extra + noise

    def getDerivativeHeightData(self, x, m=0):
        '''Return the derivative of mountain slope given x value'''
        rnge    = self.data[m]
        output  = 0
        extra   = (self.image_height / (self.num_ranges + 1) * (m + 1))
        noise   = random.randint(0, 4)

        for sine in range(self.num_sines):
            a       = rnge[sine][0]
            f       = rnge[sine][1]
            p       = rnge[sine][2]

            output += ((a * f * self.k) * math.cos(f * (self.k * x + p)))

        return output

    ##-=-=-=- Image Creator =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=##

    def createImage(self):
        '''Turn data generated from setters into pixels'''
        img = Image.new("RGB", (self.image_width, self.image_height), "white")
        draw = ImageDraw.Draw(img)
        color = tuple(self.color)
        
        for x in range(self.image_width):
            m_val       = 0
            highest_val = 0
            for rnge in range(self.num_ranges):
                val = self.getHeightData(x, rnge)
                if val > highest_val:
                    highest_val = val
            for y in range(self.image_height):
                mountain_height = self.getHeightData(x, m_val)

                if y > highest_val:
                    if random.random() > 0.99:
                        extra = random.randint(-55, 55)
                        color = (200 + extra, 200 + extra, 200 + extra)
                    else:
                        color = (50, 30, 40)
                elif y >= mountain_height and m_val < self.num_ranges - 1:
                    m_val += 1
                else:
                    #dist_to_peak = self.shadow_angle * (y - mountain_height) / float(self.image_height)
                    dist_to_peak = (y - mountain_height) / self.shadow_angle
                    if self.getDerivativeHeightData(x - dist_to_peak, m_val) < 0:
                        shadow = 0
                    else:
                        shadow = 10
                    desaturatedColor = list(self.color)
                    desaturatedColor[0] += (m_val * 20) - shadow
                    desaturatedColor[1] = desaturatedColor[0]
                    desaturatedColor[2] -= int(y / 1.5 - 30) + shadow
                    color = tuple(desaturatedColor)

                x_y = x,(self.image_height - y - 1)
                draw.point(x_y, color)
        img.show()

##-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=##

def main():
    num = int(sys.argv[1])
    if len(sys.argv) > 2:
        g = Generator(num, sys.argv[2])
    else:
        g = Generator(num)

main()
