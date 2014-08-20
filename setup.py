from distutils.core import setup
#import py2exe

import rtray
#setup(windows=['rtray.py'])

setup(
    name='rtray',
    version=rtray.__version__,
    url='https://github.com/ykmm/rtray',
    author=rtray.__author__,
    author_email=rtray.__email__,
    description=rtray.__doc__,
    packages=['rtray'],
    install_requires=['pycurl',
                      'yaml>=3.10',
                      'wx>=2.8.12.1',
                      ],
    options = {'py2exe': {'bundle_files': 1}},
    windows = [{'script': "rtray.py"}],
    zipfile = None,
)
