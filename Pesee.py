#!/usr/bin/python 
# -*- coding:utf-8 -*-


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
import Export
import sys
import pyqrcode
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import update
import epd2in9
import PIL
from PIL import Image, ImageDraw, ImageFont, ImageOps
import tm1637
import glob

import classState
import classGetch



######################################################################################################################################################################

"Intialisation des ecrans"

#Ecran Ink

epd = epd2in9.EPD()
epd.init(epd.lut_partial_update)


#######################

print ("start")

"Demarrage du systeme"


faa = Image.new('RGB', (296,128), color = "white")
draw1 = ImageDraw.Draw(faa)
font1 = ImageFont.truetype("/home/pi/Desktop/ProjetRFID/DejaVuSans.ttf",30)
draw1.text((00,00), "STARTING...WAIT", fill = 100, font = font1)
faa = faa.rotate(270)
faa.save('1.jpg')
image = Image.open('1.jpg')
epd.set_frame_memory(image, 0, 0)
epd.display_frame()
epd.set_frame_memory(image, 0, 0)
epd.display_frame()


time.sleep(3)



########################################################################################################################################################################

"Variables globales"

list_of_files = glob.glob('/home/pi/Share/Public/*.db') # * means all if need specific format then *.db
latest_file = max(list_of_files, key=os.path.getctime)
dbPath = latest_file


csvOutPath = '/home/pi/Share/Public/releve.csv'

Ink_Ring = ""
Ink_Position = ""
Ink_Weight = ""
Ink_State = ""

readerChoice = 0
Weight = ""

                                                                                                       

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
            return classState.State.rejeted
      elif WeightMes > ref.WeightMaxImp:
            return classState.State.rejeted
      elif WeightMes < ref.WeightMinPath and WeightMes > ref.WeightMinImp:
            return classState.State.pendingLow
      elif WeightMes > ref.WeightMaxPath and WeightMes < ref.WeightMaxImp:
            return classState.State.pendingHigh
      else:
            return classState.State.accepted      


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
      font1 = ImageFont.truetype("/home/pi/Desktop/ProjetRFID/DejaVuSans.ttf",26)
      font2 = ImageFont.truetype("/home/pi/Desktop/ProjetRFID/DejaVuSans-Bold.ttf", 20)
      draw1.text((00,00), " " + ring, fill = 0, font = font1)
      draw1.text((00,25), " " + position, fill = 0, font = font1)
      draw1.text((00,50), " " + weight + "g", fill = 0, font = font1)
      draw1.text((00,75), " " + state , fill = 0, font = font2)
      foo = foo.rotate(270)
      foo.save('1.jpg')
      image = Image.open('1.jpg')
      epd.set_frame_memory(image, 0, 0)
      epd.display_frame()
      epd.set_frame_memory(image, 0, 0)
      epd.display_frame()

def reset():
      faa = Image.new('RGB', (296,128), color = "white")
      draw1 = ImageDraw.Draw(faa)
      font1 = ImageFont.truetype("/home/pi/Desktop/ProjetRFID/DejaVuSans.ttf",34)
      draw1.text((00,00), "SCAN", fill = 100, font = font1)
      faa = faa.rotate(270)
      faa.save('1.jpg')
      image = Image.open('1.jpg')
      epd.set_frame_memory(image, 0, 0)
      epd.display_frame()
      epd.set_frame_memory(image, 0, 0)
      epd.display_frame()

      
      
###################################################################################################################################################################

"Configurations"


dbExists = os.path.isfile(dbPath)
if dbExists == False:
      faa = Image.new('RGB', (296,128), color = "white")
      draw1 = ImageDraw.Draw(faa)
      font1 = ImageFont.truetype("/home/pi/Desktop/ProjetRFID/DejaVuSans.ttf",20)
      draw1.text((00,00), "ERROR", fill = 100, font = font1)
      draw1.text((00,30), "DataBase_Not_Found", fill = 100, font = font1)
      faa = faa.rotate(270)
      faa.save('1.jpg')
      image = Image.open('1.jpg')
      epd.set_frame_memory(image, 0, 0)
      epd.display_frame()
      epd.set_frame_memory(image, 0, 0)
      epd.display_frame()
      sys.exit()

session = DB.createDB(dbPath)
s = session

inkey = classGetch._Getch()


#####################################################################################################################################################

date_access = DB.Log(Date = datetime.datetime.now())
s.add(date_access)


################################################################################################################################
"""Vérification date de la base de données"""

Ink_Ring = ""
Ink_Position = ""
Ink_Weight = ""
Ink_State = ""

"""if s.query(DB.Log).filter(DB.Log.ID == '1').first().Date.date() != datetime.date.today():
      faa = Image.new('RGB', (296,128), color = "white")
      draw1 = ImageDraw.Draw(faa)
      font1 = ImageFont.truetype("/home/pi/Desktop/ProjetRFID/DejaVuSans.ttf",20)
      draw1.text((00,00), "ERROR", fill = 100, font = font1)
      draw1.text((00,30), "Database_Outdated", fill = 100, font = font1)
      faa = faa.rotate(270)
      faa.save('1.jpg')
      image = Image.open('1.jpg')
      epd.set_frame_memory(image, 0, 0)
      epd.display_frame()
      epd.set_frame_memory(image, 0, 0)
      epd.display_frame()
      sys.exit()"""

try:
      serLec = serial.Serial('/dev/ttyUSB0', 9600, timeout = 1) #Lecteur Biolog par câble
      readerChoice = 0
except serial.SerialException:
      faa = Image.new('RGB', (296,128), color = "white")
      draw1 = ImageDraw.Draw(faa)
      font1 = ImageFont.truetype("/home/pi/Desktop/ProjetRFID/DejaVuSans.ttf",20)
      draw1.text((00,00), "ERROR", fill = 100, font = font1)
      draw1.text((00,30), "RFID_Reader_Disconnected", fill = 100, font = font1)
      faa = faa.rotate(270)
      faa.save('1.jpg')
      image = Image.open('1.jpg')
      epd.set_frame_memory(image, 0, 0)
      epd.display_frame()
      epd.set_frame_memory(image, 0, 0)
      epd.display_frame()
      sys.exit()

serLec.close() #Fermeture des ports pour les ouvrir seulement quand nécessaire pour eviter le stack de données
      




#######################################################################################################################################################         
def main():
      print ("start")
      while True:
            reset()
            Export.export(dbPath)
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

                        try:
                              Ink_Ring = str(persoData.ID_Reneco)
                        except AttributeError:
                              faa = Image.new('RGB', (296,128), color = "white")
                              draw1 = ImageDraw.Draw(faa)
                              font1 = ImageFont.truetype("/home/pi/Desktop/ProjetRFID/DejaVuSans.ttf",20)
                              draw1.text((00,00), "ERROR", fill = 100, font = font1)
                              draw1.text((00,30), "Bird_Chip_ Not_In_Database", fill = 100, font = font1)
                              faa = faa.rotate(270)
                              faa.save('1.jpg')
                              image = Image.open('1.jpg')
                              epd.set_frame_memory(image, 0, 0)
                              epd.display_frame()
                              epd.set_frame_memory(image, 0, 0)
                              epd.display_frame()
                              break

                        try: 
                              Ink_Position = str(persoData.Position)
                        except AttributeError:
                              faa = Image.new('RGB', (296,128), color = "white")
                              draw1 = ImageDraw.Draw(faa)
                              font1 = ImageFont.truetype("/home/pi/Desktop/ProjetRFID/DejaVuSans.ttf",20)
                              draw1.text((00,00), "ERROR", fill = 100, font = font1)
                              draw1.text((00,30), "Bird_Position_ Not_In_Database", fill = 100, font = font1)
                              faa = faa.rotate(270)
                              faa.save('1.jpg')
                              image = Image.open('1.jpg')
                              epd.set_frame_memory(image, 0, 0)
                              epd.display_frame()
                              epd.set_frame_memory(image, 0, 0)
                              epd.display_frame()
                              break

                        print(Ink_Ring)
                        print(Ink_Position)
                        ink(Ink_Ring, Ink_Position, Ink_Weight, Ink_State)
                        result = testIfEntryExists(persoData) 

                        if(result["isNew"]):
                              flagBal = True
                              Weight = ""
                              while flagBal: #Boucle de lecture de la balance
                                    time.sleep(1)
                                    try:
                                          Weight = raw_input()
                                    except EOFError:
                                          pass
                                    if Weight:
                                          print Weight
                                          flagBal = False
                                          strWeight = str(Weight) #Conversion binaire to string pour pce
                                          print strWeight
                                          intWeight = int(re.findall("\d+", strWeight)[0]) #On garde que le nombre int
                                          strWeight = str(intWeight)
                                          if len(strWeight)>=0: #Si on détecte un poids
                                                flagBal = False
                                                WeightDB = recupWeight(strWeight)
                                                valid = testWeight(persoData, WeightDB)
                                                Ink_Weight = strWeight
                                                if (valid == classState.State.accepted):
                                                      print("9.1")
                                                      Ink_State = "OK"
                                                      ink(Ink_Ring, Ink_Position, Ink_Weight, Ink_State)
                                                      s.query(DB.Session).filter(DB.Session.ID_RFID == persoData.ID_RFID).update({"Weight" : WeightDB, "Date" : datetime.datetime.now()})
                                                      s.commit()
                                                if (valid == classState.State.pendingLow or valid == classState.State.pendingHigh):
                                                      print("9.2")
                                                      if valid == classState.State.pendingLow:
                                                            Ink_State = "WEIGHT_TOO_LOW"
                                                      if valid == classState.State.pendingHigh:
                                                            Ink_State = "WEIGHT_TOO_HIGH"
                                                      ink(Ink_Ring, Ink_Position, Ink_Weight, Ink_State)
                                                      flagVal = True
                                                      p = inkey()
                                                      while flagVal:
                                                            if p == "y":
                                                                  flagVal = False
                                                                  Ink_State = "OK"
                                                                  ink(Ink_Ring, Ink_Position, Ink_Weight, Ink_State)
                                                                  s.query(DB.Session).filter(DB.Session.ID_RFID == persoData.ID_RFID).update({"Weight" : WeightDB, "Date" : datetime.datetime.now()})
                                                                  s.commit()
                                                            if p == "n":
                                                                  flagVal = False
                                                                  Ink_State = "WEIGHT_CANCELLED"
                                                                  ink(Ink_Ring, Ink_Position, Ink_Weight, Ink_State)
                                                if (valid == classState.State.rejeted):
                                                      print("9.3")
                                                      Ink_State = "IMPOSSIBLE_WEIGHT"
                                                      ink(Ink_Ring, Ink_Position, Ink_Weight, Ink_State)
                        else:
                              Ink_State = "ERROR"
                              ink(Ink_Ring, Ink_Position, Ink_Weight, Ink_State)
            Export.export(dbPath)
            time.sleep(5)


if __name__ == '__main__':
      while True:
            try:
                  main()
            except KeyboardInterrupt:
                  sys.exit()
            except:
                  pass
            '''else: 
                  break'''
