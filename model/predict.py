import os
import pickle
import pandas as pd

# Resolve paths dynamically relative to this script
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(CURRENT_DIR, "disease_dataset.csv")
MODEL_PATH = os.path.join(CURRENT_DIR, "disease_model.pkl")

# Load dataset
data = pd.read_csv(DATASET_PATH)

# Get symptom names
symptoms = list(data.drop("disease", axis=1).columns)

# Load trained model
with open(MODEL_PATH, "rb") as file:
    model = pickle.load(file)

print("=" * 50)
print("     DISEASE PREDICTION SYSTEM - CLI CHECKER     ")
print("=" * 50)
print("\nAvailable Symptoms:")
for i, symptom in enumerate(symptoms, start=1):
    print(f"  {i:2d}. {symptom.replace('_', ' ').title()}")

print("\nEnter symptom indices to test (e.g. 1, 2, 3):")


def get_symptom_choice(prompt_text):
    while True:
        try:
            val = int(input(prompt_text))
            if 1 <= val <= len(symptoms):
                return val
            print(f"Please enter a number between 1 and {len(symptoms)}.")
        except ValueError:
            print("Invalid input. Please enter an integer.")


# Get symptoms from user
choice1 = get_symptom_choice("\nEnter first symptom number: ")
choice2 = get_symptom_choice("Enter second symptom number: ")
choice3 = get_symptom_choice("Enter third symptom number: ")

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

print("\n" + "=" * 50)
print(f" Predicted Disease : {prediction}")
print(f" Confidence Score  : {round(confidence, 2)}%")
print("=" * 50 + "\n")