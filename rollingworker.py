    # worker.py
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from PyQt5 import QtCore
import time
import bitstring
from rflib import *


class RollingWorker(QObject, RfCat):
    def __init__(self, Rfcat):
        super(RollingWorker, self).__init__()
        self.dongle = Rfcat
    finished = pyqtSignal()
    messageReady = pyqtSignal(str)
    jamStart = pyqtSignal(str)
    jamStop = pyqtSignal(str)
    @pyqtSlot()
    def procListen(self): # A slot takes no params

        self.Listening = True
        capturedPackets = []
        pktcounter = 0
        #self.messageReady.emit("Listening...\n")
        while self.Listening:
            try:
                rawdata, t = self.dongle.RFrecv(1)
                hexdata = rawdata.encode('hex')
                strength= 0 - ord(str(self.dongle.getRSSI()))

                if strength > -100:
                    print("packet received")
                    pktcounter+=1
                    msg = "Packet: " + str(pktcounter) + ", with Signal Strength:" + str(strength) + ", with signal: " + str(hexdata) + " , ASCII: " +  makeFriendlyAscii(rawdata) +'\n'
                    capturedPackets.append(hexdata)
                    self.messageReady.emit(msg)
                #Force update GUI
                #app.processEvents()
                ''' 
                    if pktcounter > 1:
                        time.sleep(0.5)
                        self.jamStop.emit("")
                        print("sending packet")
                        bytePacket = bitstring.BitArray(hex=capturedPackets[pktcounter -2]).tobytes()
                        self.dongle.makePktFLEN(len(bytePacket))
                        self.dongle.RFxmit(bytePacket)
                        self.jamStart.emit("")

                '''
            except (KeyboardInterrupt):
                break
            except (ChipconUsbTimeoutException):
                pass
        print("finished")
        self.dongle.setModeIDLE()


    @pyqtSlot(str)
    def stopListen(self, foo):
        print("stopped called")
        self.Listening = False
