# main.py
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from database import get_db, Base, engine, User
from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    require_admin,
    require_user,
    OAuth2PasswordRequestForm,

)
from schemas import (
    UserCreate, UserOut,
    BoardInfo, BoardCreate, BoardUpdate,
    TestRecord, Token, QualityMetrics
)
from services import BoardService, TestService, MetricsService, ForecastService
import pandas as pd
from io import BytesIO, StringIO
from datetime import date, time
from prophet import Prophet
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

@app.post("/register-user", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed = get_password_hash(user_in.password)
    new_user = User(username=user_in.username, hashed_password=hashed, role=user_in.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# --- Boards ---
@app.get("/api/boards", response_model=list[BoardInfo])
def list_boards(db: Session = Depends(get_db), _: dict = Depends(get_current_user)):
    return BoardService(db).get_all()

@app.post("/api/boards", response_model=BoardInfo, status_code=status.HTTP_201_CREATED)
def create_board(data: BoardCreate, db: Session = Depends(get_db), __=Depends(require_admin)):
    return BoardService(db).create(data)

@app.get("/api/boards/{id}", response_model=BoardInfo)
def get_board(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return BoardService(db).get(id)

@app.put("/api/boards/{id}", response_model=BoardInfo)
def update_board(id: int, data: BoardUpdate, db: Session = Depends(get_db), __=Depends(require_admin)):
    return BoardService(db).update(id, data)

@app.delete("/api/boards/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_board(id: int, db: Session = Depends(get_db), __=Depends(require_admin)):
    BoardService(db).delete(id)

# --- Export / Import ---
@app.get("/api/boards/export/csv")
def export_boards_csv(db: Session = Depends(get_db), __=Depends(require_admin)):
    df = BoardService(db).export_df()
    buf = StringIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return StreamingResponse(buf, media_type="text/csv",
                             headers={"Content-Disposition": "attachment; filename=boards_export.csv"})

@app.get("/api/boards/export/xlsx")
def export_boards_xlsx(db: Session = Depends(get_db), __=Depends(require_admin)):
    df = BoardService(db).export_df()
    buf = BytesIO()
    df.to_excel(buf, index=False)
    buf.seek(0)
    return StreamingResponse(buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=boards.xlsx"}
    )

@app.post("/api/boards/import/csv")
def import_boards(file: UploadFile = File(...), db: Session = Depends(get_db), __=Depends(require_admin)):
    lines = file.file.read().decode().splitlines()
    count = BoardService(db).import_csv(lines)
    return {"processed": count}

# --- Tests ---
@app.get("/api/boards/{id}/tests", response_model=list[TestRecord])
def tests_by_board(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return TestService(db).get_by_board(id)

@app.get("/api/unique-tests-by-metric", response_model=list[TestRecord])
def unique_tests(
    metric_column: str = Query(...),
    metric_value:  str = Query(...),
    start_date:    str = Query(...),
    end_date:      str = Query(...),
    db:            Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return TestService(db).unique_by_metric(metric_column, metric_value, start_date, end_date)

# --- Quality Metrics ---
@app.get("/api/quality-metrics", response_model=QualityMetrics)
def quality_metrics(
    selected_date: date = Query(...),
    start_time:    time = Query(time(0,0,0)),
    end_time:      time = Query(time(23,59,59)),
    db:            Session = Depends(get_db),
):
    return MetricsService(db).quality(selected_date, start_time.strftime("%H:%M:%S"), end_time.strftime("%H:%M:%S"))

@app.get("/api/defect-forecast")
def defect_forecast(periods: int = 30):
    forecast = ForecastService.forecast(periods)
    
    # Convert Timestamp to string for JSON serialization
    forecast['ds'] = forecast['ds'].dt.strftime('%Y-%m-%d %H:%M:%S')
    forecast['yhat'] = forecast['yhat'].astype(float)  # Make sure 'yhat' is also serialized properly
    forecast['yhat_lower'] = forecast['yhat_lower'].astype(float)
    forecast['yhat_upper'] = forecast['yhat_upper'].astype(float)
    
    # Return the forecast as JSON response
    return JSONResponse(forecast.to_dict(orient="records"))


@app.get("/api/defect-backtest")
def defect_backtest(
    horizon: int = Query(8, description="Back-test horizon in days"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    svc = ForecastService(db)
    df_cv, df_perf = svc.backtest(horizon)
    if df_cv is None:
        raise HTTPException(status_code=400, detail="Not enough data for back-test")
    return {
        "cv": df_cv.to_dict(orient="records"),
        "performance": df_perf.to_dict(orient="records")
    }
