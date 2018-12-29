#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 18:01:51 2018

This code let you connect to Twitter API and get tweets from users, and get metadata
of each users. Because getting user data is slow, I only get the ids and then the metadata
in chunks of 100 users

@author: pedzenon
"""


import tweepy
import time
import pandas as pd
from datetime import datetime


def twitter_to(name):
    df_tweetsReplies = pd.DataFrame([],columns = ["id_tweet","reply",'fecha',"author","n_tweets","followers","friends","location"])
    
    counter= 0
    for tweet in tweepy.Cursor(api.search,q='to:' + name, result_type='recent',timeout=999999, tweet_mode = 'extended').items():
        if hasattr(tweet, 'in_reply_to_status_id_str'):      
            if hasattr(tweet, 'author'):  
                # guardo la respuesta!
                aux = pd.DataFrame([{'id_tweet':tweet.in_reply_to_status_id_str,'reply':tweet.full_text,'fecha':tweet.created_at,
                                     "author":tweet.author.screen_name,"n_tweets":tweet.author.statuses_count,
                                     "followers":tweet.author.followers_count,"friends": tweet.author.friends_count,
                                     "location": tweet.author.location, "destino": name}])
                df_tweetsReplies = df_tweetsReplies.append(aux)
                # still alive
                counter += 1
                if((counter % 1000) == 0):
                    print(datetime.today(),"|| " + name +" || Counter:",counter)
    
    df_tweetsReplies.to_excel("tweetsReplies" + name + ".xlsx")

# %% Main code:

# =============================================================================
#                   Initialize API
# =============================================================================

ACCESS_TOKEN = 'PRIVATE'
ACCESS_SECRET = 'PRIVATE'
CONSUMER_KEY = 'PRIVATE'
CONSUMER_SECRET = 'PRIVATE'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

api = tweepy.API(auth,wait_on_rate_limit=True)

# =============================================================================
#                   Get Tweets from API
# =============================================================================
    
df_tweetsAuthor = pd.DataFrame([],columns = ["id_tweet","tweetSource","Author","fecha"])

# Some ARG influencers...
influencers = ['DementeYT','vikypita', 'natijota', 'laufer4', 'martinciriook', 'malepichot', 'solperez', 'Pedrito_Vm']

influencers = ['Pedrito_Vm']
for name in influencers:
    try:
        twitter_to(name)
    except:
        print("Fallo de conexion en " + name + " reconectando...")
        
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)        
        api = tweepy.API(auth,wait_on_rate_limit=True)
        
        print("Conectado!")
        # arranco devuelta
        twitter_to(name)

df_aux = pd.read_excel("tweetsRepliesPedrito_Vm2.xlsx")
df_aux = df_aux.append(df_tweetsReplies)

# =============================================================================
#                   Get Users data (followers, description, etc...)
# =============================================================================

user_ids = []

try:   # ver que si le pasas api.followers solo te tira toda la data! (id, seguidores, aamigos, nombre...)
    for page in tweepy.Cursor(api.followers_ids, id='Sprite_Ar', count=5000).pages():
        user_ids.extend(page)

except tweepy.RateLimitError:
    print ("RateLimitError...waiting 1000 seconds to continue")
    time.sleep(1000)
    print("Seguimos...")
    for page in tweepy.Cursor(api.followers_ids, id='Sprite_Ar', count=5000).pages():
        user_ids.extend(page)

# Primero me descargo los user ids y luego hago queries mas heavies de a 100 usuarios
user_fullData = []
chunk = int(len(user_ids)/100)

for i in range(chunk):
    aux = user_ids[((i*100) + 1):(i+1)*100]
    chunk_ids = ''.join([ ','+str(x) for x in aux])[1:]
    user_fullData.extend(api.lookup_users(user_ids=[chunk_ids]))
    
    if(i%50):
        print("usuarios descargados: ",i*100)


UserData = pd.DataFrame([{'user_name':x.screen_name, 'followers':x.followers_count,'n_tweets':x.statuses_count,
  'likes':x.favourites_count,'friends':x.friends_count,'description':x.description,'id':x.id} for x in user_fullData])

UserData.to_excel("FollowersData.xlsx")
    
