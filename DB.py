#!/usr/bin/python 
# -*- coding:utf-8 -*-


import glob
import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Index

Base = declarative_base()

class Session(Base):
    __tablename__ = 'session'
    ID = Column(Integer, primary_key = True, autoincrement = True)
    ID_Reneco  = Column(String, index = True)
    ID_RFID = Column(String, index = True)
    Position = Column(String)
    Date_Session = Column(DateTime)
    WeightMinPath = Column(Integer)                                      
    WeightMaxPath = Column(Integer)
    WeightMinImp = Column(Integer)
    WeightMaxImp = Column(Integer)
    Date = Column(DateTime)
    Weight = Column(Integer)
    Note = Column(String)
    def __repr__(self):
        return "<Session(ID = '%s', ID_Reneco = '%s', ID_RFID = '%s', Position = '%s',  Date_Session = '%s', WeightMinPath = '%s', WeightMaxPath = '%s', WeightMinImp = '%s', WeightMaxImp = '%s', Date = '%s', Weight = '%s', Note = '%s')>" % (
            self.ID, self.ID_Reneco, self.ID_RFID, self.Position, self.Date_Session, self.WeightMinPath, self.WeightMaxPath, self.WeightMinImp, self.WeightMaxImp, self.Date, self.Weight, self.Note)


class Log(Base):
    __tablename__ = 'log'
    ID = Column(Integer, primary_key = True, autoincrement = True)
    Date = Column(DateTime)
    Comment = (String)
    def __repr__(self):
        return "<Log(ID = '%s', Date = %s, Comment = %s)>" % (
            self.ID, self.Date, self.Comment)


            
########################################################################################################################################################################################################################################

list_of_files = glob.glob('/home/pi/Share/Public/*.db') # * means all if need specific format then *.csv
latest_file = max(list_of_files, key=os.path.getctime)
dbPath = str(latest_file)

def createDB(dbPath):
    engine = create_engine('sqlite:///%s' %dbPath) #Connexion de la base de donnees
    session = sessionmaker(bind = engine)
    Base.metadata.create_all(engine)
    return session()
    