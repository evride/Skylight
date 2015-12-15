import struct
import re
class STLReader():
    def __init__(self):     
        self.header = ''
        self.triangles = []
    def load(self,filename):
        self.file = open(filename, 'rb')
        self.header = self.file.read(80)
        
        
        if re.search(b'\s*solid', self.header) is not None:
            self.binary = False
            self.file.close()
            self.file = open(filename, 'r')
            self.readAscii()
        else:
            self.binary = True
            self.readBinary()
    def readBinary(self):
        self.numTriangles = struct.unpack('i', self.file.read(4))[0]
        for i in range(0, self.numTriangles):
            self.triangles.append([
                [struct.unpack('f', self.file.read(4))[0], struct.unpack('f', self.file.read(4))[0], struct.unpack('f', self.file.read(4))[0]], #nX,nY,nZ
                [struct.unpack('f', self.file.read(4))[0], struct.unpack('f', self.file.read(4))[0], struct.unpack('f', self.file.read(4))[0]], #x1,y1,z1
                [struct.unpack('f', self.file.read(4))[0], struct.unpack('f', self.file.read(4))[0], struct.unpack('f', self.file.read(4))[0]], #x2,y2,z2
                [struct.unpack('f', self.file.read(4))[0], struct.unpack('f', self.file.read(4))[0], struct.unpack('f', self.file.read(4))[0]]  #x3,y3,z3
            
            ])
            self.file.read(2) #typically unused 16bit uint
    def translate(self, x, y, z):
        for i in range(0, self.numTriangles):
            for a in range(1,4):
                self.triangles[i][a][0] += x
                self.triangles[i][a][1] += y
                self.triangles[i][a][2] += z
    def dimensions(self):
        dim = {'minX':None, 'minY':None, 'minZ':None, 'maxX':None, 'maxY':None, 'maxZ':None}
        
        for i in range(0, self.numTriangles):
            for a in range(1,4):
                if (dim['minX'] == None or dim['minX'] > self.triangles[i][a][0]):
                    dim['minX'] = self.triangles[i][a][0];
                elif (dim['maxX'] == None or dim['maxX'] < self.triangles[i][a][0]):
                    dim['maxX'] = self.triangles[i][a][0];
                    
                if (dim['minY'] == None or dim['minY'] > self.triangles[i][a][1]):
                    dim['minY'] = self.triangles[i][a][1];
                elif (dim['maxY'] == None or dim['maxY'] < self.triangles[i][a][1]):
                    dim['maxY'] = self.triangles[i][a][1];
                    
                if (dim['minZ'] == None or dim['minZ'] > self.triangles[i][a][2]):
                    dim['minZ'] = self.triangles[i][a][2];
                elif (dim['maxZ'] == None or dim['maxZ'] < self.triangles[i][a][2]):
                    dim['maxZ'] = self.triangles[i][a][2];
        dim['width'] = dim['maxX'] - dim['minX']
        dim['depth'] = dim['maxY'] - dim['minY']
        dim['height'] = dim['maxZ'] - dim['minZ']
        
        return dim
    
    def readAscii(self):
        self.header = self.file.readline()
        
        v = 0
        triangleCount = 0
        loopCount = 0
        line = self.file.readline()
        while True:
            if not line:
                break
                
            data = re.split('\s+', line.strip())
            if data[0] == "facet":
                face = []
                face.append([float(data[2]), float(data[3]), float(data[4])])
                triangleCount += 1
                v = 0
            elif data[0] == "outer":
                v = 0
            elif data[0] == "vertex":
                face.append([float(data[1]), float(data[2]), float(data[3])])
                v+=1
            elif data[0] == "endloop":
                self.triangles.append(face)
                face = None
                v = 0
            elif data[0] == "endfacet":
                #endfacet
                v = 0
            elif data[0] == "endsolid":
                v = 0
                #endsolid
                
            line = self.file.readline()
        
        self.numTriangles = len(self.triangles)
        if self.numTriangles != triangleCount:
            print("triangle count error", self.numTriangles, triangleCount)
        
if __name__ == '__main__':

    import sys
    r = STLReader()
    r.load('teapot.stl')
    