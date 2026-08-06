# 📸 Face Attendance Recognition System

> **An AI-powered attendance management system that uses real-time face recognition to automatically identify registered students and maintain attendance records.**

A full-stack computer vision application built with **Python, Flask, OpenCV, face_recognition, dlib, and SQLite**. The system allows students to register their faces using a webcam, recognizes registered students from a live camera feed, and automatically records attendance while preventing duplicate entries.

---

## 🚀 Project Overview

Manual attendance can be time-consuming, repetitive, and difficult to maintain at scale.

This project demonstrates how **computer vision, face recognition, and web technologies** can be combined to build an automated attendance management system.

The application provides a complete workflow:

**Register Student → Capture Face Data → Recognize Face → Verify Attendance → Store Record → View Dashboard**

### ✨ Core Capabilities

* 👤 Student registration with facial data
* 📷 Real-time webcam processing
* 🧠 Face detection and recognition
* ✅ Automated attendance marking
* 🚫 Same-day duplicate attendance prevention
* 📊 Attendance dashboard
* 🗄️ Persistent SQLite database
* 🌐 Flask-based web interface

---

## 🧠 How It Works

The system follows a simple computer-vision pipeline:

```text
                    ┌───────────────────┐
                    │   Student Camera  │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   Face Detection  │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Face Recognition  │
                    │   / Comparison    │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Identify Student  │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Check Attendance  │
                    │    for Today      │
                    └─────────┬─────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
              Already Present       New Entry
                    │                   │
                    ▼                   ▼
                  Skip            Mark Present
                                        │
                                        ▼
                              ┌─────────────────┐
                              │   SQLite DB     │
                              └────────┬────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │   Dashboard     │
                              └─────────────────┘
```

---

## ✨ Features

### 👤 1. Student Face Registration

Students can register their identity and facial information through the webcam.

**Registration flow:**

1. Enter student name
2. Enter roll number
3. Enter class
4. Capture **5 face images**
5. Process facial information
6. Store student data in SQLite

---

### 🧠 2. Real-Time Face Recognition

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

This allows the system to recognize students from a live camera feed.

---

### ✅ 3. Automated Attendance

After successfully recognizing a registered student, the application checks whether an attendance record already exists for the current date.

If no record exists:

```text
Recognized Student
        ↓
Check Today's Attendance
        ↓
No Existing Record
        ↓
Mark Present
        ↓
Store in SQLite
```

If attendance has already been recorded:

```text
Recognized Student
        ↓
Check Today's Attendance
        ↓
Record Already Exists
        ↓
Skip Duplicate Entry
```

---

### 📊 4. Attendance Dashboard

The dashboard provides a structured view of stored attendance information.

It can display:

* Student information
* Attendance records
* Date-based records
* Tabular attendance data

---

### 🗄️ 5. SQLite Database

SQLite is used as the application's local persistent database.

The database stores information related to:

* Students
* Face recognition data
* Attendance records

---

## 🏗️ System Architecture

```text
┌───────────────────────────────────────────────┐
│                  Frontend                     │
│              HTML / CSS / JS                 │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│                  Flask                        │
│              Web Application                  │
└───────────────────────┬───────────────────────┘
                        │
              ┌─────────┴─────────┐
              │                   │
              ▼                   ▼
┌──────────────────────┐   ┌──────────────────────┐
│   Computer Vision    │   │      SQLite DB        │
│                      │   │                      │
│ • OpenCV             │   │ • Students           │
│ • face_recognition   │   │ • Face Data          │
│ • dlib               │   │ • Attendance         │
└──────────┬───────────┘   └──────────────────────┘
           │
           ▼
┌──────────────────────┐
│   Webcam Processing  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Face Recognition   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Attendance Update    │
└──────────────────────┘
```

---

## 🛠️ Tech Stack

| Category                           | Technology              |
| ---------------------------------- | ----------------------- |
| **Language**                       | Python                  |
| **Backend**                        | Flask                   |
| **Computer Vision**                | OpenCV                  |
| **Face Recognition**               | face_recognition        |
| **Underlying Recognition Library** | dlib                    |
| **Database**                       | SQLite3                 |
| **Frontend**                       | HTML5, CSS3, JavaScript |
| **Version Control**                | Git & GitHub            |
| **Hardware**                       | Webcam                  |

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

# ⚙️ Getting Started

## 📋 Prerequisites

Before running the project, make sure you have:

* **Python 3.x**
* **Git**
* **pip**
* **Webcam**
* A working Python virtual environment

---

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/Shlokverma0/face-attendance-recognition-system.git

cd face-attendance-recognition-system
```

---

## 2️⃣ Create a Virtual Environment

### Windows

```bash
python -m venv venv
```

### macOS / Linux

```bash
python3 -m venv venv
```

---

## 3️⃣ Activate the Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

---

## 4️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

If you encounter a `pkg_resources` issue while installing `face_recognition`, the existing project setup suggests:

```bash
pip install "setuptools<81"
pip install git+https://github.com/ageitgey/face_recognition_models
```

> **Note:** `face_recognition` depends on `dlib`, so installation can vary depending on your Python version and operating system.

---

## 5️⃣ Run the Application

```bash
python app.py
```

The Flask development server should start locally.

---

## 6️⃣ Open the Application

Open your browser and visit:

```text
http://127.0.0.1:5000
```

Make sure your browser has permission to access the webcam.

---

# 📖 Usage Guide

## Step 1 — Register a Student

Navigate to the **Register** page.

1. Start the camera
2. Enter the student's name
3. Enter the roll number
4. Enter the class
5. Capture 5 face images
6. Complete the registration process

The student's information and recognition data are stored in the SQLite database.

---

## Step 2 — Mark Attendance

Navigate to the **Mark Attendance** page.

1. Start the camera
2. Allow the application to process the webcam feed
3. Let the system detect and recognize the face
4. Allow the system to identify the registered student
5. Attendance is recorded in SQLite

---

## Step 3 — View Attendance

Open the **Dashboard** to view the attendance information stored by the application.

---

# 🔐 Duplicate Attendance Prevention

The application checks the database before creating a new attendance record.

```text
                 Recognized Student
                         │
                         ▼
                Check Today's Record
                         │
                  ┌──────┴──────┐
                  │             │
               Exists         New
                  │             │
                  ▼             ▼
                 Skip       Mark Present
                                │
                                ▼
                         Store Attendance
```

This prevents the same student from being recorded multiple times on the same day.

---

# 🎯 Learning Outcomes

Building this project provided practical experience with:

* Computer vision fundamentals
* Real-time webcam processing
* Face detection and recognition
* Python web development with Flask
* SQLite database integration
* Connecting AI/computer-vision components with web applications
* Student registration workflows
* Attendance management logic
* Git and GitHub collaboration
* Structuring a full-stack computer-vision application

---

# 🚧 Current Limitations

The current implementation is primarily intended for **local and educational use**.

Before using a system like this in a real-world environment, additional engineering would be required for:

* 🔐 Authentication and authorization
* 🛡️ Secure biometric-data storage
* 🔏 Privacy and user consent
* 🗄️ Production-grade database security
* 🎯 Recognition accuracy improvements
* 🧍 Liveness / anti-spoofing detection
* ⚡ Scalability
* ☁️ Production deployment
* 📈 Monitoring and logging

> **Important:** Facial data is biometric information. Any real deployment should consider applicable privacy, consent, security, and data-protection requirements.

---

# 🚀 Future Roadmap

## 🔐 Authentication & Authorization

* [ ] Admin login
* [ ] Teacher accounts
* [ ] Role-based access control
* [ ] Secure session management

## 📊 Analytics

* [ ] Attendance percentage
* [ ] Student-wise statistics
* [ ] Class-wise analytics
* [ ] Monthly attendance reports
* [ ] Attendance trend visualization

## 📥 Reporting

* [ ] Export attendance to CSV
* [ ] Generate PDF reports
* [ ] Automated attendance summaries

## ☁️ Cloud Infrastructure

* [ ] Cloud database
* [ ] Cloud deployment
* [ ] Remote attendance dashboard
* [ ] Centralized student management

## 🎥 Multi-Camera Support

* [ ] Multiple classroom cameras
* [ ] Separate entry and exit cameras
* [ ] Centralized attendance management

## 🔔 Notifications

* [ ] Email notifications
* [ ] Attendance alerts
* [ ] Absence notifications

## ⚡ Performance & Accuracy

* [ ] Faster face recognition
* [ ] Improved recognition accuracy
* [ ] Better multi-face handling
* [ ] Optimized camera processing
* [ ] Liveness detection

---

# 🤝 Contributors

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

# 📄 License

This project is open source and intended primarily for **educational and learning purposes**.

---

# ⭐ Support

If you found this project useful or interesting, consider giving the repository a ⭐ on GitHub.

---

<div align="center">

### Built with 🐍 Python, 👁️ Computer Vision & 🚀 a lot of experimentation

**Face Attendance Recognition System**

</div>
