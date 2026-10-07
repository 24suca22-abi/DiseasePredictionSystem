# 🩺 Care Nova | Intelligent AI Clinical Health Platform

An end-to-end intelligent healthcare web platform powered by Machine Learning and Flask. Care Nova evaluates patient symptoms, computes disease probabilities, recommends appropriate medical specialist departments, estimates diagnostic healthcare costs, and maps nearby medical facilities.

---

## 🌟 Key Features

1. **AI-Powered Disease Prediction**
   - Trained on 25 primary clinical symptoms using a **Random Forest Classifier**.
   - Outputs probable diagnosis with statistical confidence scores.
   - Categorized and searchable symptom selection interface.

2. **Specialist Doctor Referral**
   - Automatically maps diagnosed conditions to appropriate clinical departments (Neurologist, Pulmonologist, Cardiologist, Gastroenterologist, Dermatologist, etc.).
   - Integrated GPS locator and Google Maps directory integration to find certified specialists nearby.

3. **Medical Billing & Diagnostic Cost Estimation**
   - Transparent itemized cost estimation slip for doctor consultation fees and disease-specific laboratory investigations (e.g., Blood Sugar, ECG, MRI, X-Ray, CBC).
   - Clean, print-ready medical invoice layout with PDF export compatibility.

4. **User Authentication & Session Management**
   - Secure registration and login workflow backed by SQLite.
   - Session tracking with real-time UI status and flash message notifications.
   - Backward-compatible authentication with password hashing.

---

## 📁 Project Architecture

```text
DiseasePredictionSystem/
│
├── app.py                      # Core Flask application, routing, and controller logic
├── database.db                 # SQLite database storing registered user credentials
├── requirements.txt            # Python environment dependencies
├── Procfile                    # Production WSGI process declaration for deployment
├── README.md                   # System documentation and setup guide
│
├── model/                      # Machine Learning pipeline
│   ├── disease_dataset.csv     # Multi-symptom clinical training dataset (60 samples, 25 symptoms)
│   ├── disease_model.pkl       # Serialized Random Forest machine learning model
│   ├── train_model.py          # Training and model evaluation script
│   └── predict.py              # Interactive CLI prediction tool
│
├── static/                     # Web assets
│   ├── css/
│   │   └── style.css           # Healthcare design system & print stylesheet
│   └── js/
│       └── main.js             # Interactive search filter, counters, and GPS locator
│
└── templates/                  # Jinja2 HTML templates
    ├── base.html               # Master layout with responsive navbar, flash alerts & footer
    ├── index.html              # Landing page with system overview and workflow
    ├── login.html              # User login authentication card
    ├── register.html           # User account registration card
    ├── disease_prediction.html # Categorized symptom selection form with live filter
    ├── result.html             # Diagnostic outcome dashboard with confidence meter
    ├── specialist.html         # Medical specialist referral & GPS map lookup
    ├── nearby_specialist.html  # Location search for medical specialists
    └── billing.html            # Itemized clinical diagnostic estimate invoice
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- Python 3.8 or higher installed on your system.

### 2. Clone / Open Directory
```bash
cd c:\Users\ELCOT\Desktop\DiseasePredictionSystem
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. (Optional) Re-train the Machine Learning Model
To inspect dataset metrics and regenerate `disease_model.pkl`:
```bash
python model/train_model.py
```

### 5. Launch the Web Application
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000/
```

---

## 🧪 CLI Diagnostic Tool
You can also run a quick command-line prediction without launching the web server:
```bash
python model/predict.py
```

---

## 🩺 Supported Conditions & Clinical Specialties

The system analyzes symptoms against the following clinical conditions:
- **Cardiology:** Hypertension, Heart Disease
- **Pulmonology:** Asthma, Pneumonia, Tuberculosis, COVID-19
- **Neurology:** Migraine
- **Gastroenterology:** Food Poisoning, Typhoid
- **Endocrinology:** Diabetes
- **Dermatology:** Skin Allergy, Acne
- **Rheumatology / Orthopedics:** Arthritis, Joint Pain, Back Pain
- **Infectious Diseases / General Medicine:** Dengue, Malaria, Flu, Common Cold, Strep Throat

---

## 🛡️ Medical Disclaimer
This software utilizes statistical machine learning for preliminary health analysis and educational purposes only. It is not intended to serve as clinical advice or replace direct evaluation by licensed medical professionals. In medical emergencies, immediately contact your local emergency services or visit the nearest hospital.
