#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 12 14:17:00 2018

Subordinate program. Just pass as argument the hater name to scrap and port to communicate via socket with the main.
This program is executed by main (MainTweet.py). 

@author: Pedro Zenone
"""

import got3 as got # This library is tuned. I added a parameter in methods for changing user-agent and I also fixed some bugs
import time
import sys
import os
import pandas as pd
import socket
import re

def tweeter_scrap(argv):
    
    # client conection
    PORT = int(argv[1])
    s = socket.socket()   
    s.connect(("localhost", PORT))      
    
    hater = argv[0]
    
    # cargo el useragent que me pasa el main
    ua = argv[2]

    print("llego ",ua)

    fileDir = os.path.dirname(os.path.realpath('__file__'))
    fileHaters = os.path.join(os.path.join(fileDir,"data"),"sprite_users")
    #fileHaters = os.path.join(os.path.join(fileDir,"data"),"other_influencers")
    
    print("Starting subordinate")

    try: # scrap historical tweeter data and download excel
        tweetCriteria = got.manager.TweetCriteria().setQuerySearch('to:' + hater + ' since:2018-05-01').setMaxTweets(1000)
        aux = got.manager.TweetManager.getTweets(tweetCriteria,ua = ua)

        hater_tweets = pd.DataFrame(
                [{'author': x.username, 'mentions':x.mentions, 'text':x.text,'permalink':x.permalink, 'date':x.date} for x in aux])
        
        # cargo al hater
        hater_tweets.to_excel(os.path.join(fileHaters,hater + ".xlsx"))        
        
    except:
        print("Error en twitter API   ",hater)
        
    
    print('Finish subordinate')
    s.send('finish'.encode('utf-8'))
    exit(0)  # cierro todo
            

if __name__ == "__main__":
   tweeter_scrap(sys.argv[1:])
