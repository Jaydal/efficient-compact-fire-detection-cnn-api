from datetime import datetime
from genericpath import isfile
from ntpath import join
import random
import uuid
import flask
import requests
from predict import predict_fire
import os
from PIL import Image
from io import BytesIO

app = flask.Flask(__name__)
app.config["DEBUG"] = True
camera_capture = 'http://192.168.1.100/capture'
logs = []

def recent_images():
    # Path to the uploads folder
    uploads_folder = 'static/uploads/'
    # Get a list of all files in the uploads folder
    all_files = [f for f in os.listdir(uploads_folder) if isfile(join(uploads_folder, f))]
    # Filter out only image files
    image_files = [f for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    # Sort the images by modification time (newest first)
    sorted_images = sorted(image_files, key=lambda x: os.path.getmtime(os.path.join(uploads_folder, x)), reverse=True)
    # Take the five most recent images
    return sorted_images[:4]

def pick_random():
    options = ["0.0", "1.0"]
    return random.choice(options)

def get_photo():
    response = requests.get(camera_capture)
    if response.status_code == 200:
        return response.content, 200
    else:
        return 'Failed to fetch image', 400

@app.route('/', methods=['GET','POST'])
def detect():
    if flask.request.method == 'GET':
        return flask.render_template('index.html', images=recent_images() )
    elif flask.request.method == 'POST':
        print("============================")        
        data = flask.request.get_json()
        
        testMode = bool(data['testMode'])

        if(testMode):
            print("Test mode enabled")
            return {
                'nasnet':pick_random(),
                'shufflenet':pick_random(),
                'testMode':"Returns random prediction values"
            }
                    
        image_data, status_code = get_photo()
        
        if(status_code==400):
            print("Failed to capture image!")
            print("*************************")
            return 400
        
        image = Image.open(BytesIO(image_data))
        
        unique_filename = str(uuid.uuid4()) + '.png'

        print(unique_filename)
        image_path = os.path.join('static/uploads', unique_filename)
        
        image.save(image_path)
        
        #detect
        nasnet = predict_fire(image_path,'nasnetonfire')
        shufflenet = predict_fire(image_path,'shufflenetonfire')
        
        #remove file
        # os.remove(image_path)
        
        predictions = {
                'nasnet':str(nasnet),
                'shufflenet':str(shufflenet)
            }
        
        print(predictions)
        
        return flask.jsonify(predictions), 200
    
@app.route('/get_recent_images', methods=['GET'])
def get_recent_images():
    # Return the recent images as JSON
    image_list = recent_images()
    return flask.jsonify(image_list)

@app.route('/logs', methods=['POST'])
def create_log():
    if flask.request.method == 'POST':
        data = flask.request.get_json()
        if 'message' in data:
            log_message = data['message']
            log_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logs.append((log_message, log_timestamp))
            return flask.jsonify({'message': 'Log created successfully.'}), 201
        else:
            return flask.jsonify({'error': 'Message not provided.'}), 400

@app.route('/logs', methods=['GET'])
def get_logs():
    if flask.request.method == 'GET':
        reversed_logs = reversed(logs)
        return flask.render_template('logs.html', logs=reversed_logs)
    
@app.route('/logs/raw', methods=['GET'])
def get_raw_logs():
    if flask.request.method == 'GET':
        return flask.jsonify({'logs': list(reversed(logs))})

app.run(host='0.0.0.0', port=80)