    # worker.py
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import time

class ListenerWorker(QObject, dongle):
    finished = pyqtSignal()
    messageReady = pyqtSignal(str)
    self.d = dongle

    @pyqtSlot()
    def procCounter(self): # A slot takes no params
        capturedPackets = []
        pktcounter = 0
        print "recv Testing"

        while self.allowListening:
            try:
                rawdata, t = self.dongle.RFrecv(1)
                hexdata = rawdata.encode('hex')
                strength= 0 - ord(str(self.dongle.getRSSI()))

                if strength > -100:
                    pktcounter+=1
                    msg = "Packet: " + str(pktcounter) + " with Signal Strength:" + str(strength) + "with signal: " + str(hexdata) + "|| ASCII: " +  makeFriendlyAscii(rawdata)
                    capturedPackets.append(hexdata)

                self.messageReady.emit(msg)
                #Force update GUI
                #app.processEvents()

            except (KeyboardInterrupt):
                break
            except (ChipconUsbTimeoutException):
                pass
        self.dongle.setModeIDLE()



        for i in range(1, 100):
            time.sleep(1)
            self.intReady.emit(i)

        self.finished.emit()
