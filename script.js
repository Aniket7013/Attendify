document.addEventListener('DOMContentLoaded', function() {
    const togglePassword = document.querySelector('.toggle-password');
    const password = document.querySelector('#password');

    togglePassword.addEventListener('click', function () {
        const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
        password.setAttribute('type', type);
        this.classList.toggle('fa-eye');
        this.classList.toggle('fa-eye-slash');
    });
});
// Add this to script.js or the <script> block in your HTML

async function shareLocation() {
    return new Promise((resolve, reject) => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(resolve, reject);
        } else {
            reject(new Error("Geolocation is not supported by this browser."));
        }
    });
}

async function checkLocation() {
    const shareButton = document.getElementById('share-location-button');
    const markButton = document.getElementById('mark-attendance-button');
    shareButton.disabled = true;
    shareButton.innerHTML = '<div class="loading-spinner"></div> Processing...';

    try {
        const position = await shareLocation();
        const latitude = position.coords.latitude;
        const longitude = position.coords.longitude;

        document.getElementById('latitude').value = latitude;
        document.getElementById('longitude').value = longitude;

        const response = await fetch('/check-location', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `latitude=${latitude}&longitude=${longitude}`
        });

        const result = await response.text();

        if (result === 'valid') {
            shareButton.innerHTML = `Location Verified: ${latitude.toFixed(2)}, ${longitude.toFixed(2)}`;
            markButton.disabled = false;
        } else {
            shareButton.innerHTML = 'You are not in the allowed location';
            markButton.disabled = true;
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
        console.error(error);
        shareButton.innerHTML = 'Share My Location';
    } finally {
        shareButton.disabled = false;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById('share-location-button').addEventListener('click', checkLocation);
});
