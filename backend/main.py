from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import date, time, datetime, timedelta
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text, Column, Numeric, String, DateTime, Integer, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from collections import defaultdict
from typing import Literal, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import List, Dict, Optional


SECRET_KEY = "0fd58da17a8195ddf5c5e1d91f8391752550b47e29e56575b7d1fe15080a308c"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
DATABASE_URL = "mysql+pymysql://root:123@localhost/asteel"
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(10), nullable=False, default='user')

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
class RefPriceStat(BaseModel):
    ref_asteel: str
    good_count: int
    bad_count: int
    unit_price: Optional[float] = None
    total_price: Optional[float] = None

class QualityMetrics(BaseModel):
    date: date
    total_quantity: int
    good_quantity: int
    bad_quantity: int
    defect_details: dict
    ref_stats: List[RefStat] = []
    ref_price_stats: List[RefPriceStat] = []  # Ajouté ici



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
        print(f"Database error fetching user: {e}")
        raise HTTPException(status_code=500, detail="Database error during user lookup.")

async def authenticate_user(username: str, password: str):
    user = await get_user_from_db(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
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
    except JWTError:
        raise credentials_exception
    user = await get_user_from_db(token_data.username)
    if user is None:
        raise credentials_exception
    return user

def require_role(required_role: Literal['admin', 'user']):
    def role_checker(current_user: UserInDB = Depends(get_current_user)):
        if current_user.role != required_role:
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

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
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
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/boards", response_model=list[BoardInfo])
async def get_all_boards(current_user: UserInDB = Depends(get_current_user)):
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
    try:
        boards = []
        with engine.connect() as conn:
            result = conn.execute(query)
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
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/api/boards/", response_model=BoardInfo, status_code=status.HTTP_201_CREATED)
async def create_board(board_data: BoardCreate, current_user: UserInDB = Depends(require_admin())):
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
        raise HTTPException(status_code=400, detail="No data provided to create a board.")
    insert_query = text(
        f"INSERT INTO abb_dbo_board ({', '.join(columns)}) VALUES ({', '.join(values)})"
    )
    try:
        with engine.begin() as conn:
            result = conn.execute(insert_query, params)
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
            new_board_row = conn.execute(fetch_query, {"board_id": new_board_id}).fetchone()
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
                raise HTTPException(status_code=500, detail="Failed to retrieve newly created board.")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error creating board: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/api/boards/{board_id}", response_model=BoardInfo)
async def get_board_by_id(board_id: int, current_user: UserInDB = Depends(require_admin())):
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
    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"board_id": board_id}).fetchone()
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
            raise HTTPException(status_code=404, detail=f"Board with ID {board_id} not found.")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.put("/api/boards/{board_id}", response_model=BoardInfo)
async def update_board(board_id: int, board_data: BoardUpdate, current_user: UserInDB = Depends(require_admin())):
    update_fields = board_data.model_dump(exclude_unset=True)
    set_clauses = []
    params = {"board_id": board_id}
    for field, value in board_data.model_dump(exclude_unset=True).items():
        set_clauses.append(f"{field} = :{field}")
        params[field] = value
    if not set_clauses:
        raise HTTPException(status_code=400, detail="No fields provided for update.")
    update_query = text(
        f"UPDATE abb_dbo_board SET {', '.join(set_clauses)} WHERE Id = :board_id"
    )
    try:
        with engine.begin() as conn:
            result = conn.execute(update_query, params)
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail=f"Board with ID {board_id} not found.")
            fetch_query = text("""
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
            updated_board_row = conn.execute(fetch_query, {"board_id": board_id}).fetchone()
            if updated_board_row:
                mapped = updated_board_row._mapping
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
                    prix=mapped["prix"],
                )
            else:
                raise HTTPException(status_code=500, detail="Failed to retrieve updated board.")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error updating board: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.delete("/api/boards/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(board_id: int, current_user: UserInDB = Depends(require_admin())):
    delete_query = text("DELETE FROM abb_dbo_board WHERE Id = :board_id")
    try:
        with engine.begin() as conn:
            result = conn.execute(delete_query, {"board_id": board_id})
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail=f"Board with ID {board_id} not found.")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error deleting board: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
@app.get("/api/quality-metrics", response_model=QualityMetrics)
async def get_quality_metrics(
    selected_date: date = Query(...),
    start_time: time = Query(time(0,0,0)),
    end_time: time = Query(time(23,59,59))
):
    try:
        start_datetime = datetime.combine(selected_date, start_time)
        end_datetime = datetime.combine(selected_date, end_time)
        if start_datetime >= end_datetime:
            raise HTTPException(status_code=400, detail="Finish time must be after start time.")

        with engine.begin() as conn:
            total = conn.execute(
                text("""SELECT COUNT(*) FROM abb_dbo_test 
                        WHERE STR_TO_DATE(DateDebut, '%Y-%m-%d %H:%i:%s') 
                        BETWEEN :start AND :end"""),
                {"start": start_datetime, "end": end_datetime}
            ).scalar() or 0

            good = conn.execute(
                text("""SELECT COUNT(*) FROM abb_dbo_test 
                        WHERE STR_TO_DATE(DateDebut, '%Y-%m-%d %H:%i:%s') 
                        BETWEEN :start AND :end AND Result = 1"""),
                {"start": start_datetime, "end": end_datetime}
            ).scalar() or 0

            bad = conn.execute(
                text("""SELECT COUNT(*) FROM abb_dbo_test 
                        WHERE STR_TO_DATE(DateDebut, '%Y-%m-%d %H:%i:%s') 
                        BETWEEN :start AND :end AND (Result IS NULL OR Result != 1)"""),
                {"start": start_datetime, "end": end_datetime}
            ).scalar() or 0

            defect_result = conn.execute(
                text("""SELECT i.Defaut, COUNT(*) AS defect_count
                        FROM abb_dbo_intervention i
                        WHERE i.DateIntervention BETWEEN :start AND :end AND i.Defaut IS NOT NULL
                        GROUP BY i.Defaut
                        ORDER BY defect_count DESC"""),
                {"start": start_datetime, "end": end_datetime}
            )
            defects = {row.Defaut: row.defect_count for row in defect_result}

            # Statistiques ref simple good/bad
            ref_stats_query = text("""
                SELECT 
                    b.REF_AsteelFlash AS ref_asteel,
                    SUM(CASE WHEN t.Result = 1 THEN 1 ELSE 0 END) AS good_count,
                    SUM(CASE WHEN t.Result != 1 OR t.Result IS NULL THEN 1 ELSE 0 END) AS bad_count
                FROM abb_dbo_board b
                LEFT JOIN abb_dbo_test t ON t.Id_Board = b.Id
                WHERE STR_TO_DATE(t.DateDebut, '%Y-%m-%d %H:%i:%s') BETWEEN :start AND :end
                GROUP BY b.REF_AsteelFlash
                ORDER BY b.REF_AsteelFlash
            """)
            ref_stats_result = conn.execute(ref_stats_query, {"start": start_datetime, "end": end_datetime})
            ref_stats = [
                RefStat(
                    ref_asteel=row.ref_asteel,
                    good_count=row.good_count or 0,
                    bad_count=row.bad_count or 0
                )
                for row in ref_stats_result if row.ref_asteel
            ]

            # Statistiques ref avec prix total
            ref_price_stats_query = text("""
                SELECT
                    b.REF_AsteelFlash AS ref_asteel,
                    SUM(t.Result = 1) AS good_count,
                    SUM(t.Result != 1 OR t.Result IS NULL) AS bad_count,
                    b.prix AS unit_price,
                    (SUM(t.Result = 1) * b.prix) AS total_price
                FROM abb_dbo_board b
                LEFT JOIN abb_dbo_test t ON t.Id_Board = b.Id
                WHERE STR_TO_DATE(t.DateDebut, '%Y-%m-%d %H:%i:%s') BETWEEN :start AND :end
                GROUP BY b.REF_AsteelFlash, b.prix
                ORDER BY b.REF_AsteelFlash
            """)
            ref_price_stats_result = conn.execute(ref_price_stats_query, {"start": start_datetime, "end": end_datetime})
            ref_price_stats = [
                RefPriceStat(
                    ref_asteel=row.ref_asteel,
                    good_count=row.good_count or 0,
                    bad_count=row.bad_count or 0,
                    unit_price=row.unit_price,
                    total_price=row.total_price
                )
                for row in ref_price_stats_result if row.ref_asteel
            ]

            return QualityMetrics(
                date=selected_date,
                total_quantity=total,
                good_quantity=good,
                bad_quantity=bad,
                defect_details=defects,
                ref_stats=ref_stats,
                ref_price_stats=ref_price_stats,
            )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
