import sys
import os
import re

numFloat = re.compile('^(\d*\.?\d*|\d+)$')
notNumFloat = re.compile('[^\d\.]+')
notNumInt = re.compile('[^\d]+')
numInt = re.compile('^\d+$')
dotRepeat = re.compile('\.+?s')
def validateFloat(var, field):
    temp = var.get()
    changed = True
    if numFloat.match(temp) != None:
        changed = False
    temp = dotRepeat.sub('.', temp)
    first = temp.find('.')
    if first != -1:
        second = temp.find('.', first)
        second = second if second != -1 else len(temp)
        temp = temp[0:second]
    temp = float(temp)
    if temp < field['from']:
        var.set(field['from'])
    elif temp > field['to']:
        var.set(field['to'])
    elif changed:
        var.set(temp)
def validateInt(var, field):
    temp = var.get()
    changed = True
    if numInt.match(temp) != None:
        changed = False
    else:
        temp = notNumFloat.sub('', temp)
        if temp.find('.') == 0:
            temp = '0'
        elif temp.find('.') >= 1:
            temp = temp[0:temp.find('.')]
        if temp == '':
            temp = '0'
            
    temp = int(temp)
    if temp < field['from']:
        var.set(field['from'])
    elif temp > field['to']:
        var.set(field['to'])
    elif changed:
        var.set(temp)
    
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