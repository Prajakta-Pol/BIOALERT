import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE patientForm ADD COLUMN face_vector BLOB")
    print("Column 'face_vector' added successfully.")
except Exception as e:
    print("Error:", e)

conn.close()

