#!/usr/bin/env python
#
# Licensed under the BSD license. See full license in LICENSE file.
#
# Author: Christian Meffert

import curses
import time


COLOR_INACTIVE = 0
COLOR_ACTIVE = 1
COLOR_SELECTED = 2


class BoardError(Exception):
    """Fatal error"""

class BoardCurses:
    
    def __init__(self):
        self.__selected = 0
        self.__stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(False)
        curses.start_color()
        curses.init_pair(COLOR_ACTIVE, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(COLOR_SELECTED, curses.COLOR_WHITE, curses.COLOR_WHITE)
        self.__stdscr.keypad(1)
        self.__stdscr.clear()
        self.__stdscr.nodelay(1)
        self.__window = self.__stdscr.subwin((8*4)+3, (8*6)+5, 2, 2)
        self.__window.border()
        return
    
    def __del__(self):
        curses.nocbreak()
        self.__stdscr.keypad(0)
        curses.echo()
        curses.endwin()
    
    def initialize(self):
        for led in range(64):
            self.__updateLED(self.__window, led, 1, 0)
            self.__stdscr.refresh()
            time.sleep(0.01)
        
        for led in range(64):
            self.__updateLED(self.__window, led, 0, 0)
            self.__stdscr.refresh()
            time.sleep(0.01)
        
        return
    
    def getPressedButtons(self):
        pressed = []
        
        c = self.__stdscr.getch()
        if c == curses.KEY_DOWN:
            self.__selected = (self.__selected + 8) % 64
        elif c == curses.KEY_UP:
            self.__selected = (self.__selected - 8) % 64
        elif c == curses.KEY_LEFT:
            self.__selected = (self.__selected - 1) % 64
        elif c == curses.KEY_RIGHT:
            self.__selected = (self.__selected + 1) % 64
        elif c != -1:
            pressed.append(self.__selected)
        
        return pressed
    
    def __updateLED(self, window, idx, active, selected):
        x = idx % 8
        y = idx / 8
        
        w = 5
        h = 3
        
        ox = 3 + ((w+1) * x) #
        oy = 2 + ((h+1) * y)
        
        if selected:
            color = curses.color_pair(COLOR_SELECTED)
        elif active:
            color = curses.color_pair(COLOR_ACTIVE)
        else:
            color = curses.color_pair(COLOR_INACTIVE)
        
        for i in range(h):
            for j in range(w):
                window.addch((oy + i), (ox + j), ' ', color)
                
        window.refresh()
        return
    
    def setLEDs(self, leds=[]):
        for led, active in enumerate(leds):
            self.__updateLED(self.__window, led, active, (self.__selected == led))
        self.__stdscr.refresh()
        return
    
