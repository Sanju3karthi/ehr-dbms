import sqlite3
from faker import Faker
import random

fake = Faker()

# Connect to SQLite
conn = sqlite3.connect('ehr1.db')
cursor = conn.cursor()

status_options = ['Pending', 'Completed', 'Cancelled']

# Insert 50 patients
for _ in range(50):
    cursor.execute("""
        INSERT INTO patients (name, age, gender, address, phone, email)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        fake.name(),
        random.randint(1, 90),
        random.choice(['Male', 'Female']),
        fake.address().replace('\n', ', '),
        fake.phone_number(),
        fake.email()
    ))

# Insert 50 doctors
specializations = ['Cardiology', 'Neurology', 'Dermatology', 'Pediatrics', 'Orthopedics', 'General Medicine', 'ENT', 'Ophthalmology']
for _ in range(50):
    cursor.execute("""
        INSERT INTO doctors (name, specialization, phone, email)
        VALUES (?, ?, ?, ?)
    """, (
        fake.name(),
        random.choice(specializations),
        fake.phone_number(),
        fake.email()
    ))

# Insert 100 appointments with status
for _ in range(100):
    cursor.execute("""
        INSERT INTO appointments (patient_id, doctor_id, date, time, reason, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        random.randint(1, 50),
        random.randint(1, 50),
        fake.date_between(start_date='-1y', end_date='+1y').isoformat(),
        fake.time(pattern="%H:%M"),
        fake.sentence(nb_words=5),
        random.choice(status_options)
    ))

# Insert 100 records/prescriptions with status
diagnoses = ['Hypertension', 'Diabetes', 'Migraine', 'Flu', 'Eczema', 'Arthritis', 'Asthma', 'Allergy']
treatments = ['Medication', 'Therapy', 'Surgery', 'Lifestyle changes', 'Observation', 'Diet changes']
prescriptions = ['Drug A', 'Drug B', 'Drug C', 'Drug D', 'Drug E']

for _ in range(100):
    cursor.execute("""
        INSERT INTO records (patient_id, diagnosis, treatment, prescription, date, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        random.randint(1, 50),
        random.choice(diagnoses),
        random.choice(treatments),
        random.choice(prescriptions),
        fake.date_between(start_date='-1y', end_date='+1y').isoformat(),
        random.choice(status_options)
    ))

# Commit and close
conn.commit()
conn.close()

print("Database populated with status for appointments and records!")
