#!/usr/bin/python

#
# GTA-like radio widget
# 
# Requires: 
# - mplayer
# - notify-send (libnotify-bin)
#
# Adrian Lancucki, 25-01-2012
#

# TODO terminate (SIGINT) feature
# TODO all above passed as commandline args
# FIXME race condition when stopping not connected stream

import signal
import sys
import os

pidfile = "/tmp/radio-g.pid"

class Radio:

  class Station:

    def __init__(self, name, url, image="", args=[]):
      self.name, self.url, self.image, self.args = name, url, image, args

  # (name, stream, path_to_image, mplayer_args) 
  stations = [Station("Radio off", "", "off.xpm"),
              ("ESKA Rock", "http://www.radio.pionier.net.pl/stream.pls?radio=eskarockmp3", "eskarock.xpm"),
              ("Radio Wroclaw", "http://www.radio.pionier.net.pl/stream.pls?radio=prwroclaw", "prw.xpm", "ogg"),
              ("Program 3", "rtmp://stream85.polskieradio.pl/live/pr3.sdp", "pr3.xpm"),
              ("Zlote Przeboje", "http://poznan7.radio.pionier.net.pl:8000/tuba9-1.mp3", "zlote.xpm", "-softvol", "-volume", "70"),
              ("Chilli Zet", "http://www.chillizet.pl/externals/chillizet-streams/chillizetmp3.pls", "chilli.xpm", "-playlist"),
              ("OpenFM: Ballady", "rtmp://91.197.14.46:80/shoutcast/20", "openfm.xpm")]

  def __init__(self):
    self.working_dir = os.path.dirname(os.path.realpath(__file__))+"/"
    self.station, self.spawned_pid = 0, -1
    self.stopped = False
    self.next_station()

  def notify(self, msg, time_ms="500"):
    args = ["notify-send", "-t", time_ms]

    # Append an icon if available.
    if self.stations[self.station][3] != "":
      args += ["-i", self.working_dir+self.stations[self.station][3]]

    args += [self.stations[self.station][0], msg]
    os.spawnvp(os.P_NOWAIT, "notify-send", args)

  def clear_station(self):

    # Send SIGINT to the last thread.
    if self.spawned_pid != -1:
      try:
        os.kill(self.spawned_pid, signal.SIGINT)
      except:
        skip
 
  def toggle(self):
    if self.stopped:
      self.connect_station()
      self.stopped = False
    else:
      self.clear_station()
      self.notify("Stopped")
      self.stopped = True

  def connect_station(self):
    self.clear_station()

    if self.station == 0:
      self.notify("(Bye bye!)")
      return
    self.notify("Connecting...")
 
    # Fire off the thread & remember it's pid.
    args = ["mplayer"]
    if self.stations[self.station][1] == "ogg":
      args += ["-demuxer", "ogg"]
    elif self.stations[self.station][2][-4:] == ".pls":
      args += ["-playlist"]

    args.append(self.stations[self.station][2])
    self.spawned_pid = os.spawnvp(os.P_NOWAIT, "mplayer", args)

  def next_station(self):
    self.station = (self.station + 1) % len(self.stations)
    self.connect_station()

  def shutdown(self):
    print "Shutting down..."
    self.clear_station()
    self.station = 0
    self.notify("(Bye bye!)")
    try:
      os.system("rm /tmp/radio-g.pid") # XXX
    except:
      skip
    exit(0)

def signal_handler(sig, frame):

  if sig == signal.SIGINT or radio.station == len(radio.stations)-1:
    radio.shutdown()
  elif sig == signal.SIGALRM:
    radio.next_station()
  elif sig == signal.SIGUSR1:
    radio.toggle()
  
# Find out if there is a pid file
try:
  pid = int(open(pidfile, "r").read())
except IOError as e:
  pid = os.getpid()
  file(pidfile, 'w').write(str(pid))

if os.getpid() != pid:
  if len(sys.argv) > 1 and sys.argv[1] == "-toggle":
    os.kill(pid, signal.SIGUSR1)
  else:
    os.kill(pid, signal.SIGALRM)

else:
  radio = Radio()

  # Connect the signal handlers.
  signal.signal(signal.SIGALRM, signal_handler) # Station-switching signal.
  signal.signal(signal.SIGUSR1, signal_handler) # Play/pause signal.
  
  while(True):
    signal.pause()
