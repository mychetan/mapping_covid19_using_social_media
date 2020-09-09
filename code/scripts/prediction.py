#Imported Libraries

import pickle 
import pandas as pd 
import re

def predict_tweet(df):
    df = df[['tweet']].copy()

    #Feature Engineering
    df['website_link'] = df['tweet'].astype('str').map(lambda x: 1 if 'http' in x else 0)

    #Data Cleaning
    def cleaning(word):
        '''Replace URL, hashtags, @useername, non-english characters and pic.twitter with an empty string. 
        Returns cleaned tweet'''
        word = word.lower()
        word = re.sub("http(\s+|\W+|\w+)+|@(\s+|\W+|\w+)|#(\w+|\W+)", "", word) #Removes hashtags, URL, and @username
        word = re.sub('(pic.twitter.com.)\w+', "", word) #Removes sentences that start with pic.twitter
        word = re.sub('[^a-zA-z\s]', "", word) #Filter out non-english characters  
        return word

    df['tweet'] = df['tweet'].astype('str').map(cleaning)

    #Load vectorizer to vectorizer data 
    vectorizer = pickle.load(open("./pickle/vectorizer.pkl", "rb"))
    Z = vectorizer.transform(df['tweet'])
    Z_df = pd.DataFrame(Z.toarray(), columns=vectorizer.get_feature_names(), index=df.index)
    df_1 = pd.concat([df, Z_df], axis=1,)

    #Isolate selected X variable
    feature = pickle.load(open('pickle/feature.pkl', "rb"))
    feature.append('website_link')

    x =df_1[feature]

    #Load pickled model, get predictions, and save to csv 
    model = pickle.load(open('pickle/model.pkl', "rb"))
    return model.predict(x)
