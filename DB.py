from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Index


Base = declarative_base()

class Session(Base):
    __tablename__ = 'session'
    ID = Column(Integer, primary_key = True, autoincrement = True)
    BID = Column(Integer)
    ID_RFID = Column(String, index = True)
    ID_Reneco  = Column(String, index = True)
    Species = Column(String)
    Gender = Column(Integer)
    Age = Column(Integer)
    Date_Session = Column(DateTime)
    WeightMinPath = Column(Float)
    WeightMaxPath = Column(Float)
    WeightMinImp = Column(Float)
    WeightMaxImp = Column(Float)
    Weight = Column(Float)
    Date = Column(DateTime)
    def __repr__(self):
        return "<Session(ID = '%s', BID = '%s', ID_RFID = '%s', ID_Reneco = '%s', Species = '%s', Gender = '%s', Age = '%s', Date_Session = '%s', WeightMinPath = '%s', WeightMaxPath = '%s', WeightMinImp = '%s', WeightMaxImp = '%s', Weight = '%s', Date = '%s')>" % (
            self.ID, self.BID, self.ID_RFID, self.ID_Reneco, self.Species, self.Gender, self.Age, self.Date_Session, self.WeightMinPath, self.WeightMaxPath, self.WeightMinImp, self.WeightMaxImp, self.Weight, self.Date)


class Story(Base):
    __tablename__ = 'story'
    ID = Column(Integer, primary_key = True, autoincrement = True)
    ID_RFID = Column(String, index = True)
    ID_Reneco  = Column(String, index = True)
    Last_Weight = Column(Float)
    Penultimate_Weight = Column(Float)
    Antepenultimate_Weight = Column(Float)
    Last_Date = Column(DateTime)
    Penultimate_Date = Column(DateTime)
    Antepenultimate_Date = Column(DateTime)
    def __repr__(self):
        return "<Story(ID = '%s', ID_RFID = '%s', ID_Reneco = '%s', Last_Weight = '%s', Penultimate_Weight = '%s', Antepenultimate_Weight = '%s', Last_Date = '%s', Penultimate_Date = '%s', Antepenultimate_Date = '%s')>" % (
            self.ID, self.ID_RFID, self.ID_Reneco, self.Last_Weight, self.Penultimate_Weight, self.Antepenultimate_Weight, self.Last_Date, self.Penultimate_Date, self.Antepenultimate_Date)


class Log(Base):
    __tablename__ = 'log'
    ID = Column(Integer, primary_key = True, autoincrement = True)
    Date = Column(String)
    Comment = (String)
    def __repr__(self):
        return "<Log(ID = '%s', Date = %s, Comment = %s)>" % (
            self.ID, self.Date, self.Comment)


            
########################################################################################################################################################################################################################################

def createDB(dbPath):
    engine = create_engine('sqlite:///%s' % dbPath) #Connexion de la base de donnees
    session = sessionmaker(bind = engine)
    Base.metadata.create_all(engine)
    return session()