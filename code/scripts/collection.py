# import relevant libraries

import pandas as pd
import os
import pyodbc
import json
import shutil
import spacy
import prediction
from datetime import date, timedelta

# load english model for spacy NLP analysis
nlp = spacy.load('en_core_web_sm')

# create string for current date and yesterday's date for twitter search parameters
today = date.today().strftime('%Y-%m-%d')
yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')

# create dictionary of cities for twitter search. dictionary matches cities to corresponding two letter state code
city_dict = {'New York City':'NY',
             'Seattle':'WA',
             'San Francisco':'CA',
             'Los Angeles':'CA',
             'Chicago':'IL',
             'Houston':'TX',
             'Phoenix':'AZ',
             'Philadelphia':'PA',
             'San Antonio':'TX',
             'San Diego':'CA',
             'Dallas':'TX',
             'San Jose':'CA',
             'Austin':'TX',
             'Jacksonville':'FL',
             'Fort Worth':'TX',
             'Columbus':'OH',
             'Charlotte':'NC'}             

# function to remove proper nouns in tweet and replace them with PROPN             
def sterilize(tweet):
    doc = nlp(tweet)
    text = ''
    for x in iter(doc):
        if x.pos_ == 'PROPN' and 'covid' not in str(x).lower() and 'corona' not in str(x).lower():
            text += 'PROPN '
        else:
            text += str(x) + ' '
    return text[:-1]

# create empty dataframe
day_df = pd.DataFrame(columns=['tweet'])

# scrape twitter for tweets containing "tested positive" for all of the cities, then appends these tweets to the dataframe along with city, state, and date information
for city in list(city_dict.keys()):
    os.system('scrapy crawl TweetScraper -a query="tested positive since:' + yesterday + ' until:' + today + ' near:' + city + '" -a lang="en"')
    tweetdict = {'tweet':[]}
    for file in [x[2] for x in os.walk('Data/tweets')][0]:
        with open('Data/tweets/' + str(file), encoding='utf8') as f:
            data = json.load(f)
            tweetdict['tweet'].append(data['text'])
    try:
        shutil.rmtree('Data')
    except:
        print('No data directory')
        
    df = pd.DataFrame.from_dict(tweetdict)
    df.drop_duplicates(subset='tweet', inplace=True)
    df['city'] = city
    df['state'] = city_dict[city]
    day_df = day_df.append(df, ignore_index=True)

day_df['date'] = yesterday

# predict whether each tweet is referring to a local, recent case of Covid-19 using a pickled model
day_df['label'] = prediction.predict_tweet(day_df)

# remove proper nouns for privacy concerns
day_df['tweet'] = [sterilize(tweet) for tweet in day_df['tweet']]

# connect to SQL database and insert new tweets for the day into the table linked to the tableau dashboard
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=ga-cc12-s5.database.windows.net;DATABASE=ga_p5;UID=ga;PWD=[REDACTED]')
cursor = cnxn.cursor()
for index, row in day_df.iterrows():
    cursor.execute("INSERT INTO ga_p5 (tweet, city, state, date, label) values(?,?,?,?,?)", row['tweet'], row['city'], row['state'], row['date'], row['label'])
cnxn.commit()
cursor.close()


