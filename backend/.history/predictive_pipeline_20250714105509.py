
import os
import joblib
import pandas as pd
from sqlalchemy import create_engine, text
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# --- Configuration ---
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:123@localhost/asteel")
MODEL_PATH = "model_rf_prix.joblib"

# --- Data Extraction ---
engine = create_engine(DATABASE_URL)
query = text(\"\"\"
SELECT
  b.Id AS id,
  b.REF_AsteelFlash AS ref_asteel,
  b.REF_Clients AS ref_client,
  b.Designation AS designation,
  b.Client AS client,
  b.Board_Ver AS board_version,
  b.Code_Indus AS code_indus,
  b.Indice AS indice,
  b.Software AS software,
  b.Software_Ver AS software_ver,
  b.Valide AS is_valid,
  b.Id_Assembly AS id_assembly,
  b.Id_Process AS id_process,
  b.QuantCondit AS quantcondit,
  f.Nom_Famille AS family_name,
  b.prix AS prix
FROM abb_dbo_board b
LEFT JOIN abb_dbo_famille f
  ON b.Id_Famille = f.Id
WHERE b.prix IS NOT NULL
\"\"\")
df = pd.read_sql(query, engine)

# --- Preprocessing ---
# Drop any rows with missing target
df = df.dropna(subset=["prix"])

# Define features and target
X = df.drop(columns=["id", "prix"])
y = df["prix"]

# Identify numeric and categorical columns
numeric_features = ["id_assembly", "id_process", "quantcondit"]
categorical_features = [
    "ref_asteel","ref_client","designation","client",
    "board_version","code_indus","indice","software",
    "software_ver","family_name"
]

# Build preprocessing pipeline
numeric_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])
categorical_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="constant", fill_value="")),
    ("onehot", OneHotEncoder(handle_unknown="ignore", sparse=False))
])

preprocessor = ColumnTransformer(transformers=[
    ("num", numeric_transformer, numeric_features),
    ("cat", categorical_transformer, categorical_features)
])

# Combine into full pipeline
model_pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("regressor", RandomForestRegressor(n_estimators=100, random_state=42))
])

# --- Train/Test Split ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# --- Training ---
model_pipeline.fit(X_train, y_train)

# --- Evaluation ---
y_pred = model_pipeline.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"Test MSE: {mse:.2f}")
print(f"Test R^2: {r2:.2f}")

# --- Save Model ---
joblib.dump(model_pipeline, MODEL_PATH)
print(f"Model saved to {MODEL_PATH}")
