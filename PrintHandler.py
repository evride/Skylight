from threading import *
import xml.etree.ElementTree as ET
import re
import time
from tkinter import messagebox
from PrintWindow import *
from Configuration import *
from PrinterSerial import *
from utils import *
from copy import deepcopy

class PrintStatus:
    PRINTING = "running"
    PAUSED = "paused"
    SETUP = "setup"
    CONNECTING = "connecting"
    PREPARING = "preparing"

class PrintHandler(EventDispatcher):
    def __init__(self):
        EventDispatcher.__init__(self)
        self.layers = []
        self.conn = None
        self.window = None
        self.svg = None
        self.config = Configuration()
        self.state = PrintStatus.SETUP
        self.ignoreLayerHeight = False
        self.slicedLayerHeight = -1
        self.slicedFile = None
    def showWindow(self, x, y, w, h):
        if self.window == None:
            self.window = PrintWindow(x,y,w,h)
        else:
            self.window.updateDimensions(x,y,w,h)
        self.window.clear()
        self.viewport = {'x':x, 'y':y, 'width':w, 'height':h}
    def connect(self, port, baud):
        print("connect")
        if self.conn is not None:
            if self.conn.connecting or self.conn.detected:
                return
        self.conn = PrinterSerial(port, baud)
        self.conn.bind('connected', self._comConnected)
        self.conn.bind('connection-error', self._comError)
        self.conn.bind('move-complete', self._moveComplete)
        print("all bound")
    def startPrint(self, autoScaleCenter = False):
        if autoScaleCenter:
            self.setAutoScaleCenter()
		
        self.layerHeight = parseFloat(self.config.get('layerHeight'))
        self.exposureTime = parseInt(self.config.get('exposureTime')) / 1000
        self.startingExposureTime = parseInt(self.config.get('startingExposureTime')) / 1000
        self.startingLayers = parseInt(self.config.get('startingLayers'))
        self.zRetract = float(self.config.get('retractDistance'))
        self.zRetractSpeed = parseInt(self.config.get('retractSpeed'))
        self.postPause = parseInt(self.config.get('postPause')) / 1000
        self.zReturnSpeed = parseInt(self.config.get('returnSpeed'))
        self.prePause = parseInt(self.config.get('prePause')) / 1000
        
        
        monConfig = self.config.getDisplay(self.config.get('selectedDisplay'))
        
            
        sxy = float(monConfig['pixelsPerCM']) / 10
        self.setScale(sxy, sxy)
        
        dim = self.getPrintDimensions()
        self.offsetX = (int(monConfig['printArea']['width']) - (self.scaleX * dim['width'])) / 2 + int(monConfig['printArea']['x'])
        self.offsetY = (int(monConfig['printArea']['height']) - (self.scaleY * dim['height'])) / 2 + int(monConfig['printArea']['y'])
        self.setState(PrintStatus.PRINTING)
        
        self.currentLayer = -1
        self.nextLayer()
        self.window.mainloop()
    def setAutoScaleCenter(self):
        printDim = self.getPrintDimensions()
        self.offsetX = 10
        self.offsetY = 10
        self.scaleX = (self.viewport['width'] - (2 * self.offsetX) ) / printDim['width']
        self.scaleY = (self.viewport['height'] - (2 * self.offsetY) ) / printDim['height']
        if self.scaleX < self.scaleY:
            self.scaleY = self.scaleX
        elif self.scaleY < self.scaleX:
            self.scaleX = self.scaleY
        self.offsetX -= printDim['x']
        self.offsetY -= printDim['y']
    def setScale(self, x, y):
        self.scaleX = x
        self.scaleY = y
    def openFile(self, filename):
        self.svg = ET.parse(filename).getroot()
        self.processData()
    def processData(self):
        self.layers = []
        for layer in self.svg:
            polygons = []
            for poly in layer:
                style = poly.get('style')
                colorStart = style.find('fill:')
                color = "#000000"
                points = list(map(float, re.split('[ ,]', poly.get('points'))))
                if colorStart >= 0:
                    colorStart += 5
                    colorEnd = color.find(';', colorStart)
                    if colorEnd == -1:
                        colorEnd = len(style)
                    color = style[colorStart:colorEnd]
                polygons.append({'points':points, 'color':color.strip()})
            self.layers.append(polygons)
    def nextLayer(self):
        self.window.clear()
        self.currentLayer+=1
        self.window.lift()
        if self.currentLayer == len(self.svg):
            self.conn.write("M84")
            self.conn.write("M2")
            return
        layerData = self.getLayer(self.currentLayer)
        for shape in layerData:
            for i in range(0, len(shape['points'])):
                if i % 2 == 0:
                    shape['points'][int(i)] = shape['points'][int(i)] * self.scaleX + self.offsetX
                elif i % 2 == 1:
                    shape['points'][int(i)] = shape['points'][int(i)] * self.scaleY + self.offsetY
            self.window.drawShape(shape['points'], shape['color'])
        self.window.update()
        Thread(target=self._exposureWait).start()
        self.dispatch('next-layer')
    def _moveComplete(self, evt):
        if self.state is not PrintStatus.PRINTING and self.retracted == False:
            return
        if self.retracted == True:
            self.retracted = False
            self.conn.moveZ(-self.zRetract + self.layerHeight, self.zReturnSpeed)
        elif self.retracted == False:
            if self.prePause > 0:
                time.sleep(self.prePause)
            self.nextLayer()
    def _exposureWait(self):
        if self.currentLayer < self.startingLayers:
            time.sleep(self.startingExposureTime)
        else:
            time.sleep(self.exposureTime)
        self.window.clear()
        if self.postPause > 0:
            self.curePause()
        elif self.postPause == 0:
            self.retractMove()
    def _comConnected(self, evt):
        if self.state == PrintStatus.PREPARING:
            if self.ready():
                self.startPrint()

    def _comError(self, evt):
        if self.state == PrintStatus.PREPARING:
            self.setState(PrintStatus.SETUP)
            messagebox.showwarning("Connection Error", "Skylight could not detect your control board. Make sure the COM port and baud rate is correct.")
        self.conn.close()
        self.conn = None
    def setState(self, s):
        self.state = s
        self.dispatch('state-change')
    def curePause(self):
        self.window.clear()
        self.window.update()
        time.sleep(self.postPause)
        self.retractMove()
    def retractMove(self):
        self.retracted = True
        self.conn.moveZ(self.zRetract, self.zRetractSpeed)
    def getPrintDimensions(self):
        dim = {'x':False, 'y':False, 'width':False, 'height':False}
        for layer in self.layers:
            for poly in layer:
                points = poly['points']
                for i in range(0, len(points)):
                    if i % 2 == 0:
                        if dim['x'] == False or dim['x'] > points[i]:
                            dim['x'] = points[i]
                        if dim['width'] == False or dim['width'] < points[i]:
                            dim['width'] = points[i]
                    elif i % 2 == 1:
                        if dim['y'] == False or dim['y'] > points[i]:
                            dim['y'] = points[i]
                        if dim['height'] == False or dim['height'] < points[i]:
                            dim['height'] = points[i]
        dim['width'] = dim['width'] - dim['x']
        dim['height'] = dim['height'] - dim['y']
        return dim
    def numLayers(self):
        return len(self.layers)
    def getLayer(self, num):
        #always clone layer data so changes won't effect the original data
        return deepcopy(self.layers[num])
    def stopPrint(self):
        self.setState(PrintStatus.PAUSED)
    def continuePrint(self):
        self.setState(PrintStatus.PRINTING)
        self.nextLayer()
    def disconnect(self):
        if self.conn != None:
            print("disconnect")
            if self.conn.detected:
                self.conn.write("M84")
                self.conn.write("M2")
            self.conn.stopAndClose()
            self.conn = None        
    def destroyWindow(self):
        if self.window != None:
            self.window.destroy()
            self.window = None
    def shutdown(self):
        if self.conn != None:
            self.conn.stopAndClose()
        self.config.save()  
        if self.window != None:
            self.window.destroy()
    def recheckReady(*args):
        self.ready()
    def ready(self):
        serialConnected = False
        layerHeightValid = False
        displayReady = False
        fileSelected = False
        
        self.setState(PrintStatus.PREPARING)
        if type(self.conn) == PrinterSerial:
            if self.conn.detected == True:
                serialConnected = True
            elif self.conn.connecting:
                return False
            else:
                messagebox.showwarning("Connection Error", "Skylight could not detect your control board. Make sure the COM port and baud rate is correct.")
        else:
            if self.config.get('comPort') != None and self.config.get('baudRate'):
                self.connect(self.config.get('comPort'), self.config.get('baudRate'))
            else:
                messagebox.showwarning("Controller Not Selected", "Select the controller's COM port and baud rate.")
        
        if self.slicedFile != None:
            if self.svg != None:
                fileSelected = True
            else:
                messagebox.showinfo("File Slicing", "The selected model is still in the process of being sliced.")
                self.setState(PrintStatus.SETUP)
        else:
            messagebox.showwarning("Select File", "You have not selected a file to be sliced and printed.")
            self.setState(PrintStatus.SETUP)
            
        if serialConnected == False:
            self.setState(PrintStatus.SETUP)
            return False
            
        if self.slicedLayerHeight != -1:
            if self.config.get('layerHeight') == self.slicedLayerHeight:
                layerHeightValid = True
            else:
                if messagebox.askquestion('Reslice File', "The layer height has been changed since the file was last sliced. Would you like to reslice the model?"):
                    self.dispatch('reslice')
            
        
        #Display
        if self.config.get('selectedDisplay') != None:
            monConfig = self.config.getDisplay(self.config.get('selectedDisplay'))
            
            if 'printArea' in monConfig and 'pixelsPerCM' in monConfig:
                displayReady = True
            else:
                messagebox.showinfo("Configure Display", "The selected display needs to be configured before printing.")
        else:
            messagebox.showinfo("Select A Display", "Select and configure a display to print with.")
            
        return displayReady and layerHeightValid and serialConnected and fileSelected
        