import datetime
import os
import pickle
import sqlite3
import urllib.parse
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
import pandas as pd
from werkzeug.security import check_password_hash, generate_password_hash

# ---------------- APPLICATION CONFIGURATION ----------------

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "carenova-clinical-security-key-2026")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
MODEL_PATH = os.path.join(BASE_DIR, "model", "disease_model.pkl")
DATASET_PATH = os.path.join(BASE_DIR, "model", "disease_dataset.csv")

# ---------------- DATABASE INITIALIZATION & HELPERS ----------------


def get_db_connection():
    """Create a database connection with row factory for clean dict-like access."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def create_database():
    """Ensure the user authentication table exists."""
    connection = get_db_connection()
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


# ---------------- MODEL & METADATA PRELOADING ----------------

try:
    _dataset = pd.read_csv(DATASET_PATH)
    SYMPTOMS_LIST = list(_dataset.drop("disease", axis=1).columns)
except Exception:
    SYMPTOMS_LIST = [
        "fever", "cough", "headache", "fatigue", "sore_throat", "runny_nose",
        "body_pain", "nausea", "vomiting", "diarrhea", "chills", "abdominal_pain",
        "chest_pain", "shortness_of_breath", "wheezing", "skin_rash", "itching",
        "frequent_urination", "excessive_thirst", "joint_pain", "back_pain",
        "dizziness", "loss_of_taste", "loss_of_smell", "nasal_congestion"
    ]

try:
    with open(MODEL_PATH, "rb") as _f:
        MODEL = pickle.load(_f)
except Exception:
    MODEL = None


# ---------------- TEMPLATE CONTEXT PROCESSOR ----------------

@app.context_processor
def inject_user_context():
    """Make user authentication status available to all templates."""
    return {
        "current_user": session.get("username"),
        "user_fullname": session.get("fullname"),
        "is_authenticated": "username" in session,
    }


# ---------------- HOME ROUTE ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- LOGIN ROUTE ----------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        user = cursor.fetchone()
        connection.close()

        # Support both legacy plaintext passwords and hashed passwords
        if user:
            stored_password = user["password"]
            password_matches = (
                stored_password == password or
                check_password_hash(stored_password, password)
            )

            if password_matches:
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                session["fullname"] = user["fullname"]
                flash(f"Welcome back, {user['fullname']}!", "success")
                return redirect(url_for("disease_prediction"))

        flash("Invalid username or password! Please check your credentials.", "danger")
        return render_template("login.html")

    return render_template("login.html")


# ---------------- REGISTER ROUTE ----------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not fullname or not username or not email or not password:
            flash("All fields are required. Please fill in the registration form.", "warning")
            return render_template("register.html")

        connection = get_db_connection()
        cursor = connection.cursor()

        # Check for existing username or email
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            connection.close()
            flash("Username already exists! Please choose a unique username.", "warning")
            return render_template("register.html")

        hashed_password = generate_password_hash(password)

        try:
            cursor.execute(
                "INSERT INTO users (fullname, username, email, password) VALUES (?, ?, ?, ?)",
                (fullname, username, email, hashed_password)
            )
            connection.commit()
            connection.close()
            flash("Registration successful! You may now sign in.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            connection.close()
            flash("An error occurred during registration. Please try again.", "danger")
            return render_template("register.html")

    return render_template("register.html")


# ---------------- LOGOUT ROUTE ----------------

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for("login"))


# ---------------- DISEASE PREDICTION PAGE ----------------

@app.route("/disease_prediction")
def disease_prediction():
    return render_template("disease_prediction.html")


# ---------------- DISEASE PREDICTION PROCESSOR ----------------

@app.route("/predict", methods=["POST"])
def predict():
    selected_symptoms = request.form.getlist("symptoms")

    if not selected_symptoms:
        flash("Please select at least one symptom before requesting a prediction.", "warning")
        return redirect(url_for("disease_prediction"))

    # Load symptoms list from dataset
    symptoms = SYMPTOMS_LIST

    input_data = [0] * len(symptoms)

    for symptom in selected_symptoms:
        if symptom in symptoms:
            input_data[symptoms.index(symptom)] = 1

    input_df = pd.DataFrame([input_data], columns=symptoms)

    global MODEL
    if MODEL is None:
        with open(MODEL_PATH, "rb") as file:
            MODEL = pickle.load(file)

    prediction = MODEL.predict(input_df)[0]
    probabilities = MODEL.predict_proba(input_df)[0]
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
        "Tuberculosis": "Pulmonologist",
        # Comprehensive mappings for dataset classes
        "Flu": "General Physician",
        "Dengue": "Infectious Disease Specialist",
        "Malaria": "General Physician",
        "COVID-19": "Pulmonologist",
        "Strep Throat": "ENT Specialist",
    }

    specialist = specialist_map.get(prediction, "General Physician")

    # ---------------- RESULT PAGE ----------------
    return render_template(
        "result.html",
        disease=prediction,
        confidence=round(confidence, 2),
        specialist=specialist,
        selected_symptoms=selected_symptoms
    )


# ---------------- FIND NEARBY SPECIALIST ----------------

@app.route("/find_specialist")
def find_specialist():
    location = request.args.get("location")
    specialist = request.args.get("specialist", "General Physician")

    if location:
        search_text = f"{specialist} near {location}"
        maps_url = (
            "https://www.google.com/maps/search/?api=1&query="
            + urllib.parse.quote(search_text)
        )
        return redirect(maps_url)

    return render_template(
        "nearby_specialist.html",
        specialist=specialist
    )


# ---------------- SPECIALIST PAGE DIRECT ROUTE ----------------

@app.route("/specialist")
def specialist():
    disease = request.args.get("disease", "General Assessment")
    confidence = request.args.get("confidence", "95.0")
    specialist_role = request.args.get("specialist", "General Physician")

    return render_template(
        "specialist.html",
        disease=disease,
        confidence=confidence,
        specialist=specialist_role
    )


# ---------------- MEDICAL BILLING ----------------

@app.route("/billing")
def billing():
    disease = request.args.get("disease", "General Assessment")
    specialist = request.args.get("specialist", "General Physician")

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
        ],
        "Malaria": [
            ("Malaria Antigen Test", 250),
            ("Complete Blood Count (CBC)", 300)
        ],
        "Typhoid": [
            ("Widal Test", 250),
            ("Typhoid Rapid Test", 400)
        ],
        "COVID-19": [
            ("RT-PCR Test", 500),
            ("C-Reactive Protein (CRP)", 350)
        ],
        "Flu": [
            ("Influenza Rapid Antigen Test", 500),
            ("Complete Blood Count (CBC)", 300)
        ],
        "Common Cold": [
            ("Clinical Physical Examination", 250),
            ("Viral Screening Test", 300)
        ],
        "Strep Throat": [
            ("Rapid Throat Antigen", 350),
            ("Throat Culture Test", 400)
        ],
        "Hypertension": [
            ("Lipid Profile Test", 500),
            ("Kidney Function Test (KFT)", 600)
        ],
        "Skin Allergy": [
            ("Total IgE Allergy Test", 800),
            ("Skin Prick Allergy Test", 1000)
        ],
        "Acne": [
            ("Dermatological Skin Assessment", 350),
            ("Hormonal Screening Test", 650)
        ],
        "Joint Pain": [
            ("Joint X-Ray", 500),
            ("Serum Uric Acid Test", 250)
        ],
        "Back Pain": [
            ("Spine X-Ray", 600),
            ("MRI Lumbar Spine", 3000)
        ]
    }

    lab_tests = lab_test_map.get(
        disease,
        [
            ("Basic Blood Test", 250),
            ("Doctor Recommended Test", 300)
        ]
    )

    total = consultation + sum(price for _, price in lab_tests)

    # Dynamic invoice metadata for professional billing sheet
    now = datetime.datetime.now()
    invoice_id = f"{now.strftime('%Y%m%d')}-{abs(hash(disease)) % 9000 + 1000}"
    current_date = now.strftime("%B %d, %Y")

    return render_template(
        "billing.html",
        disease=disease,
        specialist=specialist,
        consultation=consultation,
        lab_tests=lab_tests,
        total=total,
        invoice_id=invoice_id,
        current_date=current_date
    )


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    create_database()
    app.run(debug=True)