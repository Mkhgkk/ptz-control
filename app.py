from flask import Flask, render_template, request, jsonify
from time import sleep
from camera_controller import CameraController  # Import the class from the new file

app = Flask(__name__)

# Initialize the camera controller with the given configuration
camera_controller = CameraController('192.168.0.133', 80, 'root', 'fsnetworks1!')
# camera_controller = CameraController('218.54.201.82', 80, 'admin', '1q2w3e4r.')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/move', methods=['POST'])
def move():
    direction = request.json['direction']
    zoom_amount = request.json.get('zoom_amount', None)  # Get zoom amount if provided
    camera_controller.move_camera(direction, zoom_amount)
    return jsonify({'status': 'success'})

@app.route('/stop', methods=['POST'])
def stop():
    camera_controller.stop_camera()
    return jsonify({'status': 'stopped'})

@app.route('/zoom_level', methods=['GET'])
def zoom_level():
    zoom = camera_controller.get_zoom_level()
    return jsonify({'zoom_level': zoom})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)