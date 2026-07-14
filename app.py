from flask import Flask, render_template, request, jsonify
import sqlite3
import base64
import numpy as np
import face_recognition
import pickle
from datetime import datetime
from io import BytesIO
from PIL import Image

app = Flask(__name__)

def init_db():
    print("Database setup start kar raha hoon...")
    conn = sqlite3.connect('database.db')
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


@app.route('/register', methods=['GET', 'POST'])
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
        conn = sqlite3.connect('database.db')
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
        return jsonify({'message': 'Image nahi mili'})

    try:
        img_array = decode_base64_image(image_data)
        face_locations = face_recognition.face_locations(img_array)

        if len(face_locations) == 0:
            return jsonify({'message': 'Koi face detect nahi hua.'})

        face_encs = face_recognition.face_encodings(img_array, face_locations)
        if len(face_encs) == 0:
            return jsonify({'message': 'Face encode nahi ho paya.'})

        current_encoding = face_encs[0]

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT id, name, roll_no, class, face_encoding FROM students')
        students = c.fetchall()

        best_match = None
        best_distance = 0.6

        for student_id, name, roll_no, student_class, encoding_blob in students:
            saved_encoding = pickle.loads(encoding_blob)
            distance = np.linalg.norm(saved_encoding - current_encoding)
            if distance < best_distance:
                best_distance = distance
                best_match = (student_id, name, roll_no, student_class)

        if best_match is None:
            conn.close()
            return jsonify({'message': 'Face match nahi hua. Pehle register karo!'})

        student_id, name, roll_no, student_class = best_match

        today = datetime.now().strftime('%Y-%m-%d')
        now_time = datetime.now().strftime('%H:%M:%S')

        c.execute('SELECT * FROM attendance WHERE student_id = ? AND date = ?', (student_id, today))
        existing = c.fetchone()

        if existing:
            conn.close()
            return jsonify({'message': name + ' ki attendance aaj pehle se mark hai.'})

        c.execute('INSERT INTO attendance (student_id, date, time, status) VALUES (?, ?, ?, ?)', (student_id, today, now_time, 'Present'))
        conn.commit()
        conn.close()

        return jsonify({'message': name + ' - Attendance marked! Time: ' + now_time})

    except Exception as e:
        print(e)
        return jsonify({'message': 'Error: ' + str(e)})


@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    query = "SELECT students.name, students.roll_no, students.class, attendance.date, attendance.time, attendance.status FROM attendance JOIN students ON attendance.student_id = students.id ORDER BY attendance.date DESC"
    c.execute(query)
    records = c.fetchall()
    conn.close()
    return render_template('dashboard.html', records=records)


if __name__ == '__main__':
    print("Flask server ab start ho raha hai...")
    app.run(debug=True)