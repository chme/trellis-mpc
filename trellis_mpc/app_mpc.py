#!/usr/bin/env python
#
# Licensed under the BSD license. See full license in LICENSE file.
#
# Author: Christian Meffert

import config
import mpd
from select import select


class AppMpcError(Exception):
    """Fatal error"""

class AppMpc:
    def __init__(self):
        self.__connected = False
        self.__retries = 0
        self.__retry_skip = 0
        self.__skip_ticks_before_retry = int(config.MPD_SECONDS_TO_WAIT_BEFORE_RETRY / config.SLEEP_TIME_BETWEEN_TICKS)
        self.__number_of_ticks_playing = 0
        self.__deactive_after_ticks_playing = int(config.MPD_SECONDS_PLAYING_BEFORE_VIZ / config.SLEEP_TIME_BETWEEN_TICKS)
        
        self.__status = {}
        self.__outputs = []
        self.__idle = mpd.MPDClient()
        
        self.__leds = [0] * 64
        self.__actions = {}
        
        ''' First row (1): 0..7 '''
        self.__actions[4] = [self.__outputvolume, 'Badezimmer', 100]
        self.__actions[5] = [self.__outputvolume, 'Wohnzimmer', 100]
        self.__actions[5] = [self.__outputvolume, 'Kueche', 100]
        self.__actions[7] = [self.__setvol, 100]
        
        ''' Row (2): 8..15 '''
        self.__actions[12] = [self.__outputvolume, 'Badezimmer', 84]
        self.__actions[13] = [self.__outputvolume, 'Wohnzimmer', 84]
        self.__actions[14] = [self.__outputvolume, 'Kueche', 84]
        self.__actions[15] = [self.__setvol, 84]
        
        ''' Row (3): 16..23 '''
        self.__actions[20] = [self.__outputvolume, 'Badezimmer', 70]
        self.__actions[21] = [self.__outputvolume, 'Wohnzimmer', 70]
        self.__actions[22] = [self.__outputvolume, 'Kueche', 70]
        self.__actions[23] = [self.__setvol, 70]
        
        ''' Row (4): 24..31 '''
        self.__actions[28] = [self.__outputvolume, 'Badezimmer', 56]
        self.__actions[29] = [self.__outputvolume, 'Wohnzimmer', 56]
        self.__actions[30] = [self.__outputvolume, 'Kueche', 56]
        self.__actions[31] = [self.__setvol, 56]
        
        ''' Row (5): 32..39 '''
        self.__actions[32] = [self.__addid, 'http:/Deutschlandradio Kultur']
        self.__actions[33] = [self.__addid, 'http:/Deutschlandfunk']
        self.__actions[34] = [self.__addid, 'http:/DRadio Wissen']
        #self.__actions[35] = [self.__addid, 'http:/DRadio Wissen']
        self.__actions[36] = [self.__outputvolume, 'Badezimmer', 42]
        self.__actions[37] = [self.__outputvolume, 'Wohnzimmer', 42]
        self.__actions[38] = [self.__outputvolume, 'Kueche', 42]
        self.__actions[39] = [self.__setvol, 42]
        
        ''' Row (6): 40..47 '''
        self.__actions[40] = [self.__addid, 'http:/RADIO BOB! Alternativ Rock']
        self.__actions[41] = [self.__addid, 'http:/laut.fm/bizarre-radio']
        self.__actions[42] = [self.__addid, 'http:/ByteFM']
        #self.__actions[43] = [self.__addid, 'http:/ByteFM']
        self.__actions[44] = [self.__outputvolume, 'Badezimmer', 28]
        self.__actions[45] = [self.__outputvolume, 'Wohnzimmer', 28]
        self.__actions[46] = [self.__outputvolume, 'Kueche', 28]
        self.__actions[47] = [self.__setvol, 28]
        
        ''' Row (7): 48..55 '''
        self.__actions[48] = [self.__load, 'spotify:/Dein Mix der Woche (spotifydiscover)']
        self.__actions[49] = [self.__load, 'spotify:/ROCK Brandneu (spotify_germany)']
        self.__actions[50] = [self.__load, 'spotify:/Indie Radar (spotify_germany)']
        #self.__actions[51] = [self.__load, 'spotify:/Indie Radar (spotify_germany)']
        self.__actions[52] = [self.__outputvolume, 'Badezimmer', 14]
        self.__actions[53] = [self.__outputvolume, 'Wohnzimmer', 14]
        self.__actions[54] = [self.__outputvolume, 'Kueche', 14]
        self.__actions[55] = [self.__setvol, 14]

        ''' Last row (8): 56..63 '''
        self.__actions[56] = [self.__playpause]
        self.__actions[57] = [self.__previous]
        self.__actions[58] = [self.__next]
        #self.__actions[59] = [self.__stop]
        self.__actions[60] = [self.__toggleoutput, 'Badezimmer']
        self.__actions[61] = [self.__toggleoutput, 'Wohnzimmer']
        self.__actions[62] = [self.__toggleoutput, 'Kueche']
        self.__actions[63] = [self.__playpause]
        
        return
    
    def deactivateNextTick(self):
        if self.__number_of_ticks_playing > self.__deactive_after_ticks_playing:
            self.__number_of_ticks_playing = 0
            return True
        return False
    
    def tick(self, pressedButtons=[]):
        if not self.__connected:
            if not self.__connect():
                return [0] * 64
            pass
        
        if not self.__updateStatus():
            return [0] * 64
        
        for button in pressedButtons:
            self.__processPressedButton(button)
        
        if len(pressedButtons) > 0:
            self.__number_of_ticks_playing = 0
        else:
            self.__number_of_ticks_playing += 1
        
        return self.__leds
    
    def __updateStatus(self):
        try:
            idle_can_read = select([self.__idle], [], [], 0)[0]
            if idle_can_read:
                changes = self.__idle.fetch_idle()
                if changes:
                    self.__status = self.__idle.status()
                    self.__outputs = self.__idle.outputs()
                    self.__idle.send_idle("player", "mixer", "output")
                    self.__updateLEDs()
            return True
        except (mpd.MPDError, IOError):
            self.__disconnect()
        
        return False

    def __updateLEDs(self):
        self.__leds = [0] * 64
        
        if self.__isPlaying():
            self.__leds[56] = 1
            self.__leds[63] = 1
            
            vol = int(self.__status['volume'])
            self.__leds[7]  = int(vol > 84)
            self.__leds[15] = int(vol > 70)
            self.__leds[23] = int(vol > 56)
            self.__leds[31] = int(vol > 42)
            self.__leds[39] = int(vol > 28)
            self.__leds[47] = int(vol > 14)
            self.__leds[55] = int(vol > 0)
            
            output = self.__getOutput('Kueche')
            if output != None:
                vol = int(output['outputvolume'])
                self.__leds[6]  = int(vol > 84)
                self.__leds[14] = int(vol > 70)
                self.__leds[22] = int(vol > 56)
                self.__leds[30] = int(vol > 42)
                self.__leds[38] = int(vol > 28)
                self.__leds[46] = int(vol > 14)
                self.__leds[54] = int(vol > 0)
                self.__leds[62] = int(output['outputenabled'])
        
            output = self.__getOutput('Wohnzimmer')
            if output != None:
                vol = int(output['outputvolume'])
                self.__leds[5]  = int(vol > 84)
                self.__leds[13] = int(vol > 70)
                self.__leds[21] = int(vol > 56)
                self.__leds[29] = int(vol > 42)
                self.__leds[37] = int(vol > 28)
                self.__leds[45] = int(vol > 14)
                self.__leds[53] = int(vol > 0)
                self.__leds[61] = int(output['outputenabled'])
        
            output = self.__getOutput('Badezimmer')
            if output != None:
                vol = int(output['outputvolume'])
                self.__leds[4] = int(vol > 84)
                self.__leds[12] = int(vol > 70)
                self.__leds[20] = int(vol > 56)
                self.__leds[28] = int(vol > 42)
                self.__leds[36] = int(vol > 28)
                self.__leds[44] = int(vol > 14)
                self.__leds[52] = int(vol > 0)
                self.__leds[60] = int(output['outputenabled'])
        return
    
    def __processPressedButton(self, button):
        if not self.__actions.has_key(button):
            return
        
        try:
            client = mpd.MPDClient()
            client.connect(config.MPD_HOST, config.MPD_PORT)
        
            action = self.__actions[button]
            action[0](client, action[1:])
                
            client.disconnect()
        except (mpd.MPDError, IOError):
            pass
            
        return
    
    def __isPlaying(self):
        return self.__status.has_key('state') and self.__status['state'] == 'play'
    
    def __getOutput(self, name):
        for output in self.__outputs:
            if output["outputname"] == name:
                return output
            
        return None
    
    def __playpause(self, client, params):
        if self.__isPlaying():
            client.pause()
        else:
            client.play()
        return
    
    def __play(self, client, params):
        client.play()
        return
        
    def __pause(self, client, params):
        client.pause()
        return
        
    def __previous(self, client, params):
        client.previous()
        return
        
    def __next(self, client, params):
        client.next()
        return
        
    def __setvol(self, client, params):
        client.setvol(params[0])
        return
        
    def __outputvolume(self, client, params):
        output = self.__getOutput(params[0])
        
        if output != None:
            client.outputvolume(int(output['outputid']), params[1])
        return
        
    def __toggleoutput(self, client, params):
        output = self.__getOutput(params[0])
        
        if output != None:
            client.toggleoutput(int(output['outputid']))
        return
        
    def __load(self, client, params):
        client.stop()
        client.clear()
        client.load(params[0])
        client.play()
        return
        
    def __addid(self, client, params):
        client.stop()
        client.clear()
        client.addid(params[0])
        client.play()
        return

    def __connect(self):
        if self.__retries >= config.MPD_MAX_CONNECTION_RETRIES and config.MPD_MAX_CONNECTION_RETRIES > 0:
            raise AppMpcError("Maximum number of retries reached")
        
        if self.__retry_skip > 0:
            self.__retry_skip -= 1
            return False
        
        try:
            self.__idle.connect(config.MPD_HOST, config.MPD_PORT)
            
            self.__connected = True
            self.__retries = 0
            self.__retry_skip = self.__deactive_after_ticks_playing
            
            self.__status = self.__idle.status()
            self.__outputs = self.__idle.outputs()
            self.__idle.send_idle("player", "mixer", "output")
            self.__updateLEDs()
            
            return True

        # Catch socket errors
        except (mpd.MPDError, IOError):
            self.__retries += 1
            self.__retry_skip = self.__deactive_after_ticks_playing
        
        return False
    
    def __disconnect(self):
        self.__connected = False
        
        self.__status = {}
        self.__outputs = []

        # Try to tell MPD we're closing the connection first
        try:
            self.__idle.close()

        # If that fails, don't worry, just ignore it and disconnect
        except (mpd.MPDError, IOError):
            pass

        try:
            self.__idle.disconnect()

        # Disconnecting failed, so use a new client object instead
        # This should never happen.  If it does, something is seriously broken,
        # and the client object shouldn't be trusted to be re-used.
        except (mpd.MPDError, IOError):
            self.__idle = mpd.MPDClient()
        
        return
    