#!/usr/bin/python 
# -*- coding:utf-8 -*-


try:
      import Tkinter
except ImportError:
      import tkinter
try:
      import thread
except ImportError:
      import _thread as thread     
import tkMessageBox
import serial
import sqlite3
import os 
import DB
import re
import datetime
import time
import tkMessageBox
import RPi.GPIO as GPIO
import ImportDB
import ExportDB
import sys
import pyqrcode
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import update
from enum import Enum
import epd2in9
import PIL
from PIL import Image, ImageDraw, ImageFont, ImageOps
import tm1637
 

########################################################################################################################################################################

"Variables globales"


dbPath = '/home/pi/Share/Public/releve.db'
csvInPath = '/home/pi/Share/Public/data.csv'
csvOutPath = '/home/pi/Share/Public/releve.csv'

Ink_Ring = ""
Ink_Position = ""
Ink_Weight = ""
Ink_State = ""

readerChoice = 0
Weight = ""

######################################################################################################################################################################

"Intialisation des ecrans"

#Ecran Ink

epd = epd2in9.EPD()
epd.init(epd.lut_partial_update)

#Ecran 7 segemnts  

led = tm1637.TM1637(CLK=21, DIO=20, brightness=7.0)
led.ShowDoublepoint(False)



###################################################################################################################################################################

"Boutons"

"""GPIO.setmode(GPIO.BCM)"""

"""GPIO.setup(13, GPIO.OUT)
GPIO.output(13, GPIO.HIGH) #Configuration des alimentations
GPIO.setup(19, GPIO.OUT)
GPIO.output(19, GPIO.HIGH)
GPIO.setup(26, GPIO.OUT)
GPIO.output(26, GPIO.HIGH)"""

"""GPIO.setup(12, GPIO.IN, pull_up_down = GPIO.PUD_UP)  #Blanc
GPIO.setup(6, GPIO.IN, pull_up_down = GPIO.PUD_UP)  #Red                   #Configuration des boutons
GPIO.setup(5, GPIO.IN, pull_up_down = GPIO.PUD_UP) #Green

GPIO.add_event_detect(12, GPIO.FALLING, bouncetime = 500)
GPIO.add_event_detect(6, GPIO.FALLING, bouncetime = 500)
GPIO.add_event_detect(5, GPIO.FALLING, bouncetime = 500)"""

"""GPIO.setup(5, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.add_event_detect(5, GPIO.FALLING, bouncetime = 500)"""


                                                                                                                                       
#################################################################################################################################################################################

class State(Enum): #Classe qui sert à verrouiller un etat
      accepted = 1
      pendingLow = 2
      pendingHigh = 3
      rejeted = 4

####################################################################################################################################################################

def pushKey(event):
      #Fonction de détection du poids
      global Weight
      if event.char:
            Weight = Weight + str(event.char)

def testIfEntryExists(testPresence):
      #Vérification de la presence de l'outade dans la base de données et si elle a deja ete pese, regarde environ 30000 outardes
      global languageChoice
      if testPresence is None:
            return {"isNew" : False} 
      elif testPresence.Weight is not None:
            return {"isNew" : False}
      else:
            return {"isNew" : True}

def testWeight(ref,WeightMes):
      #Test de la pesée pour voir si l'animal a un poids pathologique ou impossible pour eviter d'enregistreer des valeurs incoherentes et prevenir les maladies possibles de facon independante
      global languageChoice
      if  WeightMes < ref.WeightMinImp:
            return State.rejeted
      elif WeightMes > ref.WeightMaxImp:
            return State.rejeted
      elif WeightMes < ref.WeightMinPath and WeightMes > ref.WeightMinImp:
            return State.pendingLow
      elif WeightMes > ref.WeightMaxPath and WeightMes < ref.WeightMaxImp:
            return State.pendingHigh
      else:
            return State.accepted      


def conversionAzertyQwerty(strWeight):
      #Convertie les données reçues incorrects en bonne donnees pour les clavier en ou fr
      strWeight = strWeight.replace(",",".")
      strWeight = strWeight.replace(";",".")
      strWeight = strWeight.replace("&","1")
      strWeight = strWeight.replace("é","2")
      strWeight = strWeight.replace('"',"3")
      strWeight = strWeight.replace("'","4")
      strWeight = strWeight.replace("(","5")
      strWeight = strWeight.replace("-","6")
      strWeight = strWeight.replace("è","7")
      strWeight = strWeight.replace("_","8")
      strWeight = strWeight.replace("ç","9")
      strWeight = strWeight.replace("à","0")
      return strWeight

def recupUID(uid):
      #RécupérationUID
      global readerChoice
      strUid = str(uid) #Conversion binaire to string
      if readerChoice == 0:
            if len(strUid) == 31:
                  strUid = re.findall("\d+\ \d+", strUid)[0]
                  strUid = strUid.replace(" ","")
            if len(strUid) == 27:
                  strUid = strUid[9:24]      
      if readerChoice == 1:
            if len(strUid) == 14:
                  strUid = strUid.replace(" ","")
                  strUid = strUid[2:12]
            if len(strUid) == 20:
                  strUid = strUid.replace(" ","")
                  strUid = strUid[2:17]
      return strUid

def recupWeight(Weight):
      global languageChoice
      WeightStr = str(Weight)
      WeightStr = conversionAzertyQwerty(WeightStr)
      WeightDB = float(WeightStr)
      WeightStr = str(WeightDB)
      return WeightDB


def ink(ring, position, weight, state):
      foo = Image.new('RGB', (296,128), color = "white")
      draw1 = ImageDraw.Draw(foo)
      font1 = ImageFont.truetype("arial.ttf", 34)
      font2 = ImageFont.truetype("arial.ttf", 54)
      draw1.text((00,00), " " + ring, fill = 0, font = font1)
      draw1.text((00,15), " " + position, fill = 0, font = font1)
      draw1.text((00,35), " " + weight, fill = 0, font = font1)
      draw1.text((00,70), " " + state + "g", fill = 0, font = font2)
      foo = foo.rotate(90)
      foo.save('1.jpg')
      image = Image.open('1.jpg')
      epd.set_frame_memory(image, 0, 0)
      epd.display_frame()
      epd.set_frame_memory(image, 0, 0)
      epd.display_frame()

def reset():
      image = Image.open('reneco.png')
      image = image.convert('RGB')
      image = PIL.ImageOps.invert(image)
      image = image.rotate(90)
      epd.set_frame_memory(image, 0, 0)
      epd.display_frame()
      epd.set_frame_memory(image, 0, 0)
      epd.display_frame()
      led.Clear()
      led.Show([0, 0, 0, 0])
      
      
###################################################################################################################################################################

"Configurations"


dbExists = os.path.isfile(dbPath)
session = DB.createDB(dbPath)
if not dbExists:
      ImportDB.fillDB(session, csvInPath)
      ExportDB.export(dbPath,csvOutPath)
      ExportDB.convertExcel(csvOutPath)
s = session


#####################################################################################################################################################

date_access = DB.Log(Date = datetime.datetime.now())
s.add(date_access)


################################################################################################################################
"""Vérificaion date de la base de données"""

Ink_Ring = ""
Ink_Position = ""
Ink_Weight = ""
Ink_State = ""



if s.query(DB.Log).filter(DB.Log.ID == '1').first().Date.date() != datetime.date.today():
      Ink_State = "Database Outdated"
      ink(Ink_Ring, Ink_Position, Ink_Weight, Ink_State)
      sys.exit()

try:
      serLec = serial.Serial('/dev/ttyUSB0', 9600, timeout = 1) #Lecteur Biolog par câble
      readerChoice = 0
except serial.SerialException:
      Ink_State = "RFID Reader Disconnected"
      ink(Ink_Ring, Ink_Position, Ink_Weight, Ink_State)
      sys.exit()
      
      
serLec.close() #Fermeture des ports pour les ouvrir seulement quand nécessaire pour eviter le stack de données
      
reset()

#######################################################################################################################################################         
def main():
      while True:
            serLec.close()
            flagLec = True
            while flagLec: #Boucle de lecture du scanner
                  serLec.open()      
                  uid = serLec.readline()
                  serLec.close()
                  if uid: #Si on détecte un uid
                        Ink_Ring = ""
                        Ink_Position = ""
                        Ink_Weight = ""
                        Ink_State = ""
                        flagLec = False
                        serLec.close()
                        strUid = recupUID(uid)
                        persoData = s.query(DB.Session).filter(DB.Session.ID_RFID == str(strUid).strip()).first() #Recherche de l'individu dans la database et recuperation de ses infos
                        result = testIfEntryExists(persoData) #Test avec la fonction avant
                        Ink_Ring = persoData.ID_Reneco
                        ink(Ink_Ring, Ink_Position, Ink_Weight, Ink_State)
                        if(result["isNew"]):
                              flagBal = True
                              Weight = ""
                              while flagBal: #Boucle de lecture de la balance
                                    time.sleep(1)
                                    Weight = input()
                                    if Weight:
                                          flagBal = False
                                          print Weight
                                          strWeight = str(Weight) #Conversion binaire to string pour pce
                                          intWeight = int(re.findall("\d+", strWeight)[0]) #On garde que le nombre int
                                          strWeight = str(intWeight)
                                          ln = len(strWeight)
                                          if ln == 3:
                                                digits = [0, int(strWeight[0]), int(strWeight[1]),int(strWeight[2])]
                                          elif ln == 2:
                                                digits = [0, 0, int(strWeight[0]),int(strWeight[1])]
                                          elif ln == 1:
                                                digits = [0, 0, 0,int(strWeight[0])]
                                          else:
                                                digits = [int(strWeight[0]), int(strWeight[1]), int(strWeight[2]),int(strWeight[3])]
                                          led.Show(digits)
                                          if GPIO.event_detected(12):
                                                break
                                          if len(strWeight)>=0: #Si on détecte un poids
                                                flagBal = False
                                                WeightDB = recupWeight(strWeight)
                                                valid = testWeight(persoData, WeightDB)
                                                Ink_Weight = Weight
                                                print valid
                                                if (valid == State.accepted):
                                                      Ink_State = "OKAY"
                                                      ink(Ink_Ring, Ink_Position, Ink_Weight, Ink_State)
                                                      s.query(DB.Session).filter(DB.Session.ID_RFID == persoData.ID_RFID).update({"Weight" : WeightDB, "Date" : datetime.datetime.now()})
                                                      s.commit()
                                                if (valid == State.pendingLow or valid == State.pendingHigh):
                                                      if valid == State.pendingLow:
                                                            Ink_State = "LOW WEIGHT - VALIDATE ?"
                                                      if valid == State.pendingHigh:
                                                            Ink_State = "HIGH WEIGHT - VALIDATE ?"
                                                      ink(Ink_Ring, Ink_Position, Ink_Weight, Ink_State)
                                                      flagVal = True
                                                      while flagVal:
                                                            if GPIO.event_detected(12):    
                                                                  break
                                                            if GPIO.event_detected(6):
                                                                  flagVal = False
                                                                  Ink_State = "OKAY"
                                                                  ink(Ink_Ring, Ink_Position, Ink_Weight, Ink_State)
                                                                  s.query(DB.Session).filter(DB.Session.ID_RFID == persoData.ID_RFID).update({"Weight" : WeightDB, "Date" : datetime.datetime.now()})
                                                                  s.commit()
                                                            if GPIO.event_detected(5):
                                                                  flagVal = False
                                                                  Ink_State = "ERROR"
                                                                  ink(Ink_Ring, Ink_Position, Ink_Weight, Ink_State)
                                                if (valid == State.rejeted):
                                                      Ink_State = "ERROR"
                                                      ink(Ink_Ring, Ink_Position, Ink_Weight, Ink_State)
                        else:
                              Ink_State = "ERROR"
                              ink(Ink_Ring, Ink_Position, Ink_Weight, Ink_State)
            ExportDB.export(dbPath, csvOutPath)
            flagReset = True
            time.sleep(10)
            reset()
            """while flagReset:
                  if GPIO.event_detected(36):
                        flagReset = False"""

if __name__ == '__main__':
    main()