
from radio import Radio

stations = [
    Radio.Station(
        "Program 1",
        "http://stream.polskieradio.pl/program1",
        "pr1.xpm"),
    Radio.Station(
        "Program 3",
        "http://stream.polskieradio.pl/program3",
        "pr3.xpm"),
    Radio.Station(
        "Program 4",
        "http://stream.polskieradio.pl/program4",
        "pr4.xpm"),
    Radio.Station(
        "Radio Wroclaw",
        "http://stream4.nadaje.com:9240/prw",
        # "http://stream4.nadaje.com:9246/prw.ogg",
        "prw.xpm"), 
        # ["-demuxer", "ogg"]),
    Radio.Station(
        "Chilli Zet",
        "http://redir.atmcdn.pl/liveflv/o2/Eurozet/live/chillizet.livx",
        "chilli.xpm"),
    Radio.Station(
        "ESKA Rock",
        "http://s3.deb1.scdn.smcloud.net/t041-1.aac",
        "eskarock.xpm",
        ["-softvol", "-volume", "50"]),
    Radio.Station(
        "Zlote Przeboje",
        "http://poznan7.radio.pionier.net.pl:8000/tuba9-1.mp3",
        "zlote.xpm",
        ["-softvol", "-volume", "40"]),
    Radio.Station(
        "RMF Alternatywa",
        "http://195.150.20.4:8004/ALTERNATYWA",
        "rmfalt.xpm",
        ["-softvol", "-volume", "60"]),
    Radio.Station(
        "RMF Classic",
        "http://195.150.20.4:8004/RMFCLASSIC48",
        "rmfclass.xpm",
        ["-softvol", "-volume", "60"]),
    ]
