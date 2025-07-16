import os
import pandas as pd
from sqlalchemy import create_engine, text
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics
import joblib

def load_daily_defect_rate(db_url):
    engine = create_engine(db_url)
    sql = text("""
        SELECT
            DATE(t.DateDebut) AS ds,
            SUM(CASE WHEN t.Result = 0 THEN 1 ELSE 0 END) * 1.0 /
            NULLIF(COUNT(*), 0) AS defect_rate
        FROM abb_dbo_test t
        GROUP BY DATE(t.DateDebut)
        ORDER BY DATE(t.DateDebut)
    """)
    df = pd.read_sql(sql, engine).dropna(subset=['defect_rate'])
    return df

def train_forecaster(df):
    df = df.rename(columns={'defect_rate': 'y'})
    m = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=False
    )
    m.fit(df)
    return m

def evaluate_model(model, df, horizon_days):
    """Run back-test only if len(df) >= initial + horizon, else skip."""
    initial_days = horizon_days * 2
    total_needed = initial_days + horizon_days
    if len(df) < total_needed:
        print(f"⚠️ Skipping back-test: need at least {total_needed} days (you have {len(df)}).")
        return

    horizon_str = f"{horizon_days} days"
    print(f"Running back-test: initial={initial_days}d, horizon={horizon_str}")

    df_cv = cross_validation(
        model,
        initial=f"{initial_days} days",
        period=horizon_str,
        horizon=horizon_str,
        parallel="processes"
    )
    df_perf = performance_metrics(df_cv)

    # Save full tables
    df_perf.to_csv('defect_rate_performance_metrics.csv', index=False)
    df_cv.to_csv('defect_rate_backtest.csv', index=False)

    # Extract the row matching our horizon
    perf_row = df_perf[df_perf.horizon == df_perf.horizon.max()].iloc[0]
    mape     = perf_row.mape * 100
    rmse     = perf_row.rmse
    coverage = perf_row.coverage * 100

    print("\n=== Back-test Results ===")
    print(f"MAPE:     {mape:.2f}%")
    print(f"RMSE:     {rmse:.4f}")
    print(f"Coverage: {coverage:.2f}%\n")

def make_forecast(model, periods=30):
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    out = forecast[['ds','yhat','yhat_lower','yhat_upper']].copy()
    out.columns = ['Date','Forecast','Lower_CI','Upper_CI']
    out.to_csv('defect_rate_forecast.csv', index=False)
    return out

def main():
    db_url = os.getenv('DB_URL', 'mysql+pymysql://root:123@localhost/asteel')
    print("Loading daily defect rate…")
    df = load_daily_defect_rate(db_url)
    print(f"Loaded {len(df)} days of data\n")

    print("Training Prophet model…")
    model = train_forecaster(df)

    # Pick a safe horizon: no more than half your history minus 1
    desired = 30
    max_horizon = max(1, len(df)//2 - 1)
    horizon = min(desired, max_horizon)
    print(f"→ Using horizon = {horizon} days (of max possible {max_horizon})\n")

    print("Evaluating model with back-test…")
    evaluate_model(model, df, horizon_days=horizon)

    print("Forecasting next 30 days…")
    make_forecast(model, periods=30)

    joblib.dump(model, 'prophet_defect_rate.joblib')
    print("✅ Files written:")
    print("   • defect_rate_forecast.csv")
    print("   • defect_rate_performance_metrics.csv")
    print("   • defect_rate_backtest.csv")
    print("   • prophet_defect_rate.joblib")

if __name__ == '__main__':
    main()
