from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from functools import wraps
import sqlite3
import base64
import numpy as np
import face_recognition
import pickle
from datetime import datetime
from io import BytesIO
from PIL import Image
from openpyxl import Workbook
from openpyxl.styles import Font

app = Flask(__name__)
app.secret_key = 'shlok-face-attendance-secret-key-2026'  # used to sign the session cookie

# ---- Admin credentials ----
ADMIN_USERNAME = 'ADMIN'
ADMIN_PASSWORD = 'ADMIN'


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
    # NOTE: entry_time / exit_time replace the old single "time" column.
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        date DATE NOT NULL,
        entry_time TIME,
        exit_time TIME,
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

    DUPLICATE_FACE_THRESHOLD = 0.6  # same threshold used for recognition matching

    try:
        conn = sqlite3.connect('database.db', timeout=10)
        c = conn.cursor()

        # ---- Duplicate face check ----
        # Reject registration if this face is already registered under a
        # different (or the same) roll number, so one person can't be
        # enrolled twice and double up their attendance.
        c.execute('SELECT name, roll_no, face_encoding FROM students')
        existing_students = c.fetchall()

        for existing_name, existing_roll_no, existing_blob in existing_students:
            existing_encoding = pickle.loads(existing_blob)
            distance = np.linalg.norm(existing_encoding - avg_encoding)
            if distance < DUPLICATE_FACE_THRESHOLD:
                conn.close()
                return jsonify({
                    'success': False,
                    'message': 'Yeh face pehle se register hai: ' + existing_name + ' (Roll No: ' + existing_roll_no + ')'
                })

        c.execute('INSERT INTO students (name, roll_no, class, face_encoding) VALUES (?, ?, ?, ?)', (name, roll_no, student_class, encoding_blob))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': name + ' successfully register ho gaya!'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Yeh Roll Number pehle se register hai!'})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Database error: ' + str(e)})


def match_faces(img_array, known):
    """Run face detection + matching against known encodings. Returns list of
    (box, student_tuple_or_None) pairs."""
    face_locations = face_recognition.face_locations(img_array)
    if len(face_locations) == 0:
        return []

    face_encs = face_recognition.face_encodings(img_array, face_locations)
    matches = []

    for (top, right, bottom, left), current_encoding in zip(face_locations, face_encs):
        best_match = None
        best_distance = 0.6  # recognition threshold

        for student_id, name, roll_no, student_class, saved_encoding in known:
            distance = np.linalg.norm(saved_encoding - current_encoding)
            if distance < best_distance:
                best_distance = distance
                best_match = (student_id, name, roll_no, student_class)

        matches.append(([top, right, bottom, left], best_match))

    return matches


def load_known_students(c):
    """Fetch and unpickle all known face encodings. Shared by mark-attendance
    and mark-exit so both pages use the identical recognition pipeline."""
    c.execute('SELECT id, name, roll_no, class, face_encoding FROM students')
    students = c.fetchall()
    known = []
    for student_id, name, roll_no, student_class, encoding_blob in students:
        known.append((student_id, name, roll_no, student_class, pickle.loads(encoding_blob)))
    return known


# ---------------------------------------------------------------------------
# Liveness detection (anti-photo-spoofing)
#
# Uses the classic Eye Aspect Ratio (EAR) blink test: a real, live face will
# blink within a few seconds of being in front of the camera; a printed
# photo or a static image on a phone screen never will. Before any
# entry/exit is actually written to the database, the person must be
# observed going eyes-open -> eyes-closed -> eyes-open at least once.
#
# State is kept in a simple in-memory dict keyed by student_id. This is
# fine for a single-process college project; it resets if the server
# restarts, which just means everyone needs to blink again — not a problem.
# ---------------------------------------------------------------------------

liveness_state = {}

EAR_OPEN_THRESHOLD = 0.25     # eyes counted as "open" above this
EAR_CLOSED_THRESHOLD = 0.21   # eyes counted as "closed" below this
LIVENESS_WINDOW_SECONDS = 8   # if no blink within this long, restart tracking


def eye_aspect_ratio(eye_points):
    """Standard 6-point EAR formula. eye_points is a list of 6 (x, y) tuples
    as returned by face_recognition.face_landmarks()."""
    try:
        p = np.array(eye_points)
        vertical_1 = np.linalg.norm(p[1] - p[5])
        vertical_2 = np.linalg.norm(p[2] - p[4])
        horizontal = np.linalg.norm(p[0] - p[3])
        if horizontal == 0:
            return None
        return (vertical_1 + vertical_2) / (2.0 * horizontal)
    except Exception:
        return None


def compute_face_ear(img_array, face_location):
    """face_location must be a (top, right, bottom, left) tuple. Returns the
    average EAR across both eyes, or None if landmarks aren't available
    (e.g. face too small, extreme angle)."""
    try:
        landmarks_list = face_recognition.face_landmarks(img_array, [face_location])
    except Exception as e:
        print('Landmark detection error:', e)
        return None

    if not landmarks_list:
        return None

    landmarks = landmarks_list[0]
    left_eye = landmarks.get('left_eye')
    right_eye = landmarks.get('right_eye')
    if not left_eye or not right_eye:
        return None

    left_ear = eye_aspect_ratio(left_eye)
    right_ear = eye_aspect_ratio(right_eye)
    if left_ear is None or right_ear is None:
        return None

    return (left_ear + right_ear) / 2.0


def check_liveness(student_id, ear_value):
    """Tracks open -> closed -> open transitions per student. Returns True
    once a full blink has been confirmed within the tracking window."""
    now = datetime.now()
    entry = liveness_state.get(student_id)

    if entry is None or (now - entry['last_seen']).total_seconds() > LIVENESS_WINDOW_SECONDS:
        entry = {'state': 'open', 'blinked': False, 'last_seen': now}

    if ear_value is not None:
        if ear_value < EAR_CLOSED_THRESHOLD:
            entry['state'] = 'closed'
        elif ear_value > EAR_OPEN_THRESHOLD:
            if entry['state'] == 'closed':
                entry['blinked'] = True
            entry['state'] = 'open'

    entry['last_seen'] = now
    liveness_state[student_id] = entry
    return entry['blinked']


def clear_liveness(student_id):
    """Call this once a student's blink has been used to confirm an actual
    entry/exit write, so the next person doesn't inherit stale state."""
    liveness_state.pop(student_id, None)


@app.route('/mark-attendance', methods=['GET', 'POST'])
def mark_attendance():
    """Single camera page. Automatically decides ENTRY vs EXIT per person:
    - No record today yet -> mark entry
    - Entry exists, no exit yet -> mark exit
    - Both entry & exit already done -> mark a fresh re-entry (new cycle)
    A cooldown prevents the same person from toggling entry/exit every
    couple seconds just by standing in front of the camera.

    NOTE: left completely unmodified. The new /mark-exit route below is a
    separate, independent feature and does not change this route's behaviour.
    """
    if request.method == 'GET':
        return render_template('mark_attendance.html')

    data = request.get_json()
    image_data = data.get('image')

    if not image_data:
        return jsonify({'faces': [], 'error': 'Image nahi mili'})

    # Minimum gap (in seconds) required between an entry and the next
    # exit/entry action for the same person, so a person standing in
    # front of the camera doesn't get marked in and out repeatedly.
    COOLDOWN_SECONDS = 60

    try:
        img_array = decode_base64_image(image_data)

        conn = sqlite3.connect('database.db', timeout=10)
        c = conn.cursor()
        c.execute('SELECT id, name, roll_no, class, face_encoding FROM students')
        students = c.fetchall()

        known = []
        for student_id, name, roll_no, student_class, encoding_blob in students:
            known.append((student_id, name, roll_no, student_class, pickle.loads(encoding_blob)))

        matches = match_faces(img_array, known)

        if len(matches) == 0:
            conn.close()
            return jsonify({'faces': [], 'message': 'Koi face detect nahi hua.'})

        today = datetime.now().strftime('%Y-%m-%d')
        now_dt = datetime.now()
        now_time = now_dt.strftime('%H:%M:%S')

        results = []

        for box, best_match in matches:
            face_result = {'box': box}

            if best_match is None:
                face_result['name'] = 'Unknown'
                face_result['status'] = 'unknown'
                face_result['message'] = 'Face match nahi hua. Pehle register karo!'
                results.append(face_result)
                continue

            student_id, name, roll_no, student_class = best_match
            face_result['name'] = name
            face_result['roll_no'] = roll_no

            # Get the most recent row for this student today
            c.execute(
                'SELECT id, entry_time, exit_time FROM attendance '
                'WHERE student_id = ? AND date = ? ORDER BY id DESC LIMIT 1',
                (student_id, today)
            )
            existing = c.fetchone()

            def seconds_since(time_str):
                last_dt = datetime.strptime(today + ' ' + time_str, '%Y-%m-%d %H:%M:%S')
                return (now_dt - last_dt).total_seconds()

            if existing is None:
                # No record today at all -> mark entry, but only once a
                # live blink has been confirmed for this student.
                ear = compute_face_ear(img_array, tuple(box))
                if not check_liveness(student_id, ear):
                    face_result['status'] = 'liveness_pending'
                    face_result['message'] = '👁 ' + name + ' - Please blink to verify you are a real person.'
                else:
                    clear_liveness(student_id)
                    c.execute(
                        'INSERT INTO attendance (student_id, date, entry_time, status) VALUES (?, ?, ?, ?)',
                        (student_id, today, now_time, 'Present')
                    )
                    conn.commit()
                    face_result['status'] = 'marked'
                    face_result['action'] = 'entry'
                    face_result['message'] = '✅ ' + name + ' - Entry marked! Time: ' + now_time

            else:
                attendance_id, entry_time, exit_time = existing

                if entry_time is not None and exit_time is None:
                    # Currently "inside" -> next detection should mark exit,
                    # but only after the cooldown so we don't flip instantly.
                    if seconds_since(entry_time) < COOLDOWN_SECONDS:
                        face_result['status'] = 'already_marked'
                        face_result['action'] = 'entry'
                        face_result['message'] = name + ' ki entry abhi mark hui hai.'
                    else:
                        ear = compute_face_ear(img_array, tuple(box))
                        if not check_liveness(student_id, ear):
                            face_result['status'] = 'liveness_pending'
                            face_result['message'] = '👁 ' + name + ' - Please blink to verify you are a real person.'
                        else:
                            clear_liveness(student_id)
                            c.execute('UPDATE attendance SET exit_time = ? WHERE id = ?', (now_time, attendance_id))
                            conn.commit()
                            face_result['status'] = 'marked'
                            face_result['action'] = 'exit'
                            face_result['message'] = '👋 ' + name + ' - Exit marked! Time: ' + now_time

                else:
                    # Both entry & exit already done -> allow fresh re-entry,
                    # but respect cooldown after the exit too.
                    if exit_time is not None and seconds_since(exit_time) < COOLDOWN_SECONDS:
                        face_result['status'] = 'already_marked'
                        face_result['action'] = 'exit'
                        face_result['message'] = name + ' ki exit abhi mark hui hai.'
                    else:
                        ear = compute_face_ear(img_array, tuple(box))
                        if not check_liveness(student_id, ear):
                            face_result['status'] = 'liveness_pending'
                            face_result['message'] = '👁 ' + name + ' - Please blink to verify you are a real person.'
                        else:
                            clear_liveness(student_id)
                            c.execute(
                                'INSERT INTO attendance (student_id, date, entry_time, status) VALUES (?, ?, ?, ?)',
                                (student_id, today, now_time, 'Present')
                            )
                            conn.commit()
                            face_result['status'] = 'marked'
                            face_result['action'] = 'entry'
                            face_result['message'] = '✅ ' + name + ' - Re-entry marked! Time: ' + now_time

            results.append(face_result)

        conn.close()
        return jsonify({'faces': results})

    except Exception as e:
        print(e)
        return jsonify({'faces': [], 'error': str(e)})


@app.route('/mark-exit', methods=['GET', 'POST'])
def mark_exit():
    """Dedicated exit-only page/route. Does NOT touch /mark-attendance.

    Behaviour per employee detected:
    - Open record today (entry_time set, exit_time NULL) -> set exit_time.
    - Exit already recorded today                         -> "Exit already recorded."
    - No entry recorded today at all                      -> "Please mark entry first."
    Never creates a new attendance row.
    """
    if request.method == 'GET':
        return render_template('mark_exit.html')

    data = request.get_json(silent=True) or {}
    image_data = data.get('image')

    if not image_data:
        return jsonify({'faces': [], 'error': 'Image nahi mili'})

    conn = None
    try:
        img_array = decode_base64_image(image_data)

        conn = sqlite3.connect('database.db', timeout=10)
        c = conn.cursor()
        known = load_known_students(c)

        matches = match_faces(img_array, known)

        if len(matches) == 0:
            conn.close()
            return jsonify({'faces': [], 'message': 'Koi face detect nahi hua.'})

        today = datetime.now().strftime('%Y-%m-%d')
        now_time = datetime.now().strftime('%H:%M:%S')

        results = []

        for box, best_match in matches:
            face_result = {'box': box}

            if best_match is None:
                face_result['name'] = 'Unknown'
                face_result['status'] = 'unknown'
                face_result['message'] = 'Face match nahi hua. Pehle register karo!'
                results.append(face_result)
                continue

            student_id, name, roll_no, student_class = best_match
            face_result['name'] = name
            face_result['roll_no'] = roll_no

            try:
                # 1) Is there an OPEN record today (entry marked, exit not yet)?
                c.execute(
                    'SELECT id, entry_time, exit_time FROM attendance '
                    'WHERE student_id = ? AND date = ? AND entry_time IS NOT NULL AND exit_time IS NULL '
                    'ORDER BY id DESC LIMIT 1',
                    (student_id, today)
                )
                open_record = c.fetchone()

                if open_record:
                    attendance_id, entry_time, _ = open_record
                    ear = compute_face_ear(img_array, tuple(box))
                    if not check_liveness(student_id, ear):
                        face_result['status'] = 'liveness_pending'
                        face_result['entry_time'] = entry_time
                        face_result['message'] = '👁 ' + name + ' - Please blink to verify you are a real person.'
                    else:
                        clear_liveness(student_id)
                        c.execute(
                            "UPDATE attendance SET exit_time = ?, status = 'Completed' WHERE id = ?",
                            (now_time, attendance_id)
                        )
                        conn.commit()

                        face_result['status'] = 'marked'
                        face_result['entry_time'] = entry_time
                        face_result['exit_time'] = now_time
                        face_result['emp_status'] = 'Completed'
                        face_result['message'] = '👋 ' + name + ' - Exit marked! Time: ' + now_time

                else:
                    # 2) No open record — either already exited today, or never entered.
                    c.execute(
                        'SELECT entry_time, exit_time FROM attendance '
                        'WHERE student_id = ? AND date = ? AND entry_time IS NOT NULL AND exit_time IS NOT NULL '
                        'ORDER BY id DESC LIMIT 1',
                        (student_id, today)
                    )
                    completed = c.fetchone()

                    if completed:
                        entry_time, exit_time = completed
                        face_result['status'] = 'already_exited'
                        face_result['entry_time'] = entry_time
                        face_result['exit_time'] = exit_time
                        face_result['emp_status'] = 'Completed'
                        face_result['message'] = 'Exit already recorded.'
                    else:
                        face_result['status'] = 'no_entry'
                        face_result['entry_time'] = None
                        face_result['exit_time'] = None
                        face_result['emp_status'] = 'Not Entered'
                        face_result['message'] = 'Please mark entry first.'

            except sqlite3.Error as db_err:
                print('DB error while processing exit for student', student_id, ':', db_err)
                face_result['status'] = 'error'
                face_result['message'] = 'Database error while marking exit. Try again.'

            results.append(face_result)

        conn.close()
        return jsonify({'faces': results})

    except Exception as e:
        print(e)
        if conn:
            conn.close()
        return jsonify({'faces': [], 'error': str(e)})


@app.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect('database.db', timeout=10)
    c = conn.cursor()
    query = """
        SELECT attendance.id, students.name, students.roll_no, students.class,
               attendance.date, attendance.entry_time, attendance.exit_time, attendance.status
        FROM attendance
        JOIN students ON attendance.student_id = students.id
        ORDER BY attendance.date DESC, attendance.entry_time DESC
    """
    c.execute(query)
    records = c.fetchall()

    # ---- Dashboard statistics (today only) ----
    today = datetime.now().strftime('%Y-%m-%d')

    c.execute(
        'SELECT COUNT(DISTINCT student_id) FROM attendance WHERE date = ? AND entry_time IS NOT NULL',
        (today,)
    )
    total_present = c.fetchone()[0]

    c.execute(
        'SELECT COUNT(*) FROM attendance WHERE date = ? AND entry_time IS NOT NULL',
        (today,)
    )
    entry_count = c.fetchone()[0]

    c.execute(
        'SELECT COUNT(*) FROM attendance WHERE date = ? AND exit_time IS NOT NULL',
        (today,)
    )
    exit_count = c.fetchone()[0]

    c.execute(
        'SELECT COUNT(*) FROM attendance WHERE date = ? AND entry_time IS NOT NULL AND exit_time IS NULL',
        (today,)
    )
    still_inside = c.fetchone()[0]

    c.execute(
        'SELECT COUNT(*) FROM attendance WHERE date = ? AND entry_time IS NOT NULL AND exit_time IS NOT NULL',
        (today,)
    )
    completed_day = c.fetchone()[0]

    conn.close()

    stats = {
        'total_present': total_present,
        'entry_count': entry_count,
        'exit_count': exit_count,
        'still_inside': still_inside,
        'completed_day': completed_day,
    }

    return render_template('dashboard.html', records=records, stats=stats)


@app.route('/export-attendance')
@login_required
def export_attendance():
    """Generate an .xlsx export of the full attendance table on demand."""
    try:
        conn = sqlite3.connect('database.db', timeout=10)
        c = conn.cursor()
        query = """
            SELECT students.roll_no, students.name, students.class,
                   attendance.date, attendance.entry_time, attendance.exit_time, attendance.status
            FROM attendance
            JOIN students ON attendance.student_id = students.id
            ORDER BY attendance.date DESC, attendance.entry_time DESC
        """
        c.execute(query)
        records = c.fetchall()
        conn.close()

        wb = Workbook()
        ws = wb.active
        ws.title = 'Attendance'

        headers = ['Roll No', 'Name', 'Class', 'Date', 'Entry Time', 'Exit Time', 'Status']
        ws.append(headers)
        for col_idx in range(1, len(headers) + 1):
            ws.cell(row=1, column=col_idx).font = Font(bold=True)

        for roll_no, name, student_class, date, entry_time, exit_time, status in records:
            ws.append([
                roll_no,
                name,
                student_class,
                date,
                entry_time if entry_time else '-',
                exit_time if exit_time else '-',
                status
            ])

        # Auto-fit column widths roughly based on content length
        for column_cells in ws.columns:
            max_length = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column_cells)
            ws.column_dimensions[column_cells[0].column_letter].width = max_length + 4

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        filename = 'attendance_export_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.xlsx'

        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        print('Export error:', e)
        return jsonify({'success': False, 'message': 'Export failed: ' + str(e)}), 500


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
