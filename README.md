# 📸 Face Attendance Recognition System

> **An AI-powered attendance management system that uses real-time face recognition to identify students and maintain attendance records automatically.**

A full-stack computer vision application built with **Python, Flask, OpenCV, face_recognition, and SQLite**. Students can register their faces through a webcam, and the system can recognize registered students from a live camera feed and record their attendance.

---

## 🌟 Overview

Traditional attendance systems can be time-consuming and require manual record keeping.

This project explores how **computer vision and face recognition** can be integrated into a web application to automate the process.

### The system provides:

* 👤 Student face registration
* 📷 Real-time webcam processing
* 🧠 Face detection and recognition
* ✅ Automated attendance marking
* 🚫 Duplicate attendance prevention
* 📊 Attendance dashboard
* 🗄️ Persistent SQLite storage

---

## ✨ Key Features

### 👤 Face Registration

Students can register their identity and facial data through the webcam.

* Enter **Name, Roll Number, and Class**
* Capture **5 face images**
* Process facial information for recognition
* Store student information in SQLite

### 🧠 Real-Time Face Recognition

The application processes webcam input and attempts to identify registered students.

```text
Webcam
   ↓
Face Detection
   ↓
Face Encoding
   ↓
Compare With Registered Faces
   ↓
Identify Student
```

### 🕒 Automated Attendance

Once a registered student is identified, the system can record their attendance.

* Records student information
* Stores attendance data
* Prevents duplicate attendance on the same day

### 📊 Attendance Dashboard

A dedicated dashboard provides a structured view of attendance records.

* Student information
* Attendance records
* Date-based records
* Easy-to-read tabular interface

### 🗄️ SQLite Database

SQLite is used as the application's local database.

The database stores:

* Student information
* Face recognition data
* Attendance records

---

## 🏗️ Application Architecture

```text
                         ┌─────────────────────┐
                         │      Frontend       │
                         │  HTML/CSS/JS        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       Flask         │
                         │    Web Backend      │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
          ┌──────────────────┐            ┌──────────────────┐
          │ Computer Vision  │            │    SQLite DB     │
          │                  │            │                  │
          │ OpenCV           │            │ Students         │
          │ face_recognition │            │ Attendance        │
          │ dlib             │            │ Records           │
          └──────────────────┘            └──────────────────┘
                    │
                    ▼
             Webcam Processing
                    │
                    ▼
             Face Recognition
                    │
                    ▼
            Attendance Update
```

---

## 🔄 System Workflow

```text
┌─────────────────────┐
│   Register Student  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Capture 5 Face      │
│ Images via Webcam   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Store Student Data  │
│ and Recognition     │
│ Information         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Start Live Camera   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Detect Face         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Recognize Face      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Identify Registered │
│ Student             │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Check Attendance    │
│ for Current Date    │
└──────────┬──────────┘
           │
      ┌────┴─────┐
      │          │
    Exists    New Entry
      │          │
      ▼          ▼
    Skip      Mark Present
                 │
                 ▼
        ┌─────────────────┐
        │ SQLite Database │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ Attendance      │
        │ Dashboard       │
        └─────────────────┘
```

---

## 🛠️ Tech Stack

| Layer                    | Technology              |
| ------------------------ | ----------------------- |
| **Programming Language** | Python                  |
| **Backend Framework**    | Flask                   |
| **Computer Vision**      | OpenCV                  |
| **Face Recognition**     | face_recognition, dlib  |
| **Database**             | SQLite3                 |
| **Frontend**             | HTML5, CSS3, JavaScript |
| **Version Control**      | Git & GitHub            |

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

## ⚙️ Getting Started

### Prerequisites

Make sure you have the following installed:

* Python 3.x
* Git
* Webcam
* pip

---

### 1. Clone the repository

```bash
git clone https://github.com/Shlokverma0/face-attendance-recognition-system.git
cd face-attendance-recognition-system
```

---

### 2. Create a virtual environment

```bash
python -m venv venv
```

---

### 3. Activate the environment

#### Windows

```bash
venv\Scripts\activate
```

#### macOS / Linux

```bash
source venv/bin/activate
```

---

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

If you encounter a `pkg_resources` error while installing `face_recognition`, try:

```bash
pip install "setuptools<81"
pip install git+https://github.com/ageitgey/face_recognition_models
```

---

### 5. Run the application

```bash
python app.py
```

The Flask development server should start locally.

---

### 6. Open the application

Open your browser and visit:

```text
http://127.0.0.1:5000
```

Make sure your browser/application has permission to access the webcam.

---

## 📖 How to Use

### Step 1 — Register a Student

Go to the **Register** page.

1. Start the camera
2. Capture 5 face images
3. Enter the student's name
4. Enter the roll number
5. Enter the class
6. Complete registration

---

### Step 2 — Mark Attendance

Go to the **Mark Attendance** page.

1. Start the camera
2. Allow the system to process the webcam feed
3. Let the system recognize the registered face
4. Mark the student as present
5. Attendance is stored in SQLite

---

### Step 3 — View Attendance

Open the **Dashboard**.

You can view the attendance information stored by the application in a structured table.

---

## 🔐 Duplicate Attendance Prevention

The application checks the existing attendance records before creating a new entry.

```text
Recognized Student
       │
       ▼
Check Today's Record
       │
       ▼
┌──────┴───────┐
│              │
Already       Not
Present       Present
│              │
▼              ▼
Skip         Record
Entry        Attendance
```

This prevents the same student from being recorded multiple times on the same day.

---

## 🎯 What I Learned

This project provided practical experience with:

* Computer vision fundamentals
* Real-time webcam processing
* Face detection and recognition
* Flask backend development
* SQLite database integration
* Connecting AI components with web applications
* Handling user registration workflows
* Designing a basic attendance management system
* Git and GitHub based collaboration

---

## 🚀 Future Roadmap

The project can be extended into a more production-ready attendance platform.

### 🔐 Authentication

* Admin login
* Teacher accounts
* Role-based access control

### 📊 Analytics

* Attendance percentage
* Student-wise statistics
* Class-wise analytics
* Monthly attendance reports
* Attendance trends

### 📥 Reporting

* Export attendance to CSV
* Generate PDF reports
* Automated attendance summaries

### ☁️ Cloud Infrastructure

* Cloud database
* Cloud deployment
* Remote attendance dashboard
* Centralized student management

### 🎥 Multi-Camera Support

* Multiple classroom cameras
* Separate entry and exit cameras
* Centralized attendance management

### 🔔 Notifications

* Email notifications
* Attendance alerts
* Absence notifications

### ⚡ Performance Improvements

* Faster face recognition
* Improved recognition accuracy
* Better handling of multiple faces
* Optimized camera processing

---

## ⚠️ Limitations

The current implementation is primarily designed for **local and educational use**.

Potential real-world deployments would require additional work around:

* Authentication and authorization
* Secure storage of biometric information
* Privacy and consent
* Database security
* Recognition accuracy
* Liveness detection
* Scalability
* Production deployment

---

## 🤝 Contributors

<table>
<tr>
<td align="center">

<a href="https://github.com/Arpit-tyagi001">
<img src="https://github.com/Arpit-tyagi001.png" width="100px;" alt="Arpit Tyagi"/>
<br />
<b>Arpit Tyagi</b>
</a>

</td>

<td align="center">

<a href="https://github.com/shlokverma0">
<img src="https://github.com/shlokverma0.png" width="100px;" alt="Shlok Verma"/>
<br />
<b>Shlok Verma</b>
</a>

</td>
</tr>
</table>

---

## 📄 License

This project is open source and available for **educational and learning purposes**.

---

## ⭐ Support

If you found this project useful or interesting, consider giving the repository a ⭐ on GitHub.

**Built with Python, Computer Vision, and a lot of experimentation. 🚀**
