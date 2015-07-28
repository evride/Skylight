#!/usr/bin/env python
import logging
from win32api import *
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Combobox
from tkinter.ttk import Panedwindow
from tkinter.ttk import Labelframe
from tkinter.ttk import Notebook
from tkinter.ttk import Label
from tkinter.ttk import Separator
from tkinter.ttk import Radiobutton
import subprocess
import os
import re
import serial
from serial.tools.list_ports import comports
from threading import *
import time
from math import *

from utils import *
from PrintWindow import *
from PrintHandler import *
from MonitorConfig import *


root = Tk()
root.wm_title("Skylight")
	
handler = PrintHandler()
config = handler.config
monitors = EnumDisplayMonitors()
monitorList = []
comPortNames = []
comPorts = []
mConfigWindow = None

selectedComPort = handler.config.get('comPort')
selectedComPortIndex = -1
for i in serial.tools.list_ports.comports():
        
    if i[1] == 'n/a':
        comPortNames.append(i[0])
    else:
        comPortNames.append('[' + i[0] + '] - ' + i[1])
    comPorts.append(i)
    
    if selectedComPort == i[0]:
        selectedComPortIndex = len(comPorts) - 1

selectedMonIndex = -1
    
def setupMonitors():
    global selectedMonIndex
    selectedMonInfo = None
    selectedDisplay = handler.config.get('selectedDisplay')
    if selectedDisplay != None:
        selectedMonInfo = handler.config.monitorInfo(selectedDisplay)
    for i in range(len(list(monitors))):
        mX = monitors[i][2][0]
        mY = monitors[i][2][1]
        mW = monitors[i][2][2] - monitors[i][2][0]
        mH = monitors[i][2][3] - monitors[i][2][1]
        if selectedMonInfo != None:
            if int(selectedMonInfo['id']) == int(i) and int(selectedMonInfo['x']) == int(mX) and int(selectedMonInfo['y']) == int(mY) and int(selectedMonInfo['width']) == int(mW) and int(selectedMonInfo['height']) == int(mH):
                selectedMonIndex = i
        monitorList.append("%d : (%dx%d)" % (i, mW, mH) )
setupMonitors()
def load_file():

    filename = filedialog.askopenfilename(filetypes = [('Supported 3D Models', '*.stl;*.obj')])
    if filename: 
        startSlicing(filename)
def startSlicing(filename):
    _path, _tail = os.path.split(filename)
    filenameLabel.config(text=filename)
    statusLabel.config(text="Slicing file " + _tail + "...")
    root.update()
    handler.slicedLayerHeight = handler.config.get('layerHeight')
    handler.slicedFile = filename
    t1 = Thread(target=sliceFile, args=[filename, handler.slicedLayerHeight])
    t1.start()
def sliceFile(filename, layerHeight):
    print(filename, layerHeight)
    print("{0}/slic3r/slic3r.exe {1} --layer-height={2} --export-svg --output={3}temp.svg".format(currentDir(), filename, layerHeight, appdataDir()))
    subprocess.call("{0}/slic3r/slic3r.exe {1} --layer-height={2} --export-svg --output={3}temp.svg".format(currentDir(), filename, layerHeight, appdataDir()))
    sliceComplete()
    statusLabel.config(text="Done")
def sliceComplete():
    handler.openFile(appdataDir() + 'temp.svg')
    viewLayerFrame.setHandler(handler)
    viewLayerFrame.updatePrint()
def start_print():
    if handler.ready():
        handler.showWindow(monitors[monitorSelect.current()][2][0], monitors[monitorSelect.current()][2][1], monitors[monitorSelect.current()][2][2] - monitors[monitorSelect.current()][2][0], monitors[monitorSelect.current()][2][3] - monitors[monitorSelect.current()][2][1] )
        handler.startPrint()
        return
def printNextLayer(evt):
    statusLabel.config(text="Printing layer " + str(handler.currentLayer) + " of " + str(handler.numLayers()))
def printStarted(evt):
    statusLabel.config(text="Print started")
class ZMove(Frame):
    def __init__(self, master, **kwargs):
        Frame.__init__(self, master, **kwargs)
        
        self.moveZ = 0
        self.zSpeed = 0
        self.maxZSpeed = 10
        self.moveMultiplier = 1
        self.motorOn = True
        self.conn = None
        
        self.upFast = Canvas(self, width= 21, height=29)
        self.upFast.create_polygon(10, 13, 19, 28, 1, 28, fill="#333333", outline="#333333")
        self.upFast.create_polygon(10, 7, 19, 22, 1, 22, fill="#666666", outline="#666666")
        self.upFast.create_polygon(10, 1, 19, 16, 1, 16, fill="#999999", outline="#999999")
        
        self.upMed = Canvas(self, width=21, height=23)
        self.upMed.create_polygon(10, 7, 19, 22, 1, 22, fill="#333333", outline="#333333")
        self.upMed.create_polygon(10, 1, 19, 16, 1, 16, fill="#666666", outline="#666666")
        
        self.upSlow = Canvas(self, width=21, height=18)
        self.upSlow.create_polygon(10, 1, 19, 16, 1, 16, fill="#333333", outline="#333333")
        
        self.motorState = Button(self, text="Motor: ON", command=self.motorStateChanged)
        
        self.downSlow = Canvas(self, width=21, height=18)
        self.downSlow.create_polygon(10, 16, 19, 1, 1, 1, fill="#333333", outline="#333333")
        
        self.downMed = Canvas(self, width= 21, height=23)
        self.downMed.create_polygon(10, 16, 19, 1, 1, 1, fill="#333333", outline="#333333")
        self.downMed.create_polygon(10, 22, 19, 7, 1, 7, fill="#666666", outline="#666666")
        
        
        self.downFastBtn = Button(width=30, height=30)
        
        self.downFast = Canvas(self, width= 21, height=29)
        self.downFast.create_polygon(10, 16, 19, 1, 1, 1, fill="#333333", outline="#333333")
        self.downFast.create_polygon(10, 22, 19, 7, 1, 7, fill="#666666", outline="#666666")
        self.downFast.create_polygon(10, 28, 19, 13, 1, 13, fill="#999999", outline="#999999")
        
        self.downFast.bind('<Button-1>', self.buttonPressed)
        self.downMed.bind('<Button-1>', self.buttonPressed)
        self.downSlow.bind('<Button-1>', self.buttonPressed)
        self.upFast.bind('<Button-1>', self.buttonPressed)
        self.upMed.bind('<Button-1>', self.buttonPressed)
        self.upSlow.bind('<Button-1>', self.buttonPressed)
        
        self.downFast.bind('<ButtonRelease-1>', self.buttonReleased)
        self.downMed.bind('<ButtonRelease-1>', self.buttonReleased)
        self.downSlow.bind('<ButtonRelease-1>', self.buttonReleased)
        self.upFast.bind('<ButtonRelease-1>', self.buttonReleased)
        self.upMed.bind('<ButtonRelease-1>', self.buttonReleased)
        self.upSlow.bind('<ButtonRelease-1>', self.buttonReleased)
    def showButtons(self):
        
        self.upFast.pack()
        self.upMed.pack()
        self.upSlow.pack()
        self.motorState.pack()
        self.downSlow.pack()
        self.downMed.pack()
        self.downFast.pack()
    def hideButtons(self):
        
        self.upFast.pack_forget()
        self.upMed.pack_forget()
        self.upSlow.pack_forget()
        self.motorState.pack_forget()
        self.downSlow.pack_forget()
        self.downMed.pack_forget()
        self.downFast.pack_forget()
    def setConnection(self, conn):
        self.conn = conn
        self.conn.bind('move-complete', self.update)
    def buttonPressed(self, evt):
        self.motorOn = True
        self.motorState['text'] = "Motor: ON"
        self.moveZ = 0
        self.moveMultiplier = 1
        self.maxZSpeed = 5000
        
        if evt.widget == self.downFast:
            self.moveZ = -10
            self.zSpeed = 300
            self.maxZSpeed = 500
            self.moveMultiplier = 1.5
        if evt.widget == self.downMed:
            self.moveZ = -1
            self.zSpeed = 100
            self.maxZSpeed = 400
            self.moveMultiplier = 1.2
        if evt.widget == self.downSlow:
            self.moveZ = -0.01
            self.zSpeed = 10
            self.maxZSpeed = 10
            self.moveMultiplier = 1
        if evt.widget == self.upFast:
            self.moveZ = 10
            self.zSpeed = 300
            self.maxZSpeed = 500
            self.moveMultiplier = 1.5
        if evt.widget == self.upMed:
            self.moveZ = 1
            self.zSpeed = 100
            self.maxZSpeed = 400
            self.moveMultiplier = 1.2
        if evt.widget == self.upSlow:
            self.moveZ = 0.01
            self.zSpeed = 10
            self.maxZSpeed = 10
            self.moveMultiplier = 1
        self.update()
    def motorStateChanged(self, mState = None):
        if self.motorOn:
            self.conn.write("M18")
            self.motorState['text'] = "Motor: OFF"
        else:
            self.conn.write("M17")
            self.motorState['text'] = "Motor: ON"
        self.motorOn = self.motorOn == False
        
    def update(self, *args):
        if self.conn is not None:
            if self.conn.busy == False:
                if self.moveZ != 0:
                    self.conn.moveZ(self.moveZ, self.zSpeed)
    def buttonReleased(self, evt):
        self.moveZ = 0
        self.zSpeed = 0
        self.moveMultiplier = 1
        
class LayerPreview(Frame):
    def __init__(self, master, **kwargs):
        Frame.__init__(self, master, **kwargs)
        
        self.canvas = Canvas(self, width=300, height=300)
        self.canvas.pack(padx=0,pady=0)
        self.canvas.config(insertwidth=0)
        self.canvas.config(selectborderwidth=0)
        self.canvas.config(highlightthickness=0)
        
        self.canvas.create_text(150, 150, text="No file selected", fill="#0099FF")
        
        self.selectedLayer = StringVar()
        self.selectedLayer.set(0)
        self.selectedLayer.trace('w', self.layerChanged)
        
        lcFrame = Frame(self)
        lcFrame.pack(pady = 5, padx=5, side=RIGHT)
        self.numLayersLabel = Label(lcFrame)
        self.numLayersLabel.pack(side=RIGHT)
        self.layerSelector = Spinbox(lcFrame, width=10, textvariable = self.selectedLayer)
        self.layerSelector.pack(side=RIGHT)
    def setHandler(self, handler):
        self.handler = handler
        
        
    def updatePrint(self):
        self.canvas.delete('all')
        self.printDim = self.handler.getPrintDimensions()
        nLayers = self.handler.numLayers()
        if nLayers >= 1:
            self.layerSelector['to'] = self.handler.numLayers()
            self.layerSelector['from'] = 1
            self.numLayersLabel['text'] = "of " + str(self.handler.numLayers())
            self.selectedLayer.set(1)
        else:
            self.layerSelector['to'] = 0
            self.layerSelector['from'] = 0
        
    def drawLayer(self, num):
        self.canvas.delete('all')
        self.canvas.create_rectangle(0,0, 300, 300, fill="#000000")
        offsetX = (300 - (self.printDim['width'] + self.printDim['x'] * 2)) / 2
        offsetY = (300 - (self.printDim['height'] + self.printDim['y'] * 2)) / 2
        
        scale = 1
        
        if self.handler.config.get('selectedDisplay') is not None:
            monConfig = self.handler.config.getDisplay(self.handler.config.get('selectedDisplay'))
            if 'printArea' in monConfig and 'pixelsPerMM' in monConfig:
                sX = 300 / int(monConfig['printArea']['width'])
                sY = 300 / int(monConfig['printArea']['height'])
                if sX < sY:
                    scale = sX
                elif sY < sX:
                    scale = sY
                scale = scale * (float(monConfig['pixelsPerMM']) / 10)
                
                
                
        layer = self.handler.getLayer(int(num)-1)
        for shape in layer:
            for i in range(0, len(shape['points'])):
                if i % 2 == 0:
                    shape['points'][int(i)] = shape['points'][int(i)] * scale + offsetX
                elif i % 2 == 1:
                    shape['points'][int(i)] = shape['points'][int(i)] * scale + offsetY
            self.canvas.create_polygon(*shape['points'], fill=shape['color'], outline=shape['color'])
    def layerChanged(self, *args):
        validateInt(self.selectedLayer, self.layerSelector)
        self.drawLayer(int(self.selectedLayer.get()))

    
def openMonitorConfig():
    if monitorSelect.current() == -1:
        return
    global mConfigWindow
    
    rW = monitors[monitorSelect.current()][2][2] - monitors[monitorSelect.current()][2][0]
    rH = monitors[monitorSelect.current()][2][3] - monitors[monitorSelect.current()][2][1]
    rX = monitors[monitorSelect.current()][2][0]
    rY = monitors[monitorSelect.current()][2][1]
    handler.showWindow(rX, rY, rW, rH )
    mHash = handler.config.monitorHash(monitorSelect.current(), rX, rY, rW, rH)
    handler.config.set('selectedDisplay', mHash)
    if mConfigWindow == None:
        mConfigWindow = MonitorConfig(handler)
        mConfigWindow.bind('<Destroy>', monitorSettingsClosed)
    else:
        mConfigWindow.reloadDisplay()
    mConfigWindow.wm_title("Configure Monitor [" + str(monitorSelect.current()) + "]")
def monitorSettingsClosed(evt):
    global mConfigWindow
    mConfigWindow = None
    handler.window.clear()
def serialError(evt):
    messagebox.showerror("Connection Error", "There was an error connecting to the COM port. Make sure the selected COM port and baud rate is correct.")
    connectButton.configure(text="Connect", state="normal")
def serialConnected(evt):
    print(evt)
    zMoveFrame.setConnection(handler.conn)
    zMoveFrame.showButtons()
    connectButton.configure(text="Disconnect", state="normal")
def connectSerial():
    if handler.conn != None:
        handler.disconnect()
        connectButton.configure(text="Connect", state="normal")
        zMoveFrame.hideButtons()
        
    elif comSelect.current() >= 0:
        connectButton.configure(text="Connecting...", state="disabled")
        handler.connect(comPorts[comSelect.current()][0], int(vBaudRate.get()))
        handler.conn.bind('connected', serialConnected)
        handler.conn.bind('connection-error', serialError)
        if handler.conn.connectionError != False:
            serialError(None)
    
def monitorChanged(*args):
    confMonitor.configure(state="normal")
    if handler.window != None:
        resW = monitors[monitorSelect.current()][2][2] - monitors[monitorSelect.current()][2][0]
        resH = monitors[monitorSelect.current()][2][3] - monitors[monitorSelect.current()][2][1]
        resX = monitors[monitorSelect.current()][2][0]
        resY = monitors[monitorSelect.current()][2][1]
        handler.window.updateDimensions(resX, resY, resW, resH)
def comPortChanged(*args):
    if comSelect.current() >= 0:
        config.set('comPort', comPorts[comSelect.current()][0])
    if str(vBaudRate.get()).isdigit():
        config.set('baudRate', vBaudRate.get())
    checkCOMConnectable()  
def checkCOMConnectable():
    if comSelect.current() >= 0 and str(vBaudRate.get()).isdigit() and int(vBaudRate.get()) >= 300:
        connectButton.configure(state="normal")
    else:
        connectButton.configure(state="disabled")
    

class SettingsFrame(Frame):
    def __init__(self, master, **kwargs):
        Frame.__init__(self, master, **kwargs)
        
        self.vLayerHeight = StringVar()
        self.vExposureTime = StringVar()
        self.vStartingExposureTime = StringVar()
        self.vStartingLayers = StringVar()
        self.vPostPause = StringVar()
        self.vRetractDistance = StringVar()
        self.vRetractSpeed = StringVar()
        self.vReturnSpeed = StringVar()
        self.vPrePause = StringVar()
        
        Label(self, text="Layer Height (mm)").pack(anchor=W)
        self.layerHeightInput = Spinbox(self, from_=0.001, to=1, increment=0.01, format="%.3f" , textvariable=self.vLayerHeight)
        self.layerHeightInput.pack(anchor=W)

        Label(self, text="Exposure Time (ms)").pack(anchor=W)
        self.exposureTimeInput = Spinbox(self, from_=1, to=10000, increment=100 , textvariable=self.vExposureTime)
        self.exposureTimeInput.pack(anchor=W)
        Label(self, text="Starting Exposure Time (ms)").pack(anchor=W)
        self.startExposureInput = Spinbox(self, from_=1, to=10000, increment=100 , textvariable=self.vStartingExposureTime)
        self.startExposureInput.pack(anchor=W)
        Label(self, text="Starting Layers").pack(anchor=W)
        self.startingLayersInput = Spinbox(self, from_=0, to=100, increment=1 , textvariable=self.vStartingLayers)
        self.startingLayersInput.pack(anchor=W)
        Label(self, text="Post-Exposure Pause (ms)").pack(anchor=W)
        self.postPauseInput = Spinbox(self, from_=0, to=5000, increment=50 , textvariable=self.vPostPause)
        self.postPauseInput.pack(anchor=W)
        Label(self, text="Z-Retract Distance (mm)").pack(anchor=W)
        self.zRetractInput = Spinbox(self, from_=0, to=5000, increment=50 , textvariable=self.vRetractDistance)
        self.zRetractInput.pack(anchor=W)
        Label(self, text="Z-Retract Speed (mm/min)").pack(anchor=W)
        self.retractSpeedInput = Spinbox(self, from_=1, to=500, increment=50 , textvariable=self.vRetractSpeed)
        self.retractSpeedInput.pack(anchor=W)
        Label(self, text="Z-Return Speed (mm/min)").pack(anchor=W)
        self.returnSpeedInput = Spinbox(self, from_=1, to=500, increment=50 , textvariable=self.vReturnSpeed)
        self.returnSpeedInput.pack(anchor=W)
        Label(self, text="Pre-Exposure Pause (ms)").pack(anchor=W)
        self.prePauseInput = Spinbox(self, from_=0, to=5000, increment=50 , textvariable=self.vPrePause)
        self.prePauseInput.pack(anchor=W)
        
        
        
        self.vLayerHeight.set(handler.config.get('layerHeight'))
        self.vExposureTime.set(handler.config.get('exposureTime'))
        self.vStartingExposureTime.set(handler.config.get('startingExposureTime'))
        self.vStartingLayers.set(handler.config.get('startingLayers'))
        self.vPostPause.set(handler.config.get('postPause'))
        self.vRetractDistance.set(handler.config.get('retractDistance'))
        self.vRetractSpeed.set(handler.config.get('retractSpeed'))
        self.vReturnSpeed.set(handler.config.get('returnSpeed'))
        self.vPostPause.set(handler.config.get('prePause'))
        
        
        self.vLayerHeight.trace('w', self.layerHeightChanged) 
        self.vExposureTime.trace('w', self.settingChanged) 
        self.vStartingExposureTime.trace('w', self.settingChanged) 
        self.vStartingLayers.trace('w', self.settingChanged) 
        self.vPostPause.trace('w', self.settingChanged) 
        self.vRetractDistance.trace('w', self.settingChanged) 
        self.vRetractSpeed.trace('w', self.settingChanged) 
        self.vReturnSpeed.trace('w', self.settingChanged) 
        self.vPrePause.trace('w', self.settingChanged) 
        
    def layerHeightChanged(self, *args):
        validateFloat(self.vLayerHeight, self.layerHeightInput)
        config.set('layerHeight', self.vLayerHeight.get())
        if handler.slicedLayerHeight != -1:
            '''if messagebox.askquestion('Reslice File', "The layer height has been changed since the file was last sliced. Would you like to reslice the model?"):
                print("reslice")
            '''
    def settingChanged(self, *args):
        validateInt(self.vExposureTime, self.exposureTimeInput)
        validateInt(self.vStartingExposureTime, self.startExposureInput)
        validateInt(self.vStartingLayers, self.startingLayersInput)
        validateInt(self.vPostPause, self.postPauseInput)
        validateFloat(self.vRetractDistance, self.zRetractInput)
        validateInt(self.vRetractSpeed, self.retractSpeedInput)
        validateInt(self.vReturnSpeed, self.returnSpeedInput)
        validateInt(self.vPrePause, self.prePauseInput)
        
        config.set('exposureTime', self.vExposureTime.get())
        config.set('startingExposureTime', self.vStartingExposureTime.get())
        config.set('startingLayers', self.vStartingLayers.get())
        config.set('postPause', self.vPostPause.get())
        config.set('retractDistance', self.vRetractDistance.get())
        config.set('retractSpeed', self.vRetractSpeed.get())
        config.set('returnSpeed', self.vReturnSpeed.get())
        config.set('prePause', self.vPrePause.get())

handler.bind('next-layer', printNextLayer)
handler.bind('start', printStarted)



fileFrame = Labelframe(root, text="File")
fileFrame.pack(expand=True, fill=X, anchor=N, side=TOP, padx = 10, pady = 10)
filenameLabel = Label(fileFrame, text="No file selected")
filenameLabel.pack(side=LEFT)
selectFileButton = Button(fileFrame, text = 'Select File', command = load_file)
selectFileButton.pack(side=RIGHT, padx=5)


bodyFrame = Frame(root, width = 600, height=400)
bodyFrame.pack(expand=True, fill=X, padx=10, anchor=W)

view3DFrame = Frame(width=300, height=300)
viewLayerFrame = LayerPreview(root, width=300, height=300)


viewFrame = Notebook(bodyFrame)
#viewFrame.add(view3DFrame, text="3D View")
viewFrame.add(viewLayerFrame, text="Layer View")
viewFrame.pack(expand=True, side=LEFT, anchor=NW)



settingsFrame = Notebook(bodyFrame)
settingsFrame.pack(expand=True, side=LEFT, anchor=NW)

setupFrame = Frame()
setupFrame.pack(padx=10, pady=10)

printerFrame = Frame(setupFrame)
printerFrame.pack(side=TOP)

zMoveFrame = ZMove(printerFrame)
zMoveFrame.pack(side=RIGHT, anchor=E, padx=(50, 0))

sliceFrame = SettingsFrame(settingsFrame)
sliceFrame.pack(padx=10, pady=10)

settingsFrame.add(setupFrame, text="Connection")
settingsFrame.add(sliceFrame, text="Slice Settings")
printerFrame.configure(padx=10, pady = 10)
sliceFrame.configure(padx=10, pady = 10)

vMonitor = StringVar()
vComPort = StringVar()
vBaudRate = StringVar()



Label(printerFrame, text="Monitor").pack(anchor=W)
monitorSelect = Combobox(printerFrame, values = monitorList, state="readonly", textvariable=vMonitor)
monitorSelect.pack()
    

confMonitor = Button(printerFrame, text="Configure Monitor", state="disabled", command = openMonitorConfig)
confMonitor.pack(pady=5, anchor=W, fill=X)


Label(printerFrame, text="COM Port").pack(anchor=W)
comSelect = Combobox(printerFrame, values = comPortNames, state="readonly", textvariable=vComPort)
comSelect.pack()

if selectedMonIndex != -1:
    monitorSelect.current(int(selectedMonIndex))
    confMonitor.configure(state="normal")

if selectedComPortIndex != -1:
    print(selectedComPortIndex)
    vComPort.set(comPortNames[int(selectedComPortIndex)])

vBaudRate.set(config.get('baudRate'))

vMonitor.trace('w', monitorChanged)
vComPort.trace('w', comPortChanged)
vBaudRate.trace('w', comPortChanged) 

Label(printerFrame, text="Baud Rate").pack(anchor=W)
baudSelect = Combobox(printerFrame, values = [300, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 250000, 2500000], textvariable=vBaudRate)
baudSelect.pack()
connectButton = Button(printerFrame, text="Connect", state="disabled", command = connectSerial)
connectButton.pack(pady=5, anchor=W, fill=X)

checkCOMConnectable()




statusFrame = LabelFrame(root)
statusFrame.pack(expand=True, fill=X, side=BOTTOM, padx = 10, pady = 10, ipadx=10, ipady=10)


statusLabel = Label(statusFrame)
statusLabel.pack(side=LEFT)

stateButton = Button(statusFrame, text = 'Start Print', command = start_print)
stateButton.pack(side=RIGHT, padx = 10)



def handlerReslice(evt):
    startSlicing(handler.slicedFile)
def handlerStateChanged(evt):
    print(handler.state)
handler.bind('reslice', handlerReslice)
handler.bind('state-change', handlerStateChanged)



	
#root.overrideredirect(True)
#root.wm_geometry("1024x768")
#root.iconbitmap("favicon.ico")
root.iconphoto(True, PhotoImage(file=os.path.join(currentDir(), "favicon.png")))
def on_closing():
    if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
        handler.shutdown()
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

		