from tkinter import *
from tkinter.ttk import Separator
from math import *

class MonitorConfig(Tk):
    def __init__(self, monitorID, mW, mH, window, config):
        Tk.__init__(self)
        
        
        self.mW = mW
        self.mH = mH
        self.window = window
        
        self.monitorID = monitorID
        self.config = config
        
        
        self.pX = StringVar(self)
        self.pY = StringVar(self)
        self.pW = StringVar(self)
        self.pH = StringVar(self)
        self.pxMM = StringVar(self)
        self.drawState = StringVar(self)
        
        defaultW = round(mW * .8)
        defaultH = round(mH * .8)
        
        self.pX.set(round(mW * .1))
        self.pY.set(round(mH * .1))
        self.pW.set(round(mW * .80))
        self.pH.set(round(mH * .80))
        self.pxMM.set(50)
        self.drawState.set("area")
        
        self.areaCanvas = Canvas(self, width=300, height=300)
        self.areaCanvas.pack(side=LEFT)
        
        settingsFrame = Frame(self)
        
        Label(settingsFrame, text="Print Area Width").pack(anchor=W)
        self.widthText = Spinbox(settingsFrame, from_=1, to=mW,  textvariable=self.pW)
        self.widthText.pack()
        #widthText.bind('<KeyRelease>', self.valueChanged)
        Label(settingsFrame, text="Print Area Height").pack(anchor=W)
        self.heightText = Spinbox(settingsFrame, from_=1, to=mH, textvariable = self.pH)
        self.heightText.pack()
        Label(settingsFrame, text="Margin From Left").pack(anchor=W)
        self.posXText = Spinbox(settingsFrame, from_=0, to=mW, textvariable = self.pX)
        self.posXText.pack()
        Label(settingsFrame, text="Margin From Top").pack(anchor=W)
        self.posYText = Spinbox(settingsFrame, from_=0, to=mH, textvariable = self.pY)
        self.posYText.pack()
        
        Separator(settingsFrame, orient=HORIZONTAL).pack(expand=True, fill=X, pady=10)
        
        Label(settingsFrame, text="Pixels Per Centimeter").pack(anchor=W)
        
        self.pxPerMM = Spinbox(settingsFrame, from_=1, to=max(self.mW, self.mH), textvariable=self.pxMM)
        self.pxPerMM.pack()
        
        Separator(settingsFrame, orient=HORIZONTAL).pack(expand=True, fill=X, pady=10)
        Label(settingsFrame, text="Show").pack(anchor=W)
        
        showAreaBtn = Radiobutton(settingsFrame, text="Print Area", value="area", variable=self.drawState)
        showAreaBtn.pack(side=RIGHT, anchor=W)
        showGridBtn = Radiobutton(settingsFrame, text="Grid", value="grid", variable=self.drawState)
        showGridBtn.pack(side=LEFT, anchor=W)
        
        
        
        self.pX.trace("w", self.areaChanged)
        self.pY.trace("w", self.areaChanged)
        self.pW.trace("w", self.areaChanged)
        self.pH.trace("w", self.areaChanged)
        self.pxMM.trace("w", self.ratioChanged)
        self.drawState.trace("w", self.redraw)
        settingsFrame.pack(side=LEFT)
        
        self.redraw()
    def ratioChanged(self, *args):
        dState = self.drawState.set('grid')
        self.validateDim(self.pxMM, self.pxPerMM)
        
        self.config.set('pixelsPerMM', self.pxMM.get())
        self.redraw()
    def areaChanged(self, *args):
        dState = self.drawState.set('area')
        self.validateDim(self.pW, self.widthText)
        self.validateDim(self.pH, self.heightText)
        self.posXText['to'] = int(self.widthText['to']) - int(self.pW.get())
        self.posYText['to'] = int(self.heightText['to']) - int(self.pH.get())
        self.validateDim(self.pX, self.posXText)
        self.validateDim(self.pY, self.posYText)
        
        
        self.redraw()
    def redraw(self, *args):
        dState = self.drawState.get()
        if dState == "area":
            self.redrawArea()
        elif dState == "grid":
            self.redrawGrid()
    def redrawGrid(self):
        self.areaCanvas.delete('all')
        if self.mW / 300 > self.mH /300:
            scale = 300 / self.mW
            drawW = 300
            drawH = scale * self.mH
        else:
            scale = 300 / self.mH
            drawW = scale * self.mW
            drawH = 300
        bX = round((300 - drawW)/2)
        bY = round((300 - drawH)/2)
        self.areaCanvas.create_rectangle(bX, bY, drawW + bX, drawH + bY, fill="#000000")
        
        
        tempPxMM = int(self.pxMM.get())
        linesX = floor(self.mW / tempPxMM)
        if linesX % 2 == 1:
            linesX -=1
        linesX /= 2
        
        linesY = floor(self.mH / tempPxMM)
        if linesY % 2 == 1:
            linesY -= 1
        linesY /= 2
        
        diffX = self.mW / 2 - linesX * tempPxMM
        diffY = self.mH / 2 - linesY * tempPxMM
        for i in range(0, int((linesX * 2) + 1)):
            tempX = round( i * tempPxMM * scale) + scale * diffX
            self.areaCanvas.create_line(tempX + bX, bY, tempX + bX, bY + drawH, fill="#FF0000")
        for i in range(0, int((linesY * 2) + 1)):
            tempY = round( i * tempPxMM * scale) +  scale * diffY
            self.areaCanvas.create_line( bX, tempY + bY, bX + drawW, tempY + bY, fill="#FF0000")
            
        self.window.clear()
        for i in range(0, int((linesX * 2) + 1)):
            self.window.canvas.create_line(i * tempPxMM + diffX , 0, i * tempPxMM + diffX , self.mH, fill="#FF0000")
        for i in range(0, int((linesY * 2) + 1)):
            self.window.canvas.create_line(0, i * tempPxMM + diffY , self.mW, i * tempPxMM + diffY, fill="#FF0000")
    def redrawArea(self):
        self.areaCanvas.delete('all')
        self.window.clear()
        
        if self.mW / 300 > self.mH /300:
            scale = 300 / self.mW
            drawW = 300
            drawH = scale * self.mH
        else:
            scale = 300 / self.mH
            drawW = scale * self.mW
            drawH = 300
        bX = round((300 - drawW)/2)
        bY = round((300 - drawH)/2)
        self.areaCanvas.create_rectangle(bX, bY, drawW + bX, drawH + bY, fill="#000000")
        
        aX = round(scale * int(self.pX.get())) + bX
        aY = round(scale * int(self.pY.get())) + bY
        aW = round(scale * int(self.pW.get())) + aX
        aH = round(scale * int(self.pH.get())) + aY
        self.areaCanvas.create_rectangle(aX, aY, aW, aH, fill = "#FF0000", outline="#FF0000")
        
        self.window.canvas.create_rectangle(int(self.pX.get()), int(self.pY.get()), int(self.pW.get()) + int(self.pX.get()), int(self.pH.get()) +int(self.pY.get()), fill="#FF0000", outline="#FF0000")
    def validateDim(self, var, field):
        temp = var.get()
        if str(temp).isdigit() == False:
            var.set(int(field['from']))
        elif int(temp) < field['from']:
            var.set(int(field['from']))
        elif int(temp) > field['to']:
            var.set(int(field['to']))
    def setConfig(self, config):
        self.config = config
    def monitorDimensions(self, w, h):
        self.mW = w
        self.mY = h
    def printArea(self, x, y, w, h):
        '''
        self.pX = x
        self.pY = y
        self.pW = w
        self.pH = h
        '''