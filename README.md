# 🏥 Centralized Patient Record Management System

## 📘 Overview
This Django-based system provides a **secure, Aadhaar-linked, and consent-driven** digital platform for managing patient health records.

Patients can:
- Authenticate via **Aadhaar OTP** or **QR login**
- **Upload and manage medical records**
- **Group** records by hospital visit or event (e.g., *Manipal May 2025*)
- **View and download** past records anytime

Hospitals or authorized users can:
- Request access (in future versions)
- Manage patient data securely under consent-based flow

---

## ⚙️ Features
✅ Aadhaar-based OTP authentication (Twilio or local dummy)  
✅ QR code–based Aadhaar login (offline mode)  
✅ Secure patient file uploads  
✅ Record grouping, search & filtering  
✅ Persistent login with secure `remember_token`  
✅ Modular Django apps: `accounts`, `patients`, `hospitals`, `core`  
✅ Fully responsive and modern UI (HTML/CSS templates)  

---

## 🧩 Project Structure
```
patient_record_system/
│
├── accounts/
│   ├── aadhaar_provider.py
│   ├── aadhar_data.json
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── templates/accounts/
│
├── patients/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── templates/patients/
│
├── core/
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   └── templates/core/
│
├── templates/
│   ├── base.html
│   └── patients/
│
├── media/ (uploads)
├── db.sqlite3
├── manage.py
├── requirements.txt
└── README.md
```

---

## 💻 Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/yourusername/patient_record_system.git
cd patient_record_system
```

### 2️⃣ Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # (Windows)
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Apply migrations
```bash
python manage.py migrate
```

### 5️⃣ Run the development server
```bash
python manage.py runserver
```

---

## 📲 Aadhaar OTP Setup

### 🔹 Option 1: Dummy JSON (for local testing)
You can add new Aadhaar numbers and phone mappings in:
```
accounts/aadhar_data.json
```
Example:
```json
{
  "111122223333": { "mobile": "+911234567890", "name": "Demo User", "dob": "1990-01-01" }
}
```

### 🔹 Option 2: Real Twilio API
Edit credentials in:
```
accounts/aadhaar_provider.py
```
Replace:
```python
TWILIO_ACCOUNT_SID = "your_account_sid"
TWILIO_AUTH_TOKEN = "your_auth_token"
TWILIO_FROM_NUMBER = "+1XXXXXXXXXX"
```

---

## 🔐 Authentication Flows

| Login Type | Description |
|-------------|--------------|
| **Aadhaar OTP** | Sends OTP to registered number from `aadhar_data.json` or Twilio |
| **QR Login** | Scans and verifies Aadhaar QR offline |
| **Admin Login** | Traditional username/password login |

---

## 📂 Uploads
Uploaded files are stored under:
```
/media/patient_files/<patient_id>/
```
Each file is timestamped to ensure unique names.

---

## 🚀 Future Enhancements
- Secure patient-to-hospital data sharing with consent
- EHR standardization (FHIR/JSON)
- End-to-end encryption of uploaded files
- Doctor dashboard and analytics
- Blockchain-based audit trails

---

## 👨‍💻 Contributors
- **Sindhu KP**
- **Sampreetha**
- **B Samarth**

---

## 🧠 License
This project is developed for educational & research purposes.
