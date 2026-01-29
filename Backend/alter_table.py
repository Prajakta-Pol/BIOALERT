import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE patientForm ADD COLUMN email TEXT")
  

except Exception as e:
    print("Error:", e)

conn.close()

