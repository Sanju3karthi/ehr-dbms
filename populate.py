import sqlite3
import random

# Connect to ehr1.db
conn = sqlite3.connect("ehr1.db")
cursor = conn.cursor()

# --- Drop existing tables (optional clean start) ---
cursor.execute("DROP TABLE IF EXISTS users;")
cursor.execute("DROP TABLE IF EXISTS patients;")
cursor.execute("DROP TABLE IF EXISTS doctors;")
cursor.execute("DROP TABLE IF EXISTS appointments;")
cursor.execute("DROP TABLE IF EXISTS records;")

# --- Create tables ---
cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
);
""")

cursor.execute("""
CREATE TABLE patients (
    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    gender TEXT,
    contact TEXT
);
""")

cursor.execute("""
CREATE TABLE doctors (
    doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    specialization TEXT,
    contact TEXT
);
""")

cursor.execute("""
CREATE TABLE appointments (
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    doctor_id INTEGER,
    date TEXT,
    time TEXT,
    status TEXT,
    FOREIGN KEY(patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY(doctor_id) REFERENCES doctors(doctor_id)
);
""")

cursor.execute("""
CREATE TABLE records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    doctor_id INTEGER,
    diagnosis TEXT,
    prescription TEXT,
    date TEXT,
    FOREIGN KEY(patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY(doctor_id) REFERENCES doctors(doctor_id)
);
""")

# --- Users ---
users = [
    ('admin', 'admin123', 'staff'),
    ('drjohn', 'doc123', 'doctor'),
    ('patient1', 'pat123', 'patient')
]
cursor.executemany("INSERT INTO users (username, password, role) VALUES (?, ?, ?);", users)

# --- Doctors (50 entries) ---
specializations = ['Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'Dermatology']
for i in range(1, 51):
    name = f"Doctor_{i}"
    specialization = specializations[i % 5]
    contact = f"999999{i:03d}"
    cursor.execute("INSERT INTO doctors (name, specialization, contact) VALUES (?, ?, ?);",
                   (name, specialization, contact))

# --- Patients (50 entries) ---
for i in range(1, 51):
    name = f"Patient_{i}"
    age = random.randint(20, 60)
    gender = "Male" if i % 2 == 0 else "Female"
    contact = f"888888{i:03d}"
    cursor.execute("INSERT INTO patients (name, age, gender, contact) VALUES (?, ?, ?, ?);",
                   (name, age, gender, contact))

# --- Appointments (100 entries) ---
statuses = ['Waiting', 'Attended', 'Cancelled']
for i in range(1, 101):
    patient_id = (i % 50) + 1
    doctor_id = (i % 50) + 1
    date = f"2025-11-{(i % 28) + 1:02d}"
    time = f"{(i % 8) + 9:02d}:00"
    status = statuses[i % 3]
    cursor.execute("""
        INSERT INTO appointments (patient_id, doctor_id, date, time, status)
        VALUES (?, ?, ?, ?, ?);
    """, (patient_id, doctor_id, date, time, status))

# --- Commit and close ---
conn.commit()
conn.close()

print("✅ Database 'ehr1.db' created and populated successfully with sample data!")

