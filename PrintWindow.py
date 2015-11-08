import sys
from PyQt5 import QtCore, QtGui, QtWidgets
class PrintWindow(QtWidgets.QGraphicsView):
    def __init__(self, x, y, w, h):
        
        QtWidgets.QGraphicsView.__init__(self, self.scene
        
        self.layout = QtWidgets.QHBoxLayout(Form)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        
        self.resize(x, y, w, h)
        
    def preparePrint(self):
        self.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))

    def clear(self):
        self.scene.clear()
    def drawShape(self, points, color):
        self.canvas.create_polygon(*points, fill=color, outline=color)
    def resize(self, x,y,w,h):
        self.setGeometry(150, 100, 600, 400)