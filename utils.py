import sys
import os
import re

numeric = re.compile('[0-9\.]+')
def validateDim(var, field):
    temp = var.get()
    if re.search(numeric, temp) == None:
        var.set(float(field['from']))
    elif float(temp) < field['from']:
        var.set(float(field['from']))
    elif float(temp) > field['to']:
        var.set(float(field['to']))
class EventDispatcher:
    def __init__(self):
        self.listeners = {}
    def unbind(self, event, func = "all"):
        if event in self.listeners:
            if func == "all":
                self.listeners[event] = []
            elif func in self.listeners[event]:
                self.listeners[event].pop(self.listeners[event].index(func))
    def unbindAll(self):
        self.listeners = {}        
    def bind(self, event, func):
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(func)
    def dispatch(self, event):
        evt = {'event':event, 'target':self}
        if event in self.listeners:
            for i in range(0, len(self.listeners[event])):
                self.listeners[event][i](evt)
def currentDir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))
def appdataDir():
    dir_path = '%s\\Skylight\\' %  os.environ['APPDATA'] 
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path