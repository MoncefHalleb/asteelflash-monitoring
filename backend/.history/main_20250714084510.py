from fastapi import FastAPI, HTTPException, Query, Depends, status, Request, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import date, time, datetime, timedelta
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text, Column, Numeric, String, DateTime, Integer, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from collections import defaultdict
from typing import Literal, Optional, List, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.responses import StreamingResponse
from io import StringIO, BytesIO
import csv
import pandas as pd
import numpy as np
import xgboost as xgb
import pickle
import logging
import joblib
from datetime import datetime
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
SECRET_KEY = "0fd58da17a8195ddf5c5e1d91f8391752550b47e29e56575b7d1fe15080a308c"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# FastAPI app initialization
app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Configuration
DATABASE_URL = "mysql+pymysql://root:123@localhost/asteel"
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=False # Set to True to see SQL queries in logs
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Global ML Model Loading ---
# Load model components once when the application starts
model = None
scaler = None
columns = None

try:
    model = joblib.load("best_model.ubj")
    scaler = joblib.load("scaler.pkl")
    columns = joblib.load("columns.pkl")
    logger.info("Machine learning model, scaler, and columns loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load ML model components: {e}")
    # Depending on your application's requirements, you might want to exit or disable prediction features

# --- Dependency to get DB session ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Database Models ---
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

class Famille(Base):
    __tablename__ = 'abb_dbo_famille'
    Id = Column(Numeric(18, 0), primary_key=True)
    Nom_Famille = Column(String(255))
    Valide = Column(Boolean)
    Commentaires = Column(Text)

class Intervention(Base):
    __tablename__ = 'abb_dbo_intervention'
    Id = Column(Numeric(18, 0), primary_key=True)
    NumSerie = Column(String(40))
    DateIntervention = Column(DateTime)
    Action = Column(Text)
    Id_Operateur = Column(Numeric(18, 0))
    Id_Mesure = Column(Numeric(18, 0))
    Defaut = Column(String(30))

class Mesures(Base):
    __tablename__ = 'abb_dbo_mesures'
    Id = Column(Numeric(18, 0), primary_key=True)
    Id_Test = Column(Numeric(18, 0))
    Id_TypeMesure = Column(Text)
    Nom_Mesure = Column(Text)
    Low_Limit = Column(Float)
    High_Limit = Column(Float)
    Mesure = Column(Float)
    Result = Column(Integer)
    Id_TypeLimit = Column(Float)
    RepereTopo = Column(Text)

class Test(Base): # Renamed to DBTest to avoid conflict with Pydantic model below
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

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(10), nullable=False, default='user')

# --- Pydantic Models ---
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

class TestRecord(BaseModel): # Reusing this existing Pydantic model for individual test details
    id: Optional[int] = None
    id_board: Optional[int] = None
    num_serie: Optional[str] = None
    id_machine: Optional[str] = None
    id_operateur: Optional[str] = None
    date_debut: Optional[str] = None # Keeping as string for flexibility with date formats from DB
    date_fin: Optional[str] = None   # Keeping as string for flexibility with date formats from DB
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
    test_details: List[TestRecord] = [] # NEW FIELD: List of individual test records

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

class PredictionInput(BaseModel):
    Id: int
    Id_Board: int
    Num_Serie: Optional[str] = None
    Id_Machine: Optional[str] = None
    DateDebut: str
    DateFin: str
    Result: int
    Side: Optional[str] = None
    Position_Flan: float
    Id_ConfigLigne: float
    Id_Process: float
    ref_asteel: Optional[str] = None
    ref_client: int
    family_name: Optional[str] = None
    board_version: str
    is_valid: float
    designation: Optional[str] = None
    client: Optional[str] = None
    code_indus: Optional[str] = None
    indice: Optional[str] = None
    software: Optional[str] = None
    software_ver: Optional[str] = None
    id_assembly: Optional[str] = None
    id_process: Optional[str] = None
    quantcondit: float
    id_famille: float
    prix: float

class PredictionOutput(BaseModel):
    prediction: str
    probability: float
    id: int


# --- Authentication Functions ---
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_user_from_db(username: str):
    query = text("SELECT id, username, hashed_password, role FROM users WHERE username = :username")
    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"username": username}).fetchone()
            if result:
                return UserInDB(
                    username=result.username,
                    hashed_password=result.hashed_password,
                    role=result.role
                )
        return None
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching user: {e}")
        raise HTTPException(status_code=500, detail="Database error during user lookup.")
async def authenticate_user(username: str, password: str):
    user = await get_user_from_db(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_role: str = payload.get("role")
        if username is None or user_role is None:
            raise credentials_exception
        token_data = TokenData(username=username, role=user_role)
    except JWTError as e:
        logger.error(f"JWT decoding error: {e}")
        raise credentials_exception
    user = await get_user_from_db(token_data.username)
    if user is None:
        logger.warning(f"User not found for token: {token_data.username}")
        raise credentials_exception
    return user

def require_role(required_role: Literal['admin', 'user']):
    def role_checker(current_user: UserInDB = Depends(get_current_user)):
        if current_user.role != required_role:
            logger.warning(f"Access denied for user {current_user.username} with role {current_user.role}, requires {required_role}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Requires '{required_role}' role."
            )
        return current_user
    return role_checker

def require_admin():
    return require_role('admin')

def require_user():
    return require_role('user')

# --- Services Layer ---
class BoardService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_boards(self) -> List[BoardInfo]:
        query = text("""
            SELECT
                CAST(b.Id AS UNSIGNED) AS id,
                COALESCE(b.REF_AsteelFlash, '') AS ref_asteel,
                COALESCE(CAST(b.REF_Clients AS CHAR), '') AS ref_client,
                COALESCE(f.Nom_Famille, '') AS family_name,
                COALESCE(i.NumSerie, '') AS serial_number,
                COALESCE(CAST(b.Board_Ver AS CHAR), '') AS board_version,
                CASE WHEN b.Valide IS NULL THEN FALSE ELSE b.Valide END AS is_valid,
                COALESCE(b.Designation, '') AS designation,
                COALESCE(b.Client, '') AS client,
                COALESCE(b.Code_Indus, '') AS code_indus,
                COALESCE(b.Indice, '') AS indice,
                COALESCE(b.Software, '') AS software,
                COALESCE(b.Software_Ver, '') AS software_ver,
                COALESCE(CAST(b.Id_Assembly AS UNSIGNED), NULL) AS id_assembly,
                COALESCE(CAST(b.Id_Process AS UNSIGNED), NULL) AS id_process,
                COALESCE(CAST(b.QuantCondit AS UNSIGNED), NULL) AS quantcondit,
                COALESCE(CAST(b.Id_Famille AS UNSIGNED), NULL) AS id_famille,
                COALESCE(b.prix, NULL) AS prix
            FROM abb_dbo_board b
            LEFT JOIN abb_dbo_famille f ON b.Id_Famille = f.Id
            LEFT JOIN abb_dbo_intervention i ON i.Id = (
                SELECT Id FROM abb_dbo_intervention
                WHERE NumSerie IS NOT NULL
                ORDER BY DateIntervention DESC
                LIMIT 1
            )
        """)
        result = self.db.execute(query).fetchall()
        boards = []
        for row in result:
            mapped = row._mapping
            boards.append(BoardInfo(
                id=int(mapped["id"] or 0),
                ref_asteel=str(mapped["ref_asteel"] or ""),
                ref_client=str(mapped["ref_client"] or ""),
                family_name=str(mapped["family_name"] or ""),
                serial_number=str(mapped["serial_number"] or ""),
                board_version=str(mapped["board_version"] or ""),
                is_valid=bool(mapped["is_valid"]) if mapped["is_valid"] is not None else False,
                designation=str(mapped["designation"] or ""),
                client=str(mapped["client"] or ""),
                code_indus=str(mapped["code_indus"] or ""),
                indice=str(mapped["indice"] or ""),
                software=str(mapped["software"] or ""),
                software_ver=str(mapped["software_ver"] or ""),
                id_assembly=mapped["id_assembly"],
                id_process=mapped["id_process"],
                quantcondit=mapped["quantcondit"],
                id_famille=mapped["id_famille"],
                prix=mapped["prix"]
            ))
        return boards

    def create_board(self, board_data: BoardCreate) -> BoardInfo:
        columns = []
        values = []
        params = {}
        for field, value in board_data.model_dump(exclude_unset=True).items():
            columns.append(field)
            values.append(f":{field}")
            params[field] = value
        if "Date_Creation" not in columns:
            columns.append("Date_Creation")
            values.append(":Date_Creation")
            params["Date_Creation"] = datetime.now()
        if not columns:
            raise ValueError("No data provided to create a board.")

        insert_query = text(
            f"INSERT INTO abb_dbo_board ({', '.join(columns)}) VALUES ({', '.join(values)})"
        )
        result = self.db.execute(insert_query, params)
        new_board_id = result.lastrowid

        fetch_query = text("""
            SELECT
                CAST(b.Id AS UNSIGNED) AS id,
                COALESCE(b.REF_AsteelFlash, '') AS ref_asteel,
                COALESCE(CAST(b.REF_Clients AS CHAR), '') AS ref_client,
                COALESCE(f.Nom_Famille, '') AS family_name,
                '' AS serial_number,
                COALESCE(CAST(b.Board_Ver AS CHAR), '') AS board_version,
                CASE WHEN b.Valide IS NULL THEN FALSE ELSE b.Valide END AS is_valid,
                COALESCE(b.Designation, '') AS designation,
                COALESCE(b.Client, '') AS client,
                COALESCE(b.Code_Indus, '') AS code_indus,
                COALESCE(b.Indice, '') AS indice,
                COALESCE(b.Software, '') AS software,
                COALESCE(b.Software_Ver, '') AS software_ver,
                COALESCE(CAST(b.Id_Assembly AS UNSIGNED), NULL) AS id_assembly,
                COALESCE(CAST(b.Id_Process AS UNSIGNED), NULL) AS id_process,
                COALESCE(CAST(b.QuantCondit AS UNSIGNED), NULL) AS quantcondit,
                COALESCE(CAST(b.Id_Famille AS UNSIGNED), NULL) AS id_famille,
                COALESCE(b.prix, NULL) AS prix
            FROM abb_dbo_board b
            LEFT JOIN abb_dbo_famille f ON b.Id_Famille = f.Id
            WHERE b.Id = :board_id
        """)
        new_board_row = self.db.execute(fetch_query, {"board_id": new_board_id}).fetchone()
        if new_board_row:
            mapped = new_board_row._mapping
            return BoardInfo(
                id=int(mapped["id"] or 0),
                ref_asteel=str(mapped["ref_asteel"] or ""),
                ref_client=str(mapped["ref_client"] or ""),
                family_name=str(mapped["family_name"] or ""),
                serial_number="",
                board_version=str(mapped["board_version"] or ""),
                is_valid=bool(mapped["is_valid"]) if mapped["is_valid"] is not None else False,
                designation=str(mapped["designation"] or ""),
                client=str(mapped["client"] or ""),
                code_indus=str(mapped["code_indus"] or ""),
                indice=str(mapped["indice"] or ""),
                software=str(mapped["software"] or ""),
                software_ver=str(mapped["software_ver"] or ""),
                id_assembly=mapped["id_assembly"],
                id_process=mapped["id_process"],
                quantcondit=mapped["quantcondit"],
                id_famille=mapped["id_famille"],
                prix=mapped["prix"]
            )
        else:
            raise ValueError("Failed to retrieve newly created board.")

    def get_board_by_id(self, board_id: int) -> Optional[BoardInfo]:
        query = text("""
            SELECT
                CAST(b.Id AS UNSIGNED) AS id,
                COALESCE(b.REF_AsteelFlash, '') AS ref_asteel,
                COALESCE(CAST(b.REF_Clients AS CHAR), '') AS ref_client,
                COALESCE(f.Nom_Famille, '') AS family_name,
                COALESCE(b.Designation, '') AS designation,
                COALESCE(b.Client, '') AS client,
                COALESCE(CAST(b.Board_Ver AS CHAR), '') AS board_version,
                COALESCE(b.Code_Indus, '') AS code_indus,
                COALESCE(b.Indice, '') AS indice,
                COALESCE(b.Software, '') AS software,
                COALESCE(b.Software_Ver, '') AS software_ver,
                CASE WHEN b.Valide IS NULL THEN FALSE ELSE b.Valide END AS is_valid,
                COALESCE(CAST(b.Id_Assembly AS UNSIGNED), NULL) AS id_assembly,
                COALESCE(CAST(b.Id_Process AS UNSIGNED), NULL) AS id_process,
                COALESCE(CAST(b.QuantCondit AS UNSIGNED), NULL) AS quantcondit,
                COALESCE(CAST(b.Id_Famille AS UNSIGNED), NULL) AS id_famille,
                COALESCE(i.NumSerie, '') AS serial_number,
                COALESCE(b.prix, NULL) AS prix
            FROM abb_dbo_board b
            LEFT JOIN abb_dbo_famille f ON b.Id_Famille = f.Id
            LEFT JOIN abb_dbo_intervention i ON i.Id = (
                SELECT Id FROM abb_dbo_intervention
                WHERE NumSerie IS NOT NULL
                ORDER BY DateIntervention DESC
                LIMIT 1
            )
            WHERE b.Id = :board_id
        """)
        result = self.db.execute(query, {"board_id": board_id}).fetchone()
        if result:
            mapped = result._mapping
            return BoardInfo(
                id=int(mapped["id"]),
                ref_asteel=str(mapped["ref_asteel"]),
                ref_client=str(mapped["ref_client"]),
                family_name=str(mapped["family_name"]),
                designation=str(mapped["designation"]),
                client=str(mapped["client"]),
                board_version=str(mapped["board_version"]),
                code_indus=str(mapped["code_indus"]),
                indice=str(mapped["indice"]),
                software=str(mapped["software"]),
                software_ver=str(mapped["software_ver"]),
                is_valid=bool(mapped["is_valid"]),
                id_assembly=mapped["id_assembly"],
                id_process=mapped["id_process"],
                quantcondit=mapped["quantcondit"],
                id_famille=mapped["id_famille"],
                serial_number=str(mapped["serial_number"]),
                prix=mapped["prix"]
            )
        return None

    def update_board(self, board_id: int, board_data: BoardUpdate) -> Optional[BoardInfo]:
        update_fields = board_data.model_dump(exclude_unset=True)
        set_clauses = []
        params = {"board_id": board_id}
        for field, value in update_fields.items():
            set_clauses.append(f"{field} = :{field}")
            params[field] = value
        if not set_clauses:
            raise ValueError("No fields provided for update.")

        update_query = text(
            f"UPDATE abb_dbo_board SET {', '.join(set_clauses)} WHERE Id = :board_id"
        )
        result = self.db.execute(update_query, params)
        if result.rowcount == 0:
            return None # Board not found

        return self.get_board_by_id(board_id)

    def delete_board(self, board_id: int) -> bool:
        delete_query = text("DELETE FROM abb_dbo_board WHERE Id = :board_id")
        result = self.db.execute(delete_query, {"board_id": board_id})
        return result.rowcount > 0

    def export_boards_to_df(self) -> pd.DataFrame:
        query = text("""
            SELECT
                CAST(b.Id AS UNSIGNED) AS id,
                b.REF_AsteelFlash,
                b.REF_Clients,
                f.Nom_Famille AS family_name,
                b.Board_Ver AS board_version,
                b.Valide AS is_valid,
                b.Designation,
                b.Client,
                b.Code_Indus,
                b.Indice,
                b.Software,
                b.Software_Ver,
                b.Id_Assembly,
                b.Id_Process,
                b.QuantCondit,
                b.Id_Famille,
                b.prix
            FROM abb_dbo_board b
            LEFT JOIN abb_dbo_famille f ON b.Id_Famille = f.Id
        """)
        return pd.read_sql(query, self.db.connection())

    def import_boards_from_csv(self, csv_file_content: List[str]):
        reader = csv.DictReader(csv_file_content)
        rows_to_process = []
        for row in reader:
            board = {
                "REF_AsteelFlash": row.get("ref_asteel"),
                "REF_Clients": row.get("ref_client"),
                "Designation": row.get("designation"),
                "Client": row.get("client"),
                "Board_Ver": row.get("board_version"),
                "Code_Indus": row.get("code_indus"),
                "Indice": row.get("indice"),
                "Software": row.get("software"),
                "Software_Ver": row.get("software_ver"),
                "Valide": row.get("is_valid") in ['1', 'true', 'True', True],
                "Id_Assembly": int(row["id_assembly"]) if row.get("id_assembly") else None,
                "Id_Process": int(row["id_process"]) if row.get("id_process") else None,
                "QuantCondit": int(row["quantcondit"]) if row.get("quantcondit") else None,
                "Id_Famille": int(row["id_famille"]) if row.get("id_famille") else None,
                "prix": float(row["prix"]) if row.get("prix") else None,
                "Date_Creation": datetime.now()
            }
            rows_to_process.append(board)

        for board in rows_to_process:
            existing = self.db.execute(
                text("SELECT Id FROM abb_dbo_board WHERE REF_AsteelFlash = :ref"),
                {"ref": board["REF_AsteelFlash"]}
            ).fetchone()

            if existing:
                update_stmt = text("""
                    UPDATE abb_dbo_board SET
                    REF_Clients=:REF_Clients,
                    Designation=:Designation,
                    Client=:Client,
                    Board_Ver=:Board_Ver,
                    Code_Indus=:Code_Indus,
                    Indice=:Indice,
                    Software=:Software,
                    Software_Ver=:Software_Ver,
                    Valide=:Valide,
                    Id_Assembly=:Id_Assembly,
                    Id_Process=:Id_Process,
                    QuantCondit=:QuantCondit,
                    Id_Famille=:Id_Famille,
                    prix=:prix,
                    Date_Creation=:Date_Creation
                    WHERE REF_AsteelFlash = :REF_AsteelFlash
                """)
                self.db.execute(update_stmt, board)
            else:
                insert_stmt = text("""
                    INSERT INTO abb_dbo_board (
                        REF_AsteelFlash, REF_Clients, Designation, Client, Board_Ver,
                        Code_Indus, Indice, Software, Software_Ver, Valide,
                        Id_Assembly, Id_Process, QuantCondit, Id_Famille, prix, Date_Creation
                    ) VALUES (
                        :REF_AsteelFlash, :REF_Clients, :Designation, :Client, :Board_Ver,
                        :Code_Indus, :Indice, :Software, :Software_Ver, :Valide,
                        :Id_Assembly, :Id_Process, :QuantCondit, :Id_Famille, :prix, :Date_Creation
                    )
                """)
                self.db.execute(insert_stmt, board)
        return len(rows_to_process)


class TestService:
    def __init__(self, db: Session):
        self.db = db

    def get_tests_by_board_id(self, board_id: int) -> List[TestRecord]:
        query = text("""
            SELECT
                Id AS id,
                Id_Board AS id_board,
                Num_Serie AS num_serie,
                Id_Machine AS id_machine,
                Id_Operateur AS id_operateur,
                DateDebut AS date_debut,
                DateFin AS date_fin,
                Result AS result,
                TypeTest AS type_test,
                Side AS side,
                Position_Flan AS position_flan,
                Id_ConfigLigne AS id_config_ligne,
                Id_Process AS id_process,
                Comment AS comment
            FROM abb_dbo_test
            WHERE Id_Board = :board_id
        """)
        results = self.db.execute(query, {"board_id": board_id}).fetchall()

        def format_date(val):
            if val is None:
                return None
            if hasattr(val, 'strftime'):
                return val.strftime("%Y-%m-%dT%H:%M")
            return str(val)

        tests = [
            TestRecord(
                id=row.id,
                id_board=row.id_board,
                num_serie=row.num_serie,
                id_machine=row.id_machine,
                id_operateur=str(int(row.id_operateur)) if row.id_operateur is not None else None, # Handle float to int for operator ID
                date_debut=format_date(row.date_debut),
                date_fin=format_date(row.date_fin),
                result=row.result,
                type_test=row.type_test,
                side=row.side,
                position_flan=row.position_flan,
                id_config_ligne=row.id_config_ligne,
                id_process=row.id_process,
                comment=row.comment
            )
            for row in results
        ]
        return tests

    def get_unique_tests_by_metric(
        self,
        metric_column: str,
        metric_value: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[TestRecord]:
        allowed_columns = ["TypeTest", "Result", "Id_Machine", "Id_Operateur", "Id_Board", "Num_Serie", "Ref_Asteel"]

        if metric_column not in allowed_columns:
            raise ValueError(f"Invalid metric_column '{metric_column}'. Allowed columns are: {', '.join(allowed_columns)}")

        base_query_select = """
            t.Num_Serie,
            t.DateDebut AS Date_Debut,
            t.Result,
            t.TypeTest,
            t.Id_Machine,
            t.Id_Operateur,
            t.Id_Board
        """
        base_query_from = "FROM abb_dbo_test t"
        # IMPORTANT: Keep STR_TO_DATE here because DateDebut is VARCHAR in your schema
        where_condition_parts = ["STR_TO_DATE(t.DateDebut, '%Y-%m-%d %H:%i:%s') BETWEEN :start_date AND :end_date"]
        params = {
            "metric_value": metric_value,
            "start_date": start_date.strftime("%Y-%m-%d %H:%M:%S"),
            "end_date": end_date.strftime("%Y-%m-%d %H:%M:%S")
        }

        if metric_column == "Ref_Asteel":
            base_query_from += " JOIN abb_dbo_board b ON t.Id_Board = b.Id"
            where_condition_parts.append("b.REF_AsteelFlash = :metric_value")
        elif metric_column == "Num_Serie":
            where_condition_parts.append("t.Num_Serie = :metric_value")
        elif metric_column == "Result":
            try:
                params["metric_value"] = int(metric_value)
            except ValueError:
                raise ValueError("Result must be an integer.")
            where_condition_parts.append("t.Result = :metric_value")
        elif metric_column == "Id_Board":
            try:
                params["metric_value"] = int(metric_value)
            except ValueError:
                raise ValueError("Id_Board must be an integer.")
            where_condition_parts.append("t.Id_Board = :metric_value")
        else:
            where_condition_parts.append(f"t.{metric_column} = :metric_value")

        where_clause = " WHERE " + " AND ".join(where_condition_parts)

        final_query_str = f"""
            WITH RankedTests AS (
                SELECT
                    {base_query_select},
                    ROW_NUMBER() OVER (PARTITION BY t.Num_Serie ORDER BY t.DateDebut DESC) AS rn
                {base_query_from}
                {where_clause}
            )
            SELECT
                Num_Serie,
                Date_Debut,
                Result,
                TypeTest,
                Id_Machine,
                Id_Operateur,
                Id_Board
            FROM RankedTests
            WHERE rn = 1
            ORDER BY Date_Debut DESC;
        """

        result = self.db.execute(text(final_query_str), params).fetchall()

        unique_tests_data = []
        for row in result:
            unique_tests_data.append(TestRecord(
                num_serie=row.Num_Serie,
                date_debut=row.Date_Debut,
                result=row.Result,
                type_test=row.TypeTest,
                id_machine=row.Id_Machine,
                id_operateur=str(int(row.Id_Operateur)) if row.Id_Operateur is not None else None,
                id_board=row.Id_Board
            ))

        return unique_tests_data


# --- FastAPI Endpoints ---

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed login attempt for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    logger.info(f"User {user.username} logged in successfully")
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/boards", response_model=list[BoardInfo])
async def get_all_boards(
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        board_service = BoardService(db)
        boards = board_service.get_all_boards()
        logger.info(f"Boards fetched successfully for user: {current_user.username}")
        return boards
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/api/boards/", response_model=BoardInfo, status_code=status.HTTP_201_CREATED)
async def create_board(
    board_data: BoardCreate,
    current_user: UserInDB = Depends(require_admin()),
    db: Session = Depends(get_db)
):
    try:
        board_service = BoardService(db)
        new_board = board_service.create_board(board_data)
        logger.info(f"Board created successfully by user: {current_user.username}")
        return new_board
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error creating board: {e}")
        raise HTTPException(status_code=500, detail=f"Database error creating board: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/api/boards/{board_id}", response_model=BoardInfo)
async def get_board_by_id(
    board_id: int,
    current_user: UserInDB = Depends(require_admin()),
    db: Session = Depends(get_db)
):
    try:
        board_service = BoardService(db)
        board = board_service.get_board_by_id(board_id)
        if board:
            logger.info(f"Board {board_id} fetched successfully for user: {current_user.username}")
            return board
        raise HTTPException(status_code=404, detail=f"Board with ID {board_id} not found.")
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.put("/api/boards/{board_id}", response_model=BoardInfo)
async def update_board(
    board_id: int,
    board_data: BoardUpdate,
    current_user: UserInDB = Depends(require_admin()),
    db: Session = Depends(get_db)
):
    try:
        board_service = BoardService(db)
        updated_board = board_service.update_board(board_id, board_data)
        if updated_board:
            logger.info(f"Board {board_id} updated successfully by user: {current_user.username}")
            return updated_board
        raise HTTPException(status_code=404, detail=f"Board with ID {board_id} not found.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error updating board: {e}")
        raise HTTPException(status_code=500, detail=f"Database error updating board: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.delete("/api/boards/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(
    board_id: int,
    current_user: UserInDB = Depends(require_admin()),
    db: Session = Depends(get_db)
):
    try:
        board_service = BoardService(db)
        if not board_service.delete_board(board_id):
            raise HTTPException(status_code=404, detail=f"Board with ID {board_id} not found.")
        logger.info(f"Board {board_id} deleted successfully by user: {current_user.username}")
    except SQLAlchemyError as e:
        logger.error(f"Database error deleting board: {e}")
        raise HTTPException(status_code=500, detail=f"Database error deleting board: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/api/boards/{board_id}/tests", response_model=List[TestRecord])
async def get_tests_by_board(
    board_id: int,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info(f"Fetching tests for board_id: {board_id} for user: {current_user.username}")
    try:
        test_service = TestService(db)
        tests = test_service.get_tests_by_board_id(board_id)
        logger.info(f"Found {len(tests)} tests for board_id {board_id}")
        return tests
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/api/boards/export/xlsx")
async def export_boards_xlsx(
    current_user: UserInDB = Depends(require_admin()),
    db: Session = Depends(get_db)
):
    logger.info(f"Attempting Excel export for user: {current_user.username}")
    try:
        board_service = BoardService(db)
        df = board_service.export_boards_to_df()
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Boards")
        output.seek(0)
        logger.info(f"Excel export successful for user: {current_user.username}")
        return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={
            "Content-Disposition": "attachment; filename=boards_export.xlsx"
        })
    except SQLAlchemyError as e:
        logger.error(f"Database error during export: {e}")
        raise HTTPException(status_code=500, detail="Database error during export.")
    except Exception as e:
        logger.error(f"Unexpected error during export: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error during export.")
@app.get("/api/unique-tests-by-metric", response_model=List[TestRecord])
async def get_unique_tests_by_metric(
    metric_column: str = Query(..., description="Column to filter by"),
    metric_value: str = Query(..., description="Value to filter with"),
    start_date: datetime = Query(..., description="Start date (format: YYYY-MM-DD HH:MM:SS)"),
    end_date: datetime = Query(..., description="End date (format: YYYY-MM-DD HH:MM:SS)"),
    current_user: UserInDB = Depends(get_current_user), # Added for authentication
    db: Session = Depends(get_db)
):
    try:
        test_service = TestService(db)
        unique_tests = test_service.get_unique_tests_by_metric(metric_column, metric_value, start_date, end_date)
        return unique_tests
    except ValueError as e:
        logger.error(f"Validation error in get_unique_tests_by_metric: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_unique_tests_by_metric: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in get_unique_tests_by_metric: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/api/boards/import/csv")
async def import_boards_csv(
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(require_admin()),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    content = await file.read()
    csv_str = content.decode('utf-8').splitlines()

    try:
        board_service = BoardService(db)
        processed_count = board_service.import_boards_from_csv(csv_str)
        db.commit() # Commit the changes made by the service
        logger.info(f"{processed_count} records processed by user: {current_user.username}")
        return {"message": f"{processed_count} records processed successfully."}
    except Exception as e:
        db.rollback() # Rollback on error
        logger.error(f"Error processing CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")

@app.get("/api/quality-metrics", response_model=QualityMetrics)
async def get_quality_metrics(
    selected_date: date = Query(..., description="The date to analyze"),
    start_time: time = Query(time(0, 0, 0), description="Start time"),
    end_time: time = Query(time(23, 59, 59), description="End time"),
    db: Session = Depends(get_db)
):
    try:
        start_datetime = datetime.combine(selected_date, start_time)
        end_datetime = datetime.combine(selected_date, end_time)

        if start_datetime >= end_datetime:
            raise HTTPException(status_code=400, detail="Finish time must be after start time.")

        # Removed `with db.begin() as conn:` and directly used `db.execute()`
        total = db.execute(
            text("""
                SELECT COUNT(*) FROM abb_dbo_test
                WHERE STR_TO_DATE(DateDebut, '%Y-%m-%d %H:%i:%s')
                BETWEEN :start AND :end
            """),
            {"start": start_datetime, "end": end_datetime}
        ).scalar() or 0

        good = db.execute(
            text("""
                SELECT COUNT(*) FROM abb_dbo_test
                WHERE STR_TO_DATE(DateDebut, '%Y-%m-%d %H:%i:%s')
                BETWEEN :start AND :end AND Result = 1
            """),
            {"start": start_datetime, "end": end_datetime}
        ).scalar() or 0

        bad = db.execute(
            text("""
                SELECT COUNT(*) FROM abb_dbo_test
                WHERE STR_TO_DATE(DateDebut, '%Y-%m-%d %H:%i:%s')
                BETWEEN :start AND :end AND (Result IS NULL OR Result != 1)
            """),
            {"start": start_datetime, "end": end_datetime}
        ).scalar() or 0

        defect_result = db.execute(
            text("""
                SELECT i.Defaut, COUNT(*) AS defect_count
                FROM abb_dbo_intervention i
                WHERE i.DateIntervention BETWEEN :start AND :end AND i.Defaut IS NOT NULL
                GROUP BY i.Defaut
                ORDER BY defect_count DESC
            """),
            {"start": start_datetime, "end": end_datetime}
        )
        defects = {row.Defaut: row.defect_count for row in defect_result}

        ref_stats_result = db.execute(
            text("""
                SELECT
                    b.REF_AsteelFlash AS ref_asteel,
                    SUM(CASE WHEN t.Result = 1 THEN 1 ELSE 0 END) AS good_count,
                    SUM(CASE WHEN t.Result != 1 OR t.Result IS NULL THEN 1 ELSE 0 END) AS bad_count,
                    MAX(t.Num_Serie) AS serial_number
                FROM abb_dbo_board b
                LEFT JOIN abb_dbo_test t ON t.Id_Board = b.Id
                WHERE STR_TO_DATE(t.DateDebut, '%Y-%m-%d %H:%i:%s') BETWEEN :start AND :end
                GROUP BY b.REF_AsteelFlash
                ORDER BY b.REF_AsteelFlash
            """),
            {"start": start_datetime, "end": end_datetime}
        )
        ref_stats = [
            RefStat(
                ref_asteel=row.ref_asteel,
                good_count=row.good_count or 0,
                bad_count=row.bad_count or 0,
                serial_number=row.serial_number or ""
            )
            for row in ref_stats_result if row.ref_asteel
        ]

        ref_price_stats_result = db.execute(
            text("""
                SELECT
                    b.REF_AsteelFlash AS ref_asteel,
                    SUM(t.Result = 1) AS good_tests,
                    SUM(t.Result != 1 OR t.Result IS NULL) AS bad_tests,
                    b.prix AS unit_price,
                    (SUM(t.Result = 1) * b.prix) AS total_price,
                    MAX(t.Num_Serie) AS num_serie
                FROM abb_dbo_board b
                LEFT JOIN abb_dbo_test t ON t.Id_Board = b.Id
                WHERE STR_TO_DATE(t.DateDebut, '%Y-%m-%d %H:%i:%s') BETWEEN :start AND :end
                GROUP BY b.REF_AsteelFlash, b.prix
                ORDER BY b.REF_AsteelFlash
            """),
            {"start": start_datetime, "end": end_datetime}
        )
        ref_price_stats = [
            RefPriceStat(
                ref_asteel=row.ref_asteel,
                num_serie=row.num_serie or "",
                good_tests=row.good_tests or 0,
                bad_tests=row.bad_tests or 0,
                unit_price=float(row.unit_price) if row.unit_price is not None else 0.0,
                total_price=float(row.total_price) if row.total_price is not None else 0.0
            )
            for row in ref_price_stats_result if row.ref_asteel
        ]

        # NEW QUERY: Fetch all fields for individual test records
        test_details_result = db.execute(
            text("""
                SELECT
                    Id AS id,
                    Id_Board AS id_board,
                    Num_Serie AS num_serie,
                    Id_Machine AS id_machine,
                    Id_Operateur AS id_operateur,
                    DateDebut AS date_debut,
                    DateFin AS date_fin,
                    Result AS result,
                    TypeTest AS type_test,
                    Side AS side,
                    Position_Flan AS position_flan,
                    Id_ConfigLigne AS id_config_ligne,
                    Id_Process AS id_process,
                    Comment AS comment
                FROM abb_dbo_test
                WHERE STR_TO_DATE(DateDebut, '%Y-%m-%d %H:%i:%s') BETWEEN :start AND :end
                ORDER BY DateDebut DESC
            """),
            {"start": start_datetime, "end": end_datetime}
        )

        # Helper to format date strings consistently for Pydantic model
        def format_date_str(val):
            if val is None:
                return None
            return str(val)

        test_details = [
            TestRecord(
                id=row.id,
                id_board=row.id_board,
                num_serie=row.num_serie,
                id_machine=row.id_machine,
                id_operateur=str(int(row.id_operateur)) if row.id_operateur is not None else None,
                date_debut=format_date_str(row.date_debut),
                date_fin=format_date_str(row.date_fin),
                result=row.result,
                type_test=row.type_test,
                side=row.side,
                position_flan=row.position_flan,
                id_config_ligne=row.id_config_ligne,
                id_process=row.id_process,
                comment=row.comment
            )
            for row in test_details_result
        ]

        return QualityMetrics(
            date=selected_date,
            total_quantity=total,
            good_quantity=good,
            bad_quantity=bad,
            defect_details=defects,
            ref_stats=ref_stats,
            ref_price_stats=ref_price_stats,
            test_details=test_details
        )

    except SQLAlchemyError as e:
        logger.error(f"Database error in get_quality_metrics: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error in get_quality_metrics: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error")