// Add this to your JavaScript file (script.js)

document.getElementById('close-button').addEventListener('click', () => {
    if (confirm('Are you sure you want to exit?')) {
        window.open('', '_self').close();
    }
});


/*document.getElementById('add-camera').addEventListener('click', () => {
    let cameraUrl = prompt("Enter camera URL or path:");
    if (cameraUrl) {
        fetch('/add_camera', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `camera_url=${cameraUrl}`
        }).then(response => {
            if (response.status === 200) {
                location.reload();
            } else {
                alert('Failed to add camera');
            }
        });
    }
});*/

document.getElementById('add-camera').addEventListener('click', () => {
    let cameraUrl = prompt("Enter camera URL or path:");
    if (cameraUrl) {
        fetch('/add_camera', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `camera_url=${cameraUrl}`
        }).then(response => {
            if (response.ok) {
                response.json().then(data => {
                    // Display a success message
                    alert(data.message);

                    // Reload the page to display the newly added camera
                    location.reload();
                });
            } else {
                // Display an error message
                alert('Failed to add camera');
            }
        }).catch(error => {
            console.error('Error adding camera:', error);
            alert('Failed to add camera');
        });
    }
});


document.querySelectorAll('.sidebar ul li a').forEach(link => {
    link.addEventListener('click', () => {
        let cameraId = link.getAttribute('data-camera-id');
        let videoElement = document.querySelector(`#camera${cameraId} img`);
        requestFullScreen(videoElement);
    });
});

document.querySelectorAll('.grid-item img').forEach(img => {
    img.addEventListener('click', () => {
        requestFullScreen(img);
    });
});

document.getElementById('exit').addEventListener('click', () => {
    fetch('/exit', { method: 'POST' });
});

function requestFullScreen(element) {
    if (element.requestFullscreen) {
        element.requestFullscreen();
    } else if (element.mozRequestFullScreen) { // Firefox
        element.mozRequestFullScreen();
    } else if (element.webkitRequestFullscreen) { // Chrome, Safari and Opera
        element.webkitRequestFullscreen();
    } else if (element.msRequestFullscreen) { // IE/Edge
        element.msRequestFullscreen();
    }
}
