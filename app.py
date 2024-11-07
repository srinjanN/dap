from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database setup
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS patients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS appointments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        patient_id INTEGER,
                        doctor_name TEXT NOT NULL,
                        appointment_date TEXT NOT NULL,
                        FOREIGN KEY (patient_id) REFERENCES patients (id))''')
    conn.commit()
    conn.close()

init_db()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO patients (name, email, password) VALUES (?, ?, ?)', (name, email, password))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered!', 'danger')
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM patients WHERE email = ?', (email,))
        patient = cursor.fetchone()
        conn.close()
        
        if patient and check_password_hash(patient[3], password):
            session['patient_id'] = patient[0]
            session['patient_name'] = patient[1]
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('patient_id', None)
    session.pop('patient_name', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    if 'patient_id' not in session:
        flash('Please log in to book an appointment', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        doctor_name = request.form['doctor_name']
        appointment_date = request.form['appointment_date']
        patient_id = session['patient_id']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO appointments (patient_id, doctor_name, appointment_date) VALUES (?, ?, ?)', (patient_id, doctor_name, appointment_date))
        conn.commit()
        conn.close()
        flash('Appointment booked successfully', 'success')
        return redirect(url_for('index'))
    
    return render_template('book_appointment.html')

@app.route('/view_appointments')
def view_appointments():
    if 'patient_id' not in session:
        flash('Please log in to view your appointments', 'danger')
        return redirect(url_for('login'))
    
    patient_id = session['patient_id']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM appointments WHERE patient_id = ?', (patient_id,))
    appointments = cursor.fetchall()
    conn.close()
    
    return render_template('view_appointments.html', appointments=appointments)

if __name__ == '__main__':
    app.run(debug=True)
