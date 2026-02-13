import os
import pandas as pd
import json
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Load dataset
url = "https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv"
df = pd.read_csv(url, sep=";")

# Features and target
X = df.drop("quality", axis=1)
y = df["quality"]

# Train test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestRegressor(n_estimators=10, random_state=42)
model.fit(X_train, y_train)

# Predictions
pred = model.predict(X_test)

# Metrics
mse = mean_squared_error(y_test, pred)
r2 = r2_score(y_test, pred)

# Create artifacts directory
os.makedirs("app/artifacts", exist_ok=True)

# Save model
joblib.dump(model, "app/artifacts/model.pkl")

# Save metrics (important: accuracy key for Jenkins)
with open("app/artifacts/metrics.json", "w") as f:
    json.dump(
        {
            "accuracy": float(r2),
            "mse": float(mse)
        },
        f,
        indent=2
    )

print("Training complete")
print("MSE:", mse)
print("R2:", r2)
