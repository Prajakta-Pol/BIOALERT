
# 🏥 BioMediAlert

BioMediAlert is a secure emergency medical data access system that allows authorized doctors to retrieve patient medical records during critical situations. The system integrates blockchain technology to ensure data integrity and transparency.

---

## 🚀 Problem Statement

During medical emergencies (accidents, unconscious patients, critical conditions), doctors often lack immediate access to a patient's medical history. This delay can be life-threatening.

BioMediAlert solves this by providing:
- Secure emergency access
- Blockchain-verified records
- Email notifications to patients
- Access logging for transparency

---

## 🔐 Key Features

- 👨‍⚕️ Doctor Login & Dashboard
- 🔎 Search Patient by:
  - Aadhaar Number
  - PAN Card
  - Emergency ID
  - Driving License
- ⛓ Blockchain Verification (Ganache + Web3.py)
- 📧 Automatic Email Alerts to Patients
- 🧾 Access Logs Tracking
- 🔒 Secure Emergency Reason Validation

---

## 🛠 Tech Stack

### Frontend
- HTML
- Tailwind CSS
- JavaScript

### Backend
- Flask (Python)
- SQLite
- Flask-Mail
- Web3.py

### Blockchain
- Solidity Smart Contract
- Ganache (Local Ethereum Network)

---

##  How It Works

1. Doctor logs into the dashboard.
2. Doctor searches patient using ID and selects emergency reason.
3. System verifies access.
4. Patient data is retrieved.
5. Access event is:
   - Logged in database
   - Recorded on blockchain
   - Email notification sent to patient

---

## 📦 Installation Guide

### 1️⃣ Clone Repository
```bash
git clone https://github.com/yourusername/BioMediAlert.git
cd BioMediAlert