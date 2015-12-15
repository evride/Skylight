import sys
import math

from PyQt5 import QtOpenGL,  QtCore, QtGui, QtWidgets

from PyQt5.QtCore import Qt

from OpenGL import GL
from OpenGL import GLU
    
class Object3dView(QtWidgets.QOpenGLWidget):
    xRotationChanged = QtCore.pyqtSignal(int)
    yRotationChanged = QtCore.pyqtSignal(int)
    zRotationChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super(Object3dView, self).__init__(parent)
        

        self.object = 0
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        self._width = 0
        self._height = 0
        self.scale = 1
        self.drawList = []
        self.lastPos = QtCore.QPoint()
    def wheelEvent(self, evt):
        self.scale = self.scale + self.scale * evt.angleDelta().y() / 600
        #self.resizeGL(self._width, self._height)
        self.update()
    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    def setXRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.xRot:
            self.xRot = angle
            self.xRotationChanged.emit(angle)
            self.update()

    def setYRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.yRot:
            self.yRot = angle
            self.yRotationChanged.emit(angle)
            self.update()

    def setZRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.zRot:
            self.zRot = angle
            self.zRotationChanged.emit(angle)
            self.update()

    def initializeGL(self):
        self.gl = GL
        self.glu = GLU
        print("OpenGL: " + str(self.gl.glGetString(self.gl.GL_VERSION)))
        print("GLSL: " + str(self.gl.glGetString(self.gl.GL_SHADING_LANGUAGE_VERSION)))
        self.setClearColor(QtGui.QColor("#000000"))
        self.object = self.drawGrid(400, 20)
        self.gl.glShadeModel(self.gl.GL_FLAT)
        self.gl.glEnable(self.gl.GL_BLEND)
        self.gl.glEnable(self.gl.GL_DEPTH_TEST)
        self.gl.glEnable(self.gl.GL_CULL_FACE)
        self.gl.glEnable(self.gl.GL_LINE_SMOOTH)
        self.gl.glBlendFunc (self.gl.GL_SRC_ALPHA, self.gl.GL_ONE_MINUS_SRC_ALPHA)
    def paintGL(self):
        self.gl.glClear(
                self.gl.GL_COLOR_BUFFER_BIT | self.gl.GL_DEPTH_BUFFER_BIT)
        self.gl.glLoadIdentity()
        self.gl.glTranslated(0.0, 0.0, -10.0)
        self.gl.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        self.gl.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        self.gl.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        self.gl.glScale(self.scale * 0.1, self.scale * 0.1, self.scale * 0.1)
        for i in range(0, len(self.drawList)):
            self.gl.glCallList(self.drawList[i])

    def resizeGL(self, width, height):
        self._width = width
        self._height = height
        side = min(width, height)
        if side < 0:
            return
        self.gl.glViewport(0, 0, width, height)

        self.gl.glMatrixMode(self.gl.GL_PROJECTION)
        self.gl.glLoadIdentity()
        self.glu.gluPerspective(70, width/height, 1.0, 1000)
        #self.gl.glOrtho(-width/2, width/2, height/2, -height/2, -10000, 10000.0)
        self.gl.glMatrixMode(self.gl.GL_MODELVIEW)
        
    def drawGrid(self, size, sections):
        self.plane = True
        
        genList = self.gl.glGenLists(1)
        self.gl.glNewList(genList, self.gl.GL_COMPILE)
        
        '''self.gl.glBegin(self.gl.GL_TRIANGLES)
        self.gl.glColor4f(0.8, 0.0, 0.0,0.3)
        
        self.gl.glVertex3d(0.0, 0.3, -0.05)
        self.gl.glVertex3d(0.3, 0.3, -0.05)
        self.gl.glVertex3d(0.3, 0.0, -0.05)
        
        self.gl.glVertex3d(0.0, 0.0, -0.05)
        self.gl.glVertex3d(0.0, 0.3, -0.05)
        self.gl.glVertex3d(0.3, 0.0, -0.05)
        self.gl.glEnd()
        '''
        
        self.gl.glBegin(self.gl.GL_QUADS)
        self.gl.glColor4f(0.8, 0.0, 0.0,0.3)
        
        self.gl.glVertex3d(-size/2, -size/2, -0.05)
        self.gl.glVertex3d(-size/2, size/2,  0)
        self.gl.glVertex3d(size/2, size/2,  0)
        self.gl.glVertex3d(size/2, -size/2,  0)
        self.gl.glEnd()
        
        
        self.gl.glLineWidth(2.0)
        self.gl.glPolygonMode(self.gl.GL_FRONT_AND_BACK,self.gl.GL_LINE)
        self.gl.glBegin(self.gl.GL_LINES)
        self.gl.glColor4f(0, 0.0, 0.8,1.0)
        
        for i in range(0, sections+1):
            offset = i * size / sections - size / 2
            self.gl.glVertex3d(offset, -size/2, -0.1)
            self.gl.glVertex3d(offset, size/2, -0.1)
            self.gl.glVertex3d(-size/2, offset, -0.1)
            self.gl.glVertex3d(size/2, offset, -0.1)
        
        self.gl.glEnd()
        self.gl.glPolygonMode(self.gl.GL_FRONT_AND_BACK,self.gl.GL_FILL); 
        self.gl.glEndList()
        
        self.drawList.append(genList)

        return genList
        
    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & Qt.LeftButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setYRotation(self.yRot + 8 * dx)
        elif event.buttons() & Qt.RightButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setZRotation(self.zRot + 8 * dx)

        self.lastPos = event.pos()
    def addObject(self, filename):
        import STLReader
        s = STLReader.STLReader()
        s.load(filename)
        
        dim = s.dimensions()
        s.translate(0, 0, -dim['minZ'])
        
        
        genList = self.gl.glGenLists(1)
        self.gl.glNewList(genList, self.gl.GL_COMPILE)
        
        self.gl.glBegin(self.gl.GL_TRIANGLES)
        
        self.gl.glColor4f(0, .5, .8,1.0)
        for i in range(0, s.numTriangles):
            self.gl.glNormal(s.triangles[i][0][0], s.triangles[i][0][1], s.triangles[i][0][2])
            for a in range(1,4):
                self.gl.glVertex3d(s.triangles[i][a][0], s.triangles[i][a][1], s.triangles[i][a][2])
        self.gl.glEnd()
        self.gl.glEndList()
        
        self.drawList.append(genList)
        return genList
        
    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle

    def setClearColor(self, c):
        self.gl.glClearColor(c.redF(), c.greenF(), c.blueF(), c.alphaF())

    def setColor(self, c):
        self.gl.glColor4f(c.redF(), c.greenF(), c.blueF(), c.alphaF())

