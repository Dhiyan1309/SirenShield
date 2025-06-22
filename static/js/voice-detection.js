class VoiceDetector {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.stream = null;
        this.recordingInterval = null;
        this.currentLocation = null;
        this.emergencyPhrase = "help me";
    }

    async startRecording() {
        try {
            // Get location first
            await this.updateLocation();
            
            this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(this.stream);
            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };

            this.mediaRecorder.onstop = () => {
                this.processAudio();
            };

            // Start recording
            this.mediaRecorder.start();
            this.isRecording = true;

            // Record for 5 seconds (longer for better speech recognition)
            setTimeout(() => {
                this.stopRecording();
            }, 5000);

        } catch (error) {
            console.error('Error accessing microphone:', error);
            alert('Error accessing microphone. Please ensure you have granted microphone permissions.');
        }
    }

    async updateLocation() {
        return new Promise((resolve, reject) => {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    position => {
                        this.currentLocation = {
                            lat: position.coords.latitude,
                            lng: position.coords.longitude
                        };
                        resolve();
                    },
                    error => {
                        console.error('Error getting location:', error);
                        reject(error);
                    },
                    {
                        enableHighAccuracy: true,
                        timeout: 5000,
                        maximumAge: 0
                    }
                );
            } else {
                reject(new Error('Geolocation is not supported by this browser.'));
            }
        });
    }

    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.stream.getTracks().forEach(track => track.stop());
        }
    }

    async processAudio() {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');

        // Add location to form data
        if (this.currentLocation) {
            const location = `${this.currentLocation.lat},${this.currentLocation.lng}`;
            formData.append('location', location);
            this.sendToServer(formData);
        } else {
            // Try to get location again if not available
            try {
                await this.updateLocation();
                const location = `${this.currentLocation.lat},${this.currentLocation.lng}`;
                formData.append('location', location);
                this.sendToServer(formData);
            } catch (error) {
                console.error('Error getting location:', error);
                alert('Unable to get your location. Emergency alerts may not work properly.');
                this.sendToServer(formData);
            }
        }
    }

    async sendToServer(formData) {
        try {
            const response = await fetch('/process-voice/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            const data = await response.json();

            if (data.status === 'success') {
                if (data.is_emergency) {
                    alert(`Emergency alert sent! Detected phrase: "${data.detected_text}". Your contacts have been notified.`);
                    
                    // Open maps with current location
                    if (this.currentLocation) {
                        const mapUrl = `https://maps.google.com/?q=${this.currentLocation.lat},${this.currentLocation.lng}`;
                        window.open(mapUrl, '_blank');
                    }
                } else {
                    console.log('Voice processed - no emergency detected:', data.detected_text);
                }
            } else {
                console.error('Error processing voice:', data.message);
            }
        } catch (error) {
            console.error('Error sending audio to server:', error);
        }
    }
}

// Initialize voice detector
const voiceDetector = new VoiceDetector();

// Start voice detection when safety mode is active
function startVoiceDetection() {
    if (document.getElementById('voice-detection-status')) {
        setInterval(() => {
            voiceDetector.startRecording();
        }, 15000); // Check every 15 seconds (longer interval for speech recognition)
    }
}

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

// Start voice detection when the page loads
document.addEventListener('DOMContentLoaded', startVoiceDetection); 