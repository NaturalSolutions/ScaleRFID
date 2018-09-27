#!/usr/bin/python 
# -*- coding:utf-8 -*-

import serial
import sqlite3
import sqlalchemy
import os
import datetime
import glob
import RPi.GPIO
import sys
import time

import epd2in9
import epdif

import DB
import Screen
import Scale
import Reader
import Export

import classGetch

#######################################################################################################################################################         

"Définitions des constantes"

date = str(datetime.datetime.now())[0:10]
dateDB = date[8] +  date[9] + '/' + date[5] + date[6] + '/'+ date[0] + date[1] + date[2] +  date[3]

files = glob.glob('/home/pi/Share/Public/*.db')
dbFile = max(files, key=os.path.getctime)
print(dbFile)

nameFile = ("WeightsFile_" + date).replace("-","")

csvFile = '/home/pi/Share/Public/' + nameFile + '.csv'
xlsxFile = '/home/pi/Share/Public/' + nameFile + '.xlsx'

#######################################################################################################################################################         

"Initialisation"

Screen.blank()

inKey = classGetch._Getch() #Catch les touches (necessaire pour la prisede poids)

reader = Reader.initReader()

session = DB.initDB(dbFile)

DB.testSession(session)

Export.export(dbFile, nameFile, date, dateDB)


def main():
      print("0")
      while True:
            print("1")
            Screen.blank()
            print("2")
            uidBird = Reader.readChip(reader)
            print("3")
            dataBird = DB.searchDB(session, uidBird)
            print("4")
            resultBird = DB.testBird(dataBird)
            print("5")
            weight = Scale.weigh()
            print("6")
            resultWeight = Scale.control(weight, dataBird)
            print("7")
            stateBird = DB.validateBird(session, resultWeight, inKey, dataBird, weight)
            print("8")
            Export.export(dbFile, nameFile, date, dateDB)
            time.sleep(5)



if __name__ == '__main__':
      while True:
            try:
                  main()
            except KeyboardInterrupt:
                  sys.exit()
            """except BaseException:
                  print(BaseException)
                  pass"""
 