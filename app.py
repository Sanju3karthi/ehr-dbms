from flask import Flask, render_template, request, redirect, flash, send_file, url_for
import sqlite3
from fpdf import FPDF
import io
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Role to table mapping
ROLE_TABLES = {
    'doctor': 'doctors',
    'patient': 'patients'
}

@app.route('/')
def home():
    return redirect('/login')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        name = request.form.get('name')
        password = request.form.get('password')

        if not role or not name or not password:
            flash("All fields are required!")
            return redirect('/login')

        table_name = ROLE_TABLES.get(role.lower())
        if not table_name:
            flash("Invalid role selected!")
            return redirect('/login')

        conn = sqlite3.connect('ehr1.db')
        cursor = conn.cursor()

        # Check credentials
        if role.lower() == 'doctor':
            cursor.execute(
                "SELECT doctor_id FROM doctors WHERE name=? AND Password=?", (name, password)
            )
        else:
            cursor.execute(
                "SELECT patient_id FROM patients WHERE name=? AND Password=?", (name, password)
            )

        user = cursor.fetchone()
        conn.close()

        if user:
            user_id = user[0]
            if role.lower() == 'doctor':
                return redirect(f"/dashboard/doctor/{user_id}")
            else:
                return redirect(f"/dashboard/patient/{user_id}")
        else:
            flash(f"{role.title()} not found or incorrect password!")
            return redirect('/login')

    return render_template('login.html')


# Doctor dashboard: shows only their patients
@app.route('/dashboard/doctor/<int:doctor_id>')
def doctor_dashboard(doctor_id):
    conn = sqlite3.connect('ehr1.db')
    cursor = conn.cursor()

    # Get doctor info
    cursor.execute("SELECT name, specialization FROM doctors WHERE doctor_id=?", (doctor_id,))
    doctor = cursor.fetchone()

    # Get scheduled patients for this doctor
    cursor.execute("""
        SELECT p.name, p.contact, p.age, p.gender, a.date, a.time, a.status, p.medical_history
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        WHERE a.doctor_id=?
        ORDER BY a.date, a.time
    """, (doctor_id,))
    appointments = cursor.fetchall()
    conn.close()

    return render_template("doctor_dashboard.html", doctor=doctor, appointments=appointments, doctor_id=doctor_id)


# Patient dashboard: shows only assigned doctor
@app.route('/dashboard/patient/<int:patient_id>')
def patient_dashboard(patient_id):
    conn = sqlite3.connect('ehr1.db')
    cursor = conn.cursor()

    # Get patient info
    cursor.execute("SELECT name FROM patients WHERE patient_id=?", (patient_id,))
    patient = cursor.fetchone()

    # Get assigned doctor(s) for this patient
    cursor.execute("""
        SELECT d.name, d.specialization, d.contact, a.date, a.time, a.status
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE a.patient_id=?
        ORDER BY a.date, a.time
    """, (patient_id,))
    appointments = cursor.fetchall()
    conn.close()

    return render_template("patient_dashboard.html", patient=patient, appointments=appointments)


# Download PDF of scheduled patients (for doctors/staff)
@app.route('/download_pdf/doctor/<int:doctor_id>')
def download_pdf(doctor_id):
    conn = sqlite3.connect('ehr1.db')
    cursor = conn.cursor()

    # Get doctor info
    cursor.execute("SELECT name, specialization FROM doctors WHERE doctor_id=?", (doctor_id,))
    doctor = cursor.fetchone()

    # Get appointments with medical history
    cursor.execute("""
        SELECT p.name, p.contact, p.age, p.gender, a.date, a.time, a.status, p.medical_history
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        WHERE a.doctor_id=?
        ORDER BY a.date, a.time
    """, (doctor_id,))
    appointments = cursor.fetchall()
    conn.close()

    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "HealthMatrix EHR", ln=True, align='C')
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Doctor: {doctor[0]} ({doctor[1]})", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')
    pdf.ln(10)

    # Table header
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(85, 99, 222)
    pdf.set_text_color(255, 255, 255)
    headers = ["Patient Name", "Contact", "Age", "Gender", "Date", "Time", "Status"]
    col_widths = [40, 30, 10, 15, 25, 20, 25]

    for i in range(len(headers)):
        pdf.cell(col_widths[i], 10, headers[i], border=1, align='C', fill=True)
    pdf.ln()

    # Table content
    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(0, 0, 0)

    status_colors = {
        "confirmed": (0, 153, 51),  # green
        "pending": (255, 153, 0),   # orange
        "cancelled": (204, 0, 0)    # red
    }

    for appt in appointments:
        name, contact, age, gender, date, time, status, history = appt
        pdf.cell(col_widths[0], 8, name, border=1)
        pdf.cell(col_widths[1], 8, contact, border=1)
        pdf.cell(col_widths[2], 8, str(age), border=1, align='C')
        pdf.cell(col_widths[3], 8, gender, border=1, align='C')
        pdf.cell(col_widths[4], 8, date, border=1, align='C')
        pdf.cell(col_widths[5], 8, time, border=1, align='C')

        # Status with colored background
        r, g, b = status_colors.get(status.lower(), (128, 128, 128))
        pdf.set_fill_color(r, g, b)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(col_widths[6], 8, status.capitalize(), border=1, align='C', fill=True)
        pdf.ln()
        pdf.set_text_color(0, 0, 0)

        # Medical history below each patient
        pdf.set_font("Arial", 'I', 10)
        pdf.multi_cell(0, 6, f"Medical History: {history}")
        pdf.ln(2)
        pdf.set_font("Arial", '', 11)

    # Footer
    pdf.set_y(-20)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, f"Page {pdf.page_no()}", align='C')

    # Output PDF
    # Fixed
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return send_file(
    io.BytesIO(pdf_bytes),
    download_name="scheduled_patients.pdf",
    as_attachment=True,
    mimetype='application/pdf'
)



if __name__ == '__main__':
    app.run(debug=True)

