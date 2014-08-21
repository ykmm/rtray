from distutils.core import setup
import py2exe

#setup(windows=['rtray.py'])

setup(
    options = {'py2exe': {'bundle_files': 1}},
    windows = [{'script': "rtray.py"}],
    zipfile = None,
)
