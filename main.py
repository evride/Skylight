import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import subprocess
import os
import re
import serial
from serial.tools.list_ports import comports
from threading import *
from utils import *
from LayerView import LayerView
from Object3dView import Object3dView
from PrintHandler import PrintHandler
from GCodePane import *
from Configuration import *
from PrinterSetup import *
import math

class ObjectPane(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setupUi()
    def setupUi(self):
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        
        self.viewPanel = QtWidgets.QTabWidget(self)
        self.viewPanel.setTabPosition(QtWidgets.QTabWidget.South)
        self.viewPanel.setElideMode(QtCore.Qt.ElideNone)
        
        self.listContainer = QtWidgets.QWidget()
        self.listContainer.setMaximumSize(360, 10000)
        self.addObjectBtn = QtWidgets.QPushButton()
        self.addObjectBtn.setText("Add Object")
        self.objectList = QtWidgets.QListWidget(self.listContainer)
        
        
        self.view3D = Object3dView()
        self.viewLayer = LayerView()
        
        self.viewPanel.addTab(self.view3D, "3D View")
        self.viewPanel.addTab(self.viewLayer, "Layer View")
        
        self.layout.addWidget(self.viewPanel)
        self.layout.addWidget(self.listContainer)
        
        listLayout = QtWidgets.QVBoxLayout(self.listContainer)
        
        listLayout.addWidget(self.addObjectBtn)
        listLayout.addWidget(self.objectList)
        
        self.addObjectBtn.clicked.connect(self.addObject)
    def addObject(self, event):
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', None, "*.obj;*.stl")
        
        if (len(fname[0])):
            _path, _tail = os.path.split(fname[0])
            self.objectList.addItem(_tail)
            self.view3D.addObject(fname[0])
            #sliceFile(fname[0], 0.1, self.svgCreated)
            self.thread = SliceThread()
            self.thread.done.connect(self.svgCreated)
            self.thread.sliceCommand("{0}/slic3r/slic3r.exe \"{1}\" --layer-height={2} --export-svg --output=\"{3}temp.svg\"".format(currentDir(), fname[0], 0.1, appdataDir()))
            self.thread.start()
        
    def svgCreated(self):
        handler = PrintHandler()
        handler.openFile("{0}temp.svg".format(appdataDir()))
        self.viewLayer.drawLayer(handler.getLayer(3))
    
class SliceThread( QtCore.QThread ):
    done = QtCore.pyqtSignal()
    def __init__( self):
        QtCore.QThread.__init__( self )
    def sliceCommand(self, str):
        self.command = str
    def run( self ):
        subprocess.call(self.command)
        self.done.emit()
        

        


        
class PrintSettingsPane(QtWidgets.QWidget):
    def __init__(self):    
        QtWidgets.QWidget.__init__(self)
        self.setupUi()
    def setupUi(self):
        
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        
        self.labelLayerHeight = QtWidgets.QLabel("Layer Height (mm)")
        self.inputLayerHeight = QtWidgets.QDoubleSpinBox(suffix="mm", maximum=10, minimum=0, singleStep=0.05)
        
        self.labelExposureTime = QtWidgets.QLabel("Exposure Time (s)")
        self.inputExposureTime = QtWidgets.QDoubleSpinBox(suffix="s", decimals=3, maximum=100, minimum=0, singleStep=0.1)
        
        self.labelStartingExposureTime = QtWidgets.QLabel("Starting Exposure Time (s)")
        self.inputStartingExposureTime = QtWidgets.QDoubleSpinBox(suffix="s", decimals=3, maximum=100, minimum=0, singleStep=0.1)
        
        self.labelStartingLayers = QtWidgets.QLabel("Starting Layers")
        self.inputStartingLayers = QtWidgets.QSpinBox(maximum=100, minimum=0)
        
        self.labelPreExposurePause = QtWidgets.QLabel("Pre-Exposure Pause (s)")
        self.inputPreExposurePause = QtWidgets.QDoubleSpinBox(suffix="s", maximum=100, minimum=0, singleStep=0.1)
        
        self.labelPostExposurePause = QtWidgets.QLabel("Post Exposure Pause (s)")
        self.inputPostExposurePause = QtWidgets.QDoubleSpinBox(suffix="s", maximum=100, minimum=0, singleStep=0.1)
        
        self.labelRetractDistance = QtWidgets.QLabel("Z-Retract Distance (mm)")
        self.inputRetractDistance = QtWidgets.QDoubleSpinBox(suffix="mm", decimals=1, maximum=20000, minimum=0, singleStep=50)
        
        self.labelRetractSpeed = QtWidgets.QLabel("Z-Retract Speed (mm/min)")
        self.inputRetractSpeed = QtWidgets.QSpinBox(suffix="mm/min", maximum=500, minimum=0, singleStep=50)
        
        self.labelReturnSpeed = QtWidgets.QLabel("Z-Return Speed (mm/min)")
        self.inputReturnSpeed = QtWidgets.QSpinBox(suffix="mm/min", maximum=500, minimum=0, singleStep=50)
        
        
        self.layout.addWidget(self.labelLayerHeight)
        self.layout.addWidget(self.inputLayerHeight)
        self.layout.addWidget(self.labelExposureTime)
        self.layout.addWidget(self.inputExposureTime)
        self.layout.addWidget(self.labelStartingExposureTime)
        self.layout.addWidget(self.inputStartingExposureTime)
        self.layout.addWidget(self.labelPreExposurePause)
        self.layout.addWidget(self.inputPreExposurePause)
        self.layout.addWidget(self.labelPostExposurePause)
        self.layout.addWidget(self.inputPostExposurePause)
        self.layout.addWidget(self.labelRetractDistance)
        self.layout.addWidget(self.inputRetractDistance)
        self.layout.addWidget(self.labelRetractSpeed)
        self.layout.addWidget(self.inputRetractSpeed)
        self.layout.addWidget(self.labelReturnSpeed)
        self.layout.addWidget(self.inputReturnSpeed)
        
        
        
class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setupUi(self)
    def setupUi(self, Form):
        global app
        Form.resize(640, 480)
        
        Form.setWindowTitle("Skylight")
        
        self.layout = QtWidgets.QHBoxLayout(Form)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.mainTabs = QtWidgets.QTabWidget()
        self.objectTab = ObjectPane()
        self.configurationTab  = PrinterSetup(app)
        self.printSettingsTab = PrintSettingsPane()
        self.gcodeTab = GCodePane()
        self.logTab = QtWidgets.QWidget()
        
        self.mainTabs.addTab(self.objectTab, "Object")
        self.mainTabs.addTab(self.configurationTab, "Configuration")
        self.mainTabs.addTab(self.printSettingsTab, "Print Settings")
        self.mainTabs.addTab(self.gcodeTab, "Custom GCode")
        self.mainTabs.addTab(self.logTab, "Log")
        
        
        self.layout.addWidget(self.mainTabs)
        
        

    def retranslateUi(self, Form):
        print("iono")

app = QtWidgets.QApplication(sys.argv)
app.config = Configuration()

if os.path.isfile("app.css"):
    app.setStyleSheet(open('app.css', 'r').read())


form = MainWindow()
form.show()

app_icon = QtGui.QIcon()
app_icon.addFile('icons/favicon16.png', QtCore.QSize(16,16))
app_icon.addFile('icons/favicon32.png', QtCore.QSize(32,32))
app_icon.addFile('icons/favicon64.png', QtCore.QSize(64,64))
app_icon.addFile('icons/favicon128.png', QtCore.QSize(128,128))
app_icon.addFile('icons/favicon256.png', QtCore.QSize(256,256))
app.setWindowIcon(app_icon)

desktop = app.desktop()


sys.exit(app.exec_())