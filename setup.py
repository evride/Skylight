import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    'include_files':['Slic3r', 'favicon.png'],
    'include_msvcr': True

}
msi_data = {
    "Shortcut":[
        ("DesktopShortcut",
        "DesktopFolder",
        "Skylight",
        "TARGETDIR",              # Component_
         "[TARGETDIR]skylight.exe",# Target
         None,                     # Arguments
         None,                     # Description
         None,                     # Hotkey
         'favicon.ico',                     # Icon
         None,                     # IconIndex
         None,                     # ShowCmd
         'TARGETDIR'               # WkDir
         ),
         ("ProgramShortcut",
          "ProgramMenuFolder",
          "Skylight",
          "TARGETDIR",              # Component_
         "[TARGETDIR]skylight.exe",# Target
         None,                     # Arguments
         None,                     # Description
         None,                     # Hotkey
         'favicon.ico',                     # Icon
         None,                     # IconIndex
         None,                     # ShowCmd
         'TARGETDIR'               # WkDir
         )
         
        
    ]
}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "Skylight",
        version = "0.21",
        description='Skylight: A Simple DLP 3D printer controller',
        author='Evan Ridenour',
        author_email='eridenour@gmail.com',
        url='https://github.com/evride/Skylight',
        options = {"build_exe": build_exe_options},
        executables = [Executable("main.py", base=base, icon='favicon.ico', targetName="skylight.exe")])