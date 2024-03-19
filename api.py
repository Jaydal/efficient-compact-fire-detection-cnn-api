import flask
from predict import predict_fire
import os

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET','POST'])
def detect():
    if flask.request.method == 'GET':
         return flask.render_template_string('''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Upload File</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        background-color: #f0f0f0;
                        margin: 0;
                        padding: 0;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                    }
                    .container {
                        background-color: #fff;
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    }
                    h1 {
                        text-align: center;
                    }
                    form {
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                    }
                    input[type="file"] {
                        margin-bottom: 20px;
                    }
                    button[type="submit"] {
                        padding: 10px 20px;
                        border: none;
                        background-color: #007bff;
                        color: #fff;
                        border-radius: 4px;
                        cursor: pointer;
                        transition: background-color 0.3s ease;
                    }
                    button[type="submit"]:hover {
                        background-color: #0056b3;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Upload File</h1>
                    <form method="post" enctype="multipart/form-data">
                        <input type="file" name="image">
                        <button type="submit">Upload</button>
                    </form>
                </div>
            </body>
            </html>
        ''')
    elif flask.request.method == 'POST':
        # Check if the POST request contains an image
        if 'image' not in flask.request.files:
            return "No image provided", 400
        
        image = flask.request.files['image']
        
        # Save the image to disk or process it as required
        image_path = 'uploads/'+image.filename
        image.save(image_path)
        
        #detect
        nasnet = predict_fire(image_path,'nasnetonfire')
        shufflenet = predict_fire(image_path,'shufflenetonfire')
        
        #remove file
        os.remove(image_path)
        
        #return predictions
        predictions = {
                'nasnet':str(nasnet),
                'shufflenet':str(shufflenet)
            }
        return flask.jsonify(predictions), 200

app.run(host='0.0.0.0', port=3000)