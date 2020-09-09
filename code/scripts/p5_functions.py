# Import relevant libraries
import numpy as np
import pandas as pd
import os
import time
import spacy
import shutil
import json
import matplotlib.pyplot as plt
import matplotlib as mpl
# Need to download the spacy model. Use command "python -m spacy download en_core_web_lg"
from country_list import countries_for_language
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from os import walk


# Need to download driver for chrome from https://chromedriver.storage.googleapis.com/index.html?path=2.42/

# Create lists of state and country names in order to parse returned location data from user profile pages

states = ['al','ak','az','ar','ca','co','ct','de','fl','ga','hi','id','il','in','ia','ks','ky',
          'la','me','md','ma','mi','mn','ms','mo','mt','ne','nv','nh','nj','nm','ny','nc','nd','oh',
          'ok','or','pa','ri','sc','sd','tn','tx','ut','vt','va','wa','wv','wi','wy','hi', 'dc']
full_states = ['alabama','alaska','arizona','arkansas','california','colorado','connecticut','delaware',
          'florida','georgia','hawaii','idaho','illinois','indiana','iowa','kansas','kentucky',
          'louisiana','maine','maryland','massachusetts','michigan','minnesota','mississippi',
          'missouri','montana','nebraska','nevada','new hampshire','new jersey','new mexico','new york',
          'north carolina','north dakota','ohio','oklahoma','oregon','pennsylvania',
          'rhode island','south carolina','south dakota','tennessee','texas','utah',
          'vermont','virginia','washington','west virginia','wisconsin','wyoming',"hawai'i", 'washington dc']

state_dict = {full_states[x]:states[x] for x in range(len(states))}
countries = [x.lower() for x in list(dict(countries_for_language('en')).values())]
countries.remove('georgia')
countries += ['england','scotland','us','america']

# Instantiate a chrome webdriver to request user locations from twitter.com
# Load spacy model for nlp

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=chrome_options)
nlp = spacy.load('en_core_web_sm');

def sterilize(tweet):
    # Identify any words in a tweet that are proper nouns and replace them with PROPN
    
    doc = nlp(tweet)
    text = ''
    for x in iter(doc):
        if x.pos_ == 'PROPN' and 'covid' not in str(x).lower() and 'corona' not in str(x).lower():
            text += 'PROPN '
        else:
            text += str(x) + ' '
    return text[:-1]

        
def profile_loc(user):
    
    '''
    https://stackoverflow.com/questions/47793516/finding-city-names-in-string?rq=1
    https://stackoverflow.com/questions/52687372/beautifulsoup-not-returning-complete-html-of-the-page

    Reads the html location for user location if present. Parses text using spacy to identify geographic entities
    Users from other countries are identified as foreign and will be dropped later (function returns foreign as state value)
    City name and two letter state code are returned
    '''
    
    url = 'https://twitter.com/' + user
    driver.get(url)
    time.sleep(2)
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    loc_array = ['','','']
    head = soup.find('div', {'data-testid':'UserProfileHeader_Items'})
    if head is not None:
        if len(head) > 0:
            header = head.findChildren('span')
            if len(header)>0:
                loc_array[2] = header[0].text
                loc = []
                location = header[0].text
                doc = nlp(location)
                for ent in doc.ents:
                    if ent.label_ == 'GPE':
                        loc.append(str(ent))
                if len(loc) > 0:
                    location.replace(',','')
                    for x in loc.copy():
                        if x.lower() in countries and x.lower() != 'united states':
                            return ['','foreign',header[0].text]
                        if x.lower() in full_states or x.lower() == 'united states' or x.lower() == 'az' or x.lower() == 'nc':
                            loc.remove(x)
                        else:
                            location = location.replace(x, '')
                    if len(loc) > 0:
                        loc = loc[0]
                    else:
                        loc = ''
                    location = location.lower()
                    for x in full_states:
                        if (x in location or x in loc.lower()) and 'dc' not in location.split():
                            return [loc, state_dict[x].upper(), header[0].text]
                    for x in location.split():
                        if x in states:
                            if x == 'dc':
                                return['','DC',header[0].text]
                            else:
                                return [loc, x.upper(), header[0].text]

                    loc_array = [loc, '', header[0].text]

    city, state, raw = loc_array[0], loc_array[1], loc_array[2]
    return city, state, raw

def create_tweetdf(users=False):
    # Create dictionary from scraped data, then delete file directory to not clutter local memory
    # Set users to true to save the account name that posted the tweet

    tweetdict = {'tweet':[]}
    if users:
        tweetdict['user']=[]
    for file in [x[2] for x in walk('Data/tweets')][0]:
        with open('Data/tweets/' + str(file), encoding='utf8') as f:
            data = json.load(f)
            tweetdict['tweet'].append(data['text'])
            if users:
                tweetdict['user'].append(data['usernameTweet'])

    try:
        shutil.rmtree('Data')
    except:
        print('No data directory')
        
    df = pd.DataFrame.from_dict(tweetdict)
    df.drop_duplicates(subset='tweet', inplace=True)
    return df

def create_bar(x, title = None, xlabel = None, ylabel = None, ticks = '', size = (6,4), axis = 'v'):

    '''Create a bar chart using matplotlib and the passed arguments
    x - List: Series data to be plotted
    Title, xlabel, ylabel - Str: Text for the figure title and axes. Axes are reversed for horionztal charts
    Size - Tuple: Two element tuple defining the width and height of the figure
    Axis - Str: h for horizontal bar charts, y for vertical. Default = vertical
    Code for adding bar labels taken from stack overflow
    https://stackoverflow.com/questions/30228069/how-to-display-the-value-of-the-bar-on-each-bar-with-pyplot-barh'''

    mpl.style.use('ggplot')

    plt.figure(figsize=size)
    if axis == 'h':
        plt.barh(np.arange(1, len(x)+1), x, tick_label = ticks)
        plt.xlabel(ylabel, fontsize=10)
        plt.ylabel(xlabel, fontsize=10)

        for i, v in enumerate(x):
            plt.text(v + 0.02, i + .9, str(v), color='blue', fontweight='bold')
    else:
        plt.bar(np.arange(1, len(x)+1), x, tick_label = ticks)
        plt.xlabel(xlabel, fontsize=10)
        plt.ylabel(ylabel, fontsize=10)

    plt.title(title, fontsize=14)
    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)

    plt.show()