from threading import *
import xml.etree.ElementTree as ET
import re
import time
from PrintWindow import *
class PrintHandler:
    def __init__(self,config):
        self.layers = []
        self.started = False
        self.setConfig(config)
    def createWindow(self, x, y, w, h):
        self.window = PrintWindow()
        self.window.startPrint(x, y, w, h)
        self.viewport = {'x':x, 'y':y, 'width':w, 'height':h}
        self.scaleX = 1
        self.scaleY = 1
        self.offsetX = 0
        self.offsetY = 0
        self.layerHeight = .05
        self.zRetract = 5
        self.zSpeed = 50
        self.exposureTime = 0.5
        self.printing = False
        self.startingExposureTime = 0.8
        self.startingLayers = 3
    def setViewport(self, x, y, w, h):
        self.viewport = {'x':x, 'y':y, 'width':w, 'height':h}
    def setConfig(self, config):
        self.config = config
        
        
    def setController(self, conn):
        print("setController")
        self.conn = conn
        self.conn.bind('move-complete', self._moveComplete)
    def setWindow(self, window):
        self.window = window
    def startPrint(self, autoScaleCenter = False):
        if autoScaleCenter:
            self.setAutoScaleCenter()
		
        self.layerHeight = self.config.get('layerHeight')
        self.exposureTime = self.config.get('exposureTime') / 1000
        self.startingExposureTime = self.config.get('startingExposureTime') / 1000
        self.startingLayers = self.config.get('startingLayers')
        self.zRetract = self.config.get('retractDistance') / 100
        self.zRetractSpeed = self.config.get('retractSpeed')
        self.postPause = self.config.get('postPause') / 1000
        
        sxy = float(self.config.get('pixelsPerMM')) / 10
        self.setScale(sxy, sxy)
        
        dim = self.getPrintDimensions()
        self.offsetX = (self.viewport['width'] - (self.scaleX * dim['width'])) / 2
        self.offsetY = (self.viewport['height'] - (self.scaleY * dim['height'])) / 2
        self.started = True
        
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
        self.currentLayer+=1
        self.window.clear()
        self.window.lift()
        if self.currentLayer == len(self.svg):
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
    def _moveComplete(self, evt):
        print("move Complete", self.started, self.retracted)
        if self.started is not True:
            return
        if self.retracted == True:
            self.retracted = False
            self.conn.moveZ(-self.zRetract + self.layerHeight, self.zRetractSpeed)
        elif self.retracted == False:
            self.nextLayer()
    def _exposureWait(self):
        print("exposureTime", self.exposureTime)
        time.sleep(self.exposureTime)
        self.window.clear()
        if self.postPause > 0:
            self.curePause()
        elif self.postPause == 0:
            self.retractMove()
    def curePause(self):
        self.window.clear()
        self.window.update()
        print("postPause", self.postPause)
        time.sleep(self.postPause)
        self.retractMove()
    def retractMove(self):
        self.retracted = True
        print("retractMove", self.zRetract, self.zRetractSpeed)
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
        return self.layers[num]
        