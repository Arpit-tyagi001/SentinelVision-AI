from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import sqlite3
import base64
import numpy as np
import face_recognition
import pickle
from datetime import datetime
from io import BytesIO
from PIL import Image

app = Flask(__name__)
app.secret_key = 'shlok-face-attendance-secret-key-2026'  # used to sign the session cookie

# ---- Admin credentials ----
ADMIN_USERNAME = 'shlokverma'
ADMIN_PASSWORD = 'Shlok2026'


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def init_db():
    print("Database setup start kar raha hoon...")
    conn = sqlite3.connect('database.db', timeout=10)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        roll_no TEXT UNIQUE NOT NULL,
        class TEXT NOT NULL,
        face_encoding BLOB NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        date DATE NOT NULL,
        time TIME NOT NULL,
        status TEXT DEFAULT 'Present'
    )''')
    conn.commit()
    conn.close()
    print("Database ready.")

init_db()


def decode_base64_image(base64_string):
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]
    img_bytes = base64.b64decode(base64_string)
    img = Image.open(BytesIO(img_bytes)).convert('RGB')
    return np.array(img)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username')
    password = request.form.get('password')

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['logged_in'] = True
        session['username'] = username
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', error='Galat username ya password!')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if request.method == 'GET':
        return render_template('register.html')

    data = request.get_json()
    name = data.get('name')
    roll_no = data.get('roll_no')
    student_class = data.get('class')
    images = data.get('images', [])

    if not name or not roll_no or not student_class:
        return jsonify({'success': False, 'message': 'Sab fields fill karo!'})

    if len(images) < 5:
        return jsonify({'success': False, 'message': 'Kam se kam 5 images chahiye!'})

    encodings = []
    for img_data in images:
        try:
            img_array = decode_base64_image(img_data)
            face_locations = face_recognition.face_locations(img_array)
            if len(face_locations) == 0:
                continue
            face_encs = face_recognition.face_encodings(img_array, face_locations)
            if len(face_encs) > 0:
                encodings.append(face_encs[0])
        except Exception as e:
            print(e)
            continue

    if len(encodings) == 0:
        return jsonify({'success': False, 'message': 'Face detect nahi hua. Dobara try karo.'})

    avg_encoding = np.mean(encodings, axis=0)
    encoding_blob = pickle.dumps(avg_encoding)

    try:
        conn = sqlite3.connect('database.db', timeout=10)
        c = conn.cursor()
        c.execute('INSERT INTO students (name, roll_no, class, face_encoding) VALUES (?, ?, ?, ?)', (name, roll_no, student_class, encoding_blob))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': name + ' successfully register ho gaya!'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Yeh Roll Number pehle se register hai!'})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Database error: ' + str(e)})


@app.route('/mark-attendance', methods=['GET', 'POST'])
def mark_attendance():
    if request.method == 'GET':
        return render_template('mark_attendance.html')

    data = request.get_json()
    image_data = data.get('image')

    if not image_data:
        return jsonify({'faces': [], 'error': 'Image nahi mili'})

    try:
        img_array = decode_base64_image(image_data)
        # Detect ALL faces in the frame (multi-face support)
        face_locations = face_recognition.face_locations(img_array)

        if len(face_locations) == 0:
            return jsonify({'faces': [], 'message': 'Koi face detect nahi hua.'})

        face_encs = face_recognition.face_encodings(img_array, face_locations)

        conn = sqlite3.connect('database.db', timeout=10)
        c = conn.cursor()
        c.execute('SELECT id, name, roll_no, class, face_encoding FROM students')
        students = c.fetchall()

        # Pre-decode all saved encodings once (faster than re-loading per face)
        known = []
        for student_id, name, roll_no, student_class, encoding_blob in students:
            known.append((student_id, name, roll_no, student_class, pickle.loads(encoding_blob)))

        today = datetime.now().strftime('%Y-%m-%d')
        now_time = datetime.now().strftime('%H:%M:%S')

        results = []

        for (top, right, bottom, left), current_encoding in zip(face_locations, face_encs):
            best_match = None
            best_distance = 0.6  # recognition threshold

            for student_id, name, roll_no, student_class, saved_encoding in known:
                distance = np.linalg.norm(saved_encoding - current_encoding)
                if distance < best_distance:
                    best_distance = distance
                    best_match = (student_id, name, roll_no, student_class)

            face_result = {
                'box': [top, right, bottom, left]
            }

            if best_match is None:
                face_result['name'] = 'Unknown'
                face_result['status'] = 'unknown'
                face_result['message'] = 'Face match nahi hua. Pehle register karo!'
                results.append(face_result)
                continue

            student_id, name, roll_no, student_class = best_match
            face_result['name'] = name
            face_result['roll_no'] = roll_no

            # Check if already marked today
            c.execute('SELECT * FROM attendance WHERE student_id = ? AND date = ?', (student_id, today))
            existing = c.fetchone()

            if existing:
                face_result['status'] = 'already_marked'
                face_result['message'] = name + ' ki attendance aaj pehle se mark hai.'
            else:
                c.execute('INSERT INTO attendance (student_id, date, time, status) VALUES (?, ?, ?, ?)', (student_id, today, now_time, 'Present'))
                conn.commit()
                face_result['status'] = 'marked'
                face_result['message'] = '✅ ' + name + ' - Attendance marked! Time: ' + now_time

            results.append(face_result)

        conn.close()
        return jsonify({'faces': results})

    except Exception as e:
        print(e)
        return jsonify({'faces': [], 'error': str(e)})


@app.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect('database.db', timeout=10)
    c = conn.cursor()
    query = "SELECT attendance.id, students.name, students.roll_no, students.class, attendance.date, attendance.time, attendance.status FROM attendance JOIN students ON attendance.student_id = students.id ORDER BY attendance.date DESC"
    c.execute(query)
    records = c.fetchall()
    conn.close()
    return render_template('dashboard.html', records=records)


@app.route('/delete-attendance/<int:attendance_id>', methods=['POST'])
@login_required
def delete_attendance(attendance_id):
    try:
        conn = sqlite3.connect('database.db', timeout=10)
        c = conn.cursor()
        c.execute('DELETE FROM attendance WHERE id = ?', (attendance_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Record deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


if __name__ == '__main__':
    print("Flask server ab start ho raha hai...")
    app.run(debug=True)