from PyQt5 import QtCore, QtWidgets, QtGui, Qt
from utils import *
import serial
from serial.tools.list_ports import comports

class PrinterSetup(QtWidgets.QWidget):
    def __init__(self,app):
        QtWidgets.QWidget.__init__(self)
        self.app = app
        self.setupUI()
    def setupUI(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        
        self.quickView = ConfigQuickView()
        self.controllerSetup = ControllerSetup()
        self.monitorSelect = MonitorSelect()
        self.monitorCalibration = MonitorCalibration()
        self.layout.addWidget(self.quickView)
        self.quickView.bind("StartSetup", self.startNewSetup)
        
        self.controllerSetup.bind('Complete', self.stageComplete)
        self.monitorSelect.bind('Complete', self.stageComplete)
    def startNewSetup(self, event):
        print(event)
        self.quickView.setParent(None)
        self.layout.addWidget(self.controllerSetup)
    def stageComplete(self, event):
        if event.data['stage'] == "controller":
            self.controllerSetup.setParent(None)
            self.layout.addWidget(self.monitorSelect)
        if event.data['stage'] == "monitor-select":
            self.monitorSelect.setParent(None)
            self.layout.addWidget(self.monitorCalibration)
            self.monitorCalibration.configure(self.monitorSelect.selectedMonitor)
        print(event)
        
        
class ConfigQuickView(QtWidgets.QWidget, EventDispatcher):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        EventDispatcher.__init__(self)
        self.setupUi()
        self.setupListeners()
    def setupUi(self):
        
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)
        
        self.selectCreateLayout = QtWidgets.QHBoxLayout()
                
        self.printerSelect = QtWidgets.QComboBox()
        
        
        self.newSetupBtn = QtWidgets.QPushButton(text="New Printer")
        self.controllerGroup = QtWidgets.QGroupBox(title="Controller")
        self.monitorGroup = QtWidgets.QGroupBox(title="Monitor")
        
        self.layout.addLayout(self.selectCreateLayout)
        
        self.selectCreateLayout.addWidget(self.printerSelect)
        self.selectCreateLayout.addWidget(self.newSetupBtn)
        
        self.layout.addWidget(self.controllerGroup)
        self.layout.addWidget(self.monitorGroup)
        
        
        self.cGroupLayout = QtWidgets.QVBoxLayout(self.controllerGroup)
        self.mGroupLayout = QtWidgets.QVBoxLayout(self.monitorGroup)
        
        
        
    def setupListeners(self):
        self.newSetupBtn.clicked.connect(self.newSetupClicked)
        
    def newSetupClicked(self):
        self.dispatch("StartSetup")
        
class ControllerSetup(QtWidgets.QWidget, EventDispatcher):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        EventDispatcher.__init__(self)
        self.setupUi()
        self.populateComPorts()
    def setupUi(self):
        
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)
        
        self.groupBox = QtWidgets.QGroupBox(title="Controller")
        self.groupBoxLayout = QtWidgets.QVBoxLayout(self.groupBox)
        
        
        statusFrame = QtWidgets.QFrame(frameShape=QtWidgets.QFrame.Box)
        statusLayout = QtWidgets.QHBoxLayout(statusFrame)
        
        self.comPortSelect = QtWidgets.QComboBox()
        self.baudRateSelect = QtWidgets.QComboBox()
        self.connectBtn = QtWidgets.QPushButton(text="Connect")
        self.nextStepBtn = QtWidgets.QPushButton(text="Next")
        
        
        self.connectionLog = QtWidgets.QTextEdit()
        self.connectionLog.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.connectionLog.setReadOnly(True)
        
        self.baudRateSelect.addItems(['Select baud rate', '300', '1200', '2400', '4800', '9600', '19200', '38400', '57600', '115200', '230400', '250000', '2500000'])
        self.baudRateSelect.setEditable(True)
        intValid = QtGui.QIntValidator(bottom=0, top=9999999)
        self.baudRateSelect.setValidator(intValid)
        
        self.connectBtn.clicked.connect(self.connectClicked)
        self.nextStepBtn.clicked.connect(self.nextStep)
        
        
        self.layout.addWidget(self.groupBox)
        self.groupBoxLayout.addWidget(self.comPortSelect)
        self.groupBoxLayout.addWidget(self.baudRateSelect)
        self.groupBoxLayout.addWidget(self.connectBtn)
        self.layout.addWidget(self.connectionLog)
        self.layout.addWidget(statusFrame)
        statusLayout.addSpacerItem(QtWidgets.QSpacerItem(300, 10, hPolicy=QtWidgets.QSizePolicy.Expanding))
        statusLayout.addWidget(self.nextStepBtn)
    def populateComPorts(self):
        self.comPorts = serial.tools.list_ports.comports()
                
        for i in self.comPorts:
            if i[1] == 'n/a':
                self.comPortSelect.addItem(i[0])
            else:
                self.comPortSelect.addItem('[' + i[0] + '] - ' + i[1])
    def connectClicked(self, event):
        self.dispatch("Connect")
        print("connect")
    def nextStep(self, event):
        self.dispatch("Complete", {'stage':'controller'})

class MonitorSelect(QtWidgets.QGroupBox, EventDispatcher):
    def __init__(self):
        QtWidgets.QGroupBox.__init__(self, title="Select Projector Display")
        EventDispatcher.__init__(self)
        self.app = QtWidgets.QApplication.instance()
        
        self.selectedMonitor = -1;
        self.setupUi()
    def setupUi(self):
        
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)
        

        
        
        
        self.mScene = QtWidgets.QGraphicsScene()
        self.mGraphicsView  = QtWidgets.QGraphicsView(self.mScene)
       
        statusFrame = QtWidgets.QFrame(frameShape=QtWidgets.QFrame.Box)
        statusLayout = QtWidgets.QHBoxLayout(statusFrame)
        
        self.nextStepBtn = QtWidgets.QPushButton(text="Next")
        
        statusLayout.addSpacerItem(QtWidgets.QSpacerItem(300, 10, hPolicy=QtWidgets.QSizePolicy.Expanding))
        statusLayout.addWidget(self.nextStepBtn)
        
       
        self.layout.addWidget(self.mGraphicsView)
        self.layout.addWidget(statusFrame)
        
        
        self.mScene.update()
        
        
        minX = None
        minY = None
        maxX = None
        maxY = None
        maxWidth = None
        maxHeight = None
        self.monitorItems = []
        for i in range(0, self.app.desktop().screenCount()):
            dim = self.app.desktop().screenGeometry(i)
            if(minX is None or dim.x() < minX):
                minX = dim.x()
            if(maxX is None or dim.x() + dim.width() > maxX):
                maxX = dim.x() + dim.width()
            if(minY is None or dim.y() < minY):
                minY = dim.y()
            if(maxY is None or dim.y() + dim.height() > maxY):
                maxY = dim.x() + dim.height()   
            if(maxWidth is None or dim.width() > maxWidth):
                maxWidth = dim.width()
            if( maxHeight is None or dim.height() > maxHeight):
                maxHeight = dim.height()
            
            pItem = MonitorGraphicsItem(dim.width(), dim.height(), i)
            pItem.bind('click', self.monitorChanged)
            self.monitorItems.append(pItem)
            self.mScene.addItem(pItem)
           

        scaleX = (self.mGraphicsView.width() - 80) / (maxX - minX)
        scaleY = (self.mGraphicsView.height() - 80) / (maxY - minY)
        
        
        
        
        maxScaleX = (self.mGraphicsView.width() * 0.5) / maxWidth
        maxScaleY = (self.mGraphicsView.height() * 0.5) / maxHeight
        
        scale = min(scaleX, scaleY, maxScaleX, maxScaleY)
        
        
        self.mGraphicsView.scale(scale, scale)
        
        self.mScene.update()
        
        
        self.nextStepBtn.clicked.connect(self.nextStep)
        
    def monitorChanged(self, event):    
        for i in range(0, len(self.monitorItems)):
            self.monitorItems[i].setSelected(False)
            if( self.monitorItems[i] == event.target):
                self.selectedMonitor = i
            
        
        event.target.setSelected(True)
        print("monitorChanged", event)
    def nextStep(self, event):
        self.dispatch("Complete", {'stage':'monitor-select'})
        
class MonitorGraphicsItem(QtWidgets.QGraphicsRectItem, EventDispatcher):
        
    def __init__(self, width, height, num):
        QtWidgets.QGraphicsRectItem.__init__(self, 0, 0, width, height)
        EventDispatcher.__init__(self)
        
        self._selected = False
        
        self.setBrush(QtGui.QBrush(QtGui.QColor('#333')))
        self.setPen(QtGui.QPen(QtGui.QColor('#333'), 50, join = 0))
        self.numLabel = QtWidgets.QGraphicsTextItem(str(num), self)
        self.numLabel.setParentItem(self)
        self.numLabel.setDefaultTextColor(QtGui.QColor("#FFFFFF"))
        self.numLabel.setFont(QtGui.QFont('sans', 256))
        
        self.sizeLabel = QtWidgets.QGraphicsTextItem(str(width) + "x" + str(height), self)
        self.sizeLabel.setParentItem(self)
        self.sizeLabel.setDefaultTextColor(QtGui.QColor("#FFFFFF"))
        self.sizeLabel.setFont(QtGui.QFont('sans', 72))
        
        
        tRect = self.numLabel.boundingRect()
        self.numLabel.setX((width - tRect.width()) / 2)
        self.numLabel.setY((height - 150 - tRect.height()) / 2)
        
        sRect = self.sizeLabel.boundingRect()
        self.sizeLabel.setPos((width - sRect.width()) / 2, (height - sRect.height() - 100))
        
    def setSelected(self, sel):
        if sel == True:
            self.setPen(QtGui.QPen(QtGui.QColor('#0099FF'), 50, join = 0))
            self._selected =True
        else:
            self.setPen(QtGui.QPen(QtGui.QColor('#333'), 50, join = 0))
            self._selected = False
    def mousePressEvent(self, event):
        self.dispatch('click')
        
class MonitorCalibration(QtWidgets.QGroupBox, EventDispatcher):
    def __init__(self):
        QtWidgets.QGroupBox.__init__(self, title="Calibrate Projector")
        EventDispatcher.__init__(self)
        self.app = QtWidgets.QApplication.instance()
        
        self.setupUi()
    def setupUi(self):
        
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.mScene = QtWidgets.QGraphicsScene()
        self.mGraphicsView  = QtWidgets.QGraphicsView(self.mScene)
    def configure(self, num):
        self.monitorNum = num
        if( self.monitorNum < self.app.desktop().screenCount() ):
            print("works")
        self.redraw()
    def redraw(self):
        print("redraw")
        