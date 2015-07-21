# Skylight
Skylight is a simple control program for DLP 3D printers initially just for Windows. Support for other OS's will come soon.

It uses [Slic3r](http://slic3r.org/) to slice an stl or obj file into SVG layers. Slic3r is licensed under the GPLv3
https://github.com/alexrj/Slic3r

##Todo
- Clean up code
- Add OpenGL 3D view and manipulation of model before slicing.


##Language
Python 3.x

###Required Python Libraries
- pywin32
- pyserial
- pyopengl (near-future)

###

Download the installer for Python. It will be the default download option  Python-3.4.3.msi
Install for all users
When you reach the customize installation window with a tree menu, click "Add python.exe to path" to enable it
Restart the computer
Press <Start>+R, type in cmd and click run.
type in "pip install pyserial"
Download and install the [pywin32 library](http://sourceforge.net/projects/pywin32/files/pywin32/Build%20219/pywin32-219.win32-py3.4.exe/download)



##License
GPLv3
