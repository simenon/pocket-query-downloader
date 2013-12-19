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
__version__  = "0.0.2"
__author__   = "Albert Simenon"
__email__		 = "albert@simenon.nl"
__purpose__  = "Utility to download pocket queries from www.geocaching.com"
__date__     = "19/12/2013"

import argparse
import os
import progressbar
import sys
import urllib2
import re
import selenium

from selenium.webdriver.support.ui import Select
from datetime import date, timedelta

CHROMEDRIVER = "driver/chromedriver"
MAX_CACHES_PER_POCKET_QUERY = 950
MAX_CACHES_LAST_POCKET_QUERY = 500

class GCSite:
	BASE_URL = "http://www.geocaching.com"
	LOGIN_URL = "%s/login" % (BASE_URL)
	POCKET_QUERY_URL = "%s/pocket" % (BASE_URL)
	CHUNK_SIZE = 1024

	def __init__(self, driver, args):
		self.driver = driver
		self.args = args

	def login(self):
		self.driver.get(self.LOGIN_URL)
		self.driver.find_element_by_id("ctl00_ContentBody_tbUsername").send_keys(self.args.user)
		self.driver.find_element_by_id("ctl00_ContentBody_tbPassword").send_keys(self.args.password)
		self.driver.find_element_by_id("ctl00_ContentBody_btnSignIn").click()

	def download_pocket_query_by_element(self, element):
		url = element.get_attribute("href")
		filename = "%s.zip" % (element.get_attribute("text").strip())
		
		opener = urllib2.build_opener()
		for cookie in self.driver.get_cookies():
			opener.addheaders.append(('Cookie', cookie["name"] + "=" + cookie["value"]))

		fhandle = opener.open(url)
		total_size = int(fhandle.info().getheader('Content-Length').strip())
		pbar = progressbar.ProgressBar(maxval=total_size).start()
		print filename
		with open(self.args.output + filename, 'wb') as foutput:
			while True:
				data = fhandle.read(self.CHUNK_SIZE)
				if not data:
					break
				foutput.write(data)
				pbar.update(foutput.tell())
			pbar.finish();

	def download_pocket_queries(self):
		self.driver.get(self.POCKET_QUERY_URL)
		elements = self.driver.find_elements_by_xpath("//a[contains(@href,'downloadpq')]")
	
		if elements:
			for element in elements:
				self.download_pocket_query_by_element(element)
		else:
			print "No pocket queries available to download !"

def arg_parser():
	parser = argparse.ArgumentParser()
	parser.formatter_class=argparse.RawDescriptionHelpFormatter
	parser.description = "%s, version %s by %s (%s)\n\n" % (__filename__,__version__,__author__,__email__)
	parser.description += " %s" % (__purpose__)

	parser.add_argument("--download", action="store_true", help="download pocket queries")
	parser.add_argument("--user","-u", required=True, help="Geocaching.com username")
	parser.add_argument("--password","-p", required=True, help="Geocaching.com password")
	parser.add_argument("--output","-o", default='', help="output directory")

	args = parser.parse_args()

	return args

	if (args.download,args.create):
		os.environ["webdriver.chrome.driver"] = CHROMEDRIVER
		driver = selenium.webdriver.Chrome(CHROMEDRIVER)
		driver.set_window_size(800,400)
		if args.download:
			site = GCSite(driver,args)
			site.login()
			site.download_pocket_queries()
		if args.create:
			get_pocket_query_ranges(driver)
		driver.quit()

def main():
	args = arg_parser()

	if args.download:
		os.environ["webdriver.chrome.driver"] = CHROMEDRIVER
		driver = selenium.webdriver.Chrome(CHROMEDRIVER)
		driver.set_window_size(800,400)
		site = GCSite(driver,args)
		site.login()
		site.download_pocket_queries()
		driver.quit()

if __name__ == "__main__":
	main()
