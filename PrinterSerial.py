from serial import Serial
from serial.serialutil import SerialException
from threading import *
import time
import re
import os
from utils import *

class PrinterSerial(Serial, EventDispatcher):
    def __init__(self, port, baud):
        Serial.__init__(self)
        EventDispatcher.__init__(self)
        self.port = port
        self.baudrate = baud
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
        self._stopping = False
        self.connecting = True
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
        if re.search(b'grbl(?i)', currBytes) is not None:
            print("matched grbl")
            self.detected = True
            self.statusRequest = "?"
            self.readyMsg = b"idle(?i)"
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
        if self.inWaiting() >=1:
            self.accepted = self.readline()
        self.clearBuffer()
        time.sleep(3)
        if self.inWaiting() >= 1:
            repeatCount = 0
            self.waitingMessage = self.readline()
            while self.inWaiting() >= 1:
                tempWaitMsg = self.readline()
                if self.waitingMessage != tempWaitMsg:
                    self.waitingMessage = tempWaitMsg
                    repeatCount = 0
                repeatCount+=1
            if repeatCount >= 2:
                self.repeatsWaiting = True
                self.readyRegex = re.compile(self.waitingMessage)
                print("repeating", repeatCount, self.waitingMessage)
        
        self.detected = True
        self.connecting = False
        self.dispatch('connected')
    def write(self, command):
        super(PrinterSerial, self).write(str(command + "\n").encode("ASCII"))# + self.messageEnd)
    def moveZ(self, distance, speed=1500):
        if self._stopping == True and self.busy == False:
            return
            
        distance = float(distance)
        speed = float(speed)
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
        if self.repeatsWaiting or self.statusRequest:
            Thread(target=self._sleepWait, args=[timeToMove]).start()
        self.lastSpeed = speed
    def _sleepWait(self, t):
        print("_sleepWait")
        time.sleep(abs(t))
        moveCompleted = False
        self.clearBuffer()
        if self.statusRequest == False and self.repeatsWaiting == False:
            moveCompleted = True
        elif self.statusRequest != False:
            self.write(self.statusRequest)
        while moveCompleted == False:
            bytesReceived = 0
            while bytesReceived == 0:
                bytesReceived = self.inWaiting()
                time.sleep(.01)
            status = self.readline()
            print(status)
            if re.search(self.readyRegex, status) is not None:
                moveCompleted = True
        self.busy = False
        self.dispatch("move-complete")
    def stopAndClose(self):
        self.write('M18')
        self.write('M2')
        self._stopping = True
        self.unbind('move-complete')
        self.unbind('move-start')
        if self.busy == True:
            self.bind('move-complete', self.close)
        elif self.busy == False:
            self.close()
    def close(self):
        super(PrinterSerial, self).close()
        self.dispatch('connection-close')
    def clearBuffer(self):
        if self.inWaiting() >= 1:
            self.read(self.inWaiting())
                 

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
    