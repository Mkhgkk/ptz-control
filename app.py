from flask import Flask, render_template, request, jsonify
from onvif import ONVIFCamera
from time import sleep

app = Flask(__name__)

# Camera configuration
CAMERA_IP = '192.168.0.128'
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

def move_camera(direction):
    """Function to move camera based on the direction input."""
    # Create an AbsoluteMove request
    absolute_move_request = ptz_service.create_type('AbsoluteMove')
    absolute_move_request.ProfileToken = profile_token

    # Define the positions for each direction
    if direction == 'up':
        absolute_move_request.Position = {'PanTilt': {'x': 0.0, 'y': 1.0}, 'Zoom': {'x': 0.0}}
    elif direction == 'down':
        absolute_move_request.Position = {'PanTilt': {'x': 0.0, 'y': -1.0}, 'Zoom': {'x': 0.0}}
    elif direction == 'left':
        absolute_move_request.Position = {'PanTilt': {'x': -1.0, 'y': 0.0}, 'Zoom': {'x': 0.0}}
    elif direction == 'right':
        absolute_move_request.Position = {'PanTilt': {'x': 1.0, 'y': 0.0}, 'Zoom': {'x': 0.0}}
    elif direction == 'zoom_in':
        absolute_move_request.Position = {'PanTilt': {'x': 0.0, 'y': 0.0}, 'Zoom': {'x': 1.0}}
    elif direction == 'zoom_out':
        absolute_move_request.Position = {'PanTilt': {'x': 0.0, 'y': 0.0}, 'Zoom': {'x': -1.0}}

    # Optionally, define the speed (if supported by the camera)
    absolute_move_request.Speed = {'PanTilt': {'x': 0.5, 'y': 0.5}, 'Zoom': {'x': 0.5}}

    # Execute the AbsoluteMove command
    try:
        ptz_service.AbsoluteMove(absolute_move_request)
        print(f"Camera moved {direction} successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

    # Optional: Wait for the camera to move and then stop
    sleep(1)
    ptz_service.Stop({'ProfileToken': profile_token})
    print("Camera movement stopped.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
