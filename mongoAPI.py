"""---------------------------------------------------------------------------------------
--      SOURCE FILE:        mongoAPI.py - mongodb API used
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
--      This file contains the api for mongodb calls used by the rfspoofer
---------------------------------------------------------------------------------------"""
from pymongo import MongoClient
# pprint library is used to make the output look more pretty
from pprint import pprint
# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string


def getFromFile(fileName):
    mytransmits = []
    with open(fileName) as f:
        for line in f:
            line=line.split(',')
            mytransmits.append(line)
    return mytransmits

def initConnection():
    client = MongoClient('mongodb://admin:admin@ds241019.mlab.com:41019/practicum')
    db=client.practicum
    return db.transmissions

def getMaxId(collection):
    maxID = collection.find_one(sort=[("idnum", -1)])["idnum"]
    return maxID

def insertTransmission(collection, transmits):
    curMax = getMaxId(collection)
    newMax = curMax+1
    for vals in transmits:
        transmission ={
        'idnum' : newMax,
        'pktnum' : vals[0],
        'tData' : vals[1].rstrip()
        }
        results = collection.insert_one(transmission)
    print("insert complete")

def getTransmissions(collection, id):

    tData = []
    results = collection.find( { "idnum":id},{"tData":1,"_id":0})

    for res in results:
        tData.append(res['tData'])

    print(tData)
    return tData

def getAllTransmissions(collection):
    results = collection.find({})
    return results
