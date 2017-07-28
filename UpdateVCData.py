# -*- coding: utf-8 -*-

import urllib2
from bs4 import BeautifulSoup
import pymongo
import time
import math

# set up mongodb connection
client = pymongo.MongoClient('localhost', 27017)
db = client.CapitalDataTest
db_vc = db.vc_institutions

# target url = url_front + #page + url_rear
url1_base = 'http://www.newseed.cn'
url1_front = 'http://www.newseed.cn/vc/p'
url1_rear = ''

PAGE_START = 1
PAGE_STOP = 601
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
	ul = soup.select_one(".vc-list")
	li = ul.select(".table-plate")
	if len(li)==0:
		print("---------- Fail: Empty Page. Break. ----------")
		break
	# for each VC institution
	for itm in li:
		udata = {}
		tag = itm.select_one("a")
		if tag and tag.get('href'):
			udata['detail_url'] = tag.get('href')		# detail url
		tag = itm.select_one(".td2-com")
		if tag and tag.string:
			full_name = tag.string						# full name
			# update vc data if full name exists
			db_vc.find_one_and_update(
				{'full_name': full_name},
				{'$set': udata},
				upsert = True
			)
			count = count+1
	# insert to mongodb
	print(str(count)+" VC institutions updated.")
	print("---------- page "+str(page)+" complete ----------")
	print("Wait for {} secs...".format(TIME_INTERVAL))
	time.sleep(TIME_INTERVAL)
# complete
print("complete.")