import pandas as pd
from xgboost import XGBClassifier
import joblib

# Load dataset
data = pd.read_csv("data/flood_data.csv")

# Input features
X = data[["rainfall", "humidity", "river_level", "soil_moisture"]]

# Target
y = data["flood_risk"]

# Create model
model = XGBClassifier(
    n_estimators=100,
    max_depth=3,
    learning_rate=0.1,
    random_state=42
)

# Train model
model.fit(X, y)

# Save model
joblib.dump(model, "flood_model.pkl")

print("Flood prediction model trained successfully!")
print("Model saved as flood_model.pkl")