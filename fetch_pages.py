# -*- coding: utf-8 -*-

import urllib2
from bs4 import BeautifulSoup
import time
import os

TIME_INTERVAL = 6

# try to open url several times, return None if failed
def safe_open(url, count, interval=60):
	open_success = False
	for i in range(1,6):
		try:
			print("Try URL: " + url)
			response = urllib2.urlopen(url)
			open_success = True
			break
		except:
			print("Cannot open url #"+str(i)+". Wait 60 seconds and try again.")
			time.sleep(interval)
	if not open_success:
		print("Cannot open url. Giving up.")
		return None
	else:
		return response

url_start = 'http://www.newseed.cn/invest/p1'
url_next = url_start
page_count = 1
while url_next:
	response = safe_open(url1_next)
	if response:
		html = response.read()
		if html:
			# save current page
			f = open('events/page_{}.html'.format(page_count))
			f.write(html)
			f.close()
			# set url_next
			soup = BeautifulSoup(html, 'html.parser')
			tag = soup.select_one(".next")
			if tag and hasattr(tag, 'href'):
				url_next = tag.get('href')
			else:
				url_next = None
	else:
		break
	time.sleep(TIME_INTERVAL)

if not url_next:
	print("No more pages found.")
print("Complete.")