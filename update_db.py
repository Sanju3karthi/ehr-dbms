import sqlite3

# Connect to your database
conn = sqlite3.connect('ehr1.db')
cursor = conn.cursor()

# Add medical_history column if it doesn't exist
try:
    cursor.execute("ALTER TABLE patients ADD COLUMN medical_history TEXT DEFAULT 'No history available'")
    print("Added medical_history column.")
except sqlite3.OperationalError:
    print("Column medical_history already exists.")

# Add sample medical history data
sample_data = [
    (1, 'Diabetes, Hypertension, Allergic to penicillin'),
    (2, 'Asthma, Seasonal allergies'),
    (3, 'Previous surgery: appendectomy; Currently on vitamin D supplements')
]

for patient_id, history in sample_data:
    cursor.execute("UPDATE patients SET medical_history = ? WHERE patient_id = ?", (history, patient_id))

conn.commit()
conn.close()
print("Sample medical history added successfully.")
