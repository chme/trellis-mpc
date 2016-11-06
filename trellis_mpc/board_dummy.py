#!/usr/bin/env python
#
# Licensed under the BSD license. See full license in LICENSE file.
#
# Author: Christian Meffert

from sys import stdin
from sys import stdout

class BoardDummy:
    
    def __init__(self):
        self.__board = ['.', '.', '.', '.', '.', '.', '.', '.',\
                        '.', '.', '.', '.', '.', '.', '.', '.',\
                        '.', '.', '.', '.', '.', '.', '.', '.',\
                        '.', '.', '.', '.', '.', '.', '.', '.',\
                        '.', '.', '.', '.', '.', '.', '.', '.',\
                        '.', '.', '.', '.', '.', '.', '.', '.',\
                        '.', '.', '.', '.', '.', '.', '.', '.',\
                        '.', '.', '.', '.', '.', '.', '.', '.']
        return
    
    def initialize(self):
        self.printBoard()
        return
    
    def getPressedButtons(self):
        userinput = stdin.readline()
        pressed = []
        for idx in userinput.split(','):
            try:
                self.__board[int(idx)] = 'P'
                pressed.append(int(idx))
            except ValueError:
                pass
        return pressed
    
    def setLEDs(self, leds=[]):
        
        for led, active in enumerate(leds):
            if active == 0:
                if self.__board[led] == 'P':
                    self.__board[led] = '_'
                else:
                    self.__board[led] = '.'
            else:
                if self.__board[led] == 'P':
                    self.__board[led] = '#'
                else:
                    self.__board[led] = '*'
        
        self.printBoard()
        return
    
    def printBoard(self):
        stdout.write("   _________   \n")
        for i in range(len(self.__board)):
            if i % 8 == 0:
                stdout.write(str(i).zfill(2) + ' ')
            if i % 8 == 4:
                stdout.write(' ')
            stdout.write(self.__board[i])
            if i % 8 == 7:
                stdout.write(' ' + str(i).zfill(2) + "\n")
        stdout.write("   _________   \n")
        
        stdout.flush()
        return
            