from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import date

# Board schema
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

# Intervention schema
class InterventionRecord(BaseModel):
    id: Optional[int] = None
    num_serie: Optional[str] = None
    action: Optional[str] = None
    defaut: Optional[str] = None
    date_intervention: Optional[str] = None

# Test schema
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

# Famille schema
class FamilleInfo(BaseModel):
    id: int
    name: str
    valide: bool
    commentaires: Optional[str] = None

# Quality Metrics schema
class QualityMetrics(BaseModel):
    date: date
    total_quantity: int
    good_quantity: int
    bad_quantity: int
    defect_details: Dict[str, int]
    ref_stats: List[Dict[str, int]]
    ref_price_stats: List[Dict[str, float]]
    test_details: List[TestRecord]
