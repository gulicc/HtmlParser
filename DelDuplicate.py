# -*- coding: utf-8 -*-

import pymongo

# set up mongodb connection
client = pymongo.MongoClient('localhost', 27017)
db = client.CapitalData
db_vc = db.vc_institutions

namelist = []
vclist = db_vc.find()
count = 0
for vc in vclist:
	if vc['full_name'] not in namelist:
		namelist.append(vc['full_name'])
	else:
		count = count+1
		print('Duplicate found: #'+str(count)+vc['full_name'])
		to_clean_list = db_vc.find({'full_name':vc['full_name']})
		v0 = to_clean_list[0]
		v1 = to_clean_list[1]
		print('items: '+str(len(v0))+','+str(len(v1)))
		if len(v0) >= len(v1):
			db_vc.remove({'_id':v1['_id']})		# if v0 has more items, delete v1
			print("Delete id1: "+str(v1['_id']))
		else:
			db_vc.remove({'_id':v0['_id']})		# else delete v0
			print("Delete id0: "+str(v0['_id']))

print(str(count)+' duplicate documents found.')
