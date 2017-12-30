#!/usr/bin/env python
#
# Licensed under the BSD license. See full license in LICENSE file.
#
# Author: Christian Meffert

from Adafruit_Trellis import Adafruit_Trellis, Adafruit_TrellisSet
import time

I2C_BUS = 1
NUM_TRELLIS = 4
NUM_LEDS = NUM_TRELLIS * 16

# Mapping the Trellis index to a logical numeration
# starting with the upper left corner and ending in
# the lower right corner
#
#         00 01 02 03 04 05 06 07
#         08 09 10 11 12 13 14 15
#         16 17 18 19 20 21 22 23
#         24 25 26 27 28 29 30 31
#         32 33 34 35 36 37 38 39
#         40 41 42 43 44 45 46 47
#         48 49 50 51 52 53 54 55
#         56 57 58 59 60 61 62 63
#
BOARDTRELLIS = [\
        19, 23, 27, 31, 51, 55, 59, 63,\
        18, 22, 26, 30, 50, 54, 58, 62,\
        17, 21, 25, 29, 49, 53, 57, 61,\
        16, 20, 24, 28, 48, 52, 56, 60,\
         3,  7, 11, 15, 35, 39, 43, 47,\
         2,  6, 10, 14, 34, 38, 42, 46,\
         1,  5,  9, 13, 33, 37, 41, 45,\
         0,  4,  8, 12, 32, 36, 40, 44\
        ]


class BoardTrellis:
    
    def __init__(self):
        self.__trellis = Adafruit_TrellisSet(\
                                        Adafruit_Trellis(),\
                                        Adafruit_Trellis(),\
                                        Adafruit_Trellis(),\
                                        Adafruit_Trellis())
        
        self.__trellis.begin((0x70,  I2C_BUS), (0x71, I2C_BUS), (0x72, I2C_BUS), (0x73, I2C_BUS))
        return
    
    def initialize(self):
        # light up all the LEDs in order
        for i in range(NUM_LEDS):
            self.__trellis.setLED(BOARDTRELLIS[i])
            self.__trellis.writeDisplay()
            time.sleep(0.05)
        
        # then turn them off
        for i in range(NUM_LEDS):
            self.__trellis.clrLED(BOARDTRELLIS[i])
            self.__trellis.writeDisplay()
            time.sleep(0.05)
            
        return
    
    def getPressedButtons(self):
        pressed = []
        
        if self.__trellis.readSwitches():
            for i in range(NUM_LEDS):
                if self.__trellis.justPressed(BOARDTRELLIS[i]):
                    pressed.append(i)
                    
        return pressed
    
    def setLEDs(self, leds=[]):
        for i in range(NUM_LEDS):
            if leds[i] > 0:
                self.__trellis.setLED(BOARDTRELLIS[i])
            else:
                self.__trellis.clrLED(BOARDTRELLIS[i])
            
        self.__trellis.writeDisplay()
        return
    

        
