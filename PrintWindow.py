from tkinter import *
class PrintWindow(Tk):
    def __init__(self, x, y, w, h):
        Tk.__init__(self)
        self.overrideredirect(1)
        self.canvas = Canvas(self, width=w, height=h )
        self.canvas.pack(padx=0,pady=0)
        self.canvas.config(insertwidth=0)
        self.canvas.config(selectborderwidth=0)
        self.canvas.config(highlightthickness=0)
        self.canvas.config(background="#000000")
        self.configure(background="#000000")
        
        self.updateDimensions(x, y, w, h)
        #print(self.canvas.config())
        
        #Note: cursor none works but the time.sleeps prevent it from being hidden
        #print(self.canvas.config())
        #self.overrideredirect(0)
        #self.attributes("-fullscreen", True)
    def preparePrint(self):
        self.canvas.config(state=DISABLED)
        self.canvas.config(cursor="none")        
    def clear(self):
        self.canvas.delete('all')
    def drawShape(self, points, color):
        self.canvas.create_polygon(*points, fill=color, outline=color)
    def updateDimensions(self, x, y, w, h):
        self.dimensions = {'x':x, 'y':y, 'width':w, 'height':h}
        self.clear()
        self.geometry("%dx%d+%d+%d" % (w, h, x, y) )
        self.update()