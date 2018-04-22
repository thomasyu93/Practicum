#!/usr/bin/env python

import sys
import readline
import rlcompleter
readline.parse_and_bind("tab: complete")

from rflib import *

from struct import *
import bitstring
import operator
import argparse
import time
import pickle


#Default Values
frequency = 314350000
baudRate = 4800
FSK2 = "MOD_2FSK"
bandwidth = 24000


intro = """'RfCat, the greatest thing since Frequency Hoppingss!'

Research Mode: enjoy the raw power of rflib

currently your environment has an object called "d" for dongle.  this is how
you interact with the rfcat dongle:
    >>> d.ping()
    >>> d.setFreq(433000000)
    >>> d.setMdmModulation(MOD_ASK_OOK)
    >>> d.makePktFLEN(250)
    >>> d.RFxmit("HALLO")
    >>> d.RFrecv()
    >>> print d.reprRadioConfig()
"""

"""
d.setFreq(314350000)
d.setMdmModulation(MOD_2FSK)
d.setMdmDRate(4800)
d.setMaxPower()
d.lowball()
d.RFlisten()
"""

def init_dongle(dongle):
    #dongle.setFreq(frequency)
    #dongle.setMdmModulation(MOD_2FSK)
    #dongle.makePktFLEN(0)
    #dongle.setMdmDRate(baudRate)
    #dongle.lowball(0)
    #dongle.setMdmChanSpc(bandwidth)
    #dongle.setChannel(0)

    dongle.setFreq(frequency)
    dongle.setMdmModulation(MOD_2FSK)
    dongle.setMdmDRate(baudRate)
    dongle.setMaxPower()
    dongle.lowball()
    dongle.makePktFLEN(255)
    dongle.setChannel(0)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--research', default=False, action="store_true", help='Interactive Python and the "d" instance to talk to your dongle.  melikey longtime.')
    parser.add_argument('-i', '--index', default=0, type=int)
    parser.add_argument('-s', '--specan', default=False, action="store_true", help='start spectrum analyzer')
    parser.add_argument('-f', '--basefreq', default=902e6, type=float)
    parser.add_argument('-c', '--inc', default=250e3, type=float)
    parser.add_argument('-n', '--specchans', default=104, type=int)
    parser.add_argument('--bootloader', default=False, action="store_true", help='trigger the bootloader (use in order to flash the dongle)')
    parser.add_argument('--force', default=False, action="store_true", help='use this to make sure you want to set bootloader mode (you *must* flash after setting --bootloader)')
    parser.add_argument('-recv', default=False, action="store_true", help='receive mode')
    parser.add_argument('-send', default=False, action="store_true", help='send mode')
    parser.add_argument('-jam', default=False, action="store_true", help='jam a frequency')

    ifo = parser.parse_args()

    if ifo.bootloader:
        if not ifo.force:
            print "Protecting you from yourself.  If you want to trigger Bootloader mode (you will then *have* to flash a new RfCat image on it) use the --force argument as well"
            exit(-1)

        print "Entering RfCat Bootloader mode, ready for new image..."
        RfCat(ifo.index).bootloader()
        exit(0)

    elif ifo.specan:
        RfCat(ifo.index).specan(ifo.basefreq,ifo.inc,ifo.specchans)

    elif ifo.research:
        interactive(ifo.index, DongleClass=RfCat, intro=intro)

    elif ifo.recv:

        capturedPackets = []
        pktcounter = 0
        print "recv Testing"
        d= RfCat()
        init_dongle(d)

        while True:
            try:
                rawdata, t = d.RFrecv(1)
                hexdata = rawdata.encode('hex')
                strength= 0 - ord(str(d.getRSSI()))

                if strength > -100:
                    pktcounter+=1
                    print "Packet: " + str(pktcounter) + " with Signal Strength:" + str(strength) + "with signal: " + str(hexdata) + "ASCII: " +  makeFriendlyAscii(rawdata)
                    capturedPackets.append(hexdata)

                    time.sleep(3)
                    print "sending"
                    bytePacket = bitstring.BitArray(hex=hexdata).tobytes()
                    d.makePktFLEN(len(bytePacket))
                    d.RFxmit(bytePacket)
            except (KeyboardInterrupt):
                break
            except (ChipconUsbTimeoutException):
                pass
        #Send packets?
        '''
        for index,packets in enumerate(capturedPackets):
            bytePacket = bitstring.BitArray(hex=packets).tobytes()
            d.makePktFLEN(len(bytePacket))
            d.RFxmit(bytePacket)
            print("sent", index, packets)
        '''
        d.setModeIDLE()
        exit()

    elif ifo.send:

        capturedPackets = []
        pktcounter = 0
        print "send Testing"
        d= RfCat()
        init_dongle(d)



        while True:
            try:
                rawdata, t = d.RFrecv(1)
                hexdata = rawdata.encode('hex')
                strength= 0 - ord(str(d.getRSSI()))

                if strength > -100:
                    pktcounter+=1
                    print "Packet: " + str(pktcounter) + " with Signal Strength:" + str(strength) + "with signal: " + str(hexdata) + "ASCII: " +  makeFriendlyAscii(rawdata)
                    capturedPackets.append(hexdata)

            except (KeyboardInterrupt):
                break
            except (ChipconUsbTimeoutException):
                pass
        #d.RFlisten()
        d.setModeIDLE()
        print "printing packets: "
        for index,packets in enumerate(capturedPackets):
            print(index, packets)

        exit()

    elif ifo.jam:

        capturedPackets = []
        pktcounter = 0
        print "send Testing"
        d= RfCat()
        init_dongle(d)



        while True:
            try:
                d.setModeTX()

            except (KeyboardInterrupt):
                break
            except (ChipconUsbTimeoutException):
                pass
        #d.RFlisten()
        d.setModeIDLE()
        exit()





    else:
        print "Testing"
        d= RfCat()
        init_dongle(d)

        while True:
            try:
                rawdata, t = d.RFrecv(1)
                hexdata = rawdata.encode('hex')
                strength= 0 - ord(str(d.getRSSI()))

                if strength > -100:
                    print "Signal Strength:" + str(strength) + "with signal: " + str(hexdata) + "ASCII: " +  makeFriendlyAscii(rawdata)


        	#except (ChipconUsbTimeoutException):
            #    pass
            except (KeyboardInterrupt):
                break
            except (ChipconUsbTimeoutException):
                pass
        #d.RFlisten()
        d.setModeIDLE()


        exit()


        # do the full-rfcat thing
        # d = RfCat(ifo.index, debug=False)
        # d.rf_configure(**ifo.__dict__)
        # d.rf_redirection((sys.stdin, sys.stdout))
