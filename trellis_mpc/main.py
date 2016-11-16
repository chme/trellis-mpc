#!/usr/bin/env python
#
# Licensed under the BSD license. See full license in LICENSE file.
#
# Author: Christian Meffert

try:
    import config
except ImportError:
    print "Missing config.py file, create one by copying and editing config_template.py"
    raise

import app_mpc
import app_viz_spectrum
from board_dummy import BoardDummy
from board_curses import BoardCurses
import sys
import time

try:
    from board_trellis import BoardTrellis
except ImportError:
    class BoardTrellis:
        def __init__(self):
            print "Failed to load trellis module"
            raise

    
if len(sys.argv) > 1 and sys.argv[1] == 'curses':
    board = BoardCurses()
elif len(sys.argv) > 1 and sys.argv[1] == 'trellis':
    board = BoardTrellis()
else:
    board = BoardDummy()

available = [app_mpc.AppMpc(), app_viz_spectrum.AppVizSpectrum()]
active_idx = 0
active = available[active_idx]

board.initialize()

while True:
    time.sleep(config.SLEEP_TIME_BETWEEN_TICKS)
    buttons = board.getPressedButtons()
    
    if 0 in buttons or active.deactivateNextTick():
        active_idx = (active_idx + 1) % len(available)
        active = available[active_idx]
        
    board.setLEDs(active.tick(buttons))


