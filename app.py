from flask import Flask, render_template
import sqlite3
import os

app = Flask(__name__)

def init_db():
    print("🔄 Database setup start kar raha hoon...")
    
    # Agar pehle se hai toh delete nahi karenge, bas connect karenge
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Students table
    c.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        roll_no TEXT UNIQUE NOT NULL,
        class TEXT NOT NULL,
        face_encoding BLOB NOT NULL
    )''')
    
    # Attendance table
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        date DATE NOT NULL,
        time TIME NOT NULL,
        status TEXT DEFAULT 'Present'
    )''')
    
    conn.commit()
    conn.close()
    print("✅ Database 'database.db' aur dono tables successfully create/verify ho gayi!")

# Sabse pehle database initialize karo
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/mark-attendance')
def mark_attendance():
    return render_template('mark_attendance.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
@app.route('/test-camera')
def test_camera():
    import cv2
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    if ret:
        return "✅ Camera accessible! Webcam sahi kaam kar raha hai."
    else:
        return "❌ Camera not found! Webcam check karo."

if __name__ == '__main__':
    print("🚀 Flask server ab start ho raha hai...")
    app.run(debug=True)