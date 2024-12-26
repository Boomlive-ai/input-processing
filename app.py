from flask import Flask, request, jsonify
import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from processing.video_processing import process_video_file
from processing.audio_processing import process_audio_file
from processing.image_processing import extract_text_from_image
from processing.url_processing import scrape_url
from tools.automate_input_processing import detect_and_process_file, detect_and_process_json
import requests
from bs4 import BeautifulSoup

# Initialize Flask app
app = Flask(__name__)

# Directory to store uploaded video files
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configuring Flask to store video files
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'mp3', 'wav', 'jpg', 'jpeg', 'png'}

# Helper function to check for allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Route to display API documentation
@app.route('/', methods=['GET'])
def documentation():
    doc = {
        "API Documentation": {
            "upload_video": {
                "description": "Upload a video file and extract its duration and transcript",
                "method": "POST",
                "endpoint": "/upload_video",
                "parameters": {
                    "file": "The video file to upload"
                },
                "example": {
                    "url": "/upload_video"
                },
                "response": {
                    "filename": "Name of the uploaded file",
                    "duration": "Duration of the video in seconds",
                    "path": "Path to the saved file",
                    "transcript": "Transcript extracted from the video"
                }
            },
            "upload_audio": {
                "description": "Upload an audio file and generate a transcript",
                "method": "POST",
                "endpoint": "/upload_audio",
                "parameters": {
                    "file": "The audio file to upload"
                },
                "example": {
                    "url": "/upload_audio"
                },
                "response": {
                    "filename": "Name of the uploaded file",
                    "path": "Path to the saved file",
                    "transcript": "Transcript extracted from the audio"
                }
            },
            "upload_image": {
                "description": "Upload an image file and extract text from it",
                "method": "POST",
                "endpoint": "/upload_image",
                "parameters": {
                    "file": "The image file to upload"
                },
                "example": {
                    "url": "/upload_image"
                },
                "response": {
                    "filename": "Name of the uploaded file",
                    "path": "Path to the saved file",
                    "text": "Text extracted from the image"
                }
            },
            "scrape_url": {
                "description": "Scrape and extract text from a given URL",
                "method": "POST",
                "endpoint": "/scrape_url",
                "parameters": {
                    "url": "The URL to scrape"
                },
                "example": {
                    "url": "/scrape_url"
                },
                "response": {
                    "url": "The scraped URL",
                    "extracted_text": "Text extracted from the URL"
                }
            },
            "process_input": {
                "description": "Process input which can be a file or JSON data",
                "method": "POST",
                "endpoint": "/process_input",
                "parameters": {
                    "file": "A file to upload (optional, depending on the content type)",
                    "json": "JSON data to process (optional)"
                },
                "example": {
                    "url": "/process_input"
                },
                "response": {
                    "message": "Result of processing the input"
                }
            }
        }
    }
    return jsonify(doc)

# Route to upload video
@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        # Generate a unique file path to store the video in the uploads folder
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        
        # Save the uploaded video file locally
        file.save(file_path)
        
        # Process the video (Example: Get duration of the video)
        try:
            video_clip = VideoFileClip(file_path)
            duration = video_clip.duration  # Get the duration in seconds
            print(f"File: {file.filename}, Duration: {duration}")
            transcript = process_video_file(file_path).text
            print(transcript)
            # Ensure the video file is properly closed after processing
            video_clip.close()

            # Return the results (e.g., video duration)
            return jsonify({"filename": file.filename, "duration": duration, "path": file_path, "transcript": transcript}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to process video: {str(e)}"}), 500
    else:
        return jsonify({"error": "Invalid file type. Please upload a valid video file."}), 400

# Routes for uploading audio, image, and other functionalities...
# (Keep the rest of your routes as they are.)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
