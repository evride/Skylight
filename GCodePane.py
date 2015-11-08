
from PyQt5 import QtOpenGL,  QtCore, QtGui, QtWidgets

class GCodePane(QtWidgets.QWidget):
    def __init__(self):    
        QtWidgets.QWidget.__init__(self)
        self.setupUi()
        self.app = QtWidgets.QApplication.instance()
    def setupUi(self):
        
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)        
        
        self.labelBeginGcode = QtWidgets.QLabel("Beginning GCode")
        self.inputBeginGcode = QtWidgets.QTextEdit()
        self.inputBeginGcode.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.inputBeginGcode.textChanged.connect(self.textChanged)
        
        
        self.labelPreliftGcode = QtWidgets.QLabel("Pre-Lift GCode")
        self.inputPreliftGcode = QtWidgets.QTextEdit()
        self.inputPreliftGcode.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.inputPreliftGcode.textChanged.connect(self.textChanged)
        
        self.labelPostliftGcode = QtWidgets.QLabel("Post-Lift GCode")
        self.inputPostliftGcode = QtWidgets.QTextEdit()
        self.inputPostliftGcode.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.inputPostliftGcode.textChanged.connect(self.textChanged)
        
        self.labelEndGcode = QtWidgets.QLabel("Ending GCode")
        self.inputEndGcode = QtWidgets.QTextEdit()
        self.inputEndGcode.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.inputEndGcode.textChanged.connect(self.textChanged)
        
        self.layout.addWidget(self.labelBeginGcode)
        self.layout.addWidget(self.inputBeginGcode)
        
        self.layout.addWidget(self.labelPreliftGcode)
        self.layout.addWidget(self.inputPreliftGcode)
        
        self.layout.addWidget(self.labelPostliftGcode)
        self.layout.addWidget(self.inputPostliftGcode)
        
        self.layout.addWidget(self.labelEndGcode)
        self.layout.addWidget(self.inputEndGcode)
    def textChanged(self):
        self.app.config.set('gcodeBegin', self.inputBeginGcode.toPlainText());
        self.app.config.set('gcodePrelift', self.inputPreliftGcode.toPlainText());
        self.app.config.set('gcodePostlift', self.inputPostliftGcode.toPlainText());
        self.app.config.set('gcodeEnd', self.inputEndGcode.toPlainText());
