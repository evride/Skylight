import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from utils import *
from PrintHandler import *

class LayerView(QtWidgets.QGraphicsView):
    def __init__(self):
        
        self.scene = QtWidgets.QGraphicsScene()
        QtWidgets.QGraphicsView.__init__(self, self.scene)
        self.setupUi(self)
    def setupUi(self, Form):
        
        self.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(0,0,0)))
    
    def drawLayer(self, layerData):
        self.scene.clear()
        
        for h in range(0, len(layerData)):
            poly = QtGui.QPolygonF()
            i = 0
            while i < len(layerData[h]['points']):
                poly.append(QtCore.QPointF(layerData[h]['points'][i], layerData[h]['points'][i+1]))
                i+=2
            pItem = QtWidgets.QGraphicsPolygonItem(poly)
            
            pItem.setBrush(QtGui.QBrush(QtGui.QColor(layerData[h]['color'])))
            pItem.setPen(QtGui.QPen(QtGui.QColor(layerData[h]['color'])))
            
            self.scene.addItem(pItem)
        
        self.scene.update()