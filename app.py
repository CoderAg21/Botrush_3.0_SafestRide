from flask import Flask, render_template, request, send_from_directory
from model import process_image
import os

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return "No file part"

    file = request.files['image']
    if file.filename == '':
        return "No selected file"
    rows = request.form['rows']
    cols = request.form['cols']

    filepath = f"./uploads/{file.filename}"
    file.save(filepath)

    # Call your ML model here
    output_path = f"./static/processed_img/processed_{file.filename}"
    process_image(filepath,rows,cols, output_path)
    return render_template("preview.html",output_img = output_path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Run the app on 0.0.0.0 for external accessibility
    app.run(host='0.0.0.0', port=port)
 
