# -*- coding: utf-8 -*-

import urllib2
from bs4 import BeautifulSoup
import pymongo
import time
import math

url1_base = 'http://newseed.pedaily.cn'

# read VC list from mongodb
client = pymongo.MongoClient('localhost', 27017)
db = client.CapitalDataTest
db_vc = db.vc_institutions
db_investor = db.investors

# for each VC whose detail page has not been parsed
vc_cursor = db_vc.find({'info_tags':{'$exists':True}, 'invest_tags':{'$exists':True}}).batch_size(10)	# set smaller batch size to avoid cursor error due to connection timeout
for vc in vc_cursor:
	url = vc['detail_url']
	vc_id = vc['_id']
	# try to open url 5 times
	open_success = False
	for i in range(1,6):
		try:
			print("Parsing "+vc['full_name']+": "+url)
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
	soup = BeautifulSoup(html, 'html.parser')
	# get VC detail data in the page
	tag = soup.select_one(".subinfo")
	tag1 = tag.select_one("p")
	if tag1 and tag1.string and len(tag1.string) > 0:		# English name
		vc['en_name'] = tag1.string
	tag2 = tag1.next_sibling.next_sibling	# info tags
	tag_list = []
	if tag2:
		for s in tag2.stripped_strings:
			if len(s)>0:
				tag_list.append(s)
	tag2 = tag.select_one(".r.box-fix-r")
	if tag2:
		for s in tag2.stripped_strings:
			if len(s)>0:
				tag_list.append(s)
	if len(tag_list)>0:
		vc['info_tags'] = tag_list
	tag3 = tag.select_one(".box-fix-l")		# invest tags
	if tag3:
		areas = tag3.select("a")
		ll = []
		for area in areas:
			ll.append(area.string)
		if len(ll)>0:
			vc['invest_tags'] = ll
	tag4 = tag.select_one(".l")
	if tag4:
		tag4 = tag4.select_one("a")			# website
	if tag4 and hasattr(tag4, 'href'):
		vc['website'] = tag4.get('href')
	desc = ''
	tag5 = soup.select_one(".desc")			# description
	if tag5 and tag5.string:
		desc = tag5.string
	if tag5 and hasattr(tag5,'stripped_strings'):
		for s in tag5.stripped_strings:
			desc = desc + s + '\n'
	if len(desc)>0:
		vc['description'] = desc
	# update VC detail in mongodb
	db_vc.find_one_and_update({'_id':vc_id}, {'$set':vc})
	print(vc['full_name']+' updated.')
	# get investor in this VC institution
	print('Get investor list ...')
	investor_list = []
	li = []
	tag1 = soup.select_one(".people-list")	# investor list
	if tag1:
		li = tag1.select("li")
	if len(li)>0:
		for itm in li:						# each investor
			investor = {}
			tag2 = itm.select_one(".title")	# name and detail url
			if tag2:
				tag2 = tag2.select_one("a")
			if tag2 and tag2.string:
				investor['chn_name'] = tag2.string
			if tag2 and hasattr(tag2, 'href'):
				investor['detail_url'] = url1_base + tag2.get('href')
			tag3 = itm.select_one("span")	# job title
			if tag3 and tag3.string:
				investor['title'] = tag3.string
			tag4 = itm.select_one(".tag")
			if tag4:
				areas = tag4.select("a")	# concerned areas
				ll = []
				for area in areas:
					ll.append(area.string)
				if len(ll)>0:
					investor['areas'] = ll
			investor['institution_name'] = vc['full_name']	# institution name
			investor['type'] = 'VC'
			investor_list.append(investor)
		if len(investor_list)>0:
			result = db_investor.insert_many(investor_list)
			print(str(len(result.inserted_ids))+" investors inserted.")
		else:
			print("0 investors inserted.")
	else:
		print("No investors inserted.")
	# wait 2 seconds
	print('Wait 5 seconds... ----------')
	time.sleep(5)
	# break (Debug)
	break

print('Complete.')

