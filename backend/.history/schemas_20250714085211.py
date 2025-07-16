# schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import date

class BoardInfo(BaseModel):
    id: int
    ref_asteel: str
    ref_client: str
    designation: str
    client: str
    board_version: str
    code_indus: str
    indice: str
    software: str
    software_ver: str
    is_valid: bool
    id_assembly: Optional[int]
    id_process: Optional[int]
    quantcondit: Optional[int]
    id_famille: Optional[int]
    serial_number: str = ""
    family_name: str = ""
    prix: Optional[float]

    class Config:
        from_attributes = True

class BoardCreate(BaseModel):
    REF_AsteelFlash: Optional[str] = Field(None, max_length=40)
    REF_Clients: Optional[str] = Field(None, max_length=40)
    Designation: Optional[str]
    Client: Optional[str]        = Field(None, max_length=30)
    Board_Ver: Optional[str]     = Field(None, max_length=10)
    Code_Indus: Optional[str]    = Field(None, max_length=40)
    Indice: Optional[str]        = Field(None, max_length=5)
    Software: Optional[str]      = Field(None, max_length=50)
    Software_Ver: Optional[str]  = Field(None, max_length=10)
    Valide: bool = True
    Id_Assembly: Optional[int]
    Id_Process: Optional[int]
    QuantCondit: Optional[int]
    Id_Famille: Optional[int]
    prix: Optional[float]

class BoardUpdate(BoardCreate):
    pass

class TestRecord(BaseModel):
    id: Optional[int]
    id_board: Optional[int]
    num_serie: Optional[str]
    id_machine: Optional[str]
    id_operateur: Optional[str]
    date_debut: Optional[str]
    date_fin: Optional[str]
    result: Optional[int]
    type_test: Optional[str]
    side: Optional[float]
    position_flan: Optional[float]
    id_config_ligne: Optional[float]
    id_process: Optional[float]
    comment: Optional[float]

class RefStat(BaseModel):
    ref_asteel: str
    good_count: int
    bad_count: int
    serial_number: Optional[str]

class RefPriceStat(BaseModel):
    ref_asteel: str
    num_serie: Optional[str]
    good_tests: int
    bad_tests: int
    unit_price: float
    total_price: float

class QualityMetrics(BaseModel):
    date: date
    total_quantity: int
    good_quantity: int
    bad_quantity: int
    defect_details: Dict[str, int]
    ref_stats: List[RefStat]
    ref_price_stats: List[RefPriceStat]
    test_details: List[TestRecord]

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str]
    role: Optional[str]

class UserInDB(BaseModel):
    username: str
    hashed_password: str
    role: str
