// attendance.js
// Single camera page — automatically detects entry vs exit based on
// each person's attendance state today. Endpoint comes from a data
// attribute on the .card div.

document.addEventListener('DOMContentLoaded', function () {
    const card = document.querySelector('.card[data-endpoint]');
    if (!card) return; // not on an attendance page

    const ENDPOINT = card.dataset.endpoint;

    const video = document.getElementById('video');
    const overlay = document.getElementById('overlay');
    const canvas = document.getElementById('canvas');
    const startBtn = document.getElementById('startCam');
    const stopBtn = document.getElementById('stopCam');
    const resultDiv = document.getElementById('attendanceResult');

    const ctx = overlay.getContext('2d');
    const captureCtx = canvas.getContext('2d');

    let stream = null;
    let captureInterval = null;
    const NORMAL_INTERVAL_MS = 2000;  // normal polling rate
    const FAST_INTERVAL_MS = 250;     // fast rate while waiting for a blink,
                                       // fast enough to actually catch the
                                       // ~150-400ms window eyes are closed
    let currentIntervalMs = NORMAL_INTERVAL_MS;

    // Track recently shown messages per roll_no so we don't spam the UI
    // every single interval with the same message.
    const lastMessageByRoll = {};

    async function startCamera() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;

            video.onloadedmetadata = () => {
                overlay.width = video.videoWidth;
                overlay.height = video.videoHeight;
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
            };

            currentIntervalMs = NORMAL_INTERVAL_MS;
            captureInterval = setInterval(captureAndSend, currentIntervalMs);
        } catch (err) {
            console.error('Camera error:', err);
            resultDiv.innerHTML = '<p class="error">❌ Camera access denied or unavailable.</p>';
        }
    }

    function setCaptureRate(ms) {
        if (ms === currentIntervalMs) return;
        currentIntervalMs = ms;
        if (captureInterval) {
            clearInterval(captureInterval);
            captureInterval = setInterval(captureAndSend, currentIntervalMs);
        }
    }

    function stopCamera() {
        if (captureInterval) {
            clearInterval(captureInterval);
            captureInterval = null;
        }
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
        video.srcObject = null;
        ctx.clearRect(0, 0, overlay.width, overlay.height);
    }

    function captureAndSend() {
        if (!video.videoWidth || !video.videoHeight) return;

        captureCtx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageData = canvas.toDataURL('image/jpeg', 0.8);

        fetch(ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageData })
        })
            .then(res => res.json())
            .then(data => handleResponse(data))
            .catch(err => console.error('Fetch error:', err));
    }

    function handleResponse(data) {
        ctx.clearRect(0, 0, overlay.width, overlay.height);

        if (data.error) {
            resultDiv.innerHTML = '<p class="error">❌ ' + data.error + '</p>';
            return;
        }

        if (!data.faces || data.faces.length === 0) {
            setCaptureRate(NORMAL_INTERVAL_MS);
            if (data.message) {
                resultDiv.innerHTML = '<p>' + data.message + '</p>';
            }
            return;
        }

        const anyPending = data.faces.some(f => f.status === 'liveness_pending');
        setCaptureRate(anyPending ? FAST_INTERVAL_MS : NORMAL_INTERVAL_MS);

        let messagesHtml = '';

        data.faces.forEach(face => {
            drawBox(face);

            if (face.status === 'liveness_pending' && typeof face.ear !== 'undefined') {
                console.log('[liveness] ' + face.name + ' EAR = ' + face.ear);
            }

            const key = face.roll_no || face.name || 'unknown';

            // Avoid re-printing the exact same message repeatedly
            if (lastMessageByRoll[key] === face.message) return;
            lastMessageByRoll[key] = face.message;

            let cssClass = 'info';
            if (face.status === 'marked') cssClass = 'success';
            else if (face.status === 'already_marked') cssClass = 'warning';
            else if (face.status === 'liveness_pending') cssClass = 'info';
            else if (face.status === 'unknown') cssClass = 'error';

            messagesHtml += '<p class="' + cssClass + '">' + face.message + '</p>';
        });

        if (messagesHtml) {
            resultDiv.innerHTML = messagesHtml + resultDiv.innerHTML;
        }
    }

    function drawBox(face) {
        if (!face.box) return;
        const [top, right, bottom, left] = face.box;

        let color = '#888'; // unknown / default
        if (face.status === 'marked' && face.action === 'entry') color = '#22c55e';   // green = entry
        else if (face.status === 'marked' && face.action === 'exit') color = '#3b82f6'; // blue = exit
        else if (face.status === 'already_marked') color = '#f59e0b'; // amber = cooldown wait
        else if (face.status === 'liveness_pending') color = '#a855f7'; // purple = please blink

        ctx.strokeStyle = color;
        ctx.lineWidth = 3;
        ctx.strokeRect(left, top, right - left, bottom - top);

        const label = face.name || 'Unknown';
        ctx.font = '16px Arial';
        const textWidth = ctx.measureText(label).width;

        ctx.fillStyle = color;
        ctx.fillRect(left, bottom, textWidth + 10, 22);

        ctx.fillStyle = '#000';
        ctx.fillText(label, left + 5, bottom + 16);
    }

    startBtn.addEventListener('click', startCamera);
    stopBtn.addEventListener('click', stopCamera);

    // Stop the camera cleanly if the user navigates away
    window.addEventListener('beforeunload', stopCamera);
});
