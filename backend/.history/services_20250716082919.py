from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd, csv
from typing import List
from prophet import Prophet

from schemas import (
    BoardInfo, BoardCreate, BoardUpdate,
    TestRecord, RefStat, RefPriceStat, QualityMetrics
)

class BoardService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[BoardInfo]:
        sql = text("""
          SELECT
            CAST(b.Id AS UNSIGNED)                AS id,
            COALESCE(b.REF_AsteelFlash, '')       AS ref_asteel,
            COALESCE(b.REF_Clients, '')           AS ref_client,
            COALESCE(b.Designation, '')           AS designation,
            COALESCE(b.Client, '')                AS client,
            COALESCE(b.Board_Ver, '')             AS board_version,
            COALESCE(b.Code_Indus, '')            AS code_indus,
            COALESCE(b.Indice, '')                AS indice,
            COALESCE(b.Software, '')              AS software,
            COALESCE(b.Software_Ver, '')          AS software_ver,
            CASE WHEN b.Valide IS NULL THEN FALSE ELSE b.Valide END  AS is_valid,
            CAST(b.Id_Assembly AS SIGNED)         AS id_assembly,
            CAST(b.Id_Process AS SIGNED)          AS id_process,
            b.QuantCondit                         AS quantcondit,
            CAST(b.Id_Famille AS SIGNED)          AS id_famille,
            COALESCE(f.Nom_Famille, '')           AS family_name,
            ''                                     AS serial_number,
            COALESCE(b.prix, 0)                   AS prix
          FROM abb_dbo_board b
          LEFT JOIN abb_dbo_famille f
            ON b.Id_Famille = f.Id
          ORDER BY b.Id
        """)
        rows = self.db.execute(sql).fetchall()
        return [BoardInfo(**r._mapping) for r in rows]

    def create(self, data: BoardCreate) -> BoardInfo:
        fields = data.dict(exclude_unset=True)
        fields["Date_Creation"] = datetime.utcnow()
        cols = ", ".join(fields.keys())
        vals = ", ".join(f":{k}" for k in fields)
        self.db.execute(text(f"INSERT INTO abb_dbo_board ({cols}) VALUES ({vals})"), fields)
        new_id = self.db.execute(text("SELECT LAST_INSERT_ID()")).scalar()
        return self.get(new_id)

    def get(self, board_id: int) -> BoardInfo:
        sql = text("""SELECT
            CAST(b.Id AS UNSIGNED) AS id,
            COALESCE(b.REF_AsteelFlash,'') AS ref_asteel,
            COALESCE(b.REF_Clients,'')     AS ref_client,
            COALESCE(b.Designation,'')     AS designation,
            COALESCE(b.Client,'')          AS client,
            COALESCE(b.Board_Ver,'')       AS board_version,
            COALESCE(b.Code_Indus,'')      AS code_indus,
            COALESCE(b.Indice,'')          AS indice,
            COALESCE(b.Software,'')        AS software,
            COALESCE(b.Software_Ver,'')    AS software_ver,
            CASE WHEN b.Valide IS NULL THEN FALSE ELSE b.Valide END AS is_valid,
            CAST(b.Id_Assembly AS SIGNED)   AS id_assembly,
            CAST(b.Id_Process AS SIGNED)    AS id_process,
            b.QuantCondit                   AS quantcondit,
            CAST(b.Id_Famille AS SIGNED)    AS id_famille,
            ''                               AS serial_number,
            ''                               AS family_name,
            COALESCE(b.prix,0)             AS prix
          FROM abb_dbo_board b
          WHERE b.Id = :board_id
        """)
        row = self.db.execute(sql, {"board_id": board_id}).fetchone()
        if not row:
            raise ValueError("Board not found")
        return BoardInfo(**row._mapping)

    def update(self, board_id: int, data: BoardUpdate) -> BoardInfo:
        fields = data.dict(exclude_unset=True)
        if not fields:
            raise ValueError("No fields to update")
        sets = ", ".join(f"{k} = :{k}" for k in fields)
        fields["board_id"] = board_id
        self.db.execute(text(f"UPDATE abb_dbo_board SET {sets} WHERE Id = :board_id"), fields)
        return self.get(board_id)

    def delete(self, board_id: int) -> None:
        self.db.execute(text("DELETE FROM abb_dbo_board WHERE Id = :board_id"), {"board_id": board_id})

    def export_df(self) -> pd.DataFrame:
        return pd.read_sql("SELECT * FROM abb_dbo_board", self.db.bind)

    def import_csv(self, lines: List[str]) -> int:
        reader = csv.DictReader(lines)
        count = 0
        for row in reader:
            row["Valide"] = row.get("is_valid","").lower() in ("1","true")
            row["Date_Creation"] = datetime.utcnow()
            cols = ", ".join(row.keys())
            vals = ", ".join(f":{k}" for k in row)
            self.db.execute(text(f"INSERT INTO abb_dbo_board ({cols}) VALUES ({vals})"), row)
            count += 1
        return count

class TestService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_board(self, board_id: int) -> List[TestRecord]:
        sql = text("""SELECT
            Id AS id, Id_Board AS id_board, Num_Serie AS num_serie,
            Id_Machine AS id_machine, Id_Operateur AS id_operateur,
            DateDebut AS date_debut, DateFin AS date_fin,
            Result AS result, TypeTest AS type_test,
            Side AS side, Position_Flan AS position_flan,
            Id_ConfigLigne AS id_config_ligne, Id_Process AS id_process,
            Comment AS comment
          FROM abb_dbo_test WHERE Id_Board = :board_id
        """)
        rows = self.db.execute(sql, {"board_id": board_id}).fetchall()
        return [TestRecord(**r._mapping) for r in rows]

    def unique_by_metric(self, metric_column: str, metric_value: str, start: str, end: str) -> List[TestRecord]:
        allowed = {"TypeTest","Result","Id_Machine","Id_Operateur","Id_Board","Num_Serie"}
        if metric_column not in allowed:
            raise ValueError("Invalid metric_column")
        sql = text(f"""
            WITH Ranked AS (
              SELECT t.*,
                     ROW_NUMBER() OVER (PARTITION BY t.Num_Serie ORDER BY STR_TO_DATE(t.DateDebut,'%Y-%m-%d %H:%i:%s') DESC) rn
              FROM abb_dbo_test t
              WHERE STR_TO_DATE(t.DateDebut,'%Y-%m-%d %H:%i:%s') BETWEEN :start AND :end
                AND t.{metric_column} = :metric_value
            )
            SELECT
              Id AS id, Id_Board AS id_board, Num_Serie AS num_serie,
              Id_Machine AS id_machine, Id_Operateur AS id_operateur,
              DateDebut AS date_debut, DateFin AS date_fin,
              Result AS result, TypeTest AS type_test,
              Side AS side, Position_Flan AS position_flan,
              Id_ConfigLigne AS id_config_ligne, Id_Process AS id_process,
              Comment AS comment
            FROM Ranked WHERE rn = 1
        """)
        rows = self.db.execute(sql, {"start": start, "end": end, "metric_value": metric_value}).fetchall()
        return [TestRecord(**r._mapping) for r in rows]

class MetricsService:
    def __init__(self, db: Session):
        self.db = db

    def quality(self, d: date, start_t: str, end_t: str) -> QualityMetrics:
        start = f"{d} {start_t}"
        end   = f"{d} {end_t}"

        total = self.db.execute(text("""
            SELECT COUNT(*) FROM abb_dbo_test
            WHERE STR_TO_DATE(DateDebut,'%Y-%m-%d %H:%i:%s') BETWEEN :start AND :end
        """), {"start": start, "end": end}).scalar() or 0

        good = self.db.execute(text("""
            SELECT COUNT(*) FROM abb_dbo_test
            WHERE Result = 1 AND STR_TO_DATE(DateDebut,'%Y-%m-%d %H:%i:%s') BETWEEN :start AND :end
        """), {"start": start, "end": end}).scalar() or 0

        bad = total - good

        defects = dict(self.db.execute(text("""
            SELECT Defaut, COUNT(*) FROM abb_dbo_intervention
            WHERE DateIntervention BETWEEN :start AND :end AND Defaut IS NOT NULL
            GROUP BY Defaut
        """), {"start": start, "end": end}).fetchall())

        ref_stats = self.db.execute(text("""
            SELECT
              b.REF_AsteelFlash AS ref_asteel,
              SUM(t.Result = 1) AS good_count,
              SUM(t.Result != 1 OR t.Result IS NULL) AS bad_count,
              MAX(t.Num_Serie) AS serial_number
            FROM abb_dbo_board b JOIN abb_dbo_test t ON t.Id_Board = b.Id
            WHERE STR_TO_DATE(t.DateDebut,'%Y-%m-%d %H:%i:%s') BETWEEN :start AND :end
            GROUP BY b.REF_AsteelFlash
        """), {"start": start, "end": end}).mappings().all()

        ref_price = self.db.execute(text("""
            SELECT
              b.REF_AsteelFlash AS ref_asteel,
              SUM(t.Result = 1) AS good_tests,
              SUM(t.Result != 1 OR t.Result IS NULL) AS bad_tests,
              b.prix AS unit_price,
              SUM(t.Result = 1) * b.prix AS total_price,
              MAX(t.Num_Serie) AS num_serie
            FROM abb_dbo_board b JOIN abb_dbo_test t ON t.Id_Board = b.Id
            WHERE STR_TO_DATE(t.DateDebut,'%Y-%m-%d %H:%i:%s') BETWEEN :start AND :end
            GROUP BY b.REF_AsteelFlash, b.prix
        """), {"start": start, "end": end}).mappings().all()

        rows = self.db.execute(text("""
            SELECT
              Id AS id, Id_Board AS id_board, Num_Serie AS num_serie,
              Id_Machine AS id_machine, Id_Operateur AS id_operateur,
              DateDebut AS date_debut, DateFin AS date_fin,
              Result AS result, TypeTest AS type_test,
              Side AS side, Position_Flan AS position_flan,
              Id_ConfigLigne AS id_config_ligne, Id_Process AS id_process,
              Comment AS comment
            FROM abb_dbo_test
            WHERE STR_TO_DATE(DateDebut,'%Y-%m-%d %H:%i:%s') BETWEEN :start AND :end
            ORDER BY DateDebut DESC
        """), {"start": start, "end": end}).fetchall()

        detail_list = []
        for r in rows:
            m = dict(r._mapping)
            op = m.get("id_operateur")
            m["id_operateur"] = str(int(op)) if op is not None else None
            detail_list.append(TestRecord(**m))

        return QualityMetrics(
            date=d,
            total_quantity=total,
            good_quantity=good,
            bad_quantity=bad,
            defect_details=defects,
            ref_stats=[RefStat(**r) for r in ref_stats],
            ref_price_stats=[RefPriceStat(**r) for r in ref_price],
            test_details=detail_list
        )
    # services.py

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

