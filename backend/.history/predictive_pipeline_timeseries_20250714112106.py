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
    df = pd.read_sql(sql, engine)
    # drop any days where rate is null (e.g. zero total)
    return df.dropna(subset=['defect_rate'])

def train_forecaster(df):
    df = df.rename(columns={'defect_rate': 'y'})
    m = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=False
    )
    m.fit(df)
    return m

def evaluate_model(model, df):
    # rolling‐window backtest: train on first year, test next 30d, step every 6m
    df_cv = cross_validation(
        model,
        initial='365 days',
        period='180 days',
        horizon='30 days',
        parallel='processes'
    )
    df_perf = performance_metrics(df_cv)
    # save full table of metrics
    df_perf.to_csv('defect_rate_performance_metrics.csv', index=False)
    # pick the row where horizon ≈ 30 days
    last = df_perf[df_perf.horizon == df_perf.horizon.max()]
    print("\n=== 30-day horizon performance ===")
    print(f"MAPE: {last.mape.values[0]*100:.2f}%")
    print(f"RMSE: {last.rmse.values[0]:.4f}")
    print(f"Coverage: {last.coverage.values[0]*100:.2f}%\n")

def make_forecast(model, periods=30):
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    # only keep the relevant columns and rename for clarity
    out = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
    out.columns = ['Date', 'Forecast', 'Lower_CI', 'Upper_CI']
    return out

def main():
    db_url = os.getenv('DB_URL', 'mysql+pymysql://root:123@localhost/asteel')
    print("Loading daily defect rate...")
    df = load_daily_defect_rate(db_url)
    print(f"Loaded {len(df)} days of data")

    print("Training Prophet model...")
    model = train_forecaster(df)

    print("Evaluating model with back-test…")
    evaluate_model(model, df)

    print("Forecasting next 30 days…")
    forecast = make_forecast(model, periods=30)

    # save model and CSVs
    joblib.dump(model, 'prophet_defect_rate.joblib')
    forecast.to_csv('defect_rate_forecast.csv', index=False)

    print("Saved model -> prophet_defect_rate.joblib")
    print("Saved forecast -> defect_rate_forecast.csv")
    print("Saved performance metrics -> defect_rate_performance_metrics.csv")

if __name__ == '__main__':
    main()
