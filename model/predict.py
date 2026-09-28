import pandas as pd
import pickle

# Load dataset
data = pd.read_csv("disease_dataset.csv")

# Get symptom names
symptoms = list(data.drop("disease", axis=1).columns)

# Load trained model
with open("disease_model.pkl", "rb") as file:
    model = pickle.load(file)

print("\nAvailable Symptoms:")
for i, symptom in enumerate(symptoms, start=1):
    print(i, "-", symptom)

# Get symptoms from user
choice1 = int(input("\nEnter first symptom number: "))
choice2 = int(input("Enter second symptom number: "))
choice3 = int(input("Enter third symptom number: "))

# Create input with all symptoms as 0
input_data = [0] * len(symptoms)

# Set selected symptoms as 1
input_data[choice1 - 1] = 1
input_data[choice2 - 1] = 1
input_data[choice3 - 1] = 1

# Convert into DataFrame
input_df = pd.DataFrame([input_data], columns=symptoms)

# Predict disease
prediction = model.predict(input_df)[0]

# Get confidence score
probabilities = model.predict_proba(input_df)[0]
confidence = max(probabilities) * 100

print("\n--------------------------------")
print("Predicted Disease :", prediction)
print("Confidence Score  :", round(confidence, 2), "%")
print("--------------------------------")