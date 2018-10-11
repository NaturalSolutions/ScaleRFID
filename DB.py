#!/usr/bin/python 
# -*- coding:utf-8 -*-



from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Index
import datetime
import glob
import os

import Screen

Base = declarative_base()

class Session(Base):
    __tablename__ = 'session'
    ID                      =   Column(Integer, primary_key = True, autoincrement = True)
    BID                     =   Column(String, index = True)
    ID_Reneco               =   Column(String, index = True)
    ID_RFID                 =   Column(String, index = True)
    Position                =   Column(String)
    Age                     =   Column(Integer)
    Date_Last_Weight        =   Column(String)
    Days_Since_Last_Weight  =   Column(Integer)
    Last_Weight             =   Column(Integer)
    Date_Session            =   Column(DateTime)
    Weight_Min_Path         =   Column(Integer)                                      
    Weight_Max_Path         =   Column(Integer)
    Weight_Min_Imp          =   Column(Integer)
    Weight_Max_Imp          =   Column(Integer)
    Date                    =   Column(DateTime)
    Weight                  =   Column(Integer)
    Note                    =   Column(String)
    def __repr__(self):
        return "<Session(ID = '%s', ID_Reneco = '%s', ID_RFID = '%s', Position = '%s', Age = '%s', Date_Last_Weight = '%s', Days_Since_Last_Weight = '%s', Last_Weight = '%s', Date_Session = '%s', Weight_Min_Path = '%s', Weight_Max_Path = '%s', Weight_Min_Imp = '%s', Weight_Max_Imp = '%s', Date = '%s', Weight = '%s', Note = '%s')>" % (
            self.ID, self.ID_Reneco, self.ID_RFID, self.Position, self.Age, self.Date_Last_Weight, self.Days_Since_Last_Weight, self.Last_Weight, self.Date_Session, self.Weight_Min_Path, self.Weight_Max_Path, self.Weight_Min_Imp, self.Weight_Max_Imp, self.Date, self.Weight, self.Note)


class Log(Base):
    __tablename__ = 'log'
    ID = Column(Integer, primary_key = True, autoincrement = True)
    Date = Column(DateTime)
    Comment = Column(String)
    def __repr__(self):
        return "<Log(ID = '%s', Date = '%s', Comment = '%s'>" % (self.ID, self.Date, self.Comment )
########################################################################################################################################################################################################################################

# def dbExists():
#     strdate = datetime.datetime.now

def testFiles():
    list_of_files = glob.glob('/home/pi/Share/Public/*.db') # * means all if need specific format then *.db
    if len(list_of_files)== 0:
        Screen.msg("DATABASE FILE NOT FOUND",'ERROR',True)
        exit()
    strdate = datetime.datetime.now().strftime('%Y%m%d')
    list_of_files = glob.glob('/home/pi/Share/Public/Prep_Weighing_'+strdate+'*.db')
    if len(list_of_files)== 0:
        Screen.msg("DATABASE OUTDATED",'ERROR',True)
        exit()
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

def initDB(dbFile):
    engine = create_engine('sqlite:///' + dbFile) #Connexion de la base de donnees
    session = sessionmaker(bind = engine)
    Base.metadata.create_all(engine)
    
    return session()

def testSession():
    db_file = testFiles()
    session = initDB(db_file)
    date_access = Log(Date = datetime.datetime.now())
    session.add(date_access)
    session.commit()
    dateSession = (session.query(Log).filter(Log.ID == 1).first().Date)
    if dateSession.date() != datetime.date.today():
        Screen.msg("DATABASE OUTDATED",'ERROR',True)
        print("db outdated")
        return None
    else:
        Screen.msg("DATABASE UP TO DATE")
        print("db up to date")
        return {'session': session, 'file': db_file}

def searchDB(session, uid):
    dataBird = session.query(Session).filter(Session.ID_RFID == uid.strip()).first()
    return dataBird

def testBird(data):
        if data is None: #l'oiseau n'est pas dans la database
            Screen.msg("BIRD NOT IN DATABASE", 'ERROR', True)
            print("4.1")
            t = 0
            return t 
        elif data.Weight is not None: #l'oiseau a deja ete pese
            Screen.error("BIRD ALREADY WEIGHED",'NOTICE',True)
            print("4.2")
            t = 1
            return t
        else:
            Screen.ink(data.ID_Reneco,data.Position,data.Age," " ," ",  data.Last_Weight, data.Days_Since_Last_Weight)
            print("4.3")
            t = 2
            return t

def validateBird( session,result, key, data, weight):
    print result
    if result == 0:
        print("7.0")
        Screen.ink(data.ID_Reneco,data.Position,data.Age,weight ,"OK",  data.Last_Weight, data.Days_Since_Last_Weight)
        session.query(Session).filter(Session.ID_RFID == persoData.ID_RFID).update({"Weight" : weight, "Date" : datetime.datetime.now()})
        session.commit()
    elif result == 1:
        print("7.1")
        Screen.ink(data.ID_Reneco,data.Position,data.Age,weight ,"IMPOSSIBLE WEIGHT",  data.Last_Weight, data.Days_Since_Last_Weight)
    elif result == 21:
        print("7.21")
        Screen.ink(data.ID_Reneco,data.Position,data.Age,weight ,"LOW WEIGHT",  data.Last_Weight, data.Days_Since_Last_Weight)
        flagVal = True
        while flagVal:
            if key == "p":
                flagVal = False
                Screen.ink(data.ID_Reneco,data.Position,data.Age,weight ,"VALIDATED",  data.Last_Weight, data.Days_Since_Last_Weight)
                session.query(Session).filter(Session.ID_RFID == data.ID_RFID).update({"Weight" : weight, "Date" : datetime.datetime.now()})
                session.commit()
            elif key == "b":
                flagVal = False
                Screen.ink(data.ID_Reneco,data.Position,data.Age,weight ,"CANCELLED",  data.Last_Weight, data.Days_Since_Last_Weight)
    elif result == 22:
        print("7.22")
        Screen.ink(data.ID_Reneco,data.Position,data.Age,weight ,"HIGH WEIGHT",  data.Last_Weight, data.Days_Since_Last_Weight)
        flagVal = True
        while flagVal:
            if key == "p":
                flagVal = False
                Screen.ink(data.ID_Reneco,data.Position,data.Age,weight ,"VALIDATED",  data.Last_Weight, data.Days_Since_Last_Weight)
                session.query(Session).filter(Session.ID_RFID == data.ID_RFID).update({"Weight" : weight, "Date" : datetime.datetime.now()})
                session.commit()
            elif key == "b":
                flagVal = False
                Screen.ink(data.ID_Reneco,data.Position,data.Age,weight ,"CANCELLED",  data.Last_Weight, data.Days_Since_Last_Weight)

