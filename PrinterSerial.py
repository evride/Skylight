from serial import Serial
from serial.serialutil import SerialException
from threading import *
import time
import re
import os

class PrinterSerial(Serial):
    def __init__(self, port, baud):
        Serial.__init__(self)
        self.port = port
        self.baud = baud
        self.listeners = {}
        self.waiting = True
        self.detected = False
        self.readyMsg = ""
        self.repeatsWaiting = False
        self.messageEnd = b""
        self.inUse = False
        self.notFound = False
        self.connectionError = False
        self.lastSpeed = 1000
        self.statusRequest = False
        self.busy = False
        try:
            self.open()
        except SerialException as se:
            if os.name == "nt":
                if str(se).find('FileNotFoundError') >= 0:
                    self.notFound = True
                    self.dispatch('connection-error')
                elif str(se).find('PermissionError') >= 0:
                    self.inUse = True
            self.connectionError = True
            self.dispatch('connection-error')
            return
        detectThread = Thread(target=self.detectSetup)
        detectThread.start()
    def detectSetup(self):
        time.sleep(2)        
        currBytes = self.read(self.inWaiting())
        newlineRegex = re.compile(b"(\r\n|\n)")
        
        if re.match(b'grbl', currBytes) is not None:
            self.detected = True
            self.statusRequest = "$"
            self.readyMsg = b"idle"
            self.readyRegex = re.compile(self.readyMsg)
            self.dispatch('connected')
            return
        
        found = re.search(newlineRegex, currBytes)
        if found is not None:
            self.messageEnd = found.group(0)
        else:
            self.baudError = True
            self.dispatch("connection-error")
            return
        
        self.write("G91")
        time.sleep(.05)
        self.accepted = False
        while self.inWaiting() >=1:
            if self.accepted == False:
                self.accepted = self.readline()
            else:
                self.readline() #clears buffer
        time.sleep(2)
        if self.inWaiting() >= 1:
            repeatCount = 0
            self.waitingMessage = self.readline()
            while self.inWaiting() >= 1:
                if self.waitingMessage != self.readline():
                    self.waitingMessage = ""
                    self.repeatsWaiting = False
                repeatCount+=1
            if repeatCount >= 1:
                self.repeatsWaiting = True
                print("repeating", self.waitingMessage)
                
            
        self.dispatch('connected')
        '''
        checkCount = 0
        noDataCount = 0
        found = None
        while checkCount <= 3:
            checkCount+=1
            if self.inWaiting() >= 1:
                currBytes += self.read(self.inWaiting())
            else:
                noDataCount+=1
            if self.messageEnd == b"":
                found = re.search(newlineRegex, currBytes)
                if found is not None:
                    self.messageEnd = found.group(0)
                    checkCount = 0                
            time.sleep(.3)
        if self.messageEnd is not b"":
            lineSplit = re.split(newlineRegex, currBytes)
            repeatCount = 0
            for i in range(len(lineSplit)-1, 1, -1):
                if lineSplit[i] == lineSplit[i-1]: 
                    repeatCount+=1
                    self.readyMsg = lineSplit[i]
                else:
                    break
        elif self.messageEnd == b"":
            self.baudError = True
            self.dispatch("connection-error")
            return
        '''
    def waitForMessage(self, lookingFor, wait=0.1):
        lastBytes = 0
        waitingForData = True
        while self.isOpen() and waitingForData:
            time.sleep(wait)
            if lastBytes == self.inWaiting() and self.inWaiting() != 0:
                waitingForOK = False
    def waitForData(self):
        currBytes = b""
    def write(self, command):
        super(PrinterSerial, self).write(str(command + "\n").encode("ASCII"))# + self.messageEnd)
    def moveZ(self, distance, speed=1500):
        self.busy = True
        '''
            Temporary force speed to prevent issues
            Need further testing
        '''
        self.write("G1 F" + str(speed))
        self.lastSpeed = speed
        '''
            end temp code
        '''
        self.dispatch("move-start")
        self.write("G1 Z" + str(distance) + " F" + str(speed))
        timeToMove = abs(distance) / ((speed + self.lastSpeed) / 2) * 60
        if self.repeatsWaiting == False:
            Thread(target=self._sleepWait, args=[timeToMove]).start()
        self.lastSpeed = speed
    def _sleepWait(self, t):
        time.sleep(abs(t))
        moveCompleted = False
        if self.statusRequest != False:
            self.clearBuffer()
            while moveCompleted == False:
                self.write("$")
                time.sleep(.03)
                status = self.readline()
                if re.search(self.readyRegex, status) is not None:
                    moveCompleted = True
        self.busy = False
        self.dispatch("move-complete")
    def clearBuffer():
        if self.inWaiting() >= 1:
            self.read(self.inWaiting())
    def bind(self, event, func):
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(func)
    def dispatch(self, event):
        evt = {'event':event, 'target':self}
        if event in self.listeners:
            for i in range(0, len(self.listeners[event])):
                self.listeners[event][i](evt)
                 

if __name__ == "__main__":
    class TestObject():
        def dude(self, evt):
            self.count = 0
            print(evt['target'].readyMsg)
            print(evt['target'].inWaiting())
            evt['target'].moveZ(5, 400)
            print(evt['target'].inWaiting())
            if evt['target'].readline() == evt['target'].readyMsg:
                print("DUDEZ!")
        def complete(self, evt):
            print("complete")
            if self.count == 0:
                evt['target'].moveZ(-5, 400)
            elif self.count == 1:
                evt['target'].moveZ(-5, 200)
            elif self.count == 2:
                evt['target'].moveZ(-5, 500)
            elif self.count == 3:
                evt['target'].moveZ(5, 500)
            elif self.count == 4:
                evt['target'].moveZ(5, 300)
            self.count+=1
        def moveStart(self, evt):
            print("start")
        
    ps = PrinterSerial("COM6", 9600)
    to = TestObject()
    ps.bind("move-start", to.moveStart)
    ps.bind("move-complete", to.complete)
    ps.bind("connected", to.dude)
    print("asdf")
    #ps.moveZ(-5)
    