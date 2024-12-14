from flask import Flask, render_template, Response, request,jsonify
import re
import cv2

app = Flask(__name__)

# Replace with your actual RTSP URL structure
user = 'admin'
password = 'Admin@123'
base_url = f"rtsp://{user}:{password}@103.156.169.123:554/ISAPI/Streaming/Channels/"
channel_ids = [101, 201, 301, 401, 501]
camera_urls = [f"{base_url}{channel_id}" for channel_id in channel_ids]
cameras = {channel_id: cv2.VideoCapture(url) for channel_id, url in zip(channel_ids, camera_urls)}

def generate_frames(camera):
    while True:
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
    return render_template('main.html', camera_ids=channel_ids)

@app.route('/video_feed/<int:camera_id>')
def video_feed(camera_id):
    return Response(generate_frames(cameras[camera_id]), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/add_camera', methods=['POST'])
def add_camera():
    camera_url = request.form.get('camera_url')
    if camera_url:
        # Extract camera name from the URL using regular expressions
        match = re.search(r'/Channels/(\d+)$', camera_url)
        if match:
            camera_name = match.group(1)
        else:
            camera_name = 'Unknown'  # Default value if camera name cannot be extracted

        channel_id = max(channel_ids) + 1
        channel_ids.append(channel_id)
        cameras[channel_id] = cv2.VideoCapture(camera_url)
        return jsonify({
            "message": f"Camera added to channel {channel_id}",
            "camera_name": camera_name,
            "camera_url": camera_url
        }), 200
    else:
        return jsonify({"error": "Invalid camera URL provided"}), 400

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
    app.run(debug=True)



from flask import Flask, render_template, Response, request, jsonify
import re
import cv2
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(filename='app.log', level=logging.ERROR)

# Your existing code for camera setup, frame generation, and routes...

def generate_frames(camera):
    while True:
        success, frame = camera.read()
        if not success:
            logging.error("Error reading frame from camera.")
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                logging.error("Error encoding frame to JPEG.")
                continue
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# Replace with your actual RTSP URL structure
user = 'admin'
password = 'Admin@123'
base_url = f"rtsp://{user}:{password}@103.156.169.123:554/ISAPI/Streaming/Channels/"
channel_ids = [101, 201, 301, 401, 501]
camera_urls = [f"{base_url}{channel_id}" for channel_id in channel_ids]
cameras = {channel_id: cv2.VideoCapture(url) for channel_id, url in zip(channel_ids, camera_urls)}

@app.route('/')
def index():
    return render_template('main.html', camera_ids=channel_ids)

@app.route('/video_feed/<int:camera_id>')
def video_feed(camera_id):
    try:
        return Response(generate_frames(cameras[camera_id]), mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        logging.error(f"Error generating video feed for camera {camera_id}: {str(e)}")
        return Response(status=500)

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

            channel_id = max(channel_ids) + 1
            channel_ids.append(channel_id)
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
        return Response(status=500)
    

@app.route('/grid_view')
def grid_view():
    return render_template('grid_view.html', camera_ids=channel_ids)

@app.route('/exit', methods=['POST'])
def exit_app():
    try:
        for cam in cameras.values():
            cam.release()
        cv2.destroyAllWindows()
        return 'Exiting', 200
    except Exception as e:
        logging.error(f"Error exiting application: {str(e)}")
        return Response(status=500)

if __name__ == "__main__":
    app.run(debug=True)
