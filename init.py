#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup as bs
from get_agents import get_agent_list
import random
from time import sleep
import browser_cookie3
import spreadsheet

# function that creates an individual browsing session for scraping
def create_session(agents, cookie):
    session = requests.Session() # create a new browsing session object
    session.headers = {
        'User-Agent': random.choice(agents),
        'X-Forwarded-For':'1.1.1.1',
        'Referer': 'https://seekingalpha.com/earnings/earnings-call-transcripts/',
        '_px2': 'True',
        '_px': 'True',
        'PerimeterX': 'True',
        'Content-Encoding':'gzip',
        'Strict-Transport-Security':'max-age=15552000; preload',
        'X-Frame-Options':'DENY',
        'X-Content-Type-Options':'nosniff',
        #'Connection':'keep-alive',
        'Transfer-Encoding':'chunked',
    }
    session.cookies.update(cookie)
    
    return session

# function that gets an individual transcript page from the transcripts directory. Converts the page into a soup object for item extraction.
def get_page(session, url):
    try:
        response = session.get(url, timeout=5) # get a page of transcript
        soup = bs(response.text, 'html.parser') # create a beautifulsoup object from the returned page
    except Exception as err:
        print(err)
    
    return soup

# function that pulls all of the transcript urls from an individual directory page
def get_page_urls(soup):
    url_containers = soup.findAll('a', {'class':'dashboard-article-link'}) # get a list of all of the individual containers for transcript page urls
    urls = [] # list to hold all of the transcript page urls
    for container in url_containers:
        urls.append(container['href'])
    
    return urls
            
# main function
def main():
    print('Initializing script')
    agents = get_agent_list() # bring in the list of user-agents for the page requests
    cookie = browser_cookie3.chrome() # bring in a cookie from chrome; will log you into SA to allow for scraping
    
    sheet = spreadsheet.open_sheet()
    
    last_scraped_page = spreadsheet.get_last_scraped_page(sheet)
    page_to_scrape = last_scraped_page + 1
    
    s = create_session(agents, cookie) # create a new browsing session object
    while (page_to_scrape <= 5300):
        try:
            print('Getting page {} of transcripts'.format(page_to_scrape))
            url = 'https://seekingalpha.com/earnings/earnings-call-transcripts/{}'.format(page_to_scrape) # root url of SA transcripts directory
            soup = get_page(s, url) # get an individual page of transcript urls; as a soup object for working with
            page_urls = get_page_urls(soup) # get all of the individual transcript page urls from one directory page
            print('Got page {} of transcript urls'.format(page_to_scrape))
            for url in page_urls:
                spreadsheet.post_new_url(sheet, url)
            print('Posted all urls from page {} to the sheet.'.format(page_to_scrape))
            spreadsheet.update_last_scraped_page(sheet, page_to_scrape)
            page_to_scrape = spreadsheet.get_last_scraped_page(sheet) + 1
            print()
            sleep(100)
        except Exception as err:
            print(err)
        
        s.close()
        s = create_session(agents, cookie) # create a new browsing session object
        try:
            sheet = spreadsheet.open_sheet()
        except Exception as err:
            print(err)

        
