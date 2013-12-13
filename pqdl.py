#!/usr/bin/env python
#------------------------------------------------------------------------------
# Copyright (C) 2013 Albert Simenon
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#------------------------------------------------------------------------------
__filename__ = "pqdl.py"
__version__  = "0.0.1"
__author__   = "Albert Simenon"
__purpose__  = "Utility to download pocket queries from www.geocaching.com"
__date__     = "13/12/2013"

import getopt
import os
import progressbar
import sys
import urllib2

from selenium import webdriver

BASE_URL = "http://www.geocaching.com"
CHUNK_SIZE = 1024
USERNAME = ''
PASSWORD = ''
OUTPUTDIR = ''

def gc_login(self):
	self.get("%s/login" % BASE_URL)
	self.find_element_by_id("ctl00_ContentBody_tbUsername").send_keys(USERNAME)
	self.find_element_by_id("ctl00_ContentBody_tbPassword").send_keys(PASSWORD)
	self.find_element_by_id("ctl00_ContentBody_btnSignIn").click()

def download_pq(link,opener):
	url = link.get_attribute("href")
	filename = link.get_attribute("text").strip() + ".zip"

	fhandle = opener.open(url)
	total_size = int(fhandle.info().getheader('Content-Length').strip())
	pbar = progressbar.ProgressBar(maxval=total_size).start()
	print filename
	with open(OUTPUTDIR + filename, 'wb') as foutput:
		while True:
			data = fhandle.read(CHUNK_SIZE)
			if not data:
				break
			foutput.write(data)
			pbar.update(foutput.tell())
		pbar.finish();

def gc_append_cookies_to_opener(self,opener):
	cookies = self.get_cookies()
	for cookie in cookies:
		opener.addheaders.append(('Cookie', cookie["name"] + "=" + cookie["value"]))

def gc_pocket_queries(self):
	self.get("%s/pocket" % BASE_URL)
	links = self.find_elements_by_xpath("//a[contains(@href,'downloadpq')]")
	
	opener = urllib2.build_opener()
	gc_append_cookies_to_opener(self,opener)
	for link in links:
		download_pq(link,opener)

def parse_cmd_line_options(argv):
	try:
		opts,args = getopt.getopt(argv,"hu:p:o:")
	except getopt.GetOptError:
		print 'pqdl.py -h for help'
		sys.exit(2)
	if not args:
		print 'pqdl.py -h for help'
		sys.exit()
	for opt, arg in opts:
		if opt == '-h':
			print 'pqdl.py -h for help'
			sys.exit()
		elif opt == '-u':
			global username
			username = arg
		elif opt == '-p':
			global password
			password = arg
		elif opt == '-o':
			global outputdir 
			outputdir = arg

def main(argv):
	parse_cmd_line_options(argv)
	try:
		browser = webdriver.Chrome("driver/chromedriver")
		browser.set_window_size(400,400)
		gc_login(browser)
		gc_pocket_queries(browser)
		browser.quit()
	except :
		print(sys.exc_info())
		raise

if __name__ == "__main__":
	print __filename__ , ", version ", __version__, " by ", __author__
	print __purpose__

	main(sys.argv[1:])
