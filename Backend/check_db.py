import sqlite3
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Count rows
cursor.execute("SELECT COUNT(*) FROM blockchain_patient_logs")
print("Total log rows:", cursor.fetchone()[0])

# Show recent logs
cursor.execute("SELECT * FROM blockchain_patient_logs ORDER BY id DESC LIMIT 5")
print("\nRecent logs:")
for row in cursor.fetchall():
    print(row)

conn.close()
