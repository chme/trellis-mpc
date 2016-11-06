#!/usr/bin/env python
#
# Licensed under the BSD license. See full license in LICENSE file.
#
# Author: Christian Meffert

import app_mpc
import app_viz_spectrum
import board_dummy
import time

trellis = board_dummy.BoardDummy()

available = [app_mpc.AppMpc(), app_viz_spectrum.AppVizSpectrum()]
active_idx = 0
active = available[active_idx]

print "Press Ctrl-C to quit"

trellis.initialize()

while True:
    time.sleep(0.05)
    buttons = trellis.getPressedButtons()
    
    if 0 in buttons:
        active_idx = (active_idx + 1) % len(available)
        active = available[active_idx]
        
    trellis.setLEDs(active.tick(buttons))