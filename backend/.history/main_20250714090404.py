# main.py
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db, Base, engine
import pandas as pd
from io import BytesIO
from datetime import date, time
from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    require_admin,
    require_user,
    OAuth2PasswordRequestForm,
)
from schemas import (
    BoardInfo,
    BoardCreate,
    BoardUpdate,
    TestRecord,
    Token,
    QualityMetrics,
)
from services import BoardService, TestService, MetricsService

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Authentication ---
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    access_token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Boards ---
@app.get("/api/boards", response_model=list[BoardInfo])
def list_boards(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return BoardService(db).get_all()

@app.post("/api/boards", response_model=BoardInfo, status_code=status.HTTP_201_CREATED)
def create_board(
    data: BoardCreate,
    db: Session = Depends(get_db),
    __=Depends(require_admin),
):
    return BoardService(db).create(data)

@app.get("/api/boards/{id}", response_model=BoardInfo)
def get_board(
    id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    b = BoardService(db).get(id)
    if not b:
        raise HTTPException(status_code=404, detail="Not found")
    return b

@app.put("/api/boards/{id}", response_model=BoardInfo)
def update_board(
    id: int,
    data: BoardUpdate,
    db: Session = Depends(get_db),
    __=Depends(require_admin),
):
    return BoardService(db).update(id, data)

@app.delete("/api/boards/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_board(
    id: int,
    db: Session = Depends(get_db),
    __=Depends(require_admin),
):
    BoardService(db).delete(id)

# --- Export / Import ---
@app.get("/api/boards/export/xlsx")
def export_boards(
    db: Session = Depends(get_db),
    __=Depends(require_admin),
):
    df = BoardService(db).export_df()
    buf = BytesIO()
    df.to_excel(buf, index=False)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=boards.xlsx"},
    )

@app.post("/api/boards/import/csv")
def import_boards(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    __=Depends(require_admin),
):
    lines = file.file.read().decode().splitlines()
    count = BoardService(db).import_csv(lines)
    return {"processed": count}

# --- Tests ---
@app.get("/api/boards/{id}/tests", response_model=list[TestRecord])
def tests_by_board(
    id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return TestService(db).get_by_board(id)

@app.get("/api/unique-tests-by-metric", response_model=list[TestRecord])
def unique_tests(
    metric_column: str = Query(..., description="Column to filter by"),
    metric_value:  str = Query(..., description="Value to filter on"),
    start_date:    str = Query(
        ..., 
        description="Start datetime (format: 'YYYY-MM-DD HH:MM:SS')"
    ),
    end_date:      str = Query(
        ..., 
        description="End datetime (format: 'YYYY-MM-DD HH:MM:SS')"
    ),
    db:            Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return TestService(db).unique_by_metric(metric_column, metric_value, start_date, end_date)

# --- Quality Metrics ---
@app.get("/api/quality-metrics", response_model=QualityMetrics)
def quality_metrics(
    selected_date: date = Query(..., description="Date to analyze"),
    start_time:    time = Query(time(0, 0, 0), description="Start time"),
    end_time:      time = Query(time(23, 59, 59), description="End time"),
    db:            Session = Depends(get_db),
):
    return MetricsService(db).quality(selected_date, start_time.strftime("%H:%M:%S"), end_time.strftime("%H:%M:%S"))
