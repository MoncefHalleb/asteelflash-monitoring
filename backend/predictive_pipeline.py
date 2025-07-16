import os
from sqlalchemy import create_engine, text
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:123@localhost/asteel")


def load_data(connection_string: str) -> pd.DataFrame:
    """
    Connect to the database and load board pricing data
    including the family name via a LEFT JOIN.
    """
    engine = create_engine(connection_string)
    with engine.connect() as conn:
        query = text("""
            SELECT
                CAST(b.Id AS UNSIGNED) AS id,
                COALESCE(b.REF_AsteelFlash, '') AS ref_asteel,
                COALESCE(f.Nom_Famille, '') AS family_name,
                COALESCE(b.prix, 0) AS prix
            FROM abb_dbo_board b
            LEFT JOIN abb_dbo_famille f
              ON b.Id_Famille = f.Id
        """)
        df = pd.read_sql(query, conn)
    return df

def preprocess(df: pd.DataFrame):
    """
    One-hot encode categorical features and separate target.
    """
    df = df.dropna(subset=['prix'])
    X = df[['ref_asteel', 'family_name']].astype(str)
    y = df['prix']
    X = pd.get_dummies(X, columns=['ref_asteel', 'family_name'], drop_first=True)
    return X, y

def train_and_evaluate(X, y):
    """
    Split the data, train a RandomForestRegressor,
    and report RMSE and R^2.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    rmse = mean_squared_error(y_test, preds) ** 0.5
    r2 = r2_score(y_test, preds)
    print(f"RMSE: {rmse:.3f}")
    print(f"R^2:  {r2:.3f}")
    return model

def main():
    # Update this connection string to match your environment:
    connection_string = "mysql+pymysql://root:123@localhost/asteel"
    print("Loading data...")
    df = load_data(connection_string)
    print(f"Loaded {len(df)} rows.")
    print("Preprocessing...")
    X, y = preprocess(df)
    print(f"Features: {X.shape[1]}, Samples: {X.shape[0]}")
    print("Training and evaluating model...")
    model = train_and_evaluate(X, y)
    print("Saving model to 'model_rf_prix.joblib'...")
    joblib.dump(model, "model_rf_prix.joblib")
    print("Done.")

if __name__ == "__main__":
    main()
