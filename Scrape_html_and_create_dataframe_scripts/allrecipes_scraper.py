'''
This code scrapes recipes from AllRecipes.com and saves the raw .html files to a directory.
The default is to scrape random pages from within a range of page numbers. To instead scrape a specific list of pages, replace rand_choice variable with an array of selected page numbers.

Instructions: add directory paths you would like to save the raw .html files and pages tried log in USER INPUT. In USER INPUT you can also select a range of page numbers to choose randomly, or replace rand_choice with an array of page numbers you would like to scrape. Also specify the number of cores you would like to run the scraping function with, as this code runs the scraper loop in parallel to increase speed.

Code by Kaelynn Rose (c)
Created on 2/22/2021

'''

import json
import numpy as np
import numpy.random as random
import requests
import os

from bs4 import BeautifulSoup
from joblib import Parallel, delayed


################## USER INPUT ###################

html_path = 'raw_html' # path to directory you would like to store the .html files in
log_path = 'logs' # path to directory where you would like to store the log of pages tried
np_path = 'masterlog.npy'

rand_choice = np.arange(6663, 283432) # choose page range to request. pages outside of this range are blank.
random.shuffle(rand_choice)

num_cores = 16 # select number of cores on your machine you would like to use to run the scraper in parallel

################## END USER INPUT ###############


pages_tried = [] # initialize list of pages tried in case an error stops the scraper
if not os.path.exists(np_path):
    np.save(np_path, pages_tried) # save a master log of the pages already tried

def scrape_webpage(recipe_num):
    pages_tried = list(np.load(log_path + 'masterlog.npy', allow_pickle=True))
    if recipe_num not in pages_tried:
        try:
            print(f'Working on page number {recipe_num}')
            raw_html_pathname = os.path.join(html_path, f'page{recipe_num}.html')
            souped_html_pathname = os.path.join(html_path, f'page-souped{recipe_num}.html')
            if os.path.exists(raw_html_pathname):
                print(f'Page number {recipe_num} already exists at {raw_html_pathname}')
                return
            url = f'https://www.allrecipes.com/recipe/{recipe_num}'
            result = requests.get(url)
            with open(raw_html_pathname, "w") as file:
                file.write(str(result.content)) # write the file

            pages_tried.append(recipe_num)
            np.save(np_path, pages_tried) # add the page tried to the master log of pages_tried

            soup = BeautifulSoup(result.content, 'html.parser')
            text1 = str(soup.find_all('script', type='application/ld+json')[0]) # test to see whether the 'script' tag exists, if it does not this will go to the 'except' statement and then try the next page
            text_r1 = text1.split('<script type="application/ld+json">')[1].split('</script>')[0]
            pages_tried.append(recipe_num)
            np.save(np_path, pages_tried) # add the page tried to the master log of pages_tried
            print(f'Recipe # {recipe_num} EXISTS. Data obtained and saved to {souped_html_pathname}')
            with open(souped_html_pathname, "w") as file:
                file.write(str(soup))  # write the file
        except Exception as e:
            print(f'Recipe # {recipe_num} does not exist. No data obtained for this recipe.')

Parallel(n_jobs=num_cores)(delayed(scrape_webpage)(i) for i in rand_choice) # run scrape_webpage loop in parallel on num_cores for each value of rand_choice
