from flask import Flask, render_template, request, redirect
import sqlite3
import pickle
import pandas as pd
import urllib.parse


app = Flask(__name__)


def create_database():
    connection = sqlite3.connect("database.db")

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("disease.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        )

        user = cursor.fetchone()

        connection.close()

        if user:
            return redirect("/disease_prediction")

        else:
            return "Invalid username or password!"

    return render_template("login.html")


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        fullname = request.form["fullname"]
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return "Passwords do not match!"

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()

        try:
            cursor.execute("""
                INSERT INTO users
                (fullname, username, email, password)
                VALUES (?, ?, ?, ?)
            """, (fullname, username, email, password))

            connection.commit()

        except sqlite3.IntegrityError:
            connection.close()
            return "Username already exists!"

        connection.close()

        return redirect("/login")

    return render_template("register.html")


# ---------------- DISEASE PREDICTION PAGE ----------------


@app.route("/disease_prediction")
def disease_prediction():
    return render_template("disease_prediction.html")


# ---------------- DISEASE PREDICTION ----------------

@app.route("/predict", methods=["POST"])
def predict():

    selected_symptoms = request.form.getlist("symptoms")

    data = pd.read_csv("model/disease_dataset.csv")

    symptoms = list(data.drop("disease", axis=1).columns)

    input_data = [0] * len(symptoms)

    for symptom in selected_symptoms:

        if symptom in symptoms:
            input_data[symptoms.index(symptom)] = 1

    input_df = pd.DataFrame(
        [input_data],
        columns=symptoms
    )

    with open("model/disease_model.pkl", "rb") as file:
        model = pickle.load(file)

    prediction = model.predict(input_df)[0]

    probabilities = model.predict_proba(input_df)[0]

    confidence = max(probabilities) * 100


    # ---------------- SPECIALIST RECOMMENDATION ----------------

    specialist_map = {

        "Migraine": "Neurologist",

        "Food Poisoning": "Gastroenterologist",

        "Typhoid": "General Physician",

        "Stomach Pain": "Gastroenterologist",

        "Body Pain": "General Physician",

        "Fever": "General Physician",

        "Common Cold": "General Physician",

        "Allergy": "Allergist",

        "Asthma": "Pulmonologist",

        "Diabetes": "Endocrinologist",

        "Hypertension": "Cardiologist",

        "Heart Disease": "Cardiologist",

        "Skin Allergy": "Dermatologist",

        "Acne": "Dermatologist",

        "Arthritis": "Rheumatologist",

        "Joint Pain": "Orthopedic Doctor",

        "Back Pain": "Orthopedic Doctor",

        "Pneumonia": "Pulmonologist",

        "Tuberculosis": "Pulmonologist"

    }


    specialist = specialist_map.get(
        prediction,
        "General Physician"
    )


    # ---------------- RESULT PAGE ----------------

    return render_template(
        "result.html",
        disease=prediction,
        confidence=round(confidence, 2),
        specialist=specialist
    )


# ---------------- FIND NEARBY SPECIALIST ----------------

@app.route("/find_specialist")
def find_specialist():

    location = request.args.get("location")

    specialist = request.args.get(
        "specialist",
        "General Physician"
    )

    if location:

        search_text = specialist + " near " + location

        maps_url = (
            "https://www.google.com/maps/search/?api=1&query="
            + urllib.parse.quote(search_text)
        )

        return redirect(maps_url)

    return render_template(
        "nearby_specialist.html"
    )

# ---------------- MEDICAL BILLING ----------------

@app.route("/billing")
def billing():

    disease = request.args.get(
        "disease",
        "Unknown"
    )

    specialist = request.args.get(
        "specialist",
        "General Physician"
    )

    consultation = 500

    lab_test_map = {

        "Heart Disease": [
            ("ECG", 500),
            ("Echocardiogram (ECHO)", 1500),
            ("CT Scan", 2500)
        ],

        "Migraine": [
            ("MRI Brain", 3000),
            ("CT Brain", 2000)
        ],

        "Pneumonia": [
            ("Chest X-Ray", 500),
            ("CT Chest", 2500)
        ],

        "Arthritis": [
            ("X-Ray", 500),
            ("MRI Joint", 3000)
        ],

        "Dengue": [
            ("Dengue NS1 Test", 400),
            ("CBC", 300)
        ],

        "Food Poisoning": [
            ("Stool Test", 300),
            ("Ultrasound Abdomen", 1000)
        ],

        "Diabetes": [
            ("Blood Sugar Test", 150),
            ("HbA1c Test", 400)
        ],

        "Tuberculosis": [
            ("Chest X-Ray", 500),
            ("Sputum Test", 300),
            ("CT Chest", 2500)
        ],

        "Asthma": [
            ("Chest X-Ray", 500),
            ("Pulmonary Function Test", 800)
        ]
    }

    lab_tests = lab_test_map.get(
        disease,
        [
            ("Basic Blood Test", 250),
            ("Doctor Recommended Test", 300)
        ]
    )

    total = consultation + sum(
        price for test, price in lab_tests
    )

    return render_template(
        "billing.html",
        disease=disease,
        specialist=specialist,
        consultation=consultation,
        lab_tests=lab_tests,
        total=total
    )
# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":

    create_database()

    app.run(debug=True)
    