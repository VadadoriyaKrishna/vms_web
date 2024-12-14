document.querySelectorAll('.sidebar ul li a').forEach(link => {
    link.addEventListener('click', (event) => {
        event.preventDefault(); // Prevent default link behavior
        let cameraId = link.getAttribute('data-camera-id');
        let videoElement = document.querySelector(`img[data-camera-id='${cameraId}']`);
        if (videoElement) {
            requestFullScreen(videoElement);
        }
    });
});

document.querySelectorAll('.grid-item img').forEach(img => {
    img.addEventListener('click', () => {
        requestFullScreen(img);
    });
});



document.getElementById('view-1x1').addEventListener('click', () => {
    document.querySelector('.grid-container').style.gridTemplateColumns = 'repeat(1, 1fr)';
});

document.getElementById('view-2x2').addEventListener('click', () => {
    document.querySelector('.grid-container').style.gridTemplateColumns = 'repeat(2, 1fr)';
});

document.getElementById('view-3x3').addEventListener('click', () => {
    document.querySelector('.grid-container').style.gridTemplateColumns = 'repeat(3, 1fr)';
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
