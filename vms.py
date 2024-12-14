from flask import Flask, render_template, Response, request, jsonify
import re
import cv2
import sqlite3
import logging

app = Flask(__name__)

# Connect to the SQLite database
conn = sqlite3.connect('cameras.db', check_same_thread=False)
c = conn.cursor()

# Set up logging
logging.basicConfig(filename='app.log', level=logging.ERROR)

# Create a table to store camera information if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS cameras
             (id INTEGER PRIMARY KEY, name TEXT, url TEXT)''')
conn.commit()

# Replace with your actual RTSP URL structure
user = 'admin'
password = 'Admin@123'
base_url = f"rtsp://{user}:{password}@103.156.169.123:554/ISAPI/Streaming/Channels/"

# Define channel IDs and camera URLs
channel_ids = [101, 201, 301, 401, 501]
camera_urls = [f"{base_url}{channel_id}" for channel_id in channel_ids]

# Retrieve existing camera information from the database
c.execute("SELECT * FROM cameras")
rows = c.fetchall()

# Print headers for better readability
print("Channel ID | Camera Name | Camera URL")
print("--------------------------------------")

for row in rows:
    channel_id = row[0]
    camera_name = row[1]
    camera_url = row[2]
    channel_ids.append(channel_id)
    camera_urls.append(camera_url)
    print(f"{channel_id}         | {camera_name}     | {camera_url}")

# Initialize cameras dictionary
cameras = {channel_id: cv2.VideoCapture(url) for channel_id, url in zip(channel_ids, camera_urls)}

def generate_frames(camera):
    # Set the timeout for the video capture object
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 2)
    
    # Use OpenCV properties to set a timeout for reading the frames
    cap_open_timeout_ms = 30000  # Timeout in milliseconds for opening the capture
    cap_read_timeout_ms = 3000  # Timeout in milliseconds for reading the frame

    start_time = cv2.getTickCount()
    tick_frequency = cv2.getTickFrequency()
    
    while True:
        current_time = cv2.getTickCount()
        elapsed_time = (current_time - start_time) / tick_frequency * 1000
        
        if elapsed_time > cap_open_timeout_ms:
            logging.error(f"Stream timeout triggered after {elapsed_time} ms")
            break
        
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_camera_ids')
def get_camera_ids():
    return jsonify(camera_ids=channel_ids)

@app.route('/video_feed/<int:camera_id>')
def video_feed(camera_id):
    return Response(generate_frames(cameras[camera_id]), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/add_camera', methods=['POST'])
def add_camera():
    try:
        camera_url = request.form.get('camera_url')
        if camera_url:
            match = re.search(r'/Channels/(\d+)$', camera_url)
            if match:
                camera_name = match.group(1)
            else:
                camera_name = 'Unknown'

            channel_id = int(camera_name)

            with sqlite3.connect('cameras.db') as conn:
                c = conn.cursor()
                c.execute("INSERT INTO cameras (id, name, url) VALUES (?, ?, ?)", (channel_id, camera_name, camera_url))
                conn.commit()

            channel_ids.append(channel_id)
            camera_urls.append(camera_url)
            cameras[channel_id] = cv2.VideoCapture(camera_url)
            return jsonify({
                "message": f"Camera added to channel {channel_id}",
                "camera_name": camera_name,
                "camera_url": camera_url
            }), 200
        else:
            return jsonify({"error": "Invalid camera URL provided"}), 400
    except Exception as e:
        logging.error(f"Error adding camera: {str(e)}")
        return jsonify({"error": "Failed to add camera"}), 500

@app.route('/full_screen', methods=['POST'])
def full_screen():
    return 'OK', 200

@app.route('/grid_view')
def grid_view():
    return render_template('grid_view.html', camera_ids=channel_ids)

@app.route('/exit', methods=['POST'])
def exit_app():
    for cam in cameras.values():
        cam.release()
    cv2.destroyAllWindows()
    return 'Exiting', 200

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080)
