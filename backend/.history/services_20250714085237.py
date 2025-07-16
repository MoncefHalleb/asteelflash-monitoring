# services.py
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import pandas as pd
import csv
from typing import List
from schemas import (
    BoardInfo, BoardCreate, BoardUpdate,
    TestRecord, RefStat, RefPriceStat, QualityMetrics
)

class BoardService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[BoardInfo]:
        rows = self.db.execute(text("SELECT * FROM abb_dbo_board")).fetchall()
        return [BoardInfo(**r._mapping) for r in rows]

    def create(self, data: BoardCreate) -> BoardInfo:
        fields = data.dict(exclude_unset=True)
        fields["Date_Creation"] = datetime.utcnow()
        cols = ", ".join(fields.keys())
        vals = ", ".join(f":{k}" for k in fields)
        self.db.execute(text(f"INSERT INTO abb_dbo_board({cols}) VALUES ({vals})"), fields)
        new_id = self.db.execute(text("SELECT LAST_INSERT_ID()")).scalar()
        row = self.db.execute(text("SELECT * FROM abb_dbo_board WHERE Id = :id"), {"id": new_id}).fetchone()
        return BoardInfo(**row._mapping)

    def get(self, board_id: int) -> BoardInfo:
        row = self.db.execute(text("SELECT * FROM abb_dbo_board WHERE Id = :id"), {"id": board_id}).fetchone()
        if not row: raise ValueError("Not found")
        return BoardInfo(**row._mapping)

    def update(self, board_id: int, data: BoardUpdate) -> BoardInfo:
        fields = data.dict(exclude_unset=True)
        sets   = ", ".join(f"{k}=:{k}" for k in fields)
        fields["id"] = board_id
        self.db.execute(text(f"UPDATE abb_dbo_board SET {sets} WHERE Id = :id"), fields)
        return self.get(board_id)

    def delete(self, board_id: int) -> None:
        self.db.execute(text("DELETE FROM abb_dbo_board WHERE Id = :id"), {"id": board_id})

    def export_df(self) -> pd.DataFrame:
        return pd.read_sql("SELECT * FROM abb_dbo_board", self.db.bind)

    def import_csv(self, lines: List[str]) -> int:
        reader = csv.DictReader(lines)
        count = 0
        for row in reader:
            self.db.execute(text("""
                INSERT INTO abb_dbo_board (REF_AsteelFlash, REF_Clients, Designation, Client, Board_Ver, Code_Indus, Indice, Software, Software_Ver, Valide, Id_Assembly, Id_Process, QuantCondit, Id_Famille, prix, Date_Creation)
                VALUES (:REF_AsteelFlash, :REF_Clients, :Designation, :Client, :Board_Ver, :Code_Indus, :Indice, :Software, :Software_Ver, :Valide, :Id_Assembly, :Id_Process, :QuantCondit, :Id_Famille, :prix, :Date_Creation)
            """), {
                **row,
                "Valide": row.get("is_valid") in ["1","true","True"],
                "Date_Creation": datetime.utcnow()
            })
            count += 1
        return count

class TestService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_board(self, board_id: int) -> List[TestRecord]:
        rows = self.db.execute(text("SELECT * FROM abb_dbo_test WHERE Id_Board = :b"), {"b": board_id}).fetchall()
        return [TestRecord(**r._mapping) for r in rows]

    def unique_by_metric(self, col: str, val: str, start, end) -> List[TestRecord]:
        allowed = {"TypeTest","Result","Id_Machine","Id_Operateur","Id_Board","Num_Serie"}
        if col not in allowed: raise ValueError("Invalid metric")
        q = f"""
            WITH R AS (
              SELECT t.*, ROW_NUMBER() OVER (PARTITION BY Num_Serie ORDER BY DateDebut DESC) rn
              FROM abb_dbo_test t WHERE STR_TO_DATE(DateDebut,'%Y-%m-%d %H:%i:%s') BETWEEN :s AND :e
              AND t.{col} = :v
            )
            SELECT * FROM R WHERE rn=1
        """
        rows = self.db.execute(text(q), {"s": start, "e": end, "v": val}).fetchall()
        return [TestRecord(**r._mapping) for r in rows]

class MetricsService:
    def __init__(self, db: Session):
        self.db = db

    def quality(self, date, start_time, end_time) -> QualityMetrics:
        s = f"{date} {start_time}"
        e = f"{date} {end_time}"
        total = self.db.execute(text(
            "SELECT COUNT(*) FROM abb_dbo_test WHERE STR_TO_DATE(DateDebut,'%Y-%m-%d %H:%i:%s') BETWEEN :s AND :e"
        ), {"s": s, "e": e}).scalar() or 0
        good = self.db.execute(text(
            "SELECT COUNT(*) FROM abb_dbo_test WHERE Result=1 AND STR_TO_DATE(DateDebut,'%Y-%m-%d %H:%i:%s') BETWEEN :s AND :e"
        ), {"s": s, "e": e}).scalar() or 0
        bad = total - good
        defects = dict(self.db.execute(text(
            "SELECT Defaut, COUNT(*) FROM abb_dbo_intervention WHERE DateIntervention BETWEEN :s AND :e AND Defaut IS NOT NULL GROUP BY Defaut"
        ), {"s": s, "e": e}).fetchall())
        ref_stats = self.db.execute(text("""
            SELECT b.REF_AsteelFlash ref_asteel,
                   SUM(t.Result=1) good_count,
                   SUM(t.Result!=1 OR t.Result IS NULL) bad_count,
                   MAX(t.Num_Serie) serial_number
            FROM abb_dbo_board b
            JOIN abb_dbo_test t ON t.Id_Board=b.Id
            WHERE STR_TO_DATE(t.DateDebut,'%Y-%m-%d %H:%i:%s') BETWEEN :s AND :e
            GROUP BY b.REF_AsteelFlash
        """), {"s": s, "e": e}).mappings().all()
        ref_price = self.db.execute(text("""
            SELECT b.REF_AsteelFlash ref_asteel,
                   SUM(t.Result=1) good_tests,
                   SUM(t.Result!=1 OR t.Result IS NULL) bad_tests,
                   b.prix unit_price,
                   SUM(t.Result=1)*b.prix total_price
            FROM abb_dbo_board b
            JOIN abb_dbo_test t ON t.Id_Board=b.Id
            WHERE STR_TO_DATE(t.DateDebut,'%Y-%m-%d %H:%i:%s') BETWEEN :s AND :e
            GROUP BY b.REF_AsteelFlash,b.prix
        """), {"s": s, "e": e}).mappings().all()
        tests = self.db.execute(text("""
            SELECT * FROM abb_dbo_test
            WHERE STR_TO_DATE(DateDebut,'%Y-%m-%d %H:%i:%s') BETWEEN :s AND :e
            ORDER BY DateDebut DESC
        """), {"s": s, "e": e}).fetchall()
        return QualityMetrics(
            date=date,
            total_quantity=total,
            good_quantity=good,
            bad_quantity=bad,
            defect_details=defects,
            ref_stats=[RefStat(**r) for r in ref_stats],
            ref_price_stats=[RefPriceStat(**r) for r in ref_price],
            test_details=[TestRecord(**r._mapping) for r in tests]
        )
