#!/usr/bin/python 
# -*- coding: utf-8 -*-


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import datetime
import pymssql
import DB
import csv
import time
import codecs



def fillDB(dbSession, data):

    print ("Beginning creation")

    print('Processing csv data file')
    ifile = open(data, 'r')
    read = csv.reader(ifile, delimiter = ';')

    for row in read:
        
        ses = DB.Session( ID_Reneco = row[0], ID_RFID = row[1], Position = row[2].decode('iso-8859-1') , Date_Session =  datetime.datetime.strptime(row[3], '%Y-%m-%d'), WeightMinPath = row[4], WeightMaxPath = row[5], WeightMinImp = row[6], WeightMaxImp = row[7])
        dbSession.add(ses)
        dbSession.commit()


    print("Break Time !")
    time.sleep(1)

    date_creation = DB.Log(Date = datetime.datetime.now())
    dbSession.add(date_creation)

    print('Ending creation')
    
if __name__ == '__main__':
    fillDB()