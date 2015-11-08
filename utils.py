import os
import sys

class Event:
    def __init__(self, event, target, data = None):
        self.event = event
        self.target = target
        self.data = data
    
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
    def dispatch(self, event, data = None):
        evt = Event(event, self, data)
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