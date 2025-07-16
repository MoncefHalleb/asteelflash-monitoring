import os
from sqlalchemy import create_engine, text
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:123@localhost/asteel")

def load_data():
    engine = create_engine(DATABASE_URL)
    query = text("""
        SELECT
            CAST(b.Id AS UNSIGNED) AS id,
            COALESCE(b.REF_AsteelFlash, '') AS ref_asteel,
            COALESCE(f.Nom_Famille, '')      AS family_name,
            COALESCE(b.prix, 0)             AS prix
        FROM abb_dbo_board b
        LEFT JOIN abb_dbo_famille f
            ON CAST(b.Id_Famille AS SIGNED) = f.Id
    """)
    df = pd.read_sql(query, engine)qua
    return df

def preprocess(df):
    # One-hot encode 'ref_asteel' and 'family_name'
    df = pd.get_dummies(df, columns=['ref_asteel', 'family_name'], drop_first=True)
    X = df.drop(columns=['id', 'prix'])
    y = df['prix']
    return X, y

def train_and_evaluate(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                        test_size=0.2,
                                                        random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    rmse = mean_squared_error(y_test, preds, squared=False)
    r2 = r2_score(y_test, preds)
    print(f"RMSE: {rmse:.3f}")
    print(f"R²: {r2:.3f}")
    return model

def main():
    df = load_data()
    X, y = preprocess(df)
    model = train_and_evaluate(X, y)
    # Save the trained model
    joblib.dump(model, "model_rf_prix.joblib")
    print("Model saved as model_rf_prix.joblib")

if __name__ == "__main__":
    main()
