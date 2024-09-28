document.addEventListener('DOMContentLoaded', function() {
    // Initialize Typed.js for dynamic text
    var options = {
        strings: ["உழுதுண்டு வாழ்வாரே வாழ்வார்மற் றெல்லாம் <br>தொழுதுண்டு பின்செல் பவர்.&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; -திருவள்ளுவர்"],
        typeSpeed: 40,
        backSpeed: 30,
        loop: true
    };
    var typed = new Typed("#quote", options);

    // Input method selection
    const inputMethod = document.getElementById('input-method');
    const uploadSection = document.getElementById('upload-section');
    const webcamSection = document.getElementById('webcam-section');

    inputMethod.addEventListener('change', function() {
        if (this.value === 'upload') {
            uploadSection.style.display = 'block';
            webcamSection.style.display = 'none';
        } else {
            uploadSection.style.display = 'none';
            webcamSection.style.display = 'block';
        }
    });

    // File upload preview
    const fileInput = document.querySelector('input[type="file"]');
    const preview = document.createElement('img');
    preview.style.maxWidth = '300px';
    preview.style.display = 'block';
    preview.style.margin = '10px auto';

    fileInput.addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.src = e.target.result;
                uploadSection.insertBefore(preview, uploadSection.firstChild);
                preview.classList.add('animate_animated', 'animate_zoomIn');
            }
            reader.readAsDataURL(file);
        }
    });

    // Webcam functionality with OpenCV
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const startButton = document.getElementById('start-camera');
    const stopButton = document.getElementById('stop-camera');
    let stream = null;
    let cap = null;

    startButton.addEventListener('click', async function() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
            startButton.style.display = 'none';
            stopButton.style.display = 'inline-block';
            startWebcamPrediction();
        } catch (err) {
            console.error("Error accessing the camera: ", err);
        }
    });

    stopButton.addEventListener('click', function() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            video.srcObject = null;
            startButton.style.display = 'inline-block';
            stopButton.style.display = 'none';
            if (cap !== null) {
                cap.release();
                cap = null;
            }
        }
    });

    function startWebcamPrediction() {
        cap = new cv.VideoCapture(video);
        const FPS = 1;
        function processVideo() {
            try {
                let begin = Date.now();
                let src = new cv.Mat(video.height, video.width, cv.CV_8UC4);
                cap.read(src);
                cv.imshow('canvas', src);
                src.delete();

                // Send frame to server for prediction
                canvas.toBlob(blob => {
                    const formData = new FormData();
                    formData.append('image', blob, 'webcam-image.jpg');
                    
                    fetch('/webcam_predict/', {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('current-prediction').textContent = 'Disease:${data.prediction}';
                        updatePredictionHistory(data.prediction);
                    })
                    .catch(error => console.error('Error:', error));
                }, 'image/jpeg');

                // Schedule next frame
                let delay = 1000/FPS - (Date.now() - begin);
                setTimeout(processVideo, delay);
            } catch (err) {
                console.error(err);
            }
        }
        setTimeout(processVideo, 0);
    }

    function updatePredictionHistory(prediction) {
        const historyList = document.getElementById('prediction-history');
        const newPrediction = document.createElement('li');
        newPrediction.textContent = '${new Date().toLocaleString()} - ${prediction}';
        newPrediction.classList.add('animate_animated', 'animate_fadeInLeft');
        historyList.insertBefore(newPrediction, historyList.firstChild);
    }

    // Toggle history
    const toggleHistoryButton = document.getElementById('toggle-history');
    const historyContainer = document.getElementById('history-container');

    toggleHistoryButton.addEventListener('click', function() {
        if (historyContainer.style.display === 'none') {
            historyContainer.style.display = 'block';
            toggleHistoryButton.textContent = 'Hide History';
        } else {
            historyContainer.style.display = 'none';
            toggleHistoryButton.textContent = 'Show History';
        }
    });

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});