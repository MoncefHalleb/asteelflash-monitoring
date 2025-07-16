from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Literal
from datetime import date

# --- Auth schemas ---
class UserCreate(BaseModel):
    username: str = Field(..., max_length=50)
    password: str = Field(..., min_length=6)
    role: Literal["user","admin"] = "user"

class UserOut(BaseModel):
    id: int
    username: str
    role: Literal["user","admin"]

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

# --- Board schemas ---
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
        orm_mode = True

class BoardCreate(BaseModel):
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

class BoardUpdate(BoardCreate):
    pass

# --- Test schema ---
class TestRecord(BaseModel):
    id: int
    id_board: int
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

    class Config:
        orm_mode = True

# --- Metrics schemas ---
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
    defect_details: Dict[str,int]
    ref_stats: List[RefStat]
    ref_price_stats: List[RefPriceStat]
    test_details: List[TestRecord]
