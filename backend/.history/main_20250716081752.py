# services.py
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd
import csv

from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics
import joblib

from schemas import (
    BoardInfo, BoardCreate, BoardUpdate,
    TestRecord, RefStat, RefPriceStat, QualityMetrics
)

class BoardService:
    # … your existing BoardService implementation …

class TestService:
    # … your existing TestService implementation …

class MetricsService:
    # … your existing MetricsService implementation …

class ForecastService:
    """
    Handles Prophet time-series for defect_rate:
     - load: daily defect rate from abb_dbo_test
     - train: fit Prophet
     - forecast: make n-day forecast
     - backtest: cross-validate + performance metrics
    """

    def __init__(self, db: Session):
        self.db = db
        self.engine = db.bind

    def _load_defect_rate(self) -> pd.DataFrame:
        sql = """
            SELECT
              DATE(t.DateDebut) AS ds,
              SUM(CASE WHEN t.Result=0 THEN 1 ELSE 0 END) * 1.0 /
              NULLIF(COUNT(*),0) AS y
            FROM abb_dbo_test t
            GROUP BY DATE(t.DateDebut)
            ORDER BY DATE(t.DateDebut)
        """
        df = pd.read_sql(sql, self.engine)
        return df.dropna()

    def _train(self, df: pd.DataFrame) -> Prophet:
        m = Prophet(daily_seasonality=True, weekly_seasonality=True, yearly_seasonality=False)
        m.fit(df)
        return m

    def forecast(self, periods: int = 30) -> pd.DataFrame:
        """
        Returns a DataFrame with columns [ds, yhat, yhat_lower, yhat_upper]
        for the next `periods` days.
        """
        df = self._load_defect_rate()
        model = self._train(df)
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)
        return forecast[['ds','yhat','yhat_lower','yhat_upper']]

    def backtest(self, horizon: int = 8):
        """
        Performs cross-validation over the last data. 
        Returns (df_cv, df_perf) or (None,None) if insufficient data.
        """
        df = self._load_defect_rate()
        n = len(df)
        initial = horizon * 2
        if n < initial + horizon:
            return None, None

        model = self._train(df)
        df_cv = cross_validation(model,
                                 initial=f"{initial} days",
                                 horizon=f"{horizon} days",
                                 period="1 day")
        df_perf = performance_metrics(df_cv)

        # also write out CSV if you want
        df_cv.to_csv("defect_rate_backtest.csv", index=False)
        df_perf.to_csv("defect_rate_performance_metrics.csv", index=False)

        return df_cv, df_perf
