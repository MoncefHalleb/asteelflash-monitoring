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
    id_assembly: Optional[int] = None
    id_process: Optional[int] = None
    quantcondit: Optional[int] = None
    id_famille: Optional[int] = None
    serial_number: str = ""
    family_name: str = ""
    prix: Optional[float] = None

    class Config:
        from_attributes = True

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

class TestRecord(BaseModel):
    id: Optional[int] = None
    id_board: Optional[int] = None
    num_serie: Optional[str] = None
    id_machine: Optional[str] = None
    id_operateur: Optional[str] = None
    date_debut: Optional[str] = None 
    date_fin: Optional[str] = None   
    result: Optional[int] = None
    type_test: Optional[str] = None
    side: Optional[float] = None
    position_flan: Optional[float] = None
    id_config_ligne: Optional[float] = None
    id_process: Optional[float] = None
    comment: Optional[float] = None

class QualityMetrics(BaseModel):
    date: date
    total_quantity: int
    good_quantity: int
    bad_quantity: int
    defect_details: Dict[str, int]
    ref_stats: List[RefStat]
    ref_price_stats: List[RefPriceStat]
    test_details: List[TestRecord] = []

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    role: str | None = None

class UserInDB(BaseModel):
    username: str
    hashed_password: str
    role: str

class BoardCreate(BaseModel):
    REF_AsteelFlash: Optional[str] = Field(None, max_length=40)
    REF_Clients: Optional[str] = Field(None, max_length=40)
    Designation: Optional[str] = None
    Client: Optional[str] = Field(None, max_length=30)
    Board_Ver: Optional[str] = Field(None, max_length=10)
    Code_Indus: Optional[str] = Field(None, max_length=40)
    Indice: Optional[str] = Field(None, max_length=5)
    Software: Optional[str] = Field(None, max_length=50)
    Software_Ver: Optional[str] = Field(None, max_length=10)
    Valide: bool = True
    Id_Assembly: Optional[int] = None
    Id_Process: Optional[int] = None
    QuantCondit: Optional[int] = None
    Id_Famille: Optional[int] = None
    prix: Optional[float] = None

class BoardUpdate(BaseModel):
    REF_AsteelFlash: Optional[str] = Field(None, max_length=40)
    REF_Clients: Optional[str] = Field(None, max_length=40)
    Designation: Optional[str] = None
    Client: Optional[str] = Field(None, max_length=30)
    Board_Ver: Optional[str] = Field(None, max_length=10)
    Code_Indus: Optional[str] = Field(None, max_length=40)
    Indice: Optional[str] = Field(None, max_length=5)
    Software: Optional[str] = Field(None, max_length=50)
    Software_Ver: Optional[str] = Field(None, max_length=10)
    Valide: Optional[bool] = None
    Id_Assembly: Optional[int] = None
    Id_Process: Optional[int] = None
    QuantCondit: Optional[int] = None
    Id_Famille: Optional[int] = None
    prix: Optional[float] = None
