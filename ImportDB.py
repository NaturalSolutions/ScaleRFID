#!/usr/bin/python 
# -*- coding:utf-8 -*-


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import datetime
import pymssql
import DB
import csv
import time 


def fillDB(dbSession, data):

    print ("Beginning creation")

    print('Processing csv data file')
    ifile = open(data, 'r')
    read = csv.reader(ifile)

    for row in read:
        if row[5] == "Unk":
            row[5] = "0"
        ses = DB.Session(BID = row[1], ID_RFID = row[2], ID_Reneco = row[3], Species = row[4], Gender = row[5],  Age = row[6], Date_Session = datetime.datetime.now(), WeightMinPath = float(row[7].replace(',','.')), WeightMaxPath = float(row[8].replace(',','.')), WeightMinImp = float(row[9].replace(',','.')), WeightMaxImp = float(row[10].replace(',','.')))
        dbSession.add(ses)
        dbSession.commit()

    print("Break Time !")
    time.sleep(2)

    date_creation = DB.Comment(Date = datetime.datetime.now())
    s.add(date_creation)

    print('Ending creation')
    
