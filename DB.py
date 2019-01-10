#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column, String, DateTime, Integer,
    create_engine)
from sqlalchemy.orm import sessionmaker
# from sqlalchemy.schema import Index
import datetime
import glob
import os
import sys
import logging


logger = logging.getLogger()

try:
    import Screen
except ImportError as e:
    logger.debug(e)
    logging.warning('DB module: Assuming development environment, redirecting Screen functionality')  # noqa: E501
    Screen = type('Screen', (), {'msg': lambda m, e=None, b=None: logger.info('** %s **', m)})  # noqa: E501

Base = declarative_base()


class Session(Base):
    __tablename__ = 'session'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    BID = Column(String, index=True)
    ID_Reneco = Column(String, index=True)
    ID_RFID = Column(String, index=True)
    Position = Column(String)
    Age = Column(Integer)
    Date_Last_Weight = Column(String)
    Days_Since_Last_Weight = Column(Integer)
    Last_Weight = Column(Integer)
    Date_Session = Column(DateTime)
    Weight_Min_Path = Column(Integer)
    Weight_Max_Path = Column(Integer)
    Weight_Min_Imp = Column(Integer)
    Weight_Max_Imp = Column(Integer)
    Date = Column(DateTime)
    Weight = Column(Integer)
    Note = Column(String)

    def __repr__(self):
        return '<Session(ID = "%s", ID_Reneco = "%s", ID_RFID = "%s", Position = "%s", Age = "%s", Date_Last_Weight = "%s", Days_Since_Last_Weight = "%s", Last_Weight = "%s", Date_Session = "%s", Weight_Min_Path = "%s", Weight_Max_Path = "%s", Weight_Min_Imp = "%s", Weight_Max_Imp = "%s", Date = "%s", Weight = "%s", Note = "%s")>' % (  # noqa: E501
            self.ID, self.ID_Reneco, self.ID_RFID, self.Position, self.Age, self.Date_Last_Weight, self.Days_Since_Last_Weight, self.Last_Weight, self.Date_Session, self.Weight_Min_Path, self.Weight_Max_Path, self.Weight_Min_Imp, self.Weight_Max_Imp, self.Date, self.Weight, self.Note)  # noqa: E501


class Log(Base):
    __tablename__ = 'log'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    Date = Column(DateTime)
    Comment = Column(String)

    def __repr__(self):
        return '<Log(ID="%s", Date="%s", Comment="%s">' % (
            self.ID, self.Date, self.Comment)


# def dbExists():
#     strdate = datetime.datetime.now


def testFiles(DB_PATH):
    # * means all if need specific format then *.db
    list_of_files = glob.glob(os.path.join(DB_PATH, '*.db'))
    if len(list_of_files) == 0:
        Screen.msg('DATABASE FILE NOT FOUND', 'ERROR', True)
        sys.exit()
    strdate = datetime.datetime.now().strftime('%Y%m%d')
    list_of_files = glob.glob(
        os.path.abspath(os.path.join(
            DB_PATH, strdate.join(['Prep_Weighing_*_', '*.db']))))
    if len(list_of_files) == 0:
        Screen.msg('DATABASE OUTDATED', 'ERROR', True)
        sys.exit()
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


def get_export_file_name(str_file_name):
    str_splited = str_file_name.split('_')
    species = str_splited[2]
    return species


def initDB(dbFile, DB_PATH):
    # Connexion de la base de donnees
    engine = create_engine(
        'sqlite:///' + os.path.abspath(os.path.join(DB_PATH, dbFile)))
    session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    return session()


def testSession(DB_PATH):
    db_file = testFiles(DB_PATH)
    species = get_export_file_name(db_file)
    strdate = datetime.datetime.now().strftime('%Y%m%d')
    export_name = 'WeightsFile_' + species + '_' + strdate
    session = initDB(db_file, DB_PATH)
    date_access = Log(Date=datetime.datetime.now())
    session.add(date_access)
    session.commit()
    dateSession = (session.query(Log).filter(Log.ID == 1).first().Date)
    if dateSession.date() != datetime.date.today():
        Screen.msg('DATABASE OUTDATED', 'ERROR', True)
        print('db outdated')
        return None
    else:
        Screen.msg('DATABASE UP TO DATE')
        print('db up to date')
        return {
            'session': session,
            'file': db_file,
            'export_file_name': export_name}


def searchDB(session, uid):
    dataBird = session.query(Session)\
                      .filter(Session.ID_RFID == uid.strip())\
                      .first()
    return dataBird


def testBird(data):
    # l'oiseau n'est pas dans la database
    if data is None:
        Screen.msg('BIRD NOT IN DATABASE', 'ERROR', True)
        print('4.1')
        t = 0
        return t
    # l'oiseau a deja ete pese
    elif data.Weight is not None:
        Screen.error('BIRD ALREADY WEIGHED', 'NOTICE', True)
        print('4.2')
        t = 1
        return t
    else:
        Screen.ink(data.ID_Reneco, data.Position, data.Age, ' ', ' ',
                   data.Last_Weight, data.Days_Since_Last_Weight)
        print('4.3')
        t = 2
        return t


def validateBird(session, result, key, data, weight):
    print(result)
    if result == 0:
        print('7.0')
        Screen.ink(data.ID_Reneco, data.Position, data.Age, weight, 'OK',
                   data.Last_Weight, data.Days_Since_Last_Weight)
        # FIXME: persoData ?
        session.query(Session)\
               .filter(Session.ID_RFID == data.ID_RFID)\
               .update({'Weight': weight, 'Date': datetime.datetime.now()})
        session.commit()
    elif result == 1:
        print('7.1')
        Screen.ink(
            data.ID_Reneco,
            data.Position, data.Age, weight, 'IMPOSSIBLE WEIGHT',
            data.Last_Weight, data.Days_Since_Last_Weight)
    elif result == 21:
        print('7.21')
        Screen.ink(
            data.ID_Reneco,
            data.Position, data.Age, weight, 'LOW WEIGHT',
            data.Last_Weight, data.Days_Since_Last_Weight)
        flagVal = True
        while flagVal:
            if key == 'p':
                flagVal = False
                Screen.ink(
                    data.ID_Reneco,
                    data.Position, data.Age, weight, 'VALIDATED',
                    data.Last_Weight, data.Days_Since_Last_Weight)
                session.query(Session)\
                       .filter(Session.ID_RFID == data.ID_RFID)\
                       .update({'Weight': weight,
                                'Date': datetime.datetime.now()})
                session.commit()
            elif key == 'b':
                flagVal = False
                Screen.ink(
                    data.ID_Reneco,
                    data.Position, data.Age, weight, 'CANCELLED',
                    data.Last_Weight, data.Days_Since_Last_Weight)
    elif result == 22:
        print('7.22')
        Screen.ink(
            data.ID_Reneco,
            data.Position, data.Age, weight, 'HIGH WEIGHT',
            data.Last_Weight, data.Days_Since_Last_Weight)
        flagVal = True
        while flagVal:
            if key == 'p':
                flagVal = False
                Screen.ink(
                    data.ID_Reneco,
                    data.Position, data.Age, weight, 'VALIDATED',
                    data.Last_Weight, data.Days_Since_Last_Weight)
                session.query(Session)\
                       .filter(Session.ID_RFID == data.ID_RFID)\
                       .update({'Weight': weight,
                                'Date': datetime.datetime.now()})
                session.commit()
            elif key == 'b':
                flagVal = False
                Screen.ink(
                    data.ID_Reneco,
                    data.Position, data.Age, weight, 'CANCELLED',
                    data.Last_Weight, data.Days_Since_Last_Weight)
