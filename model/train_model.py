import os
import pickle
import warnings
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# Suppress minor scikit-learn warnings for cleaner CLI display
warnings.filterwarnings("ignore")

# Resolve paths dynamically relative to this script
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(CURRENT_DIR, "disease_dataset.csv")
MODEL_PATH = os.path.join(CURRENT_DIR, "disease_model.pkl")

# Load the dataset
data = pd.read_csv(DATASET_PATH)

# Separate symptoms and disease target
X = data.drop("disease", axis=1)
y = data["disease"]

print(f"Training dataset loaded: {X.shape[0]} samples with {X.shape[1]} symptom features.")
print(f"Distinct disease classes: {y.nunique()}")

# Split the data into training and testing
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.4,
    random_state=42
)

# Create the Random Forest model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# Train the model
model.fit(X_train, y_train)

# Test the model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("\n" + "=" * 50)
print(" MODEL TRAINING SUMMARY")
print("=" * 50)
print(f"Algorithm      : Random Forest Classifier (100 estimators)")
print(f"Test Accuracy  : {round(accuracy * 100, 2)}%")
print("=" * 50)

# Save the trained model
with open(MODEL_PATH, "wb") as file:
    pickle.dump(model, file)

print(f"\nModel serialized successfully to:\n  {MODEL_PATH}\n")