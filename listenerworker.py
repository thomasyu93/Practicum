"""---------------------------------------------------------------------------------------
--      SOURCE FILE:        listenworker.py - listener worker
--
--      PROGRAM:            RFSpoofer
--
--
--      DATE:               May 14, 2018
--
--      DESIGNERS:          Thomas Yu
--
--      PROGRAMMERS:        Thomas Yu
--
--      NOTES:
--      This file is responsible for listening for transmissions emitted. note
--      that this class is started as a thread from rfspoofer.py
---------------------------------------------------------------------------------------"""
    # worker.py
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from PyQt5 import QtCore
import os
import time
from rflib import *


class ListenerWorker(QObject, RfCat):
    def __init__(self, Rfcat):
        super(ListenerWorker, self).__init__()
        self.dongle = Rfcat
    finished = pyqtSignal()
    messageReady = pyqtSignal(str)
    saveReady= pyqtSignal(str)

    @pyqtSlot()
    def procListen(self): # A slot takes no params
        self.dongle.setRfMode(RFST_SRX)
        self.Listening = True
        capturedPackets = []
        pktcounter = 0
        while self.Listening:
            try:
                rawdata, t = self.dongle.RFrecv(1)
                hexdata = rawdata.encode('hex')
                strength= 0 - ord(str(self.dongle.getRSSI()))

                if strength > -100:
                    print("packet received")
                    pktcounter+=1
                    msg = "Packet: " + str(pktcounter) + ", Signal Strength: " + str(strength) + ", Transmission: " + str(hexdata) + ", ASCII: " +  makeFriendlyAscii(rawdata) + os.linesep
                    capturedPackets.append(hexdata)
                    self.messageReady.emit(msg)
                    saveMsg = str(pktcounter) + ', ' + str(hexdata) + os.linesep
                    self.saveReady.emit(saveMsg)

            except (KeyboardInterrupt):
                break
            except (ChipconUsbTimeoutException):
                pass
        print("finished")
        self.dongle.setModeRX()
        self.finished.emit()

    @pyqtSlot(str)
    def stopListen(self, foo):
        print("stopped called")
        self.Listening = False
