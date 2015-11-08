import re
import time
import json
from utils import *
class Configuration:
    def __init__(self):
        self.data = {}
        self.displays = {}
        self.controllers = {}
        self.read()
    def set(self, key, value):
        self.data[key] = value
    def get(self, key):
        val = None
        if key in self.data:
            val = self.data[key]
        return val
    def unset(self, key):
        if key in self.data:
            del self.data[key]
    def save(self):
        f = open(appdataDir() + 'settings.ini', 'w')
        json.dump({'settings':self.data, 'displays':self.displays}, f)
        f.close()
    def saveDisplay(self, id, settings):
        self.displays[id] = settings
    def getDisplay(self, id):
        if id in self.displays:
            return self.displays[id]
        else:
            return {}
    # def setDefault(self):
        # self.data['layerHeight'] = 0.1
        # self.data['exposureTime'] = 500
        # self.data['startingExposureTime'] = 800
        # self.data['startingLayers'] = 3
        # self.data['postPause'] = 0
        # self.data['retractDistance'] = 500
        # self.data['retractSpeed'] = 200
        # self.data['returnSpeed'] = 500
        # self.data['prePause'] = 0
    def read(self):
        try:
            f = open(appdataDir() + 'settings.ini', 'r')
            jsonData = json.load(f)
            self.data = jsonData['settings']
            self.displays = jsonData['displays']
        except:
            print("can't load file")
    def monitorInfo(self, hash):
        id = hash[0:hash.find(':')]
        dim = re.split(',', hash[hash.find(':')+1:])
        if len(dim) == 4:
            return {'id': id, 'x':dim[0], 'y':dim[1], 'width':dim[2], 'height':dim[3]}
        else:
            return None
    def monitorHash(self, id, x, y, w, h):
        return str(id) + ':' + str(x) + ',' + str(y) + ',' + str(w) + ',' + str(h)
    def reset(self):
        self.data = {}
        self.displays = {}
        self.controllers = {}
        self.save()
        self.setDefault()

if __name__ == "__main__":
    c = Configuration()
    c.save()