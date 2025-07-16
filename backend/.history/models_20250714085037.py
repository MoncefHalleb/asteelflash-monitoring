from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Numeric
from database import Base

class Board(Base):
    __tablename__ = 'abb_dbo_board'
    Id = Column(Integer, primary_key=True, autoincrement=True)
    REF_AsteelFlash = Column(String(40))
    REF_Clients = Column(String(40))
    Designation = Column(Text)
    Date_Creation = Column(DateTime)
    Client = Column(String(30))
    Board_Ver = Column(String(10))
    Code_Indus = Column(String(40))
    Indice = Column(String(5))
    Software = Column(String(50))
    Software_Ver = Column(String(10))
    Valide = Column(Boolean)
    Id_Assembly = Column(Numeric(18, 0))
    Id_Process = Column(Numeric(18, 0))
    QuantCondit = Column(Integer)
    Id_Famille = Column(Numeric(18, 0))
    prix = Column(Float)

class Intervention(Base):
    __tablename__ = 'abb_dbo_intervention'
    Id = Column(Numeric(18, 0), primary_key=True)
    NumSerie = Column(String(40))
    DateIntervention = Column(DateTime)
    Action = Column(Text)
    Id_Operateur = Column(Numeric(18, 0))
    Id_Mesure = Column(Numeric(18, 0))
    Defaut = Column(String(30))

class Test(Base):
    __tablename__ = 'abb_dbo_test'
    Id = Column(Integer, primary_key=True, autoincrement=True)
    Id_Board = Column(Integer)
    Num_Serie = Column(String(255))
    Id_Machine = Column(String(255))
    Id_Operateur = Column(Float)
    DateDebut = Column(String(50))
    DateFin = Column(String(50))
    Result = Column(Integer)
    TypeTest = Column(String(50))
    Side = Column(Float)
    Position_Flan = Column(Float)
    Id_ConfigLigne = Column(Float)
    Id_Process = Column(Float)
    Comment = Column(Float)

class Famille(Base):
    __tablename__ = 'abb_dbo_famille'
    Id = Column(Numeric(18, 0), primary_key=True)
    Nom_Famille = Column(String(255))
    Valide = Column(Boolean)
    Commentaires = Column(Text)
