import os
import pandas as pd
from sqlalchemy import create_engine, text
from prophet import Prophet
import joblib
from prophet.diagnostics import cross_validation, performance_metrics

def load_daily_defect_rate(db_url):
    engine = create_engine(db_url)
    # Aggregate daily counts of fails (Result=0) and totals
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
    df = df.dropna(subset=['defect_rate'])
    return df

def train_forecaster(df):
    # Prophet expects columns ds (date) and y (value)
    df = df.rename(columns={'defect_rate': 'y'})
    m = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=False
    )
    m.fit(df)
    return m

def make_forecast(model, periods=30):
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

def evaluate_model(model, df, horizon_days=8):
    """
    Evaluate the model using back-testing.
    """
    print(f"Running back-test: horizon={horizon_days} days")
    
    # Cross-validation settings: make sure 'initial' + 'horizon' does not exceed data length
    initial_days = horizon_days * 2
    if len(df) < (initial_days + horizon_days):
        print(f"⚠️ Skipping back-test: need at least {initial_days + horizon_days} days (you have {len(df)}).")
        return None, None
    
    df_cv = cross_validation(
        model,
        initial=f"{initial_days} days",
        horizon=f"{horizon_days} days",
        period="1 day"
    )
    
    df_performance = performance_metrics(df_cv)
    df_cv.to_csv('defect_rate_backtest.csv', index=False)
    df_performance.to_csv('defect_rate_performance_metrics.csv', index=False)
    return df_cv, df_performance

def main():
    # Update this connection string as needed
    db_url = os.getenv('DB_URL', 'mysql+pymysql://root:123@localhost/asteel')
    print("Loading daily defect rate...")
    df = load_daily_defect_rate(db_url) 
    print(f"Loaded {len(df)} days of data")

    print("Training Prophet model...")
    model = train_forecaster(df)

    print("Forecasting next 30 days...")
    forecast = make_forecast(model, periods=30)

    # Save model and forecast
    joblib.dump(model, 'prophet_defect_rate.joblib')
    forecast.to_csv('defect_rate_forecast.csv', index=False)

    print("Saved model -> prophet_defect_rate.joblib")
    print("Saved forecast -> defect_rate_forecast.csv")

    # Evaluate the model with back-test (only if we have enough data)
    horizon_days = 8  # Modify as needed
    print("Evaluating model with back-test...")
    df_cv, df_performance = evaluate_model(model, df, horizon_days=horizon_days)

    if df_cv is not None and df_performance is not None:
        print("Back-test results saved.")
    else:
        print("Skipping back-test due to insufficient data.")

if __name__ == '__main__':
    main()
