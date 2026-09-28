import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle

# Load the dataset
data = pd.read_csv("disease_dataset.csv")

# Separate symptoms and disease
X = data.drop("disease", axis=1)
y = data["disease"]

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

print("Model trained successfully!")
print("Model Accuracy:", round(accuracy * 100, 2), "%")

# Save the trained model
with open("disease_model.pkl", "wb") as file:
    pickle.dump(model, file)

print("Disease prediction model saved successfully!")