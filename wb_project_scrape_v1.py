#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  7 17:33:25 2019

@author: chris
"""
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import time, itertools

"""
World bank Project Scraper:

    This program was created to scrape information on various WB project from
the base URL: http://projects.worldbank.org/
There are two functions at work here. The first, wb_project_list_collector(),
collects hyperlinks to project pages. In turn, this list is passed on to
the wb_project_scrape() function. Note that wb_project_list_collector() takes
two arguments:
    1. tab_range: An integer for the number of tabs to scrape. For example,
    if the the project table has 24 pages on range, input 20 as the first
    number in a sequence in Python is 0 and the loop will run n-1 times.
    2. url: The base URL provided for testing is below. However, the search
    parameters can be easily changed and the code below should work.
    
    The second function, wb_project_scrape(), takes the list from the first and
opens a browser to navigate to each site, extracts the title of the project, 
expands the abstract (if available), and appends this data to a pandas data frame
for exporting as a CSV.

NOTE:
    Selenium is used because the site at random sends out a pop-up message that
trips out the code. Future iterations will remove this bug. For now, please
monitor the program as it runs, if the pop-up comes up to request feedback, 
close it as soon as possible. The program has a series of 5 second rest times 
built in to give you a chance to close this pop-up.

TO-DO:
    [ ] Determine fields for scraping
    [ ] Figure out how to eliminate pop-ups
"""

###########################
#   Set Global Settings   #
###########################
# Set table range (number of tabs), which you have to determine by looking at the site:
tab_range = 2

# Set the URL:
url = 'http://projects.worldbank.org/search?lang=en&searchTerm=&countrycode_exact=PK'


#########################
#   Define Functions   #
########################
def wb_project_scrape():
    # Call the hyperlink list making function:
    list_of_jumps = wb_project_list_collector(url=url, tab_range=tab_range)
    
    # Open the driver:
    driver = webdriver.Firefox()
    
    # Create a pandas data frame:
    output = pd.DataFrame()
    
    # Open and parse data from each project hyperlink:
    for jump in list_of_jumps:
        
        # Navigate to the hyperlink
        driver.get(jump)
        
        # Wait 5 seconds to allow for the site to load:
        time.sleep(5)
        
        # Get project ID:
        pid = jump.split('/')[3].replace('?lang=en', '')
        
        # Get the HTML for parsing:
        soup = bs(driver.page_source, 'lxml')
        pri_tit = soup.find('h2', attrs={'id':'primaryTitle'}).text
        
        # Maximize and extract the abstract:
        try:
            driver.find_element_by_link_text('Read More»').click()
            abstract = soup.find('div', attrs={'id':'abstract'}).find_all('p')[0].text.replace('\t','').replace('\n','')
        except NoSuchElementException:
            abstract = "No abstract"
            continue
        
        # Append both pid and abstract to the output data frame:
        output = output.append({'pid': pid, 'abstract':abstract, 'title':pri_tit}, ignore_index=True)
        
    # Close browser:
    driver.quit()
    
    # Write output as CSV:
    output.to_csv('projects.csv', index=False, sep=';')
    print("Finished writing CSV file!")

    # Return the output for pasing to a differnt function:
    return(output)

# Create a list of project hyperlinks:
def wb_project_list_collector(url=url, tab_range=tab_range):
    # Open Firefox browser on the provided url:
    driver = webdriver.Firefox()
    driver.get(url)
    
    # Wait 5 seconds to allow for the site to load:
    print("Gathering hyperlinks!")
    time.sleep(5)
    
    # Switch to the 'Projects' tab:
    driver.find_element_by_link_text('PROJECTS').click()
    
    # Create a list to populate of each project hyperlink 
    href_list = []
    
    # Loop over n number of tabs:
    for _ in itertools.repeat(None, tab_range):
        # Capture the website html, isolate the project table, find all 'a' tags, and filter and append the hyperlinks:
        time.sleep(2)
        soup=bs(driver.page_source, 'lxml')
        tabl = soup.find('div', attrs={'id':'projectsearchresult'})
        hrefs = tabl.find_all('a')
        for link in hrefs:
            temp = link.get('href')
            if temp.startswith('http'):
                href_list.append(temp)
            else:
                continue
        
        # Proceed to the next view of the table
        time.sleep(5)
        driver.find_element_by_link_text('NEXT >>').click()
    
    # Quit the browser
    driver.quit()
    print("Returning list of hyperlinks.")
    
    # pass list of hyperlinks
    return(href_list)


#######################
#   Start Function   #
######################
# Start the script:
if __name__ == "__main__":
    wb_project_scrape()