from flask import Flask, render_template, request, jsonify
from onvif import ONVIFCamera
from time import sleep

app = Flask(__name__)

# Camera configuration
CAMERA_IP = '192.168.0.133'
CAMERA_PORT = 80
USERNAME = 'root'
PASSWORD = 'fsnetworks1!'
CAMERA = ONVIFCamera(CAMERA_IP, CAMERA_PORT, USERNAME, PASSWORD)

# Create PTZ service
ptz_service = CAMERA.create_ptz_service()

# Get media profile token
media_service = CAMERA.create_media_service()
profiles = media_service.GetProfiles()
profile_token = profiles[0].token

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/move', methods=['POST'])
def move():
    direction = request.json['direction']
    move_camera(direction)
    return jsonify({'status': 'success'})

@app.route('/stop', methods=['POST'])
def stop():
    stop_camera()
    return jsonify({'status': 'stopped'})

def move_camera(direction):
    """Function to move camera based on the direction input."""
    # Create a ContinuousMove request
    continuous_move_request = ptz_service.create_type('ContinuousMove')
    continuous_move_request.ProfileToken = profile_token

    # Initialize the PTZ speed vector correctly
    continuous_move_request.Velocity = {
        'PanTilt': {'x': 0.0, 'y': 0.0},
        'Zoom': {'x': 0.0}
    }

    # Define the speed for each direction
    pan_speed = 0.1  # Speed for pan movement
    tilt_speed = 0.1  # Speed for tilt movement
    zoom_speed = 0.1  # Speed for zoom movement

    # Set the speed for each direction
    if direction == 'up':
        continuous_move_request.Velocity['PanTilt']['y'] = tilt_speed
    elif direction == 'down':
        continuous_move_request.Velocity['PanTilt']['y'] = -tilt_speed
    elif direction == 'left':
        continuous_move_request.Velocity['PanTilt']['x'] = -pan_speed
    elif direction == 'right':
        continuous_move_request.Velocity['PanTilt']['x'] = pan_speed
    elif direction == 'zoom_in':
        continuous_move_request.Velocity['Zoom']['x'] = zoom_speed
    elif direction == 'zoom_out':
        continuous_move_request.Velocity['Zoom']['x'] = -zoom_speed

    # Execute the ContinuousMove command
    try:
        ptz_service.ContinuousMove(continuous_move_request)
        print(f"Camera moving {direction} continuously.")
    except Exception as e:
        print(f"An error occurred: {e}")

def stop_camera():
    """Function to stop the camera movement."""
    stop_request = ptz_service.create_type('Stop')
    stop_request.ProfileToken = profile_token
    stop_request.PanTilt = True  # Stop PanTilt movement
    stop_request.Zoom = True     # Stop Zoom movement
    
    try:
        ptz_service.Stop(stop_request)
        print("Camera movement stopped.")
    except Exception as e:
        print(f"An error occurred while stopping: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
