# -*- coding: utf-8 -*-

import urllib2
from bs4 import BeautifulSoup
import pymongo
import time
import math

# set up mongodb connection
client = pymongo.MongoClient('localhost', 27017)
db = client.CapitalData
db_vc = db.vc_institutions

# target url = url_front + #page + url_rear
url1_base = 'http://newseed.pedaily.cn'
url1_front = 'http://newseed.pedaily.cn/vc/p'
url1_rear = ''

for page in range(151,590):
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
	soup = BeautifulSoup(html, 'html.parser')	# Parse html
	newslist = soup.find(id="newslist")
	li = newslist.select(".list-content")
	if len(li)==0:
		print("---------- Fail: Empty Page. Break. ----------")
		break
	# for each VC institution
	for itm in li:
		tag = itm.select_one(".u-name")
		if tag:
			full_name = tag.string
			# update detail page url
			detail_url = url1_base+tag.get('href')
			db_vc.find_one_and_update(
				{'full_name':full_name},
				{'$set': {'detail_url':detail_url}})
			count = count+1
	# insert to mongodb
	print(str(count)+" VC institutions updated.")
	print("---------- page "+str(page)+" complete ----------")
	print("Wait for 10 secs...")
	time.sleep(10)
# complete
print("complete.")