import sys
from PyQt5 import QtCore, QtGui, QtWidgets
class PrintWindow(QtWidgets.QWidget):
    def __init__(self, x, y, w, h):
        
        QtWidgets.QWidget.__init__(self)
        
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        
        self.scene = QtWidgets.QGraphicsScene()
        self.view  = QtWidgets.QGraphicsView(self.scene, frameShape=QtWidgets.QFrame.NoFrame)
        
        
        self.viewableAreaGraphic = QtWidgets.QGraphicsRectItem()
        self.viewableAreaGraphic.setBrush(QtGui.QBrush(QtGui.QColor('#F00')))
        
        self.layout.addWidget(self.view)
        self.resize(x, y, w, h)
        
    def preparePrint(self):
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))

    def clear(self):
        self.scene.clear()
    def drawShape(self, points, color):
        self.canvas.create_polygon(*points, fill=color, outline=color)
    def resize(self, x, y, w, h):
        self.setGeometry(x, y, w, h)
        
    def showArea(self, x, y, w, h):
        print(self.viewableAreaGraphic.parentItem())
        if (self.viewableAreaGraphic.parentItem() is None):
            self.scene.addItem(self.viewableAreaGraphic)
        self.viewableAreaGraphic.setRect(x, y, w, h)       
        
    def hideArea(self):
        print(self.viewableAreaGraphic.parentItem())
        if (self.viewableAreaGraphic.parentItem()):
            self.scene.remove(self.viewableAreaGraphic)