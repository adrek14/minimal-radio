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
import fcntl

import stations

ABS_PATH_REL_TO_SRC = lambda x: os.path.normpath(os.path.join(
                                    os.path.dirname(os.path.abspath(__file__)),
                                    x))

STATION_ICON_DIR = ABS_PATH_REL_TO_SRC('station_icons/')

PIDFILE_PATH = '/tmp/radio-g.pid'

class PidLock:
    """Provides basic pidfile manipulation (reading, writing),
    uses fcntl to lock it. Upon successfull locking,
    pidfile will be open as long as __del__ or release_lock() was called.
    """

    def __init__(self):
        self.fp = None

    def acquire_lock(self):
        """Attempts to lock the file and write pid (returns True/False)."""

        try:
            self.fp = open(PIDFILE_PATH, 'a+')
        except:
            print "Cannot open pidfile."
            raise

        try:
            fcntl.flock(self.fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            # Somebody else is holding the lock.
            return False
        except:
            print "Cannot lock."
            raise

        self.fp.seek(0)
        self.fp.truncate()
        self.fp.write(str(os.getpid()))
        self.fp.flush()
        self.fp.seek(0)

        return True

    def __del__(self):
        """Releases the resources upon deletion."""
        self.release_lock()

    def release_lock(self):
        """Closes the pidfile, automatically releasing the lock."""

        print "releasing lock"
        if self.fp == None:
            return

        try:
            self.fp.close()
        except:
            pass

    def pidfile_pid(self):
        """Gets pid from an existing pidfile."""

        pid = None
        try:
            pidfile = open(PIDFILE_PATH, 'r')
            pid = pidfile.readline().strip()
            pid = int(pid)
            pidfile.close()
        except IOError:
            print "Cannot read pid from pidfile."
            return None
        except ValueError:
            print "Pidfile doesn't containt a valid pid."
            return None
        except:
            return None

        return pid

class Radio:
    """Radio interface holding the list of stations."""

    class Station:
        """A concrete radio station (online stream)."""

        def __init__(self, name, url, image="", mplayer_args=[]):
            """Mplayer args might, for instance, be used to normalize the volume
            across different streams.
            """
            self.name, self.url = name, url
            self.args = args

            self.image_path = os.path.join(STATION_ICON_DIR, image)
            print self.image_path
            # TODO Check if the file exists.
            # TODO If none or not exists, then assign a default.

    def __init__(self):

        self.stations = [self.Station("Radio off", "", "off.xpm")] + stations.stations

        self.curr_station_ind, self.spawned_pid = 0, -1
        self.stopped = False
        self.next_station()

    def current_station(self):
        return self.stations[self.curr_station_ind]

    def notify(self, msg, time_ms="700"):
        """Sends a notification (through notify-send command)
        about the current station.
        """
        args = ["notify-send", "-t", time_ms]

        # Append an icon if available.
        if self.current_station().image_path != "":
            args += ["-i", self.current_station().image_path]

        args += [self.current_station().name, msg]
        os.spawnvp(os.P_NOWAIT, "notify-send", args)
        # XXX Popen?

    def clear_station(self):
        """Terminates the process associated with the current radio station."""

        # Send SIGINT to the last thread.
        if self.spawned_pid != -1:
            try:
                os.kill(self.spawned_pid, signal.SIGINT)
            except:
                pass
 
    def toggle(self):
        """Stops/plays the stream."""

        if self.stopped:
            self.connect_station()
        else:
            self.clear_station()
            self.notify("Stopped")
        self.stopped = not self.stopped

    def connect_station(self):
        """Attempts to connect to stream using mplayer."""

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
        """Switches to the next station in the list."""

        self.curr_station_ind += 1
        self.curr_station_ind %= len(self.stations)

        if self.stopped:
            self.notify("Stopped")
        else:
            self.connect_station()

    def shutdown(self):
        """Closes open radio stream and notifies about the shutdown."""

        self.clear_station()
        self.curr_station_ind = 0
        self.notify("(Bye bye!)")

def signal_handler(sig, frame):
    """Supported signals:
        SIGINT - shutdown
        SIGALRM - next station
        SIGUSR1 - toggle play/stop
    """

    if sig == signal.SIGINT or radio.curr_station_ind == len(radio.stations)-1:
        radio.shutdown()
        try:
            os.unlink(PIDFILE_PATH)
        except:
            raise
        sys.exit(0)

    elif sig == signal.SIGALRM:
        radio.next_station()

    elif sig == signal.SIGUSR1:
        radio.toggle()

if __name__ == "__main__":

    pidlock = PidLock()

    if pidlock.acquire_lock():
        radio = Radio()
    
        signal.signal(signal.SIGALRM, signal_handler) # Connect a station-switching signal.
        signal.signal(signal.SIGUSR1, signal_handler) # Connect a Play/pause signal.

        while(True):
            signal.pause()

    else:
        pid = pidlock.pidfile_pid()

        if pid == None:
            sys.exit(1)

        if len(sys.argv) > 1 and sys.argv[1] == "-toggle":
            os.kill(pid, signal.SIGUSR1)
        else:
            os.kill(pid, signal.SIGALRM)

