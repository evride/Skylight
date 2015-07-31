import sys
import os
import re
from math import *

numFloat = re.compile('^(\d*\.?\d*|\d+)$')
notNumFloat = re.compile('[^\d\.]+')
notNumInt = re.compile('[^\d]+')
numInt = re.compile('^\d+$')
anyNumInt = re.compile('\d')
dotRepeat = re.compile('\.+?s')
def validateFloat(var, field):
    temp = var.get()
    orig = temp
    changed = True
    if numFloat.match(temp) != None:
        changed = False
    else:
        temp = notNumFloat.sub('', temp)
        temp = dotRepeat.sub('.', temp)
        first = temp.find('.')
        if first != -1:
            second = temp.find('.', first+1)
            second = second if second != -1 else len(temp)
            temp = temp[0:second]
       
    
    if temp == "" and temp != orig:
        var.set(temp)
    elif re.search(anyNumInt, temp) != None:
        print("not none")
        if temp.find('.') == -1:
            temp = temp + ".0"
        num = float(temp)
        if num < field['from']:
            var.set(field['from'])
        elif num > field['to']:
            var.set(field['to'])
        elif changed:
            var.set(num)
def validateInt(var, field):
    temp = var.get()
    orig = temp
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
    if temp == "" and temp != orig:
        var.set(temp)
    elif temp != "":
        temp = int(temp)
        if temp < field['from']:
            var.set(field['from'])
        elif temp > field['to']:
            var.set(field['to'])
        elif changed:
            var.set(temp)
def parseFloat(s):
    try:
        n = float(s)
        return n
    except:
        s = str(s)
        #couldn't float
    s = notNumFloat.sub('', str(s))
    s = dotRepeat.sub('.', s)
    first = s.find('.')
    if first != -1:
        last = s.find('.', first+1)
        last = last if last != -1 else len(s)
        n = s[0:last]
        if re.search(anyNumInt, n) != None:
            n = float(n)
        else:
            n = 0
    else:
        if re.search(anyNumInt, s) == None:
            n = 0
        else:
            n = float(s)
    return n
def parseInt(s):
    try:
        n = int(s)
        return n
    except:
        s = str(s)        
        #couldn't int
    s = notNumFloat.sub('', str(s))
    n = 0
    if s.find('.') != -1:
        s = s[0:s.find('.')]
        if s != "":
            n = int(s)
    else:
        if s == "":
            n = 0
        else:
            n = int(s)
    return n
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