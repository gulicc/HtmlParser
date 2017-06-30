# -*- coding: utf-8 -*-

import urllib2
from bs4 import BeautifulSoup
import pymongo
import time
import math

# target url = url_front + #page + url_rear
url1_base = 'http://newseed.pedaily.cn'
url1_front = 'http://newseed.pedaily.cn/vc/p'
url1_rear = ''

# set up mongodb connection
client = pymongo.MongoClient('localhost', 27017)
db = client.CapitalDataTest
db_vc = db.vc_institutions

# clear (optional)
# db_vc.remove()

count = 0
for page in range(1, 6):
	vclist = []
	url = url1_front+str(page)+url1_rear
	# try to open url 5 times
	open_success = False
	for i in range(1,6):
		try:
			print("Parsing: "+url)
			response = urllib2.urlopen(url)
			open_success = True
			break
		except:
			print("Cannot open url #"+str(i)+". Wait 60 seconds and try again.")
			time.sleep(60)
	if not open_success:
		print("Cannot open url. Abort.")
		break
	# parse HTML
	html = response.read()
	soup = BeautifulSoup(html, 'html.parser')	# Parse html
	# get VC institution list in the page
	newslist = soup.find(id="newslist")
	li = newslist.select(".list-content")
	if len(li)==0:
		print("---------- Fail: Empty Page. Break. ----------")
		break
	# for each VC institution
	for itm in li:
		vcdict = {}
		tag = itm.select_one(".u-name")			# full name and detail url (a href)
		if tag:
			vcdict['full_name'] = tag.string
			vcdict['detail_url'] = url1_base+tag.get('href')
		else:
			continue
		tag = itm.select_one("span")			# short name
		if tag:
			vcdict['short_name'] = tag.string
		tag = itm.select_one(".content-r")		# city
		if tag:
			vcdict['city'] = tag.string
		tag = itm.select_one(".txt")			# brief introduction
		if tag:
			vcdict['brief'] = tag.string
		tag = itm.select_one(".state")			# investment cases
		if tag:
			cases = tag.select("a")
			ll = []
			for case in cases:
				ll.append(case.string)
			if len(ll)>0:
				vcdict['investment_cases'] = ll
		vclist.append(vcdict)					# append one VC
	# insert to mongodb
	result = db_vc.insert_many(vclist)
	count = count+len(result.inserted_ids)
	print(str(len(result.inserted_ids))+" VC institutions inserted.")
	print("---------- page "+str(page)+" complete ----------")
	print("Wait for 2 secs...")
	time.sleep(2)
# complete
print("complete.")