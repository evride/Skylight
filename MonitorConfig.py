from tkinter import *
from tkinter.ttk import Separator
from math import *
from utils import *

class MonitorConfig(Tk):
    def __init__(self, handler):
        Tk.__init__(self)
        
        
        self.handler = handler    
        
        
        self.pX = StringVar(self)
        self.pY = StringVar(self)
        self.pW = StringVar(self)
        self.pH = StringVar(self)
        self.pxMM = StringVar(self)
        self.dState = StringVar(self)
        self.drawState = "area"
        
        container = Frame(self)
        container.pack(side=TOP)
        
        self.dState.set("area")
        
        self.areaCanvas = Canvas(container, width=300, height=300)
        self.areaCanvas.pack(side=LEFT)
        
        settingsFrame = Frame(container)
        
        Label(settingsFrame, text="Print Area Width").pack(anchor=W)
        self.widthText = Spinbox(settingsFrame, from_=1, to=2, textvariable=self.pW)
        self.widthText.pack()
        #widthText.bind('<KeyRelease>', self.valueChanged)
        Label(settingsFrame, text="Print Area Height").pack(anchor=W)
        self.heightText = Spinbox(settingsFrame, from_=1, to=2, textvariable = self.pH)
        self.heightText.pack()
        Label(settingsFrame, text="Margin From Left").pack(anchor=W)
        self.posXText = Spinbox(settingsFrame, from_=0, to=1, textvariable = self.pX)
        self.posXText.pack()
        Label(settingsFrame, text="Margin From Top").pack(anchor=W)
        self.posYText = Spinbox(settingsFrame, from_=0, to=1, textvariable = self.pY)
        self.posYText.pack()
        
        Separator(settingsFrame, orient=HORIZONTAL).pack(expand=True, fill=X, pady=10)
        
        Label(settingsFrame, text="Pixels Per Centimeter").pack(anchor=W)
        
        self.pxPerMM = Spinbox(settingsFrame, from_=1, to=100, textvariable=self.pxMM)
        self.pxPerMM.pack()
        
        Separator(settingsFrame, orient=HORIZONTAL).pack(expand=True, fill=X, pady=10)
        Label(settingsFrame, text="Show").pack(anchor=W)
        
        showAreaBtn = Radiobutton(settingsFrame, text="Print Area", value="area", variable=self.dState)
        showAreaBtn.pack(side=RIGHT, anchor=W)
        showGridBtn = Radiobutton(settingsFrame, text="Grid", value="grid", variable=self.dState)
        showGridBtn.pack(side=LEFT, anchor=W)
        
        
        settingsFrame.pack(side=LEFT)
        
        actionFrame = Frame(self)
        actionFrame.pack(anchor=S)
        saveBtn = Button(actionFrame, text="Save", command=self.saveSettings)
        saveBtn.pack(side=LEFT, padx=10, pady=10, ipadx=8, ipady = 2)
        cancelBtn = Button(actionFrame, text="Cancel", command=self.cancel)
        cancelBtn.pack(side=LEFT, padx=10, pady=10, ipadx=8, ipady = 2)
        
        
        self.pX.trace("w", self.areaChanged)
        self.pY.trace("w", self.areaChanged)
        self.pW.trace("w", self.areaChanged)
        self.pH.trace("w", self.areaChanged)
        self.pxMM.trace("w", self.ratioChanged)
        self.dState.trace("w", self.drawChange)
        
        self.reloadDisplay()
        
        self.redraw()
    def reloadDisplay(self):
        self.mW = self.handler.window.dimensions['width']
        self.mH = self.handler.window.dimensions['height']
        
        monConfig = self.handler.config.getDisplay(self.handler.config.get('selectedDisplay'))
        
        self.widthText['to'] = self.mW
        self.heightText['to'] = self.mH
        self.posXText['to'] = self.mW
        self.posYText['to'] = self.mH
        self.pxPerMM['to'] = max(self.mW, self.mH)
        
        if 'printArea' in monConfig:
            self.pX.set(monConfig['printArea']['x'])
            self.pY.set(monConfig['printArea']['y'])
            self.pW.set(monConfig['printArea']['width'])
            self.pH.set(monConfig['printArea']['height'])
        else:
            self.pX.set(round(self.mW * .1))
            self.pY.set(round(self.mH * .1))
            self.pW.set(round(self.mW * .80))
            self.pH.set(round(self.mH * .80))
        if 'pixelsPerMM' in monConfig:
            self.pxMM.set(monConfig['pixelsPerMM'])
        else:
            self.pxMM.set(50)
        self.posXText['to'] = self.mW - int(self.pW.get())
        self.posYText['to'] = self.mH - int(self.pH.get())
    def ratioChanged(self, *args):
        validateInt(self.pxMM, self.pxPerMM)
        
        self.drawState = "grid"
        self.redraw()
    def areaChanged(self, *args):
        validateInt(self.pW, self.widthText)
        validateInt(self.pH, self.heightText)
        self.posXText['to'] = float(self.widthText['to']) - float(self.pW.get())
        self.posYText['to'] = float(self.heightText['to']) - float(self.pH.get())
        validateInt(self.pX, self.posXText)
        validateInt(self.pY, self.posYText)
        
        
        self.drawState = "area"
        self.redraw()
        
    def drawChange(self, *args):
        self.drawState = self.dState.get()
        self.redraw()
    def redraw(self):
        if self.drawState == "area":
            self.redrawArea()
        elif self.drawState == "grid":
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
        
        
        tempPxMM = float(self.pxMM.get())
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
            
        self.handler.window.clear()
        for i in range(0, int((linesX * 2) + 1)):
            self.handler.window.canvas.create_line(i * tempPxMM + diffX , 0, i * tempPxMM + diffX , self.mH, fill="#FF0000")
        for i in range(0, int((linesY * 2) + 1)):
            self.handler.window.canvas.create_line(0, i * tempPxMM + diffY , self.mW, i * tempPxMM + diffY, fill="#FF0000")
    def redrawArea(self):
        self.areaCanvas.delete('all')
        self.handler.window.clear()
        
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
        
        _pX = self.pX.get()
        _pY = self.pY.get()
        _pW = self.pW.get()
        _pH = self.pH.get()
        
        self.areaCanvas.create_rectangle(bX, bY, drawW + bX, drawH + bY, fill="#000000")
        aX = round(scale * float(_pX)) + bX
        aY = round(scale * float(_pY)) + bY
        aW = round(scale * float(_pW)) + aX
        aH = round(scale * float(_pH)) + aY
        self.areaCanvas.create_rectangle(aX, aY, aW, aH, fill = "#FF0000", outline="#FF0000")
        
        self.handler.window.canvas.create_rectangle(float(_pX), float(_pY), float(_pW) + float(_pX), float(_pH) + float(_pY), fill="#FF0000", outline="#FF0000")
    def saveSettings(self):
        self.handler.config.saveDisplay(self.handler.config.get('selectedDisplay'), {'printArea':{'x':self.pX.get(), 'y':self.pY.get(), 'width':self.pW.get(), 'height':self.pH.get()}, 'pixelsPerMM':self.pxMM.get()})
        self.destroy()
    def cancel(self):
        self.destroy()