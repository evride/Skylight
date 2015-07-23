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

for i in serial.tools.list_ports.comports():
    if i[1] == 'n/a':
        comPortNames.append(i[0])
    else:
        comPortNames.append(i[1])
    comPorts.append(i)
for i in range(len(list(monitors))):
    monitorList.append("%d : (%dx%d)" % (i, monitors[i][2][2] - monitors[i][2][0], monitors[i][2][3] - monitors[i][2][1]) )
def load_file():

    filename = filedialog.askopenfilename(filetypes = [('Supported 3D Models', '*.stl;*.obj')])
    if filename: 
        _path, _tail = os.path.split(filename)
        filenameLabel.config(text=filename)
        statusLabel.config(text="Slicing file " + _tail + "...")
        root.update()
        t1 = Thread(target=sliceFile, args=[filename, vLayerHeight.get()])
        t1.start()

def sliceFile(filename, layerHeight):
    directory = os.path.dirname(os.path.abspath(__file__))
    subprocess.call("{0}/slic3r/slic3r.exe {1} --layer-height={2} --export-svg --output={0}/temp.svg".format(directory, filename, layerHeight))
    sliceComplete()
    statusLabel.config(text="Done")
def sliceComplete():
    handler.openFile('temp.svg')
    viewLayerFrame.setHandler(handler)
def stop_print():
    handler.destroyWindow()
def start_print():
    if monitorSelect.current() >= 0:
        '''
        handler.createWindow(monitors[monitorSelect.current()][2][0], monitors[monitorSelect.current()][2][1], monitors[monitorSelect.current()][2][2] - monitors[monitorSelect.current()][2][0], monitors[monitorSelect.current()][2][3] - monitors[monitorSelect.current()][2][1] )
        handler.connectController(comPorts[comSelect.current()][0], 9600)
        '''
        
        handler.createWindow(monitors[monitorSelect.current()][2][0], monitors[monitorSelect.current()][2][1], monitors[monitorSelect.current()][2][2] - monitors[monitorSelect.current()][2][0], monitors[monitorSelect.current()][2][3] - monitors[monitorSelect.current()][2][1] )
        handler.startPrint()
    else:
        messagebox.showerror("Display error", "No display selected")
        return
class ZMove(Frame):
    def __init__(self, master, **kwargs):
        Frame.__init__(self, master, **kwargs)
        
        self.moveZ = 0
        self.zSpeed = 0
        self.maxZSpeed = 10
        self.moveMultiplier = 1
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
        
        self.motorState = Button(self, text="Motor: ON")
        self.motorState.pack()
        
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
        self.downSlow.pack()
        self.downMed.pack()
        self.downFast.pack()
    def hideButtons(self):
        
        self.upFast.pack_forget()
        self.upMed.pack_forget()
        self.upSlow.pack_forget()
        self.downSlow.pack_forget()
        self.downMed.pack_forget()
        self.downFast.pack_forget()
    def setConnection(self, conn):
        self.conn = conn
        self.conn.bind('move-complete', self.update)
    def buttonPressed(self, evt):
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
        self.layerSelector['to'] = self.handler.numLayers()
        self.layerSelector['from'] = 1
        self.numLayersLabel['text'] = "of " + str(self.handler.numLayers())
        self.selectedLayer.set(1)
        self.drawLayer(1)
    def drawLayer(self, num):
        self.canvas.delete('all')
        self.canvas.create_rectangle(0,0, 300, 300, fill="#000000")
        layer = self.handler.getLayer(int(num)-1)
        for shape in layer:
            self.canvas.create_polygon(*shape['points'], fill=shape['color'], outline=shape['color'])
    def layerChanged(self, *args):
        validateDim(self.selectedLayer, self.layerSelector)
        self.drawLayer(int(self.selectedLayer.get()))
        
def validateDim(self, var, field):
    temp = var.get()
    if str(temp).isdigit() == False:
        var.set(int(field['from']))
    elif int(temp) < field['from']:
        var.set(int(field['from']))
    elif int(temp) > field['to']:
        var.set(int(field['to']))
    
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
    handler.config.set('selectedMonitor', mHash)
    if mConfigWindow == None:
        mConfigWindow = MonitorConfig(handler)
        mConfigWindow.bind('<Destroy>', monitorSettingsClosed)
    else:
        mConfigWindow.reloadDisplay()
    mConfigWindow.wm_title("Configure Monitor [" + str(monitorSelect.current()) + "]")
def monitorSettingsClosed():
    print("asdf")
    global mConfigWindow
    mConfigWindow = None
def serialError(evt):
    print("error", evt)
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
        
    if comSelect.current() >= 0 and str(vBaudRate.get()).isdigit() and int(vBaudRate.get()) >= 300:
        connectButton.configure(state="normal")
    else:
        connectButton.configure(state="disabled")
def settingChanged(*args):
    config.set('layerHeight', float(vLayerHeight.get()))
    config.set('exposureTime', int(vExposureTime.get()))
    config.set('startingExposureTime', int(vStartingExposureTime.get()))
    config.set('startingLayers', int(vStartingLayers.get()))
    config.set('postPause', int(vPostPause.get()))
    config.set('retractDistance', float(vRetractDistance.get()))
    config.set('retractSpeed', int(vRetractSpeed.get()))
    config.set
vMonitor = StringVar()
vMonitor.trace('w', monitorChanged)

vComPort = StringVar()
vComPort.trace('w', comPortChanged)

vBaudRate = StringVar()
vBaudRate.set(config.get('baudRate'))
vBaudRate.trace('w', comPortChanged)

vLayerHeight = StringVar()
vLayerHeight.set(config.get('layerHeight'))
vLayerHeight.trace('w', settingChanged)

vExposureTime = StringVar()
vExposureTime.set(config.get('exposureTime'))
vExposureTime.trace('w', settingChanged)

vStartingExposureTime = StringVar()
vStartingExposureTime.set(config.get('startingExposureTime'))
vStartingExposureTime.trace('w', settingChanged)

vStartingLayers = StringVar()
vStartingLayers.set(config.get('startingLayers'))
vStartingLayers.trace('w', settingChanged)

vPostPause = StringVar()
vPostPause.set(config.get('postPause'))
vPostPause.trace('w', settingChanged)

vRetractDistance = StringVar()
vRetractDistance.set(config.get('retractDistance'))
vRetractDistance.trace('w', settingChanged)

vRetractSpeed = StringVar()
vRetractSpeed.set(config.get('retractSpeed'))
vRetractSpeed.trace('w', settingChanged)




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

sliceFrame = Frame()
sliceFrame.pack(padx=10, pady=10)

settingsFrame.add(setupFrame, text="Connection")
settingsFrame.add(sliceFrame, text="Slice Settings")
printerFrame.configure(padx=10, pady = 10)
sliceFrame.configure(padx=10, pady = 10)


Label(printerFrame, text="Monitor").pack(anchor=W)
monitorSelect = Combobox(printerFrame, values = monitorList, state="readonly", textvariable=vMonitor)
monitorSelect.pack()
confMonitor = Button(printerFrame, text="Configure Monitor", state="disabled", command = openMonitorConfig)
confMonitor.pack(pady=5, anchor=W, fill=X)

Label(printerFrame, text="COM Port").pack(anchor=W)
comSelect = Combobox(printerFrame, values = comPortNames, state="readonly", textvariable=vComPort)
comSelect.pack()



Label(printerFrame, text="Baud Rate").pack(anchor=W)
baudSelect = Combobox(printerFrame, values = [300, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 250000, 2500000], textvariable=vBaudRate)
baudSelect.pack()
connectButton = Button(printerFrame, text="Connect", state="disabled", command = connectSerial)
connectButton.pack(pady=5, anchor=W, fill=X)



Label(sliceFrame, text="Layer Height (mm)").pack(anchor=W)
layerHeightSelect = Spinbox(sliceFrame, from_=0.001, to=1, increment=0.01, format="%.3f" , textvariable=vLayerHeight)
layerHeightSelect.pack()

Label(sliceFrame, text="Exposure Time (ms)").pack(anchor=W)
exposureTimeInput = Spinbox(sliceFrame, from_=1, to=5000, increment=50 , textvariable=vExposureTime)
exposureTimeInput.pack()
Label(sliceFrame, text="Starting Exposure Time (ms)").pack(anchor=W)
startExposureInput = Spinbox(sliceFrame, from_=1, to=5000, increment=50 , textvariable=vStartingExposureTime)
startExposureInput.pack()
Label(sliceFrame, text="Starting Layers").pack(anchor=W)
exposureTimeInput = Spinbox(sliceFrame, from_=0, to=100, increment=1 , textvariable=vStartingLayers)
exposureTimeInput.pack()
Label(sliceFrame, text="Post-Exposure Pause (ms)").pack(anchor=W)
postPauseInput = Spinbox(sliceFrame, from_=0, to=5000, increment=50 , textvariable=vPostPause)
postPauseInput.pack()
Label(sliceFrame, text="Z-Retract Distance (mm)").pack(anchor=W)
zRetractInput = Spinbox(sliceFrame, from_=0, to=5000, increment=10 , textvariable=vRetractDistance)
zRetractInput.pack()
Label(sliceFrame, text="Z-Retract Speed (mm/min)").pack(anchor=W)
retractSpeedInput = Spinbox(sliceFrame, from_=1, to=500, increment=500 , textvariable=vRetractSpeed)
retractSpeedInput.pack()

statusFrame = LabelFrame(root)
statusFrame.pack(expand=True, fill=X, side=BOTTOM, padx = 10, pady = 10, ipadx=10, ipady=10)


statusLabel = Label(statusFrame)
statusLabel.pack(side=LEFT)

stateButton = Button(statusFrame, text = 'Start Print', command = start_print)
stateButton.pack(side=RIGHT, padx = 10)


	
#root.overrideredirect(True)
#root.wm_geometry("1024x768")
#root.iconbitmap("favicon.ico")

root.iconphoto(True, PhotoImage(file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "favicon.png")))
def on_closing():
    if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
        config.save()
        stop_print()
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

		