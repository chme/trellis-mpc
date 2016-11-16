#!/usr/bin/env python
#
# Licensed under the BSD license. See full license in LICENSE file.
#
# Author: Christian Meffert

''' Time to sleep before executing the next tick (loop) '''
SLEEP_TIME_BETWEEN_TICKS = 0.05

MPD_HOST = 'localhost'
MPD_PORT = 6600

''' Maximum number of connection attempts to the mpd server (set to < 0 for unlimited attempts) '''
MPD_MAX_CONNECTION_RETRIES = -1
''' Number of seconds to wait between to connection attempts to the mpd server '''
MPD_SECONDS_TO_WAIT_BEFORE_RETRY = 3
''' Number of seconds of no action and player is playing before activating the visualizer '''
MPD_SECONDS_PLAYING_BEFORE_VIZ = 5

VIZ_FIFOPATH = '/home/asiate/daapd-fifo'
VIZ_CHUNK_SIZE = 2048
VIZ_NUM_BINS = 8
VIZ_MIN_FREQUENCY = 10
VIZ_MAX_FREQUENCY = 8000
VIZ_SECONDS_IDLE = 5
