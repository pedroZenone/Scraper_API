# -*- coding: utf-8 -*-
"""
Created on Wed Oct 17 12:35:12 2018

This is an scrapper that connects to DCM (campaigne manager) and get the creatives,
then I download manually the report and join the id of image with the metrics.

@author: pedzenon
"""
    
# para seguir la API: https://console.developers.google.com/apis/dashboard
    
import requests
import httplib2
from oauth2client import client
from oauth2client import tools 
from oauth2client.file import Storage
import pandas as pd
import json
import os
# ojo!! Hay que estar logeado con analytics.stacommedia@gmail.com
# Hay que bajarse un json con los keys desde la pagina de la API
cred = "client_secret.json"
app_name = 'my_app'   #nombre del .dat 

# con esto cargo las credenciales o me creo el .dat en caso que no exista
def generate_or_load(Appcreds,app_name):
    flow = client.flow_from_clientsecrets( # aca le cargo el json
            Appcreds ,scope=[
                    'https://www.googleapis.com/auth/dfareporting',
                    'https://www.googleapis.com/auth/dfatrafficking',
                    'https://www.googleapis.com/auth/ddmconversions'])
    
    storage = Storage(app_name+'.dat')
    credentials = storage.get()
    
    flags = tools.argparser.parse_args(args=[])
    
  # If no credentials were found, go through the authorization process and
  # persist credentials to the credential store.
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, storage, flags)
    
      # Use the credentials to authorize an httplib2.Http instance.
    http = credentials.authorize(httplib2.Http())
    
    return http

http = generate_or_load(cred,app_name)  # ingreso

fileDir = os.path.dirname(os.path.realpath('__file__'))
fileIn= os.path.join(fileDir, 'imagenes')

nombres_files = [x.lower() for x in os.listdir(fileIn)]
nombres_files = [f for f in nombres_files
                         if (((".jpg" in f) | (".jpeg" in f) | (".bmp" in f) | (".png" in f)) & (f[0] != ".") &
                             (f[0] != "~")  & ("roto" not in f) )]

imagen_codes = [x.split('.')[0] for x in nombres_files  ]  # nombre del codigo del archivo

# cargo los creativos unicos
data_DCM = pd.read_excel("DCM01-2017a11-2018.xlsx")
data_DCM = data_DCM.loc[data_DCM["Creative Type"] == "Display"]
creativesID = data_DCM.drop_duplicates(subset = ["Creative ID"]) 

# user profile de KO!
userprofiles = str(4014971)
# limpio primero la base
pd.DataFrame([],columns = ["creativeId","status"]).to_csv("StatusDownload.csv",sep = ";",index = False)

# recorro todos los creativos!
for ind,line in creativesID.iterrows():
    advertiser_id = line["Advertiser ID"]
    id_ = line["Creative ID"]
    
    if(id_ in imagen_codes):  # si ya la tengo la salteo
        continue
    
    print("paso ",id_)
    
    # hago una llamada a la API
    json_out = http.request('https://www.googleapis.com/dfareporting/v3.2/userprofiles/'+userprofiles+'/creatives/'+id_) 
        
    if(json_out[0]["status"] == '200'):  # me fjo si me dio acceso la API
        try:
            json_parsed = json.loads(json_out[1].decode('utf8'))# .replace("'", '"')  dentro de decode
        except:
             pd.DataFrame([{"creativeId":id_,"status":"Error de parseo"}]).to_csv(   # logeo error
                     "StatusDownload.csv",mode = 'a', header = None,sep = ';',index = False)   
             continue
            
        if('creativeAssets' in list(json_parsed.keys())):
            json_asset = json_parsed["creativeAssets"][0]
            
            if('assetIdentifier' in list(json_asset.keys())):
                name = json_asset['assetIdentifier']['name']
                
                if(name[-3:].lower() in ['jpg','peg','bmp','png','tml']):  # me fijo si es una imagen
                    if(name[-3:].lower() == 'tml'):
                        if(len(json_parsed["creativeAssets"][1]) > 1):  # tiene la estructura que necesito?
                            
                            name= json_parsed["creativeAssets"][1]['assetIdentifier']['name']
                        else: # caso que no tenga un agregado en name para traermelo
                             pd.DataFrame([{"creativeId":id_,"status":"Html unparseable"}]).to_csv(
                                     "StatusDownload.csv",mode = 'a', header = None,sep = ';',index = False)
                             continue
                            
                    url = 'https://s0.2mdn.net/'+advertiser_id+'/'+name
                    response = requests.get(url)
                    if response.status_code == 200:                        
                        with open(fileIn + '\\' + str(id_) + '.' + name.split('.')[-1], 'wb') as f:
                            f.write(response.content)
                        print(str(id_))                    
                    else:
                        pd.DataFrame([{"creativeId":id_,"status":"No existe la pagina"}]).to_csv(   # logeo error
                     "StatusDownload.csv",mode = 'a', header = None,sep = ';',index = False)
                        continue
                else:
                    pd.DataFrame([{"creativeId":id_,"status":"Bad extension" + name[-3:]}]).to_csv(   # logeo error
                     "StatusDownload.csv",mode = 'a', header = None,sep = ';',index = False)
                    continue
            else:
                pd.DataFrame([{"creativeId":id_,"status":"No existe AssetIdentiffier"}]).to_csv(   # logeo error
                     "StatusDownload.csv",mode = 'a', header = None,sep = ';',index = False)     
                continue
                    
        else:
            pd.DataFrame([{"creativeId":id_,"status":"No existe creativeAssets"}]).to_csv(   # logeo error
                     "StatusDownload.csv",mode = 'a', header = None,sep = ';',index = False) 
