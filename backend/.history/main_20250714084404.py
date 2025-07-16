
# main.py
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Optional, List, Type, TypeVar, Generic
from pydantic import BaseModel
import pandas as pd
import joblib
import numpy as np
from io import BytesIO
from datetime import datetime

DATABASE_URL = "mysql+pymysql://root:123@localhost/asteel"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Database Model
class Board(Base):
    __tablename__ = "abb_dbo_board"
    Id = Column(Integer, primary_key=True, autoincrement=True)
    REF_AsteelFlash = Column(String(40))
    REF_Clients = Column(String(40))
    Designation = Column(String(255))
    Client = Column(String(30))
    Board_Ver = Column(String(10))
    Valide = Column(Boolean)
    prix = Column(Float)
    Date_Creation = Column(DateTime, default=datetime.now)

Base.metadata.create_all(bind=engine)

# Pydantic schemas
class BoardBase(BaseModel):
    REF_AsteelFlash: Optional[str]
    REF_Clients: Optional[str]
    Designation: Optional[str]
    Client: Optional[str]
    Board_Ver: Optional[str]
    Valide: Optional[bool] = True
    prix: Optional[float]

class BoardCreate(BoardBase):
    pass

class BoardUpdate(BoardBase):
    pass

class BoardOut(BoardBase):
    Id: int
    Date_Creation: Optional[datetime]
    class Config:
        orm_mode = True

# Generic CRUD Service
T = TypeVar("T", bound=Base)
class CRUDService(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model
    def get(self, db: Session, id: int) -> Optional[T]:
        return db.query(self.model).filter(self.model.Id == id).first()
    def get_all(self, db: Session) -> List[T]:
        return db.query(self.model).all()
    def create(self, db: Session, obj: BaseModel) -> T:
        db_obj = self.model(**obj.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    def update(self, db: Session, id: int, obj: BaseModel) -> T:
        db_obj = self.get(db, id)
        if not db_obj:
            raise HTTPException(404, "Not found")
        for k, v in obj.dict(exclude_unset=True).items():
            setattr(db_obj, k, v)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    def delete(self, db: Session, id: int):
        db_obj = self.get(db, id)
        if not db_obj:
            raise HTTPException(404, "Not found")
        db.delete(db_obj)
        db.commit()

crud_board = CRUDService(Board)

# ML Model loading
model = joblib.load("best_model.ubj")
scaler = joblib.load("scaler.pkl")
columns = joblib.load("columns.pkl")

# FastAPI app
app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD endpoints
@app.get("/boards/", response_model=List[BoardOut])
def read_boards(db: Session = Depends(get_db)):
    return crud_board.get_all(db)

@app.post("/boards/", response_model=BoardOut)
def create_board(board: BoardCreate, db: Session = Depends(get_db)):
    return crud_board.create(db, board)

@app.put("/boards/{board_id}", response_model=BoardOut)
def update_board(board_id: int, board: BoardUpdate, db: Session = Depends(get_db)):
    return crud_board.update(db, board_id, board)

@app.delete("/boards/{board_id}")
def delete_board(board_id: int, db: Session = Depends(get_db)):
    crud_board.delete(db, board_id)
    return {"status": "deleted"}

# CSV Import
@app.post("/boards/import/csv")
def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    df = pd.read_csv(file.file)
    boards = df.to_dict(orient="records")
    for data in boards:
        board = BoardCreate(**data)
        crud_board.create(db, board)
    return {"status": "imported"}

# Excel Export
@app.get("/boards/export/xlsx")
def export_xlsx(db: Session = Depends(get_db)):
    boards = crud_board.get_all(db)
    df = pd.DataFrame([board.__dict__ for board in boards])
    output = BytesIO()
    with pd.ExcelWriter(output) as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=boards.xlsx"})

# ML Prediction
@app.post("/boards/predict/")
def predict(data: dict):
    X = np.array([data[col] for col in columns]).reshape(1, -1)
    X_scaled = scaler.transform(X)
    pred = model.predict(X_scaled)[0]
    proba = model.predict_proba(X_scaled).max()
    return {"prediction": int(pred), "probability": proba}
