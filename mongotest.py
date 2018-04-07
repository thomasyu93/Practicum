from pymongo import MongoClient
# pprint library is used to make the output look more pretty
from pprint import pprint
# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string


mytransmits = []
with open('waves.txt') as f:
    for line in f:
        line=line.split(',')

        mytransmits.append(line)

for val in mytransmits:
    print(val[1].rstrip())

'''
client = MongoClient('mongodb+srv://thomas:admin@cluster0-ogebj.mongodb.net/test')
db=client.thomas
'''
'''
for vals in mytransmits:
    transmission ={
    'pktnum' : vals[0],
    'tData' : vals[1]
    }
    results = db.transmissions.insert_one(transmission)
print('done insert')
'''
'''
data = db.transmissions.find_one({'pktnum' : '1'})
print(data)
'''
'''
collection = db['transmissions']
cursor = collection.find({})
for document in cursor:
      print(document)
'''
