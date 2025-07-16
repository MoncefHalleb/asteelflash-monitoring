from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from database import Base

class Board(Base):
    __tablename__ = "abb_dbo_board"

    Id = Column(Integer, primary_key=True)
    REF_AsteelFlash = Column(String(40))
    REF_Clients = Column(String(40))
    Designation = Column(String(255))
    Client = Column(String(30))
    Board_Ver = Column(String(10))
    Code_Indus = Column(String(40))
    Indice = Column(String(5))
    Software = Column(String(50))
    Software_Ver = Column(String(10))
    Valide = Column(Boolean)
    Id_Assembly = Column(Integer, nullable=True)
    Id_Process = Column(Integer, nullable=True)
    QuantCondit = Column(Integer, nullable=True)
    Id_Famille = Column(Integer, nullable=True)
    prix = Column(Float, nullable=True)
    Date_Creation = Column(DateTime)
class Test(Base):
    __tablename__ = 'abb_dbo_test'

    Id = Column(Integer, primary_key=True)
    Id_Board = Column(Integer)
    Num_Serie = Column(String(255))
    Result = Column(Integer)
    DateDebut = Column(String(50))