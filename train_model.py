"""
Train AQI Prediction Model
This script trains the XGBoost model using the dataset and saves both the model and scaler
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

# Load Dataset
print("Loading dataset...")
df = pd.read_csv("city_day.csv")

# Data Preprocessing
print("Preprocessing data...")

# Drop rows with missing AQI values
df = df.dropna(subset=['AQI'])

# Select features for training
features = ['PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'NH3', 'CO', 'SO2', 'O3', 'Benzene', 'Toluene', 'Xylene']

# Fill missing values with 0 for pollutants
for feature in features:
    df[feature] = df[feature].fillna(0)

# Prepare X and y
X = df[features]
y = df['AQI']

print(f"Dataset shape: {X.shape}")
print(f"Target shape: {y.shape}")

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale the features
print("Scaling features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train the model with best parameters
print("Training XGBoost model...")
model = XGBRegressor(
    objective='reg:squarederror',
    learning_rate=0.2,
    max_depth=5,
    n_estimators=100,
    random_state=42
)

model.fit(X_train_scaled, y_train)

# Evaluate the model
print("Evaluating model...")
y_pred = model.predict(X_test_scaled)

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print(f"\nModel Performance:")
print(f"MAE: {mae:.2f}")
print(f"RMSE: {rmse:.2f}")
print(f"R2 Score: {r2:.4f}")

# Save the model and scaler
print("\nSaving model and scaler...")
joblib.dump(model, "best_aqi_model.pkl")
joblib.dump(scaler, "scaler.pkl")

print("✅ Model and scaler saved successfully!")
print("\nFiles created:")
print("  - best_aqi_model.pkl")
print("  - scaler.pkl")

# Test prediction
print("\nTesting prediction with sample data...")
sample = X_test_scaled[:1]
prediction = model.predict(sample)[0]
actual = y_test.iloc[0]
print(f"Sample Prediction: {prediction:.2f}")
print(f"Actual Value: {actual:.2f}")
print(f"Difference: {abs(prediction - actual):.2f}")