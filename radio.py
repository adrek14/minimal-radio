#!/usr/bin/python2.7

#
# GTA-like radio widget
# 
# Requires: 
# - mplayer
# - notify-send (libnotify-bin)
#
# Adrian Lancucki, 25-01-2012
#

import signal
import sys
import os
import errno # XXX ???

from subprocess import check_output

ABS_PATH_REL_TO_SRC = lambda x: os.path.normpath(os.path.join(
                                    os.path.dirname(os.path.abspath(__file__)),
                                    x))

STATION_ICON_DIR = ABS_PATH_REL_TO_SRC('station_icons/')

PIDFILE_PATH = '/tmp/radio-g.pid'

class Radio:

    class Station:
        def __init__(self, name, url, image="", args=[]):
            self.name, self.url = name, url
            self.args = args

            self.image_path = os.path.join(STATION_ICON_DIR, image)
            print self.image_path
            # TODO Check if the file exists.
            # TODO If none or not exists, then assign a default.

    def __init__(self):
        # (name, stream, path_to_image, mplayer_args) 
        self.stations = [self.Station("Radio off", "", "off.xpm"),
            self.Station("ESKA Rock", "http://www.radio.pionier.net.pl/stream.pls?radio=eskarockmp3", "eskarock.xpm"),
            self.Station("Radio Wroclaw", "http://www.radio.pionier.net.pl/stream.pls?radio=prwroclaw", "prw.xpm", ["-demuxer", "ogg"]),
            self.Station("Program 3", "rtmp://stream85.polskieradio.pl/live/pr3.sdp", "pr3.xpm"),
            self.Station("Zlote Przeboje", "http://poznan7.radio.pionier.net.pl:8000/tuba9-1.mp3", "zlote.xpm", ["-softvol", "-volume", "40"]),
            self.Station("Chilli Zet", "http://www.chillizet.pl/externals/chillizet-streams/chillizetmp3.pls", "chilli.xpm", ["-softvol", "-volume", "60", "-playlist"]),
            self.Station("OpenFM: Ballady", "rtmp://91.197.14.46:80/shoutcast/20", "openfm.xpm")]

        self.curr_station_ind, self.spawned_pid = 0, -1
        self.stopped = False
        self.next_station()

    def current_station(self):
        return self.stations[self.curr_station_ind]

    def notify(self, msg, time_ms="700"):
        args = ["notify-send", "-t", time_ms]

        # Append an icon if available.
        if self.current_station().image_path != "":
            args += ["-i", self.current_station().image_path]

        args += [self.current_station().name, msg]
        os.spawnvp(os.P_NOWAIT, "notify-send", args)
        # XXX Popen?

    def clear_station(self):

        # Send SIGINT to the last thread.
        if self.spawned_pid != -1:
            try:
                os.kill(self.spawned_pid, signal.SIGINT)
            except:
                pass
 
    def toggle(self):
        if self.stopped:
            self.connect_station()
        else:
            self.clear_station()
            self.notify("Stopped")
        self.stopped = not self.stopped

    def connect_station(self):
        self.clear_station()

        if self.curr_station_ind == 0:
            self.notify("(Bye bye!)")
            return
        self.notify("Connecting...")
 
        # Fire off the thread & remember it's pid.
        args = ["mplayer"] + self.current_station().args + \
               [self.current_station().url]
        self.spawned_pid = os.spawnvp(os.P_NOWAIT, "mplayer", args)

    def next_station(self):
        self.curr_station_ind += 1
        self.curr_station_ind %= len(self.stations)

        if self.stopped:
            self.notify("Stopped")
        else:
            self.connect_station()

    def shutdown(self):
        print "Shutting down..."
        self.clear_station()
        self.curr_station_ind = 0
        self.notify("(Bye bye!)")
        try:
            os.unlink(PIDFILE_PATH)
        except:
            raise
        exit(0)

def signal_handler(sig, frame):

    if sig == signal.SIGINT or radio.curr_station_ind == len(radio.stations)-1:
        radio.shutdown()
    elif sig == signal.SIGALRM:
        radio.next_station()
    elif sig == signal.SIGUSR1:
        radio.toggle()

if __name__ == "__main__":

    # Find out if there is a pid file
    try:
        pid = int(open(PIDFILE_PATH, "r").read())
    except IOError as e:
        pid = os.getpid()
        file(PIDFILE_PATH, 'w').write(str(pid))

    if os.getpid() != pid:
        if len(sys.argv) > 1 and sys.argv[1] == "-toggle":
            os.kill(pid, signal.SIGUSR1)
        else:
            os.kill(pid, signal.SIGALRM)
    
    else:
        radio = Radio()
    
        signal.signal(signal.SIGALRM, signal_handler) # Connect a station-switching signal.
        signal.signal(signal.SIGUSR1, signal_handler) # Connect a Play/pause signal.
      
        while(True):
            signal.pause()
