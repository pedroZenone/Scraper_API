#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 12 13:26:47 2018

Use mode: python MaterTweet.py <port number> -u <csv file column 0>(use ) or python MaterTweet.py <port number>      or..   python MasterTweet.py   and by default port num will be 9904

@author: pedzenon
"""

from NLP_preproc import NLP_preproc
import os
import pandas as pd
import joblib
import numpy as np
import socket
import signal
import subprocess
import time
import sys
from fake_useragent import UserAgent
import re

navegadores = ['chrome','firefox','safari','opera']

# Funcion para parsear la url
def parse_Agent(x):
    ua_re = re.findall(r'^(.*?)\((.*?)\)',x)
    try:
        userAgent = ua_re[0][0] + '(' + ua_re[0][1] + ')'
    except:
        userAgent = 'Opera/9.80'
        
    return userAgent

def main(argv):
    
    if(len(argv) == 0):
        PORT = 9904
    else:
        PORT = int(argv[0])    
        
    if(len(argv) == 3):
        if(argv[1] == '-u'):
            file2open = argv[2]
            
    ua = UserAgent()  # defino la clase para ir cambiandola despues
    
    j = 2
  
    
# =============================================================================
#     Cargo el modelo, levanto a todos los usuarios y me armo una lista de haters
# =============================================================================
        
#    fileDir = os.path.dirname(os.path.realpath('__file__'))
#    fileModel = os.path.join(fileDir,"model")
#              
#    # Levanto los datos
#    
#    data = pd.read_excel("./data/MoreInfluencersAzu.xlsx")
#    
#    # Preproc text
#    
#    data.columns = ["Full Text" if (x == "text") else x for x in data.columns]
#    data["Full Text"] = data["Full Text"].astype(str)
#    prepoc = NLP_preproc(data)
#    prepoc.preprocessing(True)
#    
#    single_words = [x for x in 'abcdefghijklmnopqrstuvwxyz'] 
#    prepoc.update_StopWords(single_words + ['pedro','pedrito','sol','perez','flor','gime','jimena','jime','bimbo','angela'])
#    
#    data["Text"] = prepoc.get_procTextTweets()
#    data = data.loc[data["Text"] != '']
#    
#    # cargo modelo
#    model = joblib.load(os.path.join(fileModel,'model.pkl'))
#     
#    optimal_tresh = 0.302
#    cutter = np.vectorize(lambda x: 1 if x > optimal_tresh else 0)
#    data["hater"] = cutter(model.predict_proba(data["Text"])[:,1])
#    
#    bardeos = data.loc[data["hater"] == 1]
#    haters = list(set(bardeos["author"]))
#
#    fileHaters = os.path.join(os.path.join(fileDir,"data"),"haters_scrap")
#    #fileHaters = os.path.join(os.path.join(fileDir,"data"),"other_influencers")
#    
#    # Saco los que ya estan!
#    allready_haters = os.listdir(fileHaters)
#    haters = [x for x in haters if(x + ".xlsx" not in allready_haters)]
#  
    
    fileDir = os.path.dirname(os.path.realpath('__file__'))
    fileHaters = os.path.join(os.path.join(fileDir,"data"),"sprite_users")
    
#    haters = list(pd.read_csv("Sprite_completo_Azul_brand.csv").iloc[:,0])
    haters_ = list(pd.read_csv(file2open).iloc[:,0])
    allready = [x.split('.')[0] for x in os.listdir(fileHaters)]
    haters = [x for x in haters_ if(x not in allready)]

    TIMEOUT = 60*5

# =============================================================================
# Arranco la escucha. Levanto un server para comunicarme con los procesos. El
# El flow consiste en levantar un process al que le paso el usuario hater
# y me quedo escuchando, cuando pasan 10 min sin que elñ proceso responda es porque
# se murio, con lo cual lo kileo y sigo scrapeando. Simepre de a una a la vez
# =============================================================================
    
    # Server up
    s = socket.socket()   
    s.bind(("localhost", PORT))  
    s.listen(1)  
    
    for i,hater in enumerate(haters):
        # start process
        
        if((i % 100) == 0):    # cada 300 haters cambio el user agent
            ua_new = parse_Agent(ua[navegadores[j%4]])
            j += 1            

        proc = subprocess.Popen('python oldTweetGetter.py ' + hater + ' ' + str(PORT) + ' ' + "'"+ua_new+"'", 
                           shell=True)
        
        # wait for conection...
        sc, addr = s.accept() # espero que el scraper se levante
        print("accepted ",hater)
        
        rec = ''
        counter = 1
        sc.settimeout(1)  # base time. Tick
        
        # loop wainting process finish
        while(rec != 'finish'):
            try:
                rec = sc.recv(100).decode('utf-8') # try to receive 100 bytes
                print("rec ",rec)
                #print(rec,' ',hater)
            except socket.timeout: #  after 1 second of no activity count TIMEOUT seconds and kill it
                counter += 1
                print("counter ",counter)
                # kill cond.
                if(counter > TIMEOUT):
                    os.kill(proc.pid, signal.SIGTERM)
                    print("killeando ", hater)
                    time.sleep(30) # a dormir para que se cierre bien la aplicacion
                    rec = 'finish'  # fuerzo salida
    

if __name__ == "__main__":
   main(sys.argv[1:])    
    
