# -*- coding: utf-8 -*-
"""
Created on Thu May  3 12:58:22 2018

Connection API to extract Admetricks data

@author: pedzenon
"""

import requests
import pandas as pd
import datetime
import pyodbc
from sqlalchemy import create_engine
import urllib

start_date = datetime.date(2018, 3, 1)
end_date = datetime.date(2018, 4, 10)

d = start_date
delta = datetime.timedelta(days=1)

anterior = pd.DataFrame([])

while d <= end_date:    # Recorro el calendario
    date_ = d.strftime("%Y-%m-%d")
    d += delta 
    # Accedo a la API y me traigo la data por día
    url = 'http://clientela.admetricks.com/o/token/?grant_type=password&username=USER_NAME&password=PASSWORD&client_id=IW8M80h7qgCaSz4hPm3gr3wJP89NiJTPyhkwPurT&client_secret=KnBW84uyHlxwlNrKOXyym6Ro1IT6IlYdhScdop63hHddCzJIxUwDG7VItNgEONb1U2ebEH6fBmkYgX9LrZD4uqFJlYscHYn9MLxOm2qVccNE2WGEuePpKA7t3jQ2CvMu'
    conn  = requests.post(url)
    
    if(conn.status_code == 200 ):
        data_conn = conn.json()
        data_bajada = requests.post("http://clientela.admetricks.com/market-report/data/?day=" + date_ + "&country=1&device=1&ad_type=1",headers = {'Authorization': data_conn["token_type"]+" "+data_conn["access_token"]})
        data = data_bajada.json()
        data = data["data"]
        
        bajada = pd.DataFrame(data)
        bajada["fecha"] = date_        
        print("Ready API: ",date_)
        # Escribo En la db
        server = 'sql1.publicisone-latam.com,1189'
        db = 'KO_SLBU_Competitive'
         
        params = urllib.parse.quote_plus('DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + db + ';UID=arOwner;PWD=wraJU6huw-AN')
        conn_str = 'mssql+pyodbc:///?odbc_connect={}'.format(params)
        engine = create_engine(conn_str)
        bajada.to_sql(name='Admetricks',con=engine, if_exists='append',index=False)
        
        # Me cargo una imagen de la escritura total en la variable anterior. Medio al pedo...
        print("Ready load: ",date_)
        anterior = pd.concat([anterior,bajada])
        
    else:
        print("-------- Error en dia: ",date_)
