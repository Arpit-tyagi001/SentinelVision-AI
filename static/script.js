function playBeep() {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    oscillator.type = 'sine';
    oscillator.frequency.value = 880;
    gainNode.gain.value = 0.3;

    oscillator.start();
    setTimeout(function () {
        oscillator.stop();
    }, 200);
}

function playClickSound() {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    oscillator.type = 'square';
    oscillator.frequency.value = 600;
    gainNode.gain.value = 0.15;

    oscillator.start();
    setTimeout(function () {
        oscillator.stop();
    }, 80);
}

document.addEventListener('DOMContentLoaded', function () {
    console.log('Attendance System loaded.');

    // NOTE: The automatic multi-face recognition loop that used to live
    // here (startAutoRecognition / captureAndRecognize / renderFaces) has
    // been removed. attendance.js and exit.js now own that responsibility
    // entirely for their respective pages, including liveness/blink
    // detection. Having two independent capture loops hitting
    // /mark-attendance at the same time caused them to race each other
    // and broke the blink-detection timing. This file now only handles:
    // register-page image capture, the register form submit, and the
    // dashboard delete buttons.

    let stream = null;
    let capturedImages = [];

    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');       // hidden capture canvas
    const overlay = document.getElementById('overlay');      // visible box-drawing canvas (used by attendance.js/exit.js, not here)

    // ---------- START CAMERA ----------
    // Kept generic (used by the register page, which has no auto-recognition
    // of its own). On mark_attendance.html / mark_exit.html, attendance.js /
    // exit.js handle camera start/stop themselves, so this handler simply
    // does nothing extra there beyond the click sound + local preview.
    const startCam = document.getElementById('startCam');
    if (startCam && video && !overlay) {
        // Only wire this up when there's no overlay canvas on the page —
        // i.e. NOT on the mark-attendance/mark-exit pages, which manage
        // their own camera lifecycle in attendance.js / exit.js.
        startCam.addEventListener('click', async function () {
            playClickSound();
            try {
                stream = await navigator.mediaDevices.getUserMedia({ video: true });
                video.srcObject = stream;
                console.log('Camera started successfully.');
            } catch (err) {
                console.error('Camera error:', err);
                alert('Camera access nahi mil paayi: ' + err.message);
            }
        });
    }

    // ---------- STOP CAMERA ----------
    const stopCam = document.getElementById('stopCam');
    if (stopCam && video && !overlay) {
        stopCam.addEventListener('click', function () {
            playClickSound();
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
                video.srcObject = null;
                stream = null;
                console.log('Camera stopped.');
            }
        });
    }

    // ---------- REGISTER PAGE: CAPTURE 5 IMAGES ----------
    const captureBtn = document.getElementById('captureBtn');
    if (captureBtn && video && canvas) {
        captureBtn.addEventListener('click', async function () {
            playClickSound();
            if (!stream) {
                alert('Pehle camera start karo!');
                return;
            }

            capturedImages = [];
            const statusDiv = document.getElementById('captureStatus');
            const ctx = canvas.getContext('2d');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            for (let i = 0; i < 5; i++) {
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                const dataUrl = canvas.toDataURL('image/jpeg');
                capturedImages.push(dataUrl);
                statusDiv.textContent = `📸 Capturing... ${i + 1}/5`;
                await new Promise(resolve => setTimeout(resolve, 500));
            }

            statusDiv.textContent = '✅ 5 images captured! Ab "Register" button dabao.';
            console.log('Captured images:', capturedImages.length);
        });
    }

    // ---------- REGISTER FORM SUBMIT ----------
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            if (capturedImages.length < 5) {
                alert('Pehle 5 images capture karo!');
                return;
            }

            const name = document.getElementById('name').value;
            const roll_no = document.getElementById('roll_no').value;
            const studentClass = document.getElementById('class').value;

            const statusDiv = document.getElementById('captureStatus');
            statusDiv.textContent = '⏳ Registering... please wait';

            try {
                const response = await fetch('/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name: name,
                        roll_no: roll_no,
                        class: studentClass,
                        images: capturedImages
                    })
                });

                const result = await response.json();

                if (result.success) {
                    statusDiv.textContent = '✅ ' + result.message;
                    alert('Student registered successfully!');
                    registerForm.reset();
                    capturedImages = [];
                    if (stream) {
                        stream.getTracks().forEach(track => track.stop());
                        video.srcObject = null;
                        stream = null;
                    }
                } else {
                    statusDiv.textContent = '❌ ' + result.message;
                    alert('Error: ' + result.message);
                }
            } catch (err) {
                console.error('Registration error:', err);
                statusDiv.textContent = '❌ Registration failed';
                alert('Server error: ' + err.message);
            }
        });
    }

    // ---------- DASHBOARD: DELETE ATTENDANCE ----------
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(function (btn) {
        btn.addEventListener('click', async function () {
            const attendanceId = btn.getAttribute('data-id');
            const confirmDelete = confirm('Kya aap yeh record delete karna chahte ho?');

            if (!confirmDelete) return;

            try {
                const response = await fetch('/delete-attendance/' + attendanceId, {
                    method: 'POST'
                });
                const result = await response.json();

                if (result.success) {
                    const row = document.getElementById('row-' + attendanceId);
                    if (row) row.remove();
                } else {
                    alert('Delete fail hua: ' + result.message);
                }
            } catch (err) {
                console.error('Delete error:', err);
                alert('Server error hua delete karte waqt.');
            }
        });
    });
});
