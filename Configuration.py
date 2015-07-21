import re
import time
import json
class Configuration:
    def __init__(self):
        self.data = {}
        self.displays = {}
        self.setDefault()
        self.read()
    def set(self, key, value):
        self.data[key] = value
    def get(self, key):
        val = None
        if key in self.data:
            val = self.data[key]
        return val
    def save(self):
        f = open('settings.ini', 'w')
        json.dump({'settings':self.data, 'displays':self.displays}, f)
        f.close()
    def saveDisplay(self, id, settings):
        self.displays[id] = settings
    def getDisplay(self, id):
        if id in self.displays:
            return self.displays[id]
        else:
            return {}
    def setDefault(self):
        self.data['layerHeight'] = 0.1
        self.data['exposureTime'] = 500
        self.data['startingExposureTime'] = 800
        self.data['startingLayers'] = 3
        self.data['postPause'] = 0
        self.data['retractDistance'] = 500
        self.data['retractSpeed'] = 500
    def read(self):
        try:
            f = open('settings.ini', 'r')
            jsonData = json.load(f)
            
            f.close()
        except:
            print("can't open file")
    def monitorInfo(self, hash):
        id = hash[0:hash.find(':')]
        dim = re.split(',', hash[hash.find(':')+1:])
        return {'id': id, 'x':dim[0], 'y':dim[1], 'width':dim[2], 'height':dim[3]}
    def monitorHash(self, id, x, y, w, h):
        return str(id) + ':' + str(x) + ',' + str(y) + ',' + str(w) + ',' + str(h)

if __name__ == "__main__":
    c = Configuration()
    c.save()