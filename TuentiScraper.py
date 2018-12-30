# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 15:54:25 2018

@author: pedzenon
"""

# https://foro.tuenti.com.ar/threads/10118-%C2%A1Dejanos-ac%C3%A1-tu-idea-o-sugerencia!    interesante...

from urllib.request import urlopen
from bs4 import BeautifulSoup
import urllib
from urllib.request import urlopen
from urllib.request import Request
import re
import pandas as pd
import os
import ssl
from re import finditer
import time
from fake_useragent import UserAgent
from urllib.parse import quote as url_encode
from urllib.parse import unquote as url_decode
from unicodedata import normalize

# =============================================================================
# @brief: Crawler bot that get the whole comments of threads in a given topic of
# Tuenti forum. It understand if the comment is an answer or a comment. Los resultados
# los va cargando en nombre_file. Setearlo al incio.
# =============================================================================
class crawler:

    # set csv name where the scraped comment will be loaded
    def __init__(self,nombre_file = 'actuality.csv'):
        self.pegadas = 0
        self.headers = UserAgent()  # initialize user-agent object por use it randomly
        self.header = self.headers.random
        self.context = ssl._create_unverified_context()  # needed for get url
        # preseteo el csv de input
        self.nombre_file = nombre_file
        try:
            aux = pd.read_csv(nombre_file,sep = '|',encoding = 'ANSI')
            self.allready_pages =  aux.url.values.tolist()
        except:
            pd.DataFrame([],columns = ["status","url","Respuesta","mensaje"]).to_csv(nombre_file,sep = '|',encoding = 'ANSI',index = False)
            self.allready_pages =  []
    
    def acentos_out(self,s):
        x = re.sub(
            r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1", 
            normalize( "NFD", s), 0, re.I )
        return x
    
    # corrigo las frases. Le saco todos los <...> y el enviado desde mi...    
    def parse_obtainedData(self,x):
        y = re.sub(r'<(.*?)>',' ',x)
        y = y[0:-2]
        
        if(len([x for x in finditer("enviado desde", y.lower())])> 0):
            bounds = [x for x in finditer("enviado desde", y.lower())][-1].span()
            y = y[0:bounds[0]]     # paso el mensaje a ascii!!
    
        y = ''.join(re.findall(r'[\sa-zA-Záéíóúñ@0-9]',y))
        y = re.sub(r'\s+',' ',y)  # 
        return re.sub(r'@\s*','@',y)

# =============================================================================
# @ brief: Dentro de cada thread voy navegando por todas las paginas sacando los 
# comentarios.
# =============================================================================
    def threads_scrap(self,thread_name,real_thread_name): 
        page =  urlopen('https://foro.tuenti.com.ar/threads/'+thread_name,context = self.context)        
        soup = BeautifulSoup(page, 'html.parser')
        
        page_numbers =  re.findall(r'/page(\d+)', soup.prettify().replace('\n',' '))  # me fijo cuantas paginas tiene
        
        # si solo tiene una pagina no te va a devolver nada.
        if(len(page_numbers) > 0):
            max_num = max([int(x) for x in page_numbers])
        else:
            max_num = 0
        
        page_content = pd.DataFrame([],columns = ['mensaje','Respuesta'])
        
        for i in range(max_num):           
            
            url = 'https://foro.tuenti.com.ar/threads/' + thread_name + '/page' + str(i)
            
            # pregunto si ya me traje la data de esta pagina!
            if(url in self.allready_pages):
                continue # saltea el bucle
            
            req = Request(url = url,
                          headers = {'User-Agent' : self.header})   # le agrego header para que no se de cuenta la pagina que soy un bot ;)
            page =  urlopen( req, context = self.context )
            
            if(page.status != 200):  # log error
                pd.DataFrame([{"url":url,"status":"Fail " + str(page.status), "Respuesta": None , "mensaje":None }]).to_csv(
                        self.nombre_file, mode = 'a', header = None,sep = '|',encoding = 'ANSI',index = False)  
                continue
            
            self.pegadas += 1
            # si le pegue muchas veces duermo un ratito y cambio de user agent, no quiero que me bloqueen de la pagina
            if(self.pegadas > 100):
                print("zzzzzz")
                self.pegadas = 0
                time.sleep(30)  # sleep 5 minutos        
                self.header = self.headers.random
                
            soup = BeautifulSoup(page, 'html.parser')
            pagina = re.findall(r'<blockquote class="postcontent restore ">(.*?)blockquote>', soup.prettify().replace('\n',' '))
            
            # me genero un dataframe con el mensaje limpio y identidico si el mensaje viene de una respuesta o es comentario orignial
            list_contet = []
            for page in pagina:
                if(re.findall(r'bbcode_container',page)):
                    if(len([x for x in finditer("div", page)])> 0):
                        bounds = [x for x in finditer("div", page)][-1].span()
                        list_contet.append(                               # el +1 es pora el find lo hago sobre div solo, no sobre <div>
                                {'mensaje':self.parse_obtainedData(page[bounds[1]+1:]),'Respuesta':"si"})   
                else:
                    list_contet.append({'mensaje':self.parse_obtainedData(page),'Respuesta':"no"})
                
                aux = pd.concat([pd.DataFrame( [ {"url":url,"status":"OK"}]),pd.DataFrame([list_contet[-1]]) ] ,axis=1)
                aux.to_csv(self.nombre_file, mode = 'a', header = None,sep = '|',encoding = 'ANSI',index = False)
                
            page_content = page_content.append(pd.DataFrame(list_contet),ignore_index = True)
            
        return page_content
    
# =============================================================================
# @brief: metodo principal. AL instanciarlo el crawler se va metiendo en todos los threads
# del topico elegido y descarga todos los comentarios en el csv seteado.
# =============================================================================
    def scraper(self,topico):
        
        df = pd.DataFrame([],columns = ['Respuesta', 'mensaje'])
        
        # Solo me interesa ver hasta 6 paginas para hasta 6 paginas para atras (threads mas viejos son de antes de 2018)
        # En cada ciclo del for saco los nombres de todos los threads de esa pagina.        
        for j in range(6):
            page =  urlopen('https://foro.tuenti.com.ar/forums/'+topico + '/page' + str(j),context = self.context)
            soup = BeautifulSoup(page, 'html.parser')
            threads = re.findall(r'<a class="title" href="threads/(.*?)" id', soup.prettify().replace('\n',' '))
            threads_real = [re.findall(r'(.*?)\?s=',x)[0] for x in threads]
            threads_2Use = [url_encode(x) for x in threads_real]            
            
            # comienzo a entrar thread a thread y sacar todos los comentarios.
            for threads_2Use,thread_real in zip(threads_2Use,threads_real):
                print(thread_real)
                aux = self.threads_scrap(threads_2Use,thread_real)
                df = df.append(aux,ignore_index = True)
            
        return df
    
    def acomodar_data(self):
        data = pd.read_csv(self.nombre_file,sep = '|',encoding = 'ANSI')
        data["mensaje"] = data["mensaje"].apply(lambda x:re.sub(r'\s+',' ',x))
        data["mensaje"] = data["mensaje"].apply(lambda x:re.sub(r'@\s*','@',x))
        data.to_csv(self.nombre_file,sep = '|',encoding = 'ANSI')
        return data
 
# %% Main:
           
#topic_name = '7-M%C3%A1s-amp-%E2%80%9D'     
topic_name = url_encode('20-Contanos-qué-onda-Tuenti-Feedback')
TuentiScrap = crawler(nombre_file = 'contanosQueOndaTuenti.csv')
TuentiScrap.scraper(topic_name)

topic_name = url_encode('7-M%C3%A1s-amp-%E2%80%9D')
TuentiScrap2 = crawler(nombre_file = 'masMierda.csv')
TuentiScrap2.scraper(topic_name)

# ahora me fijo cuales son los threads que me interesan!

def threads_uniques(x):
    data = pd.read_csv(x,sep = '|',encoding = 'ANSI')
    data["thread"] = data.url.apply(lambda x: re.findall(r'threads/(.*?)/page\d+',x)[0])
    data["thread"] = data.thread.apply(lambda x: url_decode(x))
    pd.DataFrame(data.thread.unique(),columns = ["Threads"]).to_excel("ThreadsUnicos_"+x[0:-4]+".xlsx",index = False)
    
threads_uniques('masMierda.csv')
threads_uniques('contanosQueOndaTuenti.csv')