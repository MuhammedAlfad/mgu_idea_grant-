import time
import os
import cv2
import numpy as np
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# --- Hardware Imports (Safe Failover) ---
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("⚠️ RPi.GPIO not found. Running in Hardware Emulation mode (Distance will be 0).")

# Configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'palm_secret_key'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Globals
simulation_thread = None
stop_flag = False
DATA_DIR = "palm_database"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# --- Real Hardware Configuration ---
TRIG_PIN = 23  # GPIO Pin for Ultrasonic Trigger
ECHO_PIN = 24  # GPIO Pin for Ultrasonic Echo

if GPIO_AVAILABLE:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)

# --- Helper: Real Distance Sensor ---
def get_real_distance():
    if not GPIO_AVAILABLE:
        return 0.0
    
    # Ensure Trigger is low
    GPIO.output(TRIG_PIN, False)
    time.sleep(0.000002) # 2 microseconds
    
    # Send 10us pulse
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)
    
    timeout = time.time() + 0.04 # 40ms timeout
    pulse_start = time.time()
    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()
        if pulse_start > timeout: return -1

    pulse_end = time.time()
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()
        if pulse_end > timeout: return -1

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150 # Speed of sound
    return round(distance, 1)

# --- Helper: Computer Vision (Tilt & Match) ---
def analyze_frame(frame):
    """
    Analyzes a frame to detect if a hand is present and its tilt.
    Returns: (is_valid, tilt_status, processed_frame)
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 70, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return False, "NONE", frame

    # Find largest contour (assumed to be hand)
    max_contour = max(contours, key=cv2.contourArea)
    
    if cv2.contourArea(max_contour) < 5000:
        return False, "NONE", frame

    # Determine Tilt using MinAreaRect
    rect = cv2.minAreaRect(max_contour)
    angle = rect[-1]
    
    # Normalize angle
    if angle < -45: angle = 90 + angle
    
    tilt = "STRAIGHT"
    if angle > 15: tilt = "RIGHT"
    elif angle < -15: tilt = "LEFT"

    return True, tilt, frame

def match_palm(captured_frame, user_id):
    """
    Uses ORB feature matching to compare captured frame with stored user image.
    """
    user_path = os.path.join(DATA_DIR, f"{user_id}.jpg")
    if not os.path.exists(user_path):
        return False, 0.0

    stored_img = cv2.imread(user_path, 0)
    current_img = cv2.cvtColor(captured_frame, cv2.COLOR_BGR2GRAY)

    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(stored_img, None)
    kp2, des2 = orb.detectAndCompute(current_img, None)

    if des1 is None or des2 is None:
        return False, 0.0

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    
    # Calculate score based on number of good matches
    matches = sorted(matches, key=lambda x: x.distance)
    score = len(matches)
    
    # Heuristic: > 15 good matches = verified
    is_match = score > 15 
    confidence = min(score / 50.0, 0.99) # Normalize cap
    
    return is_match, confidence

# --- 🧠 Real Sensor Flow ---
def sensor_control_loop(mode, user_id):
    global stop_flag
    stop_flag = False
    
    # Initialize Camera
    cap = cv2.VideoCapture(0) # Index 0 for default camera
    
    if not cap.isOpened():
        emit_status(mode, "instruction", "Camera Error", 0, "NONE", "NONE", 0)
        return

    try:
        current_state = "IDLE"
        progress = 0
        
        while not stop_flag:
            # 1. Read Distance
            dist = get_real_distance()
            
            # 2. Determine Position State
            if dist > 30:
                state = "TOO_FAR"
                text = "Please place hand above sensor"
            elif dist < 5:
                state = "TOO_CLOSE"
                text = "Too close! Move back."
            elif 5 <= dist <= 20:
                state = "PERFECT"
                text = "Hold still..."
            else:
                state = "TOO_FAR"
                text = "Move closer..."

            # 3. Read Camera & Check Tilt
            ret, frame = cap.read()
            tilt = "NONE"
            if ret:
                valid_hand, tilt, _ = analyze_frame(frame)
                if not valid_hand and state == "PERFECT":
                    text = "Hand not detected clearly"
                    state = "PROCESSING"

            # 4. Logic Flow
            if state == "PERFECT" and tilt == "STRAIGHT":
                progress += 5
                text = "Scanning palm..."
                
                if progress >= 100:
                    # Perform Action
                    emit_status(mode, "capture", "Processing...", dist, "CAPTURING", tilt, 100)
                    
                    if mode == 'registration':
                        cv2.imwrite(os.path.join(DATA_DIR, f"{user_id}.jpg"), frame)
                        emit_final(mode, f"User {user_id} Registered", dist, "PERFECT", tilt, 0.99)
                    else:
                        success, conf = match_palm(frame, user_id)
                        res_text = f"User Verified" if success else "Access Denied"
                        emit_final(mode, res_text, dist, "PERFECT", tilt, conf)
                    break
            else:
                # Reset progress if hand moves or tilts
                progress = max(0, progress - 2)

            emit_status(mode, "instruction", text, dist, state, tilt, progress)
            socketio.sleep(0.1) # Rate limit loop

    finally:
        cap.release()
        if stop_flag:
            emit_status(mode, "instruction", "Stopped", 0, "NONE", "NONE", 0)

def emit_status(mode, msg_type, text, distance, state, tilt, progress):
    payload = {
        "type": msg_type, "text": text, "distance_cm": distance,
        "state": state, "mode": mode, "tilt": tilt, "progress": progress, "confidence": None
    }
    socketio.emit('status_update', payload)

def emit_final(mode, text, distance, state, tilt, confidence):
    payload = {
        "type": "result", "text": text, "distance_cm": distance,
        "state": state, "mode": mode, "tilt": tilt, "progress": 100, "confidence": confidence
    }
    socketio.emit('status_update', payload)

# --- API Routes ---
@app.route('/start_register', methods=['POST'])
def start_register():
    global simulation_thread, stop_flag
    data = request.json
    user_id = data.get('user_id', 'unknown')
    stop_flag = True 
    if simulation_thread: socketio.sleep(1)
    simulation_thread = socketio.start_background_task(sensor_control_loop, 'registration', user_id)
    return jsonify({"status": "started", "mode": "registration", "user": user_id})

@app.route('/start_match', methods=['POST'])
def start_match():
    global simulation_thread, stop_flag
    data = request.json
    user_id = data.get('user_id', 'unknown')
    stop_flag = True