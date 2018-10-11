#!/usr/bin/python 
# -*- coding:utf-8 -*-



###############################################################################

"Import"


try:
      import thread
except ImportError:
      import _thread as thread     
import serial
import sqlite3
import os 
import DB
import re
import datetime
import time
import RPi.GPIO as GPIO
import Export
import Screen
import sys
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import update
import epd2in9
import PIL
from PIL import Image, ImageDraw, ImageFont, ImageOps
import glob

import classState
import classGetch



###############################################################

"Intialisation des ecrans"

epd = epd2in9.EPD()
epd.init(epd.lut_partial_update)
Screen.reset()

##############################################

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



# def ch

########################################################################################################################################################################

"Variables"

# list_of_files = glob.glob('/home/pi/Share/Public/*.db') # * means all if need specific format then *.db
# if len(list_of_files)== 0:
#       Screen.msg("Database not found", 'ERROR', True)
#       exit()
# latest_file = max(list_of_files, key=os.path.getctime)
# dbPath = latest_file
#TOTDO = dynamicfilename
filename= 'WeightsFile_201801011.csv'
csvOutPath = '/home/pi/Share/Public/releve.csv'

Ink_Ring = ""
Ink_Position = ""
Ink_Weight = ""
Ink_Last_Weight = ""
Ink_State = ""
Ink_Day_Since = ""

Weight = ""


# dbExists = os.path.isfile(dbPath)

# if dbExists == False:
#       Screen.msg("Database not found", 'ERROR', True)
      
      # faa = Image.new('RGB', (296,128), color = "white")
      # draw1 = ImageDraw.Draw(faa)
      # font1 = ImageFont.truetype("/home/pi/Desktop/ProjetRFID/DejaVuSans.ttf",20)
      # draw1.text((00,00), "ERROR", fill = 100, font = font1)
      # draw1.text((00,30), "Database Not Found", fill = 100, font = font1)
      # faa = faa.rotate(270)
      # faa.save('1.jpg')
      # image = Image.open('1.jpg')
      # epd.set_frame_memory(image, 0, 0)
      # epd.display_frame()
      # epd.set_frame_memory(image, 0, 0)
      # epd.display_frame()
      # sys.exit()

# session = DB.createDB(dbPath)
dbinfos = DB.testSession() 
# s = session
# if DB.testSession(s) == False:
#       exit()
s = dbinfos['session']
dbPath = dbinfos['file']

# # print('tested')

inkey = classGetch._Getch()

# date_access = DB.Log(Date = datetime.datetime.now())
# s.add(date_access)


                                                                                                      
####################################################################################################################################################################

"Fonctions"


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
      if  WeightMes < ref.Weight_Min_Imp:
            return classState.State.rejeted
      elif WeightMes > ref.Weight_Max_Imp:
            return classState.State.rejeted
      elif WeightMes < ref.Weight_Min_Path and WeightMes > ref.Weight_Min_Imp:
            return classState.State.pendingLow
      elif WeightMes > ref.Weight_Max_Path and WeightMes < ref.Weight_Max_Imp:
            return classState.State.pendingHigh
      else:
            return classState.State.accepted      

def recupUID(uid):
      uid = str(uid)
      start = '$A0112OKD'
      end = '#'
      print('luid . ' + uid)
      # try:
      uid = (uid.split(start))[1].split(end)[0]
      # except Exception:
            # return None
      uid = uid[0:15]
      print uid
 
      return uid

def recupWeight(Weight):
      global languageChoice
      WeightStr = str(Weight)
      WeightDB = float(WeightStr)
      WeightStr = str(WeightDB)
      return WeightDB


# def ink(ring, position, weight, state):
#       foo = Image.new('RGB', (296,128), color = "white")
#       draw1 = ImageDraw.Draw(foo)
#       font1 = ImageFont.truetype("/home/pi/Desktop/ProjetRFID/DejaVuSans.ttf",26)
#       font2 = ImageFont.truetype("/home/pi/Desktop/ProjetRFID/DejaVuSans-Bold.ttf", 20)
#       draw1.text((00,00), " " + ring, fill = 0, font = font1)
#       draw1.text((00,25), " " + position, fill = 0, font = font1)
#       draw1.text((00,50), " " + weight + "g", fill = 0, font = font1)
#       draw1.text((00,75), " " + state , fill = 0, font = font2)
#       foo = foo.rotate(270)
#       foo.save('1.jpg')
#       image = Image.open('1.jpg')
#       epd.set_frame_memory(image, 0, 0)
#       epd.display_frame()
#       epd.set_frame_memory(image, 0, 0)
#       epd.display_frame()

# def reset():
#       faa = Image.new('RGB', (296,128), color = "white")
#       draw1 = ImageDraw.Draw(faa)
#       font1 = ImageFont.truetype("/home/pi/Desktop/ProjetRFID/DejaVuSans.ttf",34)
#       draw1.text((00,00), "READY", fill = 100, font = font1)
#       faa = faa.rotate(270)
#       faa.save('1.jpg')
#       image = Image.open('1.jpg')
#       epd.set_frame_memory(image, 0, 0)
#       epd.display_frame()
#       epd.set_frame_memory(image, 0, 0)
#       epd.display_frame()

       


################################################################################################################################
"""Vérification date de la base de données"""

Ink_Ring = ""
Ink_Position = ""
Ink_Weight = ""
Ink_State = ""

def remarks():
      Screen.msg_multi_lines(['1 - No remark','2 - Skinny', '3 - Fat', '4 - Other problem'], 'ACTION', 7)
      flagVal = True
      p = inkey()

      while flagVal:
            if p == 'a':
                  flagVal = False
                  return ''
            elif p == 'b':
                  flagVal = False
                  return 'Skinny'
            elif p == 'c':
                  flagVal = False
                  return 'Fat'
            elif p == 'd':
                  flagVal = False
                  return 'Some problem have been noticed'



#TEst des affichages a suppr 0 intérets
def screenmethis():
      print('reset')
      epd.clear_frame_memory(0xFF)
      epd.display_frame()
      time.sleep(2)
      print('endreset')
      print('grande taille : ' + str(len('Bird chip not in database')))      
      Screen.msg('Bird chip not in database', 'ERROR', True)
      time.sleep(2)
      Screen.msg('Bird chip not in database', 'ERROR', True)                              
      time.sleep(2)      
      print('grande taille : ' + str(len('Bird position not in database')))
      Screen.msg('Bird position not in database', 'ERROR', True)
      time.sleep(2)      
      Screen.msg('Bird already weighted','ERROR', True)
      time.sleep(2)      
      Screen.msg('Bird chip not in database','ERROR', True)                                
      time.sleep(2)
      exit()      

# screenmethis()
##FINB TEst affichage Normal² 
##Tes affichage multi ligne full info outardes
def screen_my_bustard():
      Screen.msg('Bloupi machine plus plus','Boulp',0)
      time.sleep(2)
      Screen.msg('Bloupi machine plus plus','Boulp',1)
      
      # Screen.msg_multi_lines(['Boulp','Bloupi machine plus plus','Le bigorno des pres n est pas propre'],'Olala l\'erreur', True)
      exit()
# screen_my_bustard()

def hard_reset():
      epd.clear_frame_memory(0xFF)
      epd.display_frame()
      epd.clear_frame_memory(0xFF)
      epd.display_frame()

print('hard')      
hard_reset()
print('endhard')      
# screen_my_bustard()
##Fin test multi ligne
try:
      serLec = serial.Serial('/dev/ttyUSB0', 9600, timeout = 1) #Lecteur 
except serial.SerialException:
      Screen.msg('RFID Reader Disconnected', 'ERROR', True)      
      sys.exit()

serLec.close() #Fermeture des ports pour les ouvrir seulement quand nécessaire pour eviter le stack de données





#######################################################################################################################################################         
def main():
      print("start weight")
      while True:
            Screen.reset()
            Screen.msg('Scan ready')
            Export.export(dbPath, filename)
            serLec.close()
            flagLec = True
            while flagLec: #Boucle de lecture du scanner
                  serLec.open()   
                  uid = serLec.readline(100)
                  serLec.close()
                  if uid: #Si on détecte un uid
                        flagLec = False
                        serLec.close()
                        Ink_Ring = ""
                        Ink_Position = ""
                        Ink_Weight = ""
                        Ink_State = ""            
                        print('uid : ' + uid)
                        try:
                              strUid = recupUID(uid)
                        except Exception:
                              print(Exception.message)
                              break
                        # if strUid == None:
                        #       Screen.msg('Please scan again','ERROR',True)
                        #       sleep(1)
                        #       break
                        print('struid  = ' + strUid)
                        persoData = s.query(DB.Session).filter(DB.Session.ID_RFID == str(strUid).strip()).first() #Recherche de l'individu dans la database et recuperation de ses infos
                        print('persoData', persoData)

                        if str(persoData) == 'None':
                              Screen.msg('Bird Chip Not In Database', 'ERROR', True)                             
                              break  

                        try:
                              Ink_Ring = str(persoData.ID_Reneco) #test en double
                        except AttributeError:
                              Screen.msg('Bird Chip Not In Database', 'ERROR', True)                                                           
                              # break

                        try: 
                              Ink_Position = str(persoData.Position)
                        except AttributeError:
                              Screen.msg('Bird Position Not In Database', 'ERROR', True)                             
                              break

                        Ink_Day_Since = str(persoData.Days_Since_Last_Weight)                        
                        Ink_Last_Weight = str(persoData.Last_Weight)  
                        print('Ink_Day_Since  ' + Ink_Day_Since)                      
                        print('Ink_Last_Weight   ' + Ink_Last_Weight)                      
 
                        try:
                              Ink_Weight = str(persoData.Weight)
                              if Ink_Weight != 'None':
                                    Screen.msg('Bird Already Weighed','NOTICE', True)                                   
                                    break
                              if Ink_Weight == 'None':
                                    Ink_Weight = ""
                        except AttributeError:
                              Screen.msg('Bird Chip Not In Database','ERROR', True)                                                           
                              break  

                        Screen.bird_it(Ink_Ring, Ink_Position, Ink_Last_Weight, Ink_Day_Since)
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
                                          flagBal = False
                                          strWeight = str(Weight) #Conversion binaire to string pour pce
                                          print strWeight
                                          intWeight = int(re.findall("\d+", strWeight)[0]) #On garde que le nombre int
                                          strWeight = str(intWeight)
                                          if len(strWeight)>=0: #Si on détecte un poids                                                
                                                WeightDB = recupWeight(strWeight)
                                                valid = testWeight(persoData, WeightDB)
                                                Ink_Weight = strWeight
                                                if (valid == classState.State.accepted):
                                                      Ink_State = "OK"
                                                      Screen.bird_it(Ink_Ring, Ink_Position, Ink_Last_Weight, Ink_Day_Since, Ink_Weight, Ink_State)
                                                      time.sleep(2)
                                                      current_remark = remarks()
                                                      s.query(DB.Session).filter(DB.Session.ID_RFID == persoData.ID_RFID).update({"Weight" : WeightDB, "Date" : datetime.datetime.now(), 'Note': current_remark})
                                                      s.commit()
                                                if (valid == classState.State.pendingLow or valid == classState.State.pendingHigh):
                                                      if valid == classState.State.pendingLow:
                                                            Ink_State = "LOW WEIGHT"
                                                      if valid == classState.State.pendingHigh:
                                                            Ink_State = "HIGH WEIGHT"
                                                      Screen.bird_it(Ink_Ring, Ink_Position, Ink_Last_Weight, Ink_Day_Since, Ink_Weight, Ink_State)
                                                      time.sleep(2)
                                                      flagVal = True
                                                      Screen.msg_multi_lines(['1 - OK','4 - Cancel'], 'ACTION', 7) 
                                                      p = inkey()
                                                      while flagVal:
                                                            if p == "a":
                                                                  flagVal = False
                                                                  Ink_State = "OK"
                                                                  Screen.bird_it(Ink_Ring, Ink_Position, Ink_Last_Weight, Ink_Day_Since, Ink_Weight, Ink_State)
                                                                  time.sleep(2) 
                                                                  current_remark = remarks()                                                                                                                                   
                                                                  s.query(DB.Session).filter(DB.Session.ID_RFID == persoData.ID_RFID).update({"Weight" : WeightDB, "Date" : datetime.datetime.now(), 'Note': current_remark})
                                                                  s.commit()
                                                            if p == "d":
                                                                  flagVal = False
                                                                  Ink_State = "WEIGHT CANCELLED"
                                                                  Screen.bird_it(Ink_Ring, Ink_Position, Ink_Last_Weight, Ink_Day_Since, Ink_Weight, Ink_State)
                                                if (valid == classState.State.rejeted):
                                                      print("9.3")
                                                      Ink_State = "IMPOSSIBLE WEIGHT"
                                                      Screen.bird_it(Ink_Ring, Ink_Position, Ink_Last_Weight, Ink_Day_Since, Ink_Weight, Ink_State)
                        else:
                              faa = Image.new('RGB', (296,128), color = "white")
                              draw1 = ImageDraw.Draw(faa)
                              font1 = ImageFont.truetype("/home/pi/Desktop/ProjetRFID/DejaVuSans.ttf",30)
                              draw1.text((00,00), "ERROR", fill = 100, font = font1)
                              faa = faa.rotate(270)
                              faa.save('1.jpg')
                              image = Image.open('1.jpg')
                              epd.set_frame_memory(image, 0, 0)
                              epd.display_frame()
                              epd.set_frame_memory(image, 0, 0)
                              epd.display_frame()
                              break   
            print('fin')
            Export.export(dbPath, filename)
            time.sleep(3)


if __name__ == '__main__':
      main()
      while True:
            try:
                  main()
            except KeyboardInterrupt:
                  sys.exit()
            except:
                  pass

