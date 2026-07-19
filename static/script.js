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

    let stream = null;
    let capturedImages = [];

    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');       // hidden capture canvas
    const overlay = document.getElementById('overlay');     // visible box-drawing canvas

    // ---------- START CAMERA ----------
    const startCam = document.getElementById('startCam');
    if (startCam && video) {
        startCam.addEventListener('click', async function () {
            playClickSound();
            try {
                stream = await navigator.mediaDevices.getUserMedia({ video: true });
                video.srcObject = stream;
                console.log('Camera started successfully.');

                // If we're on the mark-attendance page, kick off auto recognition
                if (overlay) {
                    video.addEventListener('loadedmetadata', function onMeta() {
                        video.removeEventListener('loadedmetadata', onMeta);
                        startAutoRecognition();
                    });
                }
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
            playClickSound();
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
                video.srcObject = null;
                stream = null;
                console.log('Camera stopped.');
            }
            stopAutoRecognition();
            if (overlay) {
                const octx = overlay.getContext('2d');
                octx.clearRect(0, 0, overlay.width, overlay.height);
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

    // ---------- MARK ATTENDANCE PAGE: AUTOMATIC MULTI-FACE RECOGNITION ----------
    let recognitionTimer = null;
    let isBusy = false;                 // prevents overlapping requests
    const alreadyBeeped = new Set();    // avoid repeat beep spam for same person this session

    function startAutoRecognition() {
        if (!video || !canvas || !overlay) return;
        if (recognitionTimer) return; // already running

        overlay.width = video.videoWidth;
        overlay.height = video.videoHeight;

        recognitionTimer = setInterval(captureAndRecognize, 1500); // every 1.5s
    }

    function stopAutoRecognition() {
        if (recognitionTimer) {
            clearInterval(recognitionTimer);
            recognitionTimer = null;
        }
    }

    async function captureAndRecognize() {
        if (!stream || isBusy) return;
        isBusy = true;

        try {
            const ctx = canvas.getContext('2d');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            const imageData = canvas.toDataURL('image/jpeg');

            const response = await fetch('/mark-attendance', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: imageData })
            });

            const result = await response.json();
            renderFaces(result.faces || [], result.message);
        } catch (err) {
            console.error('Recognition error:', err);
        } finally {
            isBusy = false;
        }
    }

    function renderFaces(faces, noFaceMessage) {
        const resultDiv = document.getElementById('attendanceResult');
        const octx = overlay.getContext('2d');
        octx.clearRect(0, 0, overlay.width, overlay.height);

        if (!faces || faces.length === 0) {
            if (resultDiv) resultDiv.textContent = noFaceMessage || 'Koi face detect nahi hua.';
            return;
        }

        const lines = [];

        faces.forEach(function (face) {
            const [top, right, bottom, left] = face.box;
            const boxColor = face.status === 'marked' ? '#22c55e'
                            : face.status === 'already_marked' ? '#3b82f6'
                            : '#ef4444';

            octx.strokeStyle = boxColor;
            octx.lineWidth = 3;
            octx.strokeRect(left, top, right - left, bottom - top);

            octx.fillStyle = boxColor;
            octx.font = '18px sans-serif';
            const label = face.name || 'Unknown';
            const textY = top > 20 ? top - 8 : bottom + 20;
            octx.fillText(label, left, textY);

            lines.push(face.message);

            if (face.status === 'marked' && !alreadyBeeped.has(face.name)) {
                alreadyBeeped.add(face.name);
                playBeep();
            }
        });

        if (resultDiv) resultDiv.innerHTML = lines.join('<br>');
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