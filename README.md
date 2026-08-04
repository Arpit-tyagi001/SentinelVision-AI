# 📸 Face Attendance Recognition System

An AI-powered **face recognition based attendance management system** built with Python and Flask. The system allows students to register their faces using a webcam and automatically marks attendance when their face is recognized.

Built as a practical computer vision project combining **face recognition, real-time webcam processing, Flask, and SQLite**.

---

## ✨ Features

### 👤 Student Registration

* Register students with **Name, Roll Number, and Class**
* Capture **5 face images** through the webcam
* Store registered student information in SQLite

### 🧠 Face Recognition

* Real-time webcam-based face detection and recognition
* Matches live faces against registered students
* Automatically identifies recognized students

### 🕒 Attendance Management

* Automatically records attendance for recognized students
* Prevents duplicate attendance entries on the same day
* Stores attendance records with student information

### 📊 Attendance Dashboard

* View attendance records through a web dashboard
* Display student and attendance information in a structured table

### 🗄️ Database

* Uses **SQLite3** for lightweight local data storage
* Maintains student and attendance records

---

## 🛠️ Tech Stack

| Category             | Technologies           |
| -------------------- | ---------------------- |
| **Language**         | Python                 |
| **Backend**          | Flask                  |
| **Computer Vision**  | OpenCV                 |
| **Face Recognition** | face_recognition, dlib |
| **Database**         | SQLite3                |
| **Frontend**         | HTML, CSS, JavaScript  |
| **Version Control**  | Git, GitHub            |

---

## 🏗️ System Workflow

```text
        ┌─────────────────────┐
        │   Student Register  │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │ Capture Face Images │
        │      via Webcam     │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │ Store Student Data  │
        │    in SQLite DB     │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │   Live Webcam Feed  │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │ Face Detection &    │
        │    Recognition      │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │ Identify Registered │
        │      Student        │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │ Mark Attendance     │
        │   in SQLite DB      │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │ Attendance Dashboard│
        └─────────────────────┘
```

---

## 📂 Project Structure

```text
face-attendance-recognition-system/
│
├── static/
│   ├── style.css
│   └── script.js
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── mark_attendance.html
│   └── dashboard.html
│
├── app.py
├── database.db
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/Shlokverma0/face-attendance-recognition-system.git
cd face-attendance-recognition-system
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows**

```bash
venv\Scripts\activate
```

**macOS / Linux**

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

If you encounter a `pkg_resources` error while installing `face_recognition`, try:

```bash
pip install "setuptools<81"
pip install git+https://github.com/ageitgey/face_recognition_models
```

### 5. Start the application

```bash
python app.py
```

### 6. Open the application

Visit:

```text
http://127.0.0.1:5000
```

---

## 📖 Usage

### Step 1 — Register a Student

Navigate to the **Register** page.

1. Start the webcam
2. Capture 5 face images
3. Enter the student's details
4. Register the student

### Step 2 — Mark Attendance

Navigate to **Mark Attendance**.

1. Start the webcam
2. Allow the system to recognize the student's face
3. Click **Mark Present**
4. The attendance record is stored in the database

### Step 3 — View Attendance

Open the **Dashboard** to view stored attendance records.

---

## 🔐 Attendance Logic

The system checks whether a recognized student has already been marked present on the same day.

```text
Recognize Face
      ↓
Find Student
      ↓
Check Today's Attendance
      ↓
 ┌────┴────┐
 │         │
Exists    Doesn't Exist
 │         │
 ▼         ▼
Skip     Mark Present
```

This helps prevent duplicate attendance records for the same student on the same day.

---

## 🎯 Project Objectives

* Apply computer vision to a real-world attendance problem
* Implement webcam-based face recognition
* Build a web interface using Flask
* Manage student and attendance data using SQLite
* Understand the integration of AI components with a backend application

---

## 🚀 Future Improvements

Potential improvements for future versions include:

* 🔐 Authentication for teachers and administrators
* 📱 Responsive mobile-friendly dashboard
* 📈 Attendance analytics and statistics
* 📥 Export attendance reports to CSV/PDF
* ☁️ Cloud database integration
* 🎥 Support for multiple camera sources
* 🔔 Real-time attendance notifications
* ⚡ Improved recognition performance
* 🧑‍💼 Admin and teacher role management

---

## 🤝 Contributors

* **[Arpit Tyagi](https://github.com/Arpit-tyagi001)**
* **[Shlok Verma](https://github.com/shlokverma0)**

---

## ⚠️ Disclaimer

This project is intended for **educational and experimental purposes**. Face recognition involves biometric data, so any real-world deployment should consider appropriate privacy, security, consent, and data-protection requirements.

---

## 📄 License

This project is open source and available for educational purposes.
