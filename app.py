from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_session import Session
from functools import wraps
from flask import redirect, session, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'medicalsystem'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # Fetch results as dictionaries

# Configure Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

mysql = MySQL(app)

def get_db_connection():
    return mysql.connection.cursor()

@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['full_name']
        age = request.form['age']
        gender = request.form['gender']
        email = request.form['email']
        password = request.form['password']
        username = full_name.replace(' ', '_') + '_' + age
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (full_name, age, gender, email, username, password) VALUES (%s, %s, %s, %s, %s, %s)", (full_name, age, gender, email, username, password))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = get_db_connection()
        cursor.execute('SELECT id, username, password, role FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            # Store user information in session
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']

            # Successful login, redirect to the appropriate homepage
            if user['role'] == 'patient':
                return redirect(url_for('patient_homepage'))
            elif user['role'] == 'staff':
                return redirect(url_for('staff_homepage'))
            elif user['role'] == 'doctor':
                return redirect(url_for('doctor_homepage'))
        else:
            # Invalid credentials, redirect back to the login page
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@app.route('/profile')
def profile():
    if session.get('user_id'):
        # User is logged in, fetch additional data from session if needed
        user_id = session['user_id']
        username = session['username']
        role = session['role']
        return render_template('profile.html', username=username, role=role)
    else:
        # User is not logged in, redirect to login page
        return redirect(url_for('login'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/patient_homepage')
@login_required
def patient_homepage():
    return render_template('patient_homepage.html')
@app.route('/Medecin')
@login_required
def Medecin():
    return render_template('Medecin.html')
@app.route('/add_staff', methods=['POST'])
@login_required
def add_staff():
    full_name = request.form['full_name']
    role = request.form['role']
    department = request.form['department']
    email = request.form['email']
    phone = request.form['phone']

    cursor = get_db_connection()
    
    # Insert the new staff into the `users` table
    cursor.execute("""
        INSERT INTO users (full_name, role, email) VALUES (%s, %s, %s)
    """, (full_name, role, email))
    
    user_id = cursor.lastrowid  # Get the ID of the newly created user
    
    # Insert into the `staff` table
    cursor.execute("""
        INSERT INTO staff (user_id, position, department, phone_number, hire_date, salary) 
        VALUES (%s, %s, %s, %s, CURDATE(), 0)  # Set initial salary to 0 or any default value
    """, (user_id, role, department, phone))
    
    mysql.connection.commit()
    cursor.close()
    
    return redirect(url_for('addremovestaff'))










@app.route('/remove_staff', methods=['POST'])
@login_required
def remove_staff():
    staff_id = request.form['staff_id']

    cursor = get_db_connection()
    
    # Delete from the `staff` table
    cursor.execute("DELETE FROM staff WHERE user_id = %s", (staff_id,))
    
    # Optionally, delete from the `users` table if you want to completely remove the user
    cursor.execute("DELETE FROM users WHERE id = %s", (staff_id,))
    
    mysql.connection.commit()
    cursor.close()
    
    return redirect(url_for('addremovestaff'))
@app.route('/staff_homepage')
@login_required
def staff_homepage():
    user_id = session.get('user_id')
    cursor = get_db_connection()

    # Fetch staff details
    cursor.execute('''
        SELECT u.full_name, u.email, u.age, u.gender, s.position, s.department, s.hire_date, s.salary, s.phone_number, s.address, s.city, s.state, s.zip_code
        FROM users u
        JOIN staff s ON u.id = s.user_id
        WHERE u.id = %s
    ''', (user_id,))
    staff = cursor.fetchone()
    cursor.close()

    return render_template('staff_homepage.html', staff=staff)

@app.route('/laboratory')
@login_required
def laboratory():
    return render_template('laboratory.html')


@app.route('/departments')
@login_required
def departments():
    user_id = session.get('user_id')
    role = session.get('role')
    cursor = get_db_connection()

    if role == 'doctor':
        # If the user is a doctor, fetch department data for that doctor
        cursor.execute('SELECT department, doctor_name, avilable_time, no_of_patients, id, doctor_images FROM appoitments WHERE id = %s', (user_id,))
    else:
        # For other roles (e.g., staff, patient), fetch all department data
        cursor.execute('SELECT department, doctor_name, avilable_time, no_of_patients, id, doctor_images FROM appoitments')
    
    departments_data = cursor.fetchall()
    
    cursor.close()

    return render_template('departemnts.html', departments=departments_data)

@app.route('/start_session')
@login_required
def start_session():
    user_id = session.get('user_id')
    cursor = get_db_connection()

    # Fetch doctor details
    cursor.execute('SELECT full_name, email FROM users WHERE id = %s', (user_id,))
    doctor = cursor.fetchone()

    # Fetch patients appointments for the logged-in doctor
    cursor.execute('''
        SELECT pa.patient_name, pa.appointment_time
        FROM patients_appointments pa
        JOIN appoitments a ON pa.appointment_id = a.id
        WHERE a.id = %s
    ''', (user_id,))
    patients_appointments = cursor.fetchall()

    cursor.close()

    return render_template('start_session.html', doctor=doctor, patients_appointments=patients_appointments)
@app.route('/Appointments')
@login_required
def Appointments():
    user_id = session.get('user_id')
    cursor = get_db_connection()

    # Fetch doctor details
    cursor.execute('SELECT full_name, email FROM users WHERE id = %s', (user_id,))
    doctor = cursor.fetchone()

    # Fetch patients appointments for the logged-in doctor
    cursor.execute('''
        SELECT pa.patient_name, pa.appointment_time
        FROM patients_appointments pa
        JOIN appoitments a ON pa.appointment_id = a.id
        WHERE a.id = %s
    ''', (user_id,))
    patients_appointments = cursor.fetchall()

    cursor.close()

    return render_template('Appointments.html', doctor=doctor, patients_appointments=patients_appointments)


@app.route('/doctor_homepage')
@login_required
def doctor_homepage():
    user_id = session.get('user_id')
    cursor = get_db_connection()

    # Fetch doctor details
    cursor.execute('SELECT full_name, email FROM users WHERE id = %s', (user_id,))
    doctor = cursor.fetchone()

    # Fetch patients appointments for the logged-in doctor
    cursor.execute('''
        SELECT pa.patient_name, pa.appointment_time
        FROM patients_appointments pa
        JOIN appoitments a ON pa.appointment_id = a.id
        WHERE a.id = %s
    ''', (user_id,))
    patients_appointments = cursor.fetchall()

    cursor.close()

    return render_template('doctor_homepage.html', doctor=doctor, patients_appointments=patients_appointments)

@app.route('/addremovestaff')
@login_required
def addremovestaff():
    cursor = get_db_connection()
    cursor.execute("""
        SELECT users.id, users.full_name, users.email, staff.position, staff.department, staff.hire_date, staff.salary, staff.phone_number 
        FROM users
        JOIN staff ON users.id = staff.user_id
    """)
    staff_list = cursor.fetchall()
    cursor.close()
    return render_template('addremovestaff.html', staff_list=staff_list)

if __name__ == '__main__':
    app.run(debug=True)
