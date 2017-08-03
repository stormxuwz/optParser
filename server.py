import argparse
import pycurl
import json
import time
import random
import math
import codecs
import os.path
import re
import datetime
from flask import Flask, url_for, json, request
python3 = False
try:
    from StringIO import StringIO
except ImportError:
    python3 = True
    import io as bytesIOModule
from bs4 import BeautifulSoup
if python3:
    import certifi

SEARCH_URL = 'http://www.trackitt.com/usa-immigration-trackers/opt/page/'

START_SEARCH_IMG_INDEX = 0
WAIT_RANGE = [50, 60]

MAX_RESULT_NUM = 100
MEME_TAG = "pipixia" #"pepe"
currentTagIndex = 0

MIN_RESULT_NUM = 1 # per page

DATA_FOLDER = "results/"

urlParameters = {
    'showDates': "&as_qdr=y15",
    'disablePersonalSearch': "&pws=0",
    # 'sortByDate': "&tbs=sbd:1",
    # 'startIndex': "&start=" +,
    # 'numPerPage': "&num=" + str(2)
}

def scrape():
    # Init results
    global results
    # Reset results variable
    results = {
        'items': {} # key: user name
    }

    # Create a file to store the results or open the file and get old results
    resultFile = DATA_FOLDER + "results.json"
    if(os.path.isfile(resultFile)):
        with open(resultFile, 'r') as f:
            results = json.loads(f.read())
            print "-- Opened previous results"
            f.close()
    else:
        print "-- No previous results, create a new file"

    numNewResults = MIN_RESULT_NUM + 1 # fake, so as to enter the loop
    numTotalResults = len((results['items']))
    while (numNewResults > MIN_RESULT_NUM) and len((results['items'])) < MAX_RESULT_NUM:
        code = getPage(math.floor(numTotalResults/50) + 1)
        numNewResults = parseResults(code)
        waitSecond = random.randint(WAIT_RANGE[0], WAIT_RANGE[1])
        numTotalResults += numNewResults
        print "-- [" + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + "] Got results " + str(numNewResults) + " Total=" + str(numTotalResults) + " Wait=" + str(waitSecond)

        # Store the results for every search
        if numNewResults > 0:
            with open(resultFile, 'wb') as f:
                json.dump(results, codecs.getwriter('utf-8')(f), ensure_ascii=False)
                f.close()

        time.sleep(waitSecond)

    
    return "Done!"

def getPage(pageIndex):
    """Perform the image search and return the HTML page response."""
    global results

    if python3:
        returned_code = bytesIOModule.BytesIO()
    else:
        returned_code = StringIO()

    full_url = SEARCH_URL + str(int(pageIndex))

    print "-- [" + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + "] Scrapping page *" + str(pageIndex) +"*" + " URL=" + full_url

    conn = pycurl.Curl()
    if python3:
        conn.setopt(conn.CAINFO, certifi.where())
    conn.setopt(conn.URL, str(full_url))
    conn.setopt(conn.FOLLOWLOCATION, 1)
    conn.setopt(conn.USERAGENT, 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.97 Safari/537.11')
    conn.setopt(conn.WRITEFUNCTION, returned_code.write)
    conn.perform()
    conn.close()
    if python3:
        return returned_code.getvalue().decode('UTF-8')
    else:
        return returned_code.getvalue()

def parseResults(code):
    """Parse/Scrape the HTML code for the info we want."""
    soup = BeautifulSoup(code, 'html.parser')

    global results

    # Exit if recaptcha
    if soup.find('div', attrs={'id':'recaptcha'}) != None:
        print soup
        print "**Robot**"
        exit()

    # Get all rows
    divs = soup.findAll('tr', attrs={'class':re.compile('row')})

    print len(divs)
    exit()

    # Grab Items
    for div in divs:
        item = {}
        # Basic Info
        item['imageID'] = imageId
        item['originalImageLink'] = imageLink
        item['index'] = len(results['items'])
        item['exportDate'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item['searchURL'] = results['searchURL']

        # Search Result Info
        item['title'] = div.find('h3', attrs={'class':'r'}).get_text()
        item['timestamp'] = div.find('span', attrs={'class':'f'})
        if item['timestamp'] != None:
            item['timestamp'] = item['timestamp'].get_text()
        item['description'] = div.find('span', attrs={'class':'st'})
        if item['description'] != None:
            item['description'] = item['description'].get_text()
        item['link'] = div.find('a')
        if item['link'] != None:
            item['link'] = item['link']['href']
        results['items'].append(item)

    return len(divs)

def main():
    scrape()
    

if __name__ == '__main__':
    main()
