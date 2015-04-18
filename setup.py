from distutils.core import setup
import py2exe
import sys


setup(
    name = 'Video2Theora',
    description = """Video2Theora is a small program thats sole purpose is to
    convert any video to the new theora video format for use with firefox 3.1 online
    video.""",
    url = 'http://www.majorsilence.com/apps/',
    version = '0.1',

    # also can try: console, windows = 
    windows = [
        {
            'script': 'v2t_main.py',
            'icon_resources': [(1, "data\majorsilence.ico")],
        }
    ],

    options = {
        'py2exe': {
            'packages':'encodings',
            'includes': 'cairo, pango, pangocairo, atk, gobject, win32api, win32process, subprocess',
        }
    },

    
    data_files=[
        'ffmpeg2theora-0.22-thusnelda.exe',
        'v2t_execute.py',
        'v2t_main.py',
        
        ("data",
            ["data/v2t.glade",
            "data/majorsilence.ico",
            "data/majorsilence128x128.png"
            ]
        ),
        ("docs",
                [
                'docs/license.html',
                ]
        ),
        ("po",
            [
            "po/video2theora.pot",
            "po/v2t.glade.h",
            ]
        ),
    ]
)

