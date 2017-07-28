# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

import urllib2
from bs4 import BeautifulSoup
import pymongo
import time
import math

# set up mongodb connection
client = pymongo.MongoClient('localhost', 27017)
db = client.CapitalDataTest
db_events = db.events

# target url = url_front + #page + url_rear
url1_front = 'http://www.newseed.cn/invest/p'
url1_rear = ''

PAGE_START = 1
PAGE_STOP = 2
TIME_INTERVAL = 6

for page in range(PAGE_START,PAGE_STOP+1):
	count = 0
	url = url1_front+str(page)+url1_rear
	# try 5 times to open url
	open_success = False
	for i in range(1,5):
		try:
			print("Parsing: "+url)
			response = urllib2.urlopen(url)
			open_success = True
			break
		except:
			print("Cannot open url #"+str(i)+". Wait a minute and try again.")
			time.sleep(60)
	if not open_success:
		print("Cannot open url. Abort.")
		break
	html = response.read()
	# extract information
	soup = BeautifulSoup(html, 'html.parser')
	ul = soup.select_one(".table-list")
	li = ul.select("tr")
	if len(li)<2:
		print("---------- Fail: Empty Page. Break. ----------")
		break
	li.pop(0)	# remove table header
	# for each investment event
	for itm in li:
		udata = {}
		tag = itm.select_one(".td2-tit")
		if tag:
			tag = tag.select_one("a")
		if tag and tag.get('href'):
			udata['company_url'] = tag.get('href')		# company url
		if tag and tag.string:
			project_name = tag.string					# project name (index) of the event
		tag = itm.select_one(".td2-com")
		if tag and tag.string:
			udata['area'] = tag.string					# industry / area
		tag = itm.select_one(".td3")
		if tag and tag.string:
			udata['time'] = tag.string					# event time
		tag = itm.select_one(".td4")
		if tag and tag.string:
			udata['financing_stage'] = tag.string		# financing stage
		tag = itm.select_one(".td5")
		if tag and hasattr(tag, 'stripped_strings'):
			i = 0
			for s in tag.stripped_strings:
				i = i + 1
				if (i == 1):
					udata['amount'] = s 				# capital amount
				else:
					if (i == 2):
						udata['currency'] = s 			# currency
					else:
						break
		tag = itm.select_one(".td6")
		if tag:
			ll = []
			investors = tag.select("a")
			for tt in investors:
				if tt.string:
					ll.append(tt.string)
			if len(ll)>0:
				udata['vc_list'] = ll 					# vc institution list
		tag = itm.select_one(".tools")
		if tag:
			tag = tag.select_one("a")
			if tag and hasattr(tag, 'href'):
				udata['detail_url'] = tag.get('href')	# detail url

			# update vc data if full name exists
			db_events.find_one_and_update(
				{'project_name': project_name},
				{'$set': udata},
				upsert = True
			)
			count = count+1
	# output information
	print("{} VC institutions updated.".format(count))
	print("---------- page "+str(page)+" complete ----------")
	print("Wait for {} secs...".format(TIME_INTERVAL))
	time.sleep(TIME_INTERVAL)
# complete
print("complete.")