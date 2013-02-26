#!/usr/bin/python2.7

# gta-like-radio - Radio stream player with a cyclic interface.
#
# Copyright (C) 2013 Adrian Lancucki
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import signal
import sys
import os
import errno

from subprocess import check_output

ABS_PATH_REL_TO_SRC = lambda x: os.path.normpath(os.path.join(
                                    os.path.dirname(os.path.abspath(__file__)),
                                    x))

STATION_ICON_DIR = ABS_PATH_REL_TO_SRC('station_icons/')

PIDFILE_PATH = '/tmp/radio-g.pid'

class PidLock:

    @staticmethod
    def acquire_lock():
        
        fd = None
        for attempt_num in range(2):
        
            try:
                fd = os.open(PIDFILE_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                break
            except OSError, e:
                if e.errno != errno.EEXIST:
                    raise
                # There was a pid file with no corresponding process.
                # Someone has created a pidfile in the meantime.
                if attempt_num == 1:
                    raise
        
            # Opening failed in the first loop; check if the old process is running.
            old_pid = PidLock.get_pidfile_pid()
        
            if PidLock.is_running_with_pid(old_pid):
                return (False, old_pid)
                    
            try:
                os.unlink(PIDFILE_PATH)
            except:
                # The process is not running.
                raise
        
        # If got here, then the fd was safely acquired.
        # Write pid. Save.
        try:
            new_pid = os.getpid()
            os.write(fd, str(new_pid))
            os.close(fd)
        except:
            raise
        
        return (True, new_pid)

    @staticmethod
    def is_running_with_pid(pid):

        ret = check_output(
                  'ps up '+str(pid)+' >/dev/null && echo "1" || echo "0"',
                  shell=True)

        return True if ret.rstrip() == "1" else False

    @staticmethod
    def get_pidfile_pid():

        try: 
            fd = os.open(PIDFILE_PATH, os.O_RDWR)
            pid = os.read(fd, 1024).strip()
            os.close(fd)
        except:
            return -1

        try:
            return int(pid)
        except ValueError:
            return -1

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

    (lock_acquired, pid) = PidLock.acquire_lock()

    if lock_acquired:
        radio = Radio()
    
        signal.signal(signal.SIGALRM, signal_handler) # Connect a station-switching signal.
        signal.signal(signal.SIGUSR1, signal_handler) # Connect a Play/pause signal.

        while(True):
            signal.pause()
    else:
        if len(sys.argv) > 1 and sys.argv[1] == "-toggle":
            os.kill(pid, signal.SIGUSR1)
        else:
            os.kill(pid, signal.SIGALRM)

    sys.exit(0)

