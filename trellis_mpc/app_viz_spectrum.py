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
        
        self.__number_of_ticks_idle = 0
        self.__deactive_after_ticks_idle = int(config.VIZ_SECONDS_IDLE / config.SLEEP_TIME_BETWEEN_TICKS)
        
        self.__window = hanning(0)
        self.__fifo = os.open(config.VIZ_FIFOPATH, os.O_RDONLY | os.O_NONBLOCK)
        
        octaves = (log(config.VIZ_MAX_FREQUENCY / config.VIZ_MIN_FREQUENCY)) / log(2)
        octaves_per_channel = octaves / config.VIZ_NUM_BINS
        
        self.__frequency_limits = []
        self.__frequency_limits.append(config.VIZ_MIN_FREQUENCY)
        for i in range(1, config.VIZ_NUM_BINS + 1):
            self.__frequency_limits.append(self.__frequency_limits[-1]*2**octaves_per_channel)
            
        sample_rate = 44100
        self.__piff = []
        for freqlim in self.__frequency_limits:
            self.__piff.append(self.__calcPiff(freqlim, sample_rate))
        
        return

    def tick(self, pressedButtons=[]):
        # Deactivate viz if a button was pressed
        if len(pressedButtons) > 0:
            self.__number_of_ticks_idle = self.__deactive_after_ticks_idle + 1
            return [0] * 64
        
        try:
            data = os.read(self.__fifo, config.VIZ_CHUNK_SIZE)
            if len(data):
                matrix = self.__calculateLevels(data);
                self.__updateLEDs(matrix)
                self.__number_of_ticks_idle = 0
            return self.__leds
        
        except OSError:
            self.__leds = [0] * 64
        
        self.__number_of_ticks_idle += 1
        return self.__leds
    
    def deactivateNextTick(self):
        if self.__number_of_ticks_idle > self.__deactive_after_ticks_idle:
            self.__number_of_ticks_idle = 0
            return True
        return False

    def __updateLEDs(self, matrix):
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
        
        matrix = [0 for i in range(config.VIZ_NUM_BINS)]
        for i in range(config.VIZ_NUM_BINS):
            # take the log10 of the resulting sum to approximate how human ears perceive sound levels
            matrix[i] = log10(sum(power[self.__piff[i] :self.__piff[i+1] :1]))
    
        return matrix
    
    def __calcPiff(self, val, sample_rate):
        '''Return the power array index corresponding to a particular frequency.'''
        return int(config.VIZ_CHUNK_SIZE * val / sample_rate)

