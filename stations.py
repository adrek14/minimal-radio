
from radio import Radio

stations = [
    Radio.Station(
        "ESKA Rock",
        "http://www.radio.pionier.net.pl/stream.pls?radio=eskarockmp3",
        "eskarock.xpm"),
    Radio.Station(
        "Radio Wroclaw",
        "http://www.radio.pionier.net.pl/stream.pls?radio=prwroclaw",
        "prw.xpm", 
        ["-demuxer", "ogg"]),
    Radio.Station(
        "Program 3",
        "rtmp://stream85.polskieradio.pl/live/pr3.sdp",
        "pr3.xpm"),
    Radio.Station(
        "Program 4",
        "rtmp://stream85.polskieradio.pl/live/pr4.sdp",
        "pr4.xpm"),
    Radio.Station(
        "Zlote Przeboje",
        "http://poznan7.radio.pionier.net.pl:8000/tuba9-1.mp3",
        "zlote.xpm",
        ["-softvol", "-volume", "40"]),
    Radio.Station(
        "Chilli Zet",
        "http://www.chillizet.pl/externals/chillizet-streams/chillizetmp3.pls",
        "chilli.xpm",
        ["-softvol", "-volume", "60", "-playlist"]),
    Radio.Station(
        "OpenFM: Ballady",
        "rtmp://91.197.14.46:80/shoutcast/20",
        "openfm.xpm")]
