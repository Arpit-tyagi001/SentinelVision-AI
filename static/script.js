document.addEventListener('DOMContentLoaded', function () {
    console.log('Attendance System loaded.');

    let stream = null;
    let capturedImages = []; // base64 images yahan store honge

    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');

    // ---------- START CAMERA (dono pages ke liye kaam karega) ----------
    const startCam = document.getElementById('startCam');
    if (startCam && video) {
        startCam.addEventListener('click', async function () {
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
    if (stopCam && video) {
        stopCam.addEventListener('click', function () {
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
            if (!stream) {
                alert('Pehle camera start karo! (Is page pe "Start Camera" button add karna hoga)');
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
                await new Promise(resolve => setTimeout(resolve, 500)); // 0.5 sec gap
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

    // ---------- MARK ATTENDANCE PAGE ----------
    const markBtn = document.getElementById('markBtn');
    if (markBtn && video && canvas) {
        markBtn.addEventListener('click', async function () {
            if (!stream) {
                alert('Pehle camera start karo!');
                return;
            }

            const ctx = canvas.getContext('2d');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            const imageData = canvas.toDataURL('image/jpeg');

            const resultDiv = document.getElementById('attendanceResult');
            resultDiv.textContent = '⏳ Recognizing face...';

            try {
                const response = await fetch('/mark-attendance', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image: imageData })
                });

                const result = await response.json();
                resultDiv.textContent = result.message;
            } catch (err) {
                console.error('Attendance error:', err);
                resultDiv.textContent = '❌ Error marking attendance';
            }
        });
    }
});