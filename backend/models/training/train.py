import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import lightgbm as lgb
import joblib
from pathlib import Path
import matplotlib.pyplot as plt

PROCESSED_CSV = Path(__file__).resolve().parents[2] / "data" / "processed" / "energy_features.csv"
MODELS_DIR = Path(__file__).resolve().parents[2] / "models"

def load_and_prepare_data():
    df = pd.read_csv(PROCESSED_CSV, index_col='timestamp', parse_dates=True)
    
    # Features and target
    feature_cols = [col for col in df.columns if col not in ['Total_Consumption', 'timestamp']]
    X = df[feature_cols]
    y = df['Total_Consumption']
    
    return X, y, df

def train_random_forest(X_train, y_train):
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    return model

def train_xgboost(X_train, y_train):
    model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    return model

def train_lightgbm(X_train, y_train):
    model = lgb.LGBMRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test, model_name):
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"\n{model_name} Performance:")
    print(f"RMSE: {rmse:.4f}")
    print(f"MAE: {mae:.4f}")
    print(f"R²: {r2:.4f}")
    
    return {'rmse': rmse, 'mae': mae, 'r2': r2}

def save_model(model, model_name):
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODELS_DIR / f"{model_name}.pkl")
    print(f"Saved {model_name} to {MODELS_DIR / f'{model_name}.pkl'}")

def main():
    print("Loading data...")
    X, y, df = load_and_prepare_data()
    
    # Time series split
    tscv = TimeSeriesSplit(n_splits=5)
    
    # Split into train/test (last 20% for test)
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    print(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples")
    
    models = {}
    performances = {}
    
    # Train Random Forest
    print("\nTraining Random Forest...")
    rf_model = train_random_forest(X_train, y_train)
    models['random_forest'] = rf_model
    performances['random_forest'] = evaluate_model(rf_model, X_test, y_test, "Random Forest")
    
    # Train XGBoost
    print("\nTraining XGBoost...")
    xgb_model = train_xgboost(X_train, y_train)
    models['xgboost'] = xgb_model
    performances['xgboost'] = evaluate_model(xgb_model, X_test, y_test, "XGBoost")
    
    # Train LightGBM
    print("\nTraining LightGBM...")
    lgb_model = train_lightgbm(X_train, y_train)
    models['lightgbm'] = lgb_model
    performances['lightgbm'] = evaluate_model(lgb_model, X_test, y_test, "LightGBM")
    
    # Save all models
    for name, model in models.items():
        save_model(model, name)
    
    # Save the best model as energy_model.pkl for backward compatibility
    best_model = min(performances, key=lambda x: performances[x]['rmse'])
    save_model(models[best_model], "energy_model")
    print(f"\nBest model ({best_model}) saved as energy_model.pkl")
    
    # Save performances
    joblib.dump(performances, MODELS_DIR / "model_performances.pkl")
    
    # Feature importance for Random Forest
    if hasattr(rf_model, 'feature_importances_'):
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': rf_model.feature_importances_
        }).sort_values('importance', ascending=False)
        print("\nTop 10 Feature Importances (Random Forest):")
        print(feature_importance.head(10))
        
        # Save feature importance
        feature_importance.to_csv(MODELS_DIR / "feature_importance.csv", index=False)

if __name__ == "__main__":
    main()
