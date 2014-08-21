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
                      'pyaml>=3.10'
                      ],
    data_files=[('assets', ['rtray/assets/rtray.ico',
                            'rtray/assets/rtray_alert.ico',
                            'rtray/assets/rtray_blink_on.ico',
                            'rtray/assets/rtray_blink_off.ico',
                            'rtray/assets/rtray_error.ico',
                            'rtray/assets/rtray_idle.ico',
                            'rtray/assets/rtray_load.ico']),
                ('.', ['rtray/rtray.yaml',
                       'rtray/rtray-example.yaml',
                       'rtray/logging.conf'])], 
    #scripts = ['rtray/rtray.py'],  #Install as executable script
    entry_points="""[console_scripts]
    rtray = rtray.rtray:main
    """,
    options = {'py2exe': {'bundle_files': 1}},
    #windows = [{'script': "rtray.py"}],
    #zipfile = None,
)
