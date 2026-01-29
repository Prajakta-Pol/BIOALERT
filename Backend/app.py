import email
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import sqlite3
import os
import traceback
import bcrypt
from datetime import datetime, time
import re
import random
import string

from Blockchain import hash_data, store_hash_on_chain
from flask import send_from_directory

from web3 import Web3
import hashlib
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText


# ---------- APP SETUP ----------
app = Flask(__name__)

from flask_mail import Mail, Message

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'          # Gmail SMTP server
app.config['MAIL_PORT'] = 587                         # TLS port
app.config['MAIL_USE_TLS'] = True                     # Use TLS
app.config['MAIL_USE_SSL'] = False                    # Do NOT use SSL with TLS
app.config['MAIL_USERNAME'] = 'vaishnavijayade2@gmail.com'  # Replace with your Gmail
app.config['MAIL_PASSWORD'] = 'avvu gwfn nmuw sscc'     # Replace with the App Password

# Initialize Mail
mail = Mail(app)

def send_access_email(to_email, patient_name, doctor_name, reason, date, time):
    msg = MIMEText(f"""
Hello {patient_name},

Your medical data was accessed during an emergency.

Doctor: {doctor_name}
Reason: {reason}
Date: {date}
Time: {time}

If this was unauthorized, please contact support immediately.

— BioMediAlert
""")

    msg["Subject"] = "⚠️ Emergency Medical Data Access Alert"
    msg["From"] = "biomedialert@gmail.com"
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("vaishnavijayade2@gmail.com", "avvugwfnnmuwsscc")
        server.send_message(msg)


UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
CORS(app)

def generate_emergency_id(aadhaar):
    # Example: EMG-1234-5678
    random_part = ''.join(random.choices(string.digits, k=4))
    return f"EMG-{aadhaar[-4:]}-{random_part}"
#-------Ganache-----
from web3 import Web3
import hashlib
import json

# Blockchain config - UPDATE THESE AFTER DEPLOYMENT
GANACHE_URL = 'http://127.0.0.1:7545'
CONTRACT_ADDRESS = '0xD63B838041472CcC1FFd9694eAC7b84da1ac5e1B'  # UPDATE after deploy
GANACHE_ACCOUNT = '0x17AC1edCE6e28C187bf8bAad3784eCd69b3B4cBD'     # UPDATE from test_ganache.py
GANACHE_PRIVATE_KEY = '0x4308dc7d31c82c33d85e665e8b70155bb994e4c04eb025986bc2d780ef4c7c17'  # UPDATE

w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
with open('contracts/AuditLog.json', 'r') as f:
    contract_data = json.load(f)

AuditLogContract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_data['abi'])
print("✅ Blockchain connected!")



# ---------- DATABASE SETUP ----------
def init_blockchain_tables():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # Enhanced patient_logs with blockchain columns
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blockchain_patient_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_aadhaar TEXT NOT NULL,
            emergency_id TEXT,
            doctor_license TEXT NOT NULL,
            doctor_name TEXT,
            hospital_name TEXT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            access_method TEXT,
            reason TEXT,
            action TEXT NOT NULL,
            blockchain_tx TEXT,
            log_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_aadhaar) REFERENCES patientForm(aadhaar)
        )
    """)
    conn.commit()
    conn.close()

# Call it
init_blockchain_tables()

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Patient signup table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PatSignup (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aadhaar TEXT UNIQUE,
            Fullname TEXT NOT NULL
        )
    ''')

    # Patient form table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patientForm (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Fullname TEXT NOT NULL,
            dob TEXT NOT NULL,
            gender TEXT NOT NULL,
            aadhaar TEXT UNIQUE NOT NULL,
            emergencyName TEXT,
            emergencyPhone TEXT,
            bloodGroup TEXT,
            allergies TEXT,
            chronic TEXT,
            medications TEXT,
            history TEXT,
            instructions TEXT,
            address TEXT,
            photo TEXT,
            pan TEXT,
            license TEXT,
            FOREIGN KEY (aadhaar) REFERENCES PatSignup(aadhaar)
        )
    ''')

    # Patient login history
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS loggedPat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aadhaar TEXT NOT NULL,
    password TEXT NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')


    #Doctor Logs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS doctor_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id TEXT NOT NULL,
        patient_id TEXT NOT NULL,
        action TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Doctor signup table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Docsignup (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        licenseNo TEXT UNIQUE,
        hospital TEXT NOT NULL,
        Fullname TEXT NOT NULL,
        password TEXT NOT NULL
    )
''')



    # Doctor login history
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS loggeddoc (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        licenseNo TEXT NOT NULL,
        password TEXT NOT NULL,
        login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

    


    # Doctor form table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Docform (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Fullname TEXT NOT NULL,
            gender TEXT NOT NULL,
            dob TEXT NOT NULL,
            licenseNo TEXT UNIQUE NOT NULL,
            hospital TEXT NOT NULL,
            specialization TEXT NOT NULL,
            experience INTEGER NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            qualification TEXT,
            certifications TEXT,
            photo TEXT,
            address TEXT
        )
    ''')
    
 #   cursor.execute("DROP TABLE IF EXISTS patient_logs")
    conn.commit()
    conn.close()
#print("patient_logs table dropped successfully.")
init_db()
# ---------------- STRONG PASSWORD CHECK FUNCTION ----------------
def is_strong_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[@$!%*?&#^()_+=-]", password):
        return False
    return True

# ---------- PATIENT ROUTES ----------
@app.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.get_json()
        aadhaar = data.get("aadhaar")
        Fullname = data.get("Fullname")
        password = data.get("password")

        if not aadhaar or not Fullname or not password:
            return jsonify({"success": False, "message": "Aadhaar and Fullname required"}), 400

        if len(aadhaar) != 12 or not aadhaar.isdigit():
            return jsonify({"success": False, "message": "Invalid Aadhaar number"}), 400
        
         # 🔒 Strong Password Check
        if not is_strong_password(password):
            return jsonify({
                "success": False,
                "message": "Weak Password! Must contain: 8+ chars, uppercase, lowercase, number, special symbol."
            }), 400
        
        # Hash Password
        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        # ⭐ Generate Emergency ID linked with Aadhaar
        emergency_id = generate_emergency_id(aadhaar)

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO PatSignup (aadhaar, Fullname, password, emergency_id) VALUES (?, ?, ?,?)",
                (aadhaar, Fullname, hashed_pw, emergency_id)
            )

            conn.commit()

        return jsonify({"success": True, "message": "Signup successful!","emergency_id": emergency_id}), 201

    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Aadhaar already registered!"}), 409
    except sqlite3.OperationalError as e:
        print("🔥 Signup OperationalError:", e)
        return jsonify({"success": False, "message": "Database is locked. Try again."}), 500
    except Exception as e:
        print("🔥 Signup error:", e)
        traceback.print_exc()
        return jsonify({"success": False, "message": "Server error. Try again later."}), 500


@app.route("/patient", methods=["POST"])
def save_patient():
    try:
        data = request.form
        email = data.get("email", "").strip()
        if not email:
            return jsonify({"success": False, "message": "Email is required!"}), 400

        file = request.files.get("photo")

        required = ["Fullname", "dob","email", "gender", "aadhaar", "emergencyName", "emergencyPhone", "bloodGroup"]
        for f in required:
            if not data.get(f):
                return jsonify({"success": False, "message": f"{f} is required!"}), 400
         # PAN VALIDATION HERE (✅ inside function)
        pan = data.get("pan", "").upper()

        if pan and not re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]$", pan):
            return jsonify({
                "success": False,
                "message": "Invalid PAN Format! Example: ABCDE1234F"
            }), 400

        # LICENSE NUMBER (only digits allowed)
        license_no = data.get("license", "")
        if license_no and not license_no.isdigit():
            return jsonify({
                "success": False,
                "message": "License must contain digits only!"
            }), 400
        
          # PHOTO HANDLING
        photo_filename = None
        if file:
            filename = secure_filename(file.filename)
            photo_filename = f"{data['aadhaar']}_{filename}"
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], photo_filename))

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM PatSignup WHERE aadhaar=?", (data["aadhaar"],))
            if not cursor.fetchone():
                return jsonify({"success": False, "message": "User must signup first!"}), 400

            cursor.execute('''
                INSERT OR REPLACE INTO patientForm
                (Fullname, dob,email, gender, aadhaar, emergencyName, emergencyPhone, bloodGroup,
                allergies, chronic, medications, history, instructions, address, photo,pan,license)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?)
            ''', (
                data["Fullname"], data["dob"],data["email"], data["gender"], data["aadhaar"],
                data["emergencyName"], data["emergencyPhone"], data["bloodGroup"],
                data.get("allergies", ""), data.get("chronic", ""), data.get("medications", ""),
                data.get("history", ""), data.get("instructions", ""), data.get("address", ""),
                photo_filename,
                data.get("pan", ""), data.get("license", "")
            ))
            conn.commit()

        return jsonify({"success": True, "message": "Patient details saved!"}), 201

    except Exception as e:
        print("🔥 save_patient error:", e)
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        aadhaar = data.get("aadhaar")
        password = data.get("password")
        

        if not aadhaar or not password:
            return jsonify({"success": False, "message": "Aadhaar and Password required!"}), 400

        if not aadhaar or len(aadhaar) != 12 or not aadhaar.isdigit():
            return jsonify({"success": False, "message": "Invalid Aadhaar format!"}), 400

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # Fetch hashed password for Aadhaar
        cursor.execute("SELECT password FROM PatSignup WHERE aadhaar=?", (aadhaar,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return jsonify({"success": False, "message": "Aadhaar not found. Please signup first!"}), 404

        stored_hash = row[0]  # hash from database

        # Compare entered password with stored hashed password
        if not bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
            conn.close()
            return jsonify({"success": False, "message": "Incorrect password!"}), 401
         # Store login in log table (no Fullname now)
        cursor.execute(
            "INSERT INTO loggedPat (aadhaar, password) VALUES (?, ?)",
            (aadhaar,stored_hash)
        )
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Login successful!", "aadhaar": aadhaar}), 200

    except Exception as e:
        print("🔥 login error:", e)
        traceback.print_exc()
        return jsonify({"success": False, "message": "Server error"}), 500


@app.route("/api/patient/details", methods=["GET"])
def get_logged_patient_details():
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT aadhaar FROM loggedPat ORDER BY login_time DESC LIMIT 1")
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({"error": "No logged-in patient found"}), 404

        aadhaar = row[0]
        cursor.execute('''
            SELECT Fullname, dob, gender, aadhaar, emergencyName, emergencyPhone,
                bloodGroup, allergies, chronic, medications, history, instructions,
                address, photo
            FROM patientForm WHERE aadhaar=?
        ''', (aadhaar,))
        row = cursor.fetchone()
        

        if not row:
            return jsonify({"error": "Profile not found"}), 404
        cursor.execute("SELECT emergency_id FROM PatSignup WHERE aadhaar=?", (aadhaar,))
        emg = cursor.fetchone()
        conn.close()

        return jsonify({
            "Fullname": row[0],
            "dob": row[1],
            "gender": row[2],
            "aadhaar": row[3],
            "emergencyName": row[4],
            "emergencyPhone": row[5],
            "bloodGroup": row[6],
            "allergies": row[7],
            "chronic": row[8],
            "medications": row[9],
            "history": row[10],
            "instructions": row[11],
            "address": row[12],
            "photo": f"/uploads/{row[13]}" if row[13] else None,
            "emergency_id": emg[0] if emg else None

        })

    except Exception as e:
        print("🔥 get_logged_patient_details error:", e)
        traceback.print_exc()
        return jsonify({"error": "Server error"}), 500


@app.route("/api/patient/update", methods=["POST", "OPTIONS"])
def update_logged_patient_details():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    try:
        data = request.form if request.form else request.get_json()
        file = request.files.get("photo") if "photo" in request.files else None

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT aadhaar FROM loggedPat ORDER BY login_time DESC LIMIT 1")
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({"error": "No logged-in patient found"}), 404

        aadhaar = row[0]

        photo_filename = None
        if file:
            filename = secure_filename(file.filename)
            photo_filename = f"{aadhaar}_{filename}"
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], photo_filename))

        params = (
            data.get("Fullname", ""), data.get("dob", ""), data.get("gender", ""),
            data.get("emergencyName", ""), data.get("emergencyPhone", ""), data.get("bloodGroup", ""),
            data.get("allergies", ""), data.get("chronic", ""), data.get("medications", ""),
            data.get("history", ""), data.get("instructions", ""), data.get("address", ""),
            photo_filename, aadhaar
        )

        cursor.execute('''
            UPDATE patientForm
            SET Fullname=?, dob=?, gender=?, emergencyName=?, emergencyPhone=?,
                bloodGroup=?, allergies=?, chronic=?, medications=?, history=?,
                instructions=?, address=?, photo=COALESCE(?, photo)
            WHERE aadhaar=?
        ''', params)
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Profile updated successfully!"})

    except Exception as e:
        print("🔥 update error:", e)
        traceback.print_exc()
        return jsonify({"error": "Server error", "details": str(e)}), 500

    
@app.route('/getPatientLogs', methods=['GET'])
def get_patient_logs():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT aadhaar FROM loggedPat ORDER BY login_time DESC LIMIT 1")
    patient_row = cursor.fetchone()
    if not patient_row:
        return jsonify({"logs": []})
    
    aadhaar = patient_row[0]
    cursor.execute("""
        SELECT doctor_license, doctor_name, hospital_name, date, time, access_method, reason, blockchain_tx 
        FROM blockchain_patient_logs WHERE patient_aadhaar=? ORDER BY created_at DESC
    """, (aadhaar,))
    logs = cursor.fetchall()
    conn.close()
    
    logs_list = [{"doctorName": log[1] or log[0], "hospitalName": log[2], "date": log[3], "time": log[4], 
                "access_method": log[5], "reason": log[6], "blockchain_status": "✅ Verified" if log[7] else "📋 DB"} 
                for log in logs]
    return jsonify({"logs": logs_list})

@app.route("/api/logout", methods=["POST"])
def logout():
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM loggedPat WHERE id = (SELECT id FROM loggedPat ORDER BY login_time DESC LIMIT 1)"
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Logged out successfully"}), 200
    except Exception as e:
        print("🔥 Logout error:", e)
        traceback.print_exc()
        return jsonify({"success": False, "message": "Logout failed"}), 500



@app.route("/api/patient/resolve", methods=["GET"])
def resolve_current_patient():
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute("SELECT aadhaar FROM loggedPat ORDER BY login_time DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()

        if not row:
            return jsonify({
                "success": False,
                "message": "No logged-in patient found"
            }), 404

        return jsonify({
            "success": True,
            "aadhaar": row[0]
        })

    except Exception as e:
        print("🔥 resolve_current_patient error:", e)
        return jsonify({
            "success": False,
            "message": "Server error resolving patient"
        }), 500


# ---------- DOCTOR ROUTES ----------
def is_strong_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[@$!%*?&#^()_+=-]", password):
        return False
    return True

@app.route("/doctor/signup", methods=["POST"])
def doctor_signup():
    try:
        data = request.get_json()
        licenseNo = data.get("licenseNo")
        hospital = data.get("hospital")
        Fullname = data.get("Fullname")
        password = data.get("password")

        if not licenseNo or not hospital or not Fullname  or not password:
            return jsonify({"success": False, "message": "Required fields missing"}), 400

        if len(licenseNo) < 5:
            return jsonify({"success": False, "message": "License number must be at least 5 characters!"}), 400

         # Validate password strength
        if not is_strong_password(password):
            return jsonify({
                "success": False,
                "message": "Weak password! Must include uppercase, lowercase, number, special char, and be 8+ characters."
            }), 400
        
         # Hash the password
        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Docsignup (licenseNo, hospital, Fullname,password, status) VALUES (?, ?, ?, ?, 'PENDING')",
            (licenseNo, hospital, Fullname,hashed_pw)
        )
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Doctor signup successful!"}), 201

    except sqlite3.IntegrityError as e:
        print("IntegrityError:", e)
        return jsonify({"success": False, "message": "License number or username already exists!"}), 409
    except Exception as e:
        print("🔥 Doctor signup error:", e)
        traceback.print_exc()
        return jsonify({"success": False, "message": "Server error"}), 500


@app.route("/doctor/login", methods=["POST"])
def doctor_login():
    try:
        data = request.get_json()
        licenseNo = data.get("licenseNo")
        password = data.get("password")

        if not licenseNo or not password:
            return jsonify({"success": False, "message": "License number and Password required!"}), 400

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # fetch stored password hash + fullname
        cursor.execute(
            "SELECT password, Fullname, status FROM Docsignup WHERE licenseNo=?",
            (licenseNo,)
        )
        row = cursor.fetchone()


        if not row:
            conn.close()
            return jsonify({"success": False, "message": "Doctor not found. Please signup first!"}), 404

        stored_hash = row[0]
        Fullname = row[1]
        status = row[2]

        # 🔒 Block unverified doctors
        if status != "VERIFIED":
            conn.close()
            return jsonify({
                "success": False,
                "message": "Doctor not verified by admin yet"
            }), 403

        # Verify password
        if not bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
            conn.close()
            return jsonify({"success": False, "message": "Incorrect password!"}), 401

        # Insert into login history (no Fullname now, only license + password hash)
        cursor.execute(
            "INSERT INTO loggeddoc (licenseNo, password) VALUES (?, ?)",
            (licenseNo, stored_hash)
        )

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Login successful!",
            "licenseNo": licenseNo,
            "Fullname": Fullname
        }), 200

    except Exception as e:
        print("🔥 doctor login error:", e)
        traceback.print_exc()
        return jsonify({"success": False, "message": "Server error"}), 500

    
# Save Doctor Form
@app.route("/api/doctor/details", methods=["POST"])
def save_doctor_details():
    try:
        data = request.form
        file = request.files.get("photo")

        required = ["Fullname", "gender", "dob", "licenseNo", "hospital", "specialization", "experience", "phone", "email"]
        for f in required:
            if not data.get(f):
                return jsonify({"success": False, "message": f"{f} is required!"}), 400

        photo_filename = None
        if file:
            filename = secure_filename(file.filename)
            photo_filename = f"{data['licenseNo']}_{filename}"
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], photo_filename))

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            # Insert or replace doctor info
            cursor.execute('''
                INSERT OR REPLACE INTO Docform
                (Fullname,gender, dob,licenseNo, hospital, specialization, experience,
                phone, email, qualification, certifications,  photo, address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data["Fullname"], data["gender"],data["dob"],data["licenseNo"], 
                data["hospital"], data["specialization"], int(data["experience"]),
                data["phone"], data["email"], data.get("qualification", ""),
                data.get("certifications", ""),  photo_filename, data.get("address", "")
            ))
            conn.commit()

        return jsonify({"success": True, "message": "Doctor profile saved!"}), 201

    except Exception as e:
        print("🔥 save_doctor error:", e)
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500


# Get Doctor Form by License
@app.route("/api/doctor/details", methods=["GET"])
def get_logged_doctor_details():
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # Get the most recent logged-in doctor
        cursor.execute("SELECT licenseNo FROM loggeddoc ORDER BY login_time DESC LIMIT 1")
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({"error": "No logged-in doctor found"}), 404

        licenseNo = row[0]

        # Fetch doctor details
        cursor.execute('''
            SELECT Fullname, gender, dob, licenseNo, hospital, specialization,
                experience, phone, email, qualification,
                certifications, address , photo
            FROM Docform WHERE licenseNo=?
        ''', (licenseNo,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return jsonify({"error": "Profile not found"}), 404

        return jsonify({
            
            "Fullname": row[0],
            "gender": row[1],
            "dob": row[2],
            "licenseNo": row[3],
            "hospital": row[4],
            "specialization": row[5],
            "experience": row[6],
            "phone": row[7],
            "email": row[8],
            "qualification": row[9],
            "certifications": row[10],
            "address": row[11],
            "photo": f"/uploads/{row[12]}" if row[12] else None
        })

    except Exception as e:
        print("🔥 get_logged_doctor_details error:", e)
        traceback.print_exc()
        return jsonify({"error": "Server error"}), 500


@app.route("/api/doctor/update", methods=["POST", "OPTIONS"])
def update_logged_doctor_details():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    try:
        data = request.form if request.form else request.get_json()
        
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # Get most recent logged-in doctor
        cursor.execute("SELECT licenseNo FROM loggeddoc ORDER BY login_time DESC LIMIT 1")
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({"error": "No logged-in doctor found"}), 404

        licenseNo = row[0]


        params = (
            data.get("Fullname", ""), data.get("gender", ""), data.get("dob", ""),
            data.get("hospital", ""), data.get("specialization", ""),
            data.get("experience", ""), data.get("phone", ""), data.get("email", ""),
            data.get("qualification", ""), data.get("certifications", ""),
            data.get("address", ""), licenseNo
        )

        cursor.execute('''
            UPDATE Docform
            SET Fullname=?, gender=?, dob=?, hospital=?, specialization=?,
                experience=?, phone=?, email=?, qualification=?, certifications=?,
                address=?
            WHERE licenseNo=?
        ''', params)
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Profile updated successfully!"})

    except Exception as e:
        print("🔥 update_logged_doctor_details error:", e)
        traceback.print_exc()
        return jsonify({"error": "Server error", "details": str(e)}), 500
# ---------- Doctor Search Patient ----------
@app.route("/api/doctor/search_patient", methods=["POST"])
def doctor_search_patient():
    try:
        data = request.get_json()
        aadhaar = data.get("aadhaar")
        pan = data.get("pan")
        license = data.get("license")
        emergency_id = data.get("emergencyId")
        access_method = data.get("access_method", "unknown")
        reason = data.get("reason", "emergency")

        if not aadhaar or len(aadhaar) != 12 or not aadhaar.isdigit():
            return jsonify({"success": False, "message": "Invalid Aadhaar"}), 400

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # 🔐 STEP 0 — Get logged-in doctor
        cursor.execute("""
            SELECT licenseNo 
            FROM loggeddoc 
            ORDER BY login_time DESC 
            LIMIT 1
        """)
        doc_row = cursor.fetchone()

        if not doc_row:
            conn.close()
            return jsonify({
                "success": False,
                "message": "Doctor not logged in. Please login again."
            }), 401
        doctor_license = doc_row[0]


        # STEP 1 — Identify Aadhaar from ANY field
        final_aadhaar = None
        # a) Direct Aadhaar
        if aadhaar:
            cursor.execute("SELECT aadhaar FROM patientForm WHERE aadhaar=?", (aadhaar,))
            row = cursor.fetchone()
            if row:
                final_aadhaar = row[0]

        # b) PAN → Aadhaar
        if not final_aadhaar and pan:
            cursor.execute("SELECT aadhaar FROM patientForm WHERE pan=?", (pan,))
            row = cursor.fetchone()
            if row:
                final_aadhaar = row[0]

        # c) Driving License → Aadhaar
        if not final_aadhaar and license:
            cursor.execute("SELECT aadhaar FROM patientForm WHERE license=?", (license,))
            row = cursor.fetchone()
            if row:
                final_aadhaar = row[0]

        # d) Emergency ID → Aadhaar (from signup table)
        if not final_aadhaar and emergency_id:
            cursor.execute("SELECT aadhaar FROM PatSignup WHERE emergency_id=?", (emergency_id,))
            row = cursor.fetchone()
            if row:
                final_aadhaar = row[0]

        # If NOTHING matched → patient not found
        if not final_aadhaar:
            conn.close()
            return jsonify({"success": False, "message": "Patient not found"}), 404
        print("🔎 SEARCH INPUT:", data)
        print("✅ FINAL AADHAAR RESOLVED:", final_aadhaar)

        # STEP 2 — Fetch full patient details using Aadhaar + LOG BLOCKCHAIN
        cursor.execute("""
            SELECT * 
            FROM patientForm
            WHERE aadhaar = ?
        """, (final_aadhaar,))
        row = cursor.fetchone()



        cursor.execute(
            "SELECT status FROM Docsignup WHERE licenseNo=?",
            (doctor_license,)
        )
        status_row = cursor.fetchone()

        if not status_row or status_row[0] != "VERIFIED":
            conn.close()
            return jsonify({
                "success": False,
                "message": "Doctor not verified by admin yet."
            }), 403

        # 🔥 Get doctor details for log
        cursor.execute("SELECT Fullname, hospital FROM Docform WHERE licenseNo=?", (doctor_license,))
        doctor_info = cursor.fetchone() or (doctor_license, "Unknown Hospital")

        # 🔥 NEW: Get emergency_id for blockchain
        cursor.execute("SELECT emergency_id FROM PatSignup WHERE aadhaar=?", (final_aadhaar,))
        emg_row = cursor.fetchone()
        emergency_id_log = emg_row[0] if emg_row else final_aadhaar

        # 🔥 NEW: Log to blockchain table
        now = datetime.now()
        cursor.execute("""
            INSERT INTO blockchain_patient_logs 
            (patient_aadhaar, emergency_id, doctor_license, doctor_name, hospital_name, 
            date, time, access_method, reason, action)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (final_aadhaar, emergency_id_log, doctor_license, doctor_info[0], doctor_info[1], 
            now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), access_method, reason, "Emergency access"))
        
        #to get the patient adhaar for finding email
        cursor.execute("""
            SELECT email, Fullname
            FROM patientForm
            WHERE aadhaar = ?
        """, (final_aadhaar,))

        patient = cursor.fetchone()

        try:
            if patient and patient[0]:
                send_access_email(
                    patient[0],
                    patient[1],
                    doctor_info[0],
                    reason,
                    now.strftime("%Y-%m-%d"),
                    now.strftime("%H:%M:%S")
        )
        except Exception as mail_error:
            print("📧 Email failed but access logged:", mail_error)


        log_id = cursor.lastrowid 

        
        # 🔥 NEW: Blockchain transaction (if setup)
        blockchain_tx = None
        log_hash = None
        if 'w3' in globals() and w3 and 'AuditLogContract' in globals():
            log_string = f"{emergency_id_log}|{doctor_license}|{now.isoformat()}|{access_method}|{reason}"
            log_hash = hashlib.sha256(log_string.encode()).hexdigest()
            
            try:
                nonce = w3.eth.get_transaction_count(GANACHE_ACCOUNT)
                tx = AuditLogContract.functions.recordAccess(
                emergency_id_log, doctor_license, access_method, reason, w3.to_bytes(hexstr=log_hash)
                ).build_transaction({
                'from': GANACHE_ACCOUNT, 
                'gas': 300000, 
                'gasPrice': w3.to_wei('20', 'gwei'), 
                'nonce': nonce
                })
    
                signed_tx = w3.eth.account.sign_transaction(tx, GANACHE_PRIVATE_KEY)
                tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)  # ✅ 2min timeout
                blockchain_tx = tx_hash.hex()
    
                cursor.execute("UPDATE blockchain_patient_logs SET blockchain_tx=?, log_hash=? WHERE id=?", 
                    (blockchain_tx, log_hash, log_id))
                print(f"✅ Blockchain logged: {blockchain_tx[:16]}...")
    
            except Exception as e:
                print(f"⚠️ Blockchain failed (DB logged): {str(e)[:100]}")
    # Don't rollback - DB log stays even if blockchain fails

        conn.commit()
        conn.close()


        if row:
            keys = ["id","Fullname","dob","gender","aadhaar","emergencyName","emergencyPhone",
                    "bloodGroup","allergies","chronic","medications","history","instructions",
                    "address","photo","pan","license"]
            patient = dict(zip(keys, row))
            return jsonify({
                "success": True, 
                "patient": patient,
                "log_id": log_id,
                "doctor_license": doctor_license,
                "doctor_name": doctor_info[0],
                "blockchain_tx": blockchain_tx,
                "blockchain_status":"✅ Blockchain Recorded" if blockchain_tx else "📋 Database Logged",
                "access_method": access_method,
                "reason": reason 

            }), 200
        else:
            return jsonify({"success": False, "message": "Patient not found"}), 404

    except Exception as e:
        print("🔥 doctor_search_patient error:", e)
        traceback.print_exc()
        return jsonify({"success": False, "message": "Server error"}), 500

@app.route('/getDoctorLogs', methods=['GET'])
def get_doctor_logs():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Get currently logged-in doctor license
    cursor.execute("""
        SELECT licenseNo
        FROM loggeddoc
        ORDER BY login_time DESC
        LIMIT 1
    """)
    doctor_row = cursor.fetchone()

    if not doctor_row:
        conn.close()
        return jsonify({"logs": []})

    doctor_license = doctor_row[0]

    cursor.execute("""
        SELECT patient_aadhaar, emergency_id, date, time,
               access_method, reason, blockchain_tx
        FROM blockchain_patient_logs
        WHERE doctor_license = ?
        ORDER BY created_at DESC
    """, (doctor_license,))

    logs = cursor.fetchall()
    conn.close()

    logs_list = [
        {
            "patient_aadhaar": log[0],
            "emergency_id": log[1],
            "date": log[2],
            "time": log[3],
            "access_method": log[4],
            "reason": log[5],
            "blockchain_status": "✅ Verified" if log[6] else "📋 DB"
        }
        for log in logs
    ]

    return jsonify({"logs": logs_list})

@app.route("/api/doctor/patient_by_aadhaar")
def get_patient_by_aadhaar():
    aadhaar = request.args.get("aadhaar")

    if not aadhaar:
        return jsonify({"error": "Aadhaar required"}), 400

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patientForm WHERE aadhaar=?", (aadhaar,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Patient not found"}), 404

    keys = ["id","Fullname","dob","gender","aadhaar","emergencyName","emergencyPhone",
            "bloodGroup","allergies","chronic","medications","history","instructions",
            "address","photo","pan","license"]

    return jsonify(dict(zip(keys, row)))


#-------Admin---------
@app.route('/api/admin/logs', methods=['GET'])
def get_admin_logs():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT patient_aadhaar, doctor_license, doctor_name,
               access_method, reason, action,
               blockchain_tx, date, time
        FROM blockchain_patient_logs
        ORDER BY created_at DESC
        LIMIT 50
    """)

    logs = []
    for r in cursor.fetchall():
        logs.append({
            "patient_aadhaar": r[0],
            "doctor_license": r[1],
            "doctor_name": r[2],
            "access_method": r[3],
            "reason": r[4],
            "action": r[5],
            "blockchain_tx": r[6],
            "date": r[7],
            "time": r[8]
        })

    conn.close()
    return jsonify({"logs": logs})


@app.route("/api/public/verified_doctors", methods=["GET"])
def get_verified_doctors():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT Fullname, hospital, licenseNo
        FROM Docsignup
        WHERE status = 'VERIFIED'
        ORDER BY Fullname
    """)

    doctors = []
    for d in cursor.fetchall():
        doctors.append({
            "name": d[0],
            "hospital": d[1],
            "license": d[2]
        })

    conn.close()
    return jsonify({"doctors": doctors})

@app.route("/api/admin/doctors", methods=["GET"])
def get_all_doctors():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT Fullname, licenseNo, hospital, status
        FROM Docsignup
        ORDER BY status, Fullname
    """)

    doctors = []
    for d in cursor.fetchall():
        doctors.append({
            "name": d[0],
            "license": d[1],
            "hospital": d[2],
            "status": d[3] or "PENDING"
        })

    conn.close()
    return jsonify({"doctors": doctors})


@app.route("/api/admin/verify_doctor", methods=["POST"])
def verify_doctor():
    data = request.get_json()
    licenseNo = data.get("licenseNo")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Docsignup SET status='VERIFIED' WHERE licenseNo=?",
        (licenseNo,)
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True,"message": "Doctor verified"})


@app.route("/api/admin/block_doctor", methods=["POST"])
def block_doctor():
    data = request.get_json()
    licenseNo = data.get("licenseNo")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Docsignup SET status='BLOCKED' WHERE licenseNo=?",
        (licenseNo,)
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Doctor blocked"})
    
@app.route("/api/doctor/view-patient", methods=["POST"])
def view_patient():
    data = request.json
    doctor_id = data.get("doctor_id")
    patient_aadhaar = data.get("aadhaar")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # 🔹 Fetch patient
    cursor.execute("SELECT * FROM patients WHERE aadhaar = ?", (patient_aadhaar,))
    patient = cursor.fetchone()

    if not patient:
        conn.close()
        return jsonify({"success": False, "message": "Patient not found"}), 404

    # 🔹 CREATE LOG
    cursor.execute("""
        INSERT INTO doctor_logs (doctor_id, patient_aadhaar, action)
        VALUES (?, ?, ?)
    """, (doctor_id, patient_aadhaar, "VIEWED_PATIENT_DATA"))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "patient": patient
    })

@app.route("/api/doctor/logs/<doctor_id>", methods=["GET"])
def doctor_logs(doctor_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT patient_aadhaar, action, timestamp
        FROM doctor_logs
        WHERE doctor_id = ?
        ORDER BY timestamp DESC
    """, (doctor_id,))

    logs = cursor.fetchall()
    conn.close()

    return jsonify({
        "success": True,
        "logs": [
            {
                "patient_aadhaar": row[0],
                "action": row[1],
                "timestamp": row[2]
            } for row in logs
        ]
    })

def send_patient_email(patient_email, subject, message):
    try:
        msg = Message(
            subject=subject,
            sender=app.config['MAIL_USERNAME'],
            recipients=[patient_email],
            body=message
        )
        mail.send(msg)
        print(f"✅ Email sent to {patient_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

#-----end admin-------
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/api/patient/resolve", methods=["POST"])
def resolve_patient():
    try:
        data = request.get_json()
        search_type = data.get("type")
        value = data.get("value")

        if not search_type or not value:
            return jsonify({
                "success": False,
                "message": "Missing search data"
            }), 400

        column_map = {
            "aadhaar": "aadhaar",
            "pancard": "pan",
            "license": "license",
            "emergency": "emergency_id"
        }

        if search_type not in column_map:
            return jsonify({
                "success": False,
                "message": "Invalid search type"
            }), 400

        column = column_map[search_type]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # IMPORTANT: emergency_id is in PatSignup, others in patientForm
        if column == "emergency_id":
            cursor.execute(
                "SELECT aadhaar FROM PatSignup WHERE emergency_id = ?",
                (value,)
            )
        else:
            cursor.execute(
                f"SELECT aadhaar FROM patientForm WHERE {column} = ?",
                (value,)
            )

        row = cursor.fetchone()
        conn.close()

        if not row:
            return jsonify({
                "success": False,
                "message": "Patient not found"
            }), 404

        return jsonify({
            "success": True,
            "aadhaar": row[0]
        }), 200

    except Exception as e:
        print("🔥 resolve error:", e)
        return jsonify({
            "success": False,
            "message": "Server error"
        }), 500

# ---------- RUN APP ----------
if __name__ == "__main__":
    app.run(debug=True, port=5037)
