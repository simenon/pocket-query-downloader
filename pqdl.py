#!/usr/bin/env python
""" Gecoaching.com python utility """
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
__email__    = "albert@simenon.nl"
__purpose__  = "Utility to download pocket queries from www.geocaching.com"
__date__     = "19/12/2013"

import argparse
import os
import progressbar
import urllib2

from selenium import webdriver

CHROMEDRIVER = "driver/chromedriver"
MAX_CACHES_PER_POCKET_QUERY = 950
MAX_CACHES_LAST_POCKET_QUERY = 500

class GCSite:
    """ Geocaching.com web browser class """
    BASE_URL = "http://www.geocaching.com"
    LOGIN_URL = "%s/login" % (BASE_URL)
    POCKET_QUERY_URL = "%s/pocket" % (BASE_URL)
    CHUNK_SIZE = 1024
    XPATH_DOWNLOADPQ = "//a[contains(@href,'downloadpq')]"

    def __init__(self, driver, args):
        self.driver = driver
        self.args = args

    def login(self):
        """ Login on Geocaching.com """
        self.driver.get(self.LOGIN_URL)
        element = self.driver.find_element_by_id("ctl00_ContentBody_tbUsername")
        element.send_keys(self.args.user)
        element = self.driver.find_element_by_id("ctl00_ContentBody_tbPassword")
        element.send_keys(self.args.password)
        element = self.driver.find_element_by_id("ctl00_ContentBody_btnSignIn")
        element.click()

    def download_pq_by_element(self, element):
        """ Download pocket query with selenium webelement """
        url = element.get_attribute("href")
        filename = "%s.zip" % (element.get_attribute("text").strip())
       
        opener = urllib2.build_opener()
        for cookie in self.driver.get_cookies():
            opener.addheaders.append(
                ('Cookie', cookie["name"] + "=" + cookie["value"]))

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
            pbar.finish()

    def download_pocket_queries(self):
        """ Download all pocket queries on geocaching.com """
        self.driver.get(self.POCKET_QUERY_URL)
        elements = self.driver.find_elements_by_xpath(self.XPATH_DOWNLOADPQ)

        if elements:
            for element in elements:
                self.download_pq_by_element(element)
        else:
            print "No pocket queries available to download !"

def arg_parser():
    """ Argument parser """
    parser = argparse.ArgumentParser()
    parser.formatter_class = argparse.RawDescriptionHelpFormatter
    parser.description = "%s, version %s by %s (%s)\n\n%s" \
        % (__filename__,__version__,__author__,__email__,__purpose__)
  
    parser.add_argument(
         "--download", 
         action="store_true", 
         help="download pocket queries")
    parser.add_argument(
         "--user","-u", 
         required=True, 
         help="Geocaching.com username")
    parser.add_argument(
         "--password","-p", 
         required=True, 
         help="Geocaching.com password")
    parser.add_argument(
         "--output","-o", 
         default='', 
         help="output directory")
  
    args = parser.parse_args()
  
    return args
  
def main():
    """ Obviously the main routine """
    args = arg_parser()

    if args.download:
        os.environ["webdriver.chrome.driver"] = CHROMEDRIVER
        driver = webdriver.Chrome(CHROMEDRIVER)
        driver.set_window_size(800, 400)
        site = GCSite(driver, args)
        site.login()
        site.download_pocket_queries()
        driver.quit()

if __name__ == "__main__":
    main()
