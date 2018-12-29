#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 29 19:03:08 2018

This script download images from links in the csv passed as argument.

Use: python FacebookImageScraper.py links.csv outFolder

the links.csv has in colmn 0 all the links to scrap. outFolder is where images will be dowloaded

@author: pedzenon
"""

import sys
import pandas as pd
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import pandas as pd
from os import listdir
from os.path import isfile, join,dirname
import os


def main(argv):
    
    fileDir = os.path.dirname(os.path.realpath('__file__'))
    fileOut= os.path.join(fileDir, argv[1])
    
    data = pd.read_csv(argv[0]).iloc[:,0]
    
    for ind,line in data.iterrows():
        x = line["Link"]
        ext = re.findall(r'facebook.com/(.*)',x)[0]
        url = 'https://mobile.facebook.com/'+ext     # Generate url to scrap
        page =  urlopen(url)
        # esta caida la pagina?
        if(page.code == 200):
                
            soup = BeautifulSoup(page, 'html.parser')
           
            # todas las fotos de esta campaña estan en https_//scontent....
            pagina = re.findall(r'(scontent).+?(.+?)"', soup.prettify())
            paginas = [x[1] for x in pagina]      
            
            if(len(paginas)):   # me fijo si la pagina de facebook esta depricated
                paginas_unique = []
                j = 0
                for i in paginas:  # saco duplicados
                       if i not in paginas_unique:
                          paginas_unique.append(i)  
                          
                # como siempre te baja dos imagenes (una en alta resolucion y otra en baja), me quedo con la de alta resolucion
                pagina_unique = [x for x in paginas_unique if('/fr/' in x)][0]            
                y = "https://scontent-"+ pagina_unique.replace('amp;','')  # corrijo la url de la pagina a la foto
                
                if(len(paginas_unique) > 0):
                    
                    if(sum(["jpg" in y])):
                        ext = "jpg"
                    elif(sum(["png" in y])):
                       ext = "png"
                    elif(sum(["jpeg" in y])):
                       ext = "jpeg"
                    else:
                        print("Bad extension ",y)                                    
                        continue
                    
                    response = requests.get(y)
                    if response.status_code == 200:   
                        print(line["IMGcode"])                     
                        with open(join(fileOut, str(line["IMGcode"]) + '.' + ext), 'wb') as f:
                            f.write(response.content)  
            
if __name__ == "__main__":
   main(sys.argv[1:])    