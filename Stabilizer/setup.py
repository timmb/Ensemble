from setuptools import setup
import py2app
import PySide

APP = ['stabilizer.py']
DATA_FILES = []
OPTIONS = {'argv_emulation': False,
			'includes' : 'PySide',
			'resources' : "qt_menu.nib"
			}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)