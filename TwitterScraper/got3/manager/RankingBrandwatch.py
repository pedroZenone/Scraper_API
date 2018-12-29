#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 20 15:08:03 2018

@author: pedzenon
"""

import pandas as pd
from os.path import join
import os

fileDir = os.path.dirname(os.path.realpath('__file__'))

data = pd.read_excel(join(join(fileDir,"data_varios"),"2015669735_Gorda.xlsx"))
data.columns = data.iloc[5,:].values
data = data.drop(list(range(6)))

data = data.dropna(subset = ["Mentioned Authors"])
rank = data[["Mentioned Authors"]].groupby(["Mentioned Authors"]).size().reset_index()

