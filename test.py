#!/usr/bin/env
import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtCore
from pymongo import MongoClient
from pprint import pprint
from mongoAPI import *
import listenerworker,jamworker, rollingworker, transmitworker
import threading
import readline
import rlcompleter
import time
readline.parse_and_bind("tab: complete")
from rflib import *



#Globals
#Default Values
#frequency = 314350000
baudRate = 4800
FSK2 = "MOD_2FSK"
chanWidth = 24000
chanBW = 70000

class Display(QWidget):
    def __init__(self):
        super(Display, self).__init__()
        self.allowListening = True
        self.initUI()
        self.initConnection()
    def initUI(self):
        self.fileName = "waves.txt"
        self.setFixedSize(1100, 500)
        self.setWindowTitle('RF Spoofer')
        #label = QLabel('RF Spoofer')
        layout = QGridLayout()
        #layout.addWidget(label)
        self.testButton = QPushButton('Initialize', self)
        self.listenButton = QPushButton('Listen', self)
        self.sendButton = QPushButton('Transmit File', self)
        self.jamButton = QPushButton('Jam', self)
        self.stopButton = QPushButton('Stop', self)
        self.exitButton = QPushButton('Exit', self)
        self.rollingButton = QPushButton('Rolling Attack', self)
        self.ListButton = QPushButton('Database List', self)
        self.DataSendButton = QPushButton('Transmit from Database ', self)
        self.testButton.setStyleSheet("background-color:green")
        self.jamButton.setStyleSheet("background-color:orange")
        self.exitButton.setStyleSheet("background-color: red")


        #self.stopButton.setEnabled(False)
        self.listenButton.setEnabled(False)
        self.sendButton.setEnabled(False)
        self.jamButton.setEnabled(False)
        self.rollingButton.setEnabled(False)
        self.ListButton.setEnabled(False)
        self.DataSendButton.setEnabled(False)

        self.testButton.clicked.connect(self.handleButtonTest)
        self.exitButton.clicked.connect(self.closeEvent)
        self.listenButton.clicked.connect(self.handleButtonListen)
        self.stopButton.clicked.connect(self.handleButtonStop)
        self.jamButton.clicked.connect(self.handleButtonJam)
        self.rollingButton.clicked.connect(self.handleButtonRolling)
        self.sendButton.clicked.connect(self.handleButtonSend)
        self.ListButton.clicked.connect(self.handleButtonList)
        self.DataSendButton.clicked.connect(self.handleButtonDataSend)

        self.modLabel = QLabel('Modulation:')
        layout.addWidget(self.modLabel,2,5)
        self.b1 = QRadioButton("2FSK")
        self.b1.setChecked(True)
        self.b1.toggled.connect(lambda:self.radioButtonState(self.b1))
        layout.addWidget(self.b1,3,5)

        self.b2 = QRadioButton("ASK")
        self.b2.toggled.connect(lambda:self.radioButtonState(self.b2))
        layout.addWidget(self.b2,3,6)

        self.frequencyLabel = QLabel('Frequency (Hz):')
        self.frequencyLine = QLineEdit('314350000')
        self.frequencyLabel.setFixedWidth(100)
        self.frequencyLine.setFixedWidth(100)

        self.baudLabel = QLabel('Baud Rate (bps):')
        self.BaudLine = QLineEdit('4800')
        self.baudLabel.setFixedWidth(100)
        self.BaudLine.setFixedWidth(100)


        #self.dlg.setFilter("*.txt")
        #self.filenames = QStringList()

        self.fileLineEdit = QLineEdit("Please Select File")
        #self.fileLineEdit.setFixedWidth(100)
        self.fileButton = QPushButton("Select File")
        self.fileLineEdit.setReadOnly(True)
        self.fileLabel = QLabel("File Save Location: ")
        self.fileButton.clicked.connect(self.handleButtonFile)

        layout.addWidget(self.fileLabel,18,0)
        layout.addWidget(self.fileLineEdit,18,1,1,3)
        layout.addWidget(self.fileButton,18,4)
        layout.addWidget(self.frequencyLabel,0,5)
        layout.addWidget(self.frequencyLine,0,6)
        layout.addWidget(self.baudLabel,1,5)
        layout.addWidget(self.BaudLine,1,6)

        #layout.addRow(self.frequencyLabel,self.frequencyLine)


        self.text = QTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text,0,0,18,5)


        layout.addWidget(self.testButton,19,0)
        layout.addWidget(self.listenButton,19,1)
        layout.addWidget(self.sendButton,19,2)
        layout.addWidget(self.jamButton,19,3)
        layout.addWidget(self.stopButton,19,4)
        layout.addWidget(self.rollingButton,19,5)
        layout.addWidget(self.ListButton,18,5)
        layout.addWidget(self.exitButton,19,6)
        layout.addWidget(self.DataSendButton, 19,5)

        #layout.setColumnStretch(0, 1)
        #layout.setColumnStretch(1, 3)
        #layout.setRowStretch(0, 3)
        #layout.setRowStretch(1, 1)
        #layout.setAlignment(Qt.AlignRight)
        self.setLayout(layout)

    def initConnection(self):
        client = MongoClient('mongodb://admin:admin@ds241019.mlab.com:41019/practicum')
        db=client.practicum
        self.transmissions = db.transmissions

    def handleButtonDataSend(self):
        idnum = self.getint()
        tData = getTransmissions(self.transmissions, idnum)


        self.dSendObj = transmitworker.TransmitWorker(self.dongle, tData)
        self.thread = QThread()

        self.dSendObj.messageReady.connect(self.onMessageReady)

        self.dSendObj.moveToThread(self.thread)
        self.dSendObj.finished.connect(self.thread.quit)

        self.thread.started.connect(self.dSendObj.procTransmit)
        self.thread.start()
        self.text.append("starting sending...")

    def getint(self):
        num,ok = QInputDialog.getInt(self,"integer input dualog","enter the ID number")
        if ok:
            return num

    def handleButtonSend(self):
        fileTransmits = getFromFile(self.fileName)
        rawTransmits = []
        for transmit in fileTransmits:
            rawTransmits.append(transmit[1].rstrip())
            #print(transmit[1].rstrip())


        self.repObj = transmitworker.TransmitWorker(self.dongle, rawTransmits)
        self.thread = QThread()

        self.repObj.messageReady.connect(self.onMessageReady)

        self.repObj.moveToThread(self.thread)
        self.repObj.finished.connect(self.thread.quit)

        self.thread.started.connect(self.repObj.procTransmit)
        self.thread.start()
        self.text.append("starting sending...")



    def handleButtonList(self):
        results = getAllTransmissions(self.transmissions)
        for res in results:
            msg = "ID : " + str(res["idnum"]) + " pktnum: " + str(res["pktnum"]) + " tdata: " +  str(res["tData"])
            self.text.append(msg)

    def handleButtonFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if self.fileName:
           self.fileLineEdit.setText(self.fileName)
        self.fileName = os.path.basename(self.fileName)
        print(self.fileName)
    def handleButtonTest(self):
        self.text.append("Initializing...")

        #Force update GUI
        app.processEvents()
        frequency = int(self.frequencyLine.text())

        try:
            self.initDongle(2,frequency)
        except (ChipconUsbTimeoutException):
            self.text.append('Timd out... try again later')
            return
        except Exception as e:
            self.text.append(str(e))
            self.text.append('Dongle is busy, please try again later')
            return
        self.text.append("Initializing succesful:")

        self.text.append("Dongle 1:")
        self.text.append(self.dongle.reprHardwareConfig())
        self.text.append(self.dongle.reprSoftwareConfig())
        self.text.append(self.dongle.reprMdmModulation())
        self.text.append(self.dongle.reprFreqConfig())
        self.text.append(self.dongle.reprModemConfig() + "\n")
        try:
            self.text.append("Dongle 2:")
            self.text.append(self.dongle2.reprHardwareConfig())
            self.text.append(self.dongle2.reprSoftwareConfig())
            self.text.append(self.dongle2.reprMdmModulation())
            self.text.append(self.dongle2.reprFreqConfig())
            self.text.append(self.dongle2.reprModemConfig() + "\n")
        except:
            pass

        self.listenButton.setEnabled(True)
        self.sendButton.setEnabled(True)
        self.jamButton.setEnabled(True)
        self.stopButton.setEnabled(True)
        self.rollingButton.setEnabled(True)
        self.ListButton.setEnabled(True)
        self.DataSendButton.setEnabled(True)

    def initDongle(self,numOfDongles,freq):
        self.numOfDongles = numOfDongles
        if numOfDongles==1:
            self.dongle= RfCat()
            self.dongle.setFreq(freq)
            self.dongle.setMdmModulation(MOD_2FSK)
            self.dongle.setMdmDRate(baudRate)
            self.dongle.setMaxPower()
            self.dongle.lowball(1)
            self.dongle.makePktFLEN(255)
            self.dongle.setChannel(0)
        else:
            try:
                #Listen Dongle
                self.dongle= RfCat(idx=0)
                self.dongle.setFreq(freq)
                self.dongle.setMdmModulation(MOD_2FSK)
                self.dongle.setMdmDRate(baudRate)
                self.dongle.setMaxPower()
                self.dongle.lowball(1)
                self.dongle.setMdmChanBW(chanBW)
                self.dongle.setMdmChanSpc(chanWidth)
                self.dongle.makePktFLEN(255)
                self.dongle.setChannel(0)
            except Exception as e :
                #print(str(e))
                self.text.append("Error in setting up usb1")
                self.text.append(str(e))
                #print ('index out of range')
                pass

                #time.sleep(2)
            try:
                #Jam dongle
                jamFreq = freq - 400000
                self.dongle2= RfCat(idx=1)
                self.dongle2.setFreq(jamFreq)
                self.dongle2.setMdmModulation(MOD_2FSK)
                self.dongle2.setMdmDRate(baudRate)
                #self.dongle2.setMaxPower()
                self.dongle2.setPower(50)
                self.dongle2.lowball(1)
                self.dongle2.setMdmChanBW(chanBW)
                self.dongle2.setMdmChanSpc(chanWidth)
                self.dongle2.makePktFLEN(255)
                self.dongle2.setChannel(0)
            except Exception as e :
                #print(str(e))
                self.text.append("error in setting up usb2")
                self.text.append(str(e))
                #print ('index out of range')
                pass


    def handleButtonRolling(self):
        self.objRoll = rollingworker.RollingWorker(self.dongle)
        self.thread = QThread()

        self.objRoll.messageReady.connect(self.rollingMessageReady)
        self.objRoll.saveReady.connect(self.onSaveReady)


        self.objRoll.jamStart.connect(self.jamStartReady)
        self.objRoll.jamStop.connect(self.jamStopReady)


        self.objRoll.moveToThread(self.thread)
        self.objRoll.finished.connect(self.thread.quit)

        self.thread.started.connect(self.objRoll.procListen)
        self.thread.start()


        self.objJam = jamworker.JamWorker(self.dongle2)
        self.jamThread = QThread()

        self.objJam.jamMessageReady.connect(self.onMessageReady)

        self.objJam.moveToThread(self.jamThread)
        self.objJam.finished.connect(self.jamThread.quit)

        self.jamThread.started.connect(self.objJam.procJam)
        self.jamThread.start()


    #Thread handle
    def handleButtonListen(self):
        #t1 = threading.Thread(target=self.listenThreadWorker)
        #t1.start()


        self.obj = listenerworker.ListenerWorker(self.dongle)
        self.thread = QThread()

        self.obj.messageReady.connect(self.onMessageReady)
        self.obj.saveReady.connect(self.onSaveReady)

        self.obj.moveToThread(self.thread)
        self.obj.finished.connect(self.thread.quit)

        self.thread.started.connect(self.obj.procListen)
        self.thread.start()
        self.text.append("starting listener")

    def handleButtonJam(self):

        self.objJam = jamworker.JamWorker(self.dongle)
        self.jamThread = QThread()

        self.objJam.jamMessageReady.connect(self.onMessageReady)

        self.objJam.moveToThread(self.jamThread)
        self.objJam.finished.connect(self.jamThread.quit)

        self.jamThread.started.connect(self.objJam.procJam)
        self.jamThread.start()


    def rollingMessageReady(self,msg):
        self.text.append(msg + "rolling")


    def rollingStopJamming(self,msg):
        self.text.append("Stopping jamming....")
        #self.saveToFile(self.fileName,msg)
        try:
            QtCore.QMetaObject.invokeMethod(self.objJam, 'stopJam', Qt.DirectConnection)
        #Thread didn't start, therefore object does not exist
        except(AttributeError):
            pass
        #self.allowListening = False


    def jamStartReady(self,msg):
        print("starting jam again")

        self.text.append(msg + "rolling")
        try:
            QtCore.QMetaObject.invokeMethod(self.objJam, 'procJam', Qt.DirectConnection)
        #Thread didn't start, therefore object does not exist
        except(AttributeError):
            pass
        #self.allowListening = False


    def jamStopReady(self,msg):
        print("starting jam stop Ready")

        self.text.append(msg + "starting jam stop Ready")
        try:
            QtCore.QMetaObject.invokeMethod(self.objJam, 'stopJam', Qt.DirectConnection)
        #Thread didn't start, therefore object does not exist
        except(AttributeError):
            pass
        #self.allowListening = False


    def onMessageReady(self, msg):
        self.text.append(msg)
        #self.saveToFile(self.fileName,msg)

    def onSaveReady(self,msg):
        self.saveToFile(self.fileName,msg)

    def handleButtonStop(self):

        self.text.append("Stopping...")
        try:
            QtCore.QMetaObject.invokeMethod(self.obj, 'stopListen', Qt.DirectConnection, Q_ARG(str, 'test'))
        #Thread didn't start, therefore object does not exist
        except(AttributeError):
            pass

        try:
            QtCore.QMetaObject.invokeMethod(self.objRoll, 'stopListen', Qt.DirectConnection, Q_ARG(str, 'test'))
        #Thread didn't start, therefore object does not exist
        except(AttributeError):
            pass

        try:
            QtCore.QMetaObject.invokeMethod(self.objJam, 'stopJam', Qt.DirectConnection)
        #Thread didn't start, therefore object does not exist
        except(AttributeError):
            pass
        #self.allowListening = False

    def radioButtonState(self,b):
        msg = b.text() + " is selected"
        #self.text.append(msg)
        if b.text() == "2FSK":
            if b.isChecked() == True:
                self.text.append(b.text()+" modulation is selected")
            else:
                pass
                #self.text.append(b.text()+" is deselected")
        if b.text() == "ASK":
            if b.isChecked() == True:
                self.text.append(b.text()+" modulation is selected")
            else:
                pass
                #self.text.append(b.text()+" is deselected")


    def closeEvent(self, event):
        try:
            self.dongle.setModeIDLE()
            self.dongle2.setModeIDLE()
        #If no dongle binded
        except:
            self.dongle.setModeIDLE()
            print(event)
            pass
        self.close()

    def saveToFile(self,fileName,data):
        file = open(fileName, 'a')
        file.write(data)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ui = Display()
    ui.show()
    sys.exit(app.exec_())
