from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BoardBase(BaseModel):
    REF_AsteelFlash: Optional[str]
    REF_Clients: Optional[str]
    Designation: Optional[str]
    Client: Optional[str]
    Board_Ver: Optional[str]
    Code_Indus: Optional[str]
    Indice: Optional[str]
    Software: Optional[str]
    Software_Ver: Optional[str]
    Valide: Optional[bool] = True
    Id_Assembly: Optional[int]
    Id_Process: Optional[int]
    QuantCondit: Optional[int]
    Id_Famille: Optional[int]
    prix: Optional[float]

class BoardCreate(BoardBase):
    pass

class BoardUpdate(BoardBase):
    pass

class BoardInfo(BoardBase):
    Id: int
    Date_Creation: Optional[datetime]

    class Config:
        from_attributes = True
