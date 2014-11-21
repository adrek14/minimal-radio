What is it (for)?
-----------------
It's a small python wrapper for `mplayer` and `notify-send`, targeted for Linux (well, any POSIX system with `mplayer` should do). It lets you __play Internet radio streams__ with a __minimalistic interface__ similar to that in the Grand Theft Auto series - a keystroke switches to the next station and displays a small OSD notification.

Nowadays listening to the radio via the Internet is cumbersome - most of the stations force on you custom, flash-based players (presumably because of built-in ads). Fortunately, in most cases raw streams can be sniffed out by examining the network traffic e.g. with [Wireshark](http://www.wireshark.org/).

*TODO: Throw in some links on wireshark sniffing.*

Features
--------
gta-like-radio gives you the simplest interface possible;
* only two commands (next station and play/pause toggle),
* mplayer takes care of handling exotic formats and station-specific settings,
* notify-send tells you what station is on with an optional pretty station icon.

Radio stations (streams' addresses) rarely change, so once you've set it up, you don't have to do anything else.

Aren't enough players out there already?
---------------------------------------
Yes, but they either:
* suck,
* don't play rtmp streams (or choke on some other formats),
* try to blend radio streams and audio files on single playlist,
* need a bunch of resources, partly for a GUI which you don't need for a radio,
* cannot handle per-station settings (like volume),
* cannot have global key shortcuts assigned,
* suck even more.

gta-like-radio aims at making listening to radio stations a painless experience (as it once was with good ol' FM/AM radio receivers).

Setup & usage
-------------
* Get `mplayer` and `notify-send`.
* Assign two keystrokes (with you window manager or a third-party tool) to commands `./radio.py` and `./radio.py -toggle`.
* Put your stations in `stations.py`.
* Optionally, put radio icons (`.xpm` files trailored for `notify-send`) in `gta-like-radio/station_icons/`.
