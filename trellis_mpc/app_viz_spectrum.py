#!/usr/bin/env python
#
# Licensed under the BSD license. See full license in LICENSE file.
#
# Author: Christian Meffert

"""
FFT code inspired from the code posted here:
https://www.raspberrypi.org/forums/viewtopic.php?p=314087#p314087
https://www.raspberrypi.org/forums/viewtopic.php?p=315444#p315444
https://www.raspberrypi.org/forums/viewtopic.php?p=317839#p317839
http://www.lightshowpi.com/
http://www.instructables.com/id/Raspberry-Pi-Spectrum-Analyzer-with-RGB-LED-Strip-/
"""

import config
import errno
from numpy import abs
from numpy import array
from numpy import delete
from numpy import float32
from numpy import frombuffer
from numpy import fft
from numpy import hanning
from numpy import int16
from numpy import log10
from numpy import log
from numpy import sum
from numpy import zeros
import os


class AppVizSpectrum:
    def __init__(self):
        self.__leds = [0] * 64
        
        self.__window = hanning(0)
        self.__fifo = os.open(config.VIZ_FIFOPATH, os.O_RDONLY | os.O_NONBLOCK)
        
        octaves = (log(config.VIZ_MAX_FREQUENCY / config.VIZ_MIN_FREQUENCY)) / log(2)
        octaves_per_channel = octaves / config.VIZ_NUM_BINS
        
        self.__frequency_limits = []
        self.__frequency_limits.append(config.VIZ_MIN_FREQUENCY)
        for i in range(1, config.VIZ_NUM_BINS + 1):
            self.__frequency_limits.append(self.__frequency_limits[-1]*2**octaves_per_channel)
        
        print "init viz"
        print self.__frequency_limits
        
        return

    def tick(self, pressedButtons=[]):
        print "reading from fifo"
        try:
            data = os.read(self.__fifo, config.VIZ_CHUNK_SIZE)

        except OSError as err:
            print err.errno
            if err.errno == errno.EAGAIN or err.errno == errno.EWOULDBLOCK:
                return [0] * 64
            return [0] * 64
        
        if len(data):
            matrix = self.__calculateLevels(data);
            self.__updateLEDs(matrix)
        
        return self.__leds
    
    def __updateLEDs(self, matrix):
        # this writes out light and color information to a continuous RGB LED
        # strip that's been wrapped around into 5 columns.
        # numbers comes in at 9-15 ish
        for x in range(config.VIZ_NUM_BINS):
            value = (matrix[x] - 9.0) / 5
            if value < 0.1:
                value = 0.0
            elif value > 1.0:
                value = 1.0
            
            value = int(value * 8.0)
            for y in range(config.VIZ_NUM_BINS):
                self.__leds[x + ((7-y) * 8)] = (value > y)
        
        return
    
    def __calculateLevels(self, data):
        #print "calculate levels"
        data_stereo = frombuffer(data, dtype=int16)
        data_mono = array(data_stereo[::2])
        
        if len(data_mono) != len(self.__window):
            self.__window = hanning(len(data_mono)).astype(float32)

        data_mono = data_mono * self.__window
        #print data_mono
        
        if all(data_mono == 0.0):
            return zeros(64, dtype=float32)
        
        # Apply FFT - real data
        fourier = fft.rfft(data_mono)
        
        # Remove last element in array to make it the same size as CHUNK_SIZE
        fourier = delete(fourier, len(fourier) - 1)
    
        # Calculate the power spectrum
        power = abs(fourier) ** 2
        
        sample_rate = 44100
        matrix = [0 for i in range(config.VIZ_NUM_BINS)]
        for i in range(config.VIZ_NUM_BINS):
            # take the log10 of the resulting sum to approximate how human ears perceive sound levels
            matrix[i] = log10(sum(power[self.__piff(self.__frequency_limits[i], sample_rate)
                                              :self.__piff(self.__frequency_limits[i+1], sample_rate):1]))
    
        return matrix
    
    def __piff(self, val, sample_rate):
        '''Return the power array index corresponding to a particular frequency.'''
        return int(config.VIZ_CHUNK_SIZE * val / sample_rate)

