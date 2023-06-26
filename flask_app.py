from flask import Flask, Response, request, jsonify, render_template, redirect, flash
from dotenv import load_dotenv
from uuid import uuid4
from pathlib import Path
from typing import Dict
from threading import Thread, Event
import os
import datetime
import json
import sys
import asyncio
import time
from presentation_parser import PresentationParser
from slide_handler import SlideHandler
from output_manage import OutputManage


app = Flask(__name__)
stop_event = Event()

WINDOWS_PLATFORM = 'win'
UPLOADS_FOLDER = "uploads"
OUTPUTS_FOLDER = "outputs"
TIME_TO_SLEEP = 10


def setup_app():
    """
    Sets up the Flask application by loading environment variables from a .env file,
    configuring app settings, and creating the uploads and outputs folders if they don't exist.
    Additionally, on Windows platforms, it sets the event loop policy to asyncio.WindowsSelectorEventLoopPolicy().
    """
    load_dotenv()
    app.secret_key = os.getenv("SECRET_KEY")
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    # Create the uploads and outputs folders if they don't exist
    Path(UPLOADS_FOLDER).mkdir(parents=True, exist_ok=True)
    Path(OUTPUTS_FOLDER).mkdir(parents=True, exist_ok=True)
    if sys.platform.startswith(WINDOWS_PLATFORM):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def generate_uid() -> str:
    """
    Generates a unique identifier (UID) using the UUID4 algorithm.

    Returns:
        str: The generated unique identifier.
    """
    return str(uuid4())


def save_upload(file) -> str:
    """
    Saves the uploaded file to the uploads folder with a unique filename,
    based on the original filename, timestamp, and UID.

    Args:
        file: The file object to be saved.

    Returns:
        str: The generated UID associated with the saved file.
    """
    uid = generate_uid()
    name, file_type = os.path.splitext(file.filename)
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{name}_{timestamp}_{uid}{file_type}"
    file.save(os.path.join(UPLOADS_FOLDER, filename))
    return uid


def get_file_info(filename: str) -> Dict[str, str]:
    """
    Extracts information from the filename of an uploaded file.

    Args:
        filename (str): The filename of the uploaded file.

    Returns:
        Dict[str, str]: A dictionary containing the extracted file information,
                        including name, timestamp, and UID.
    """
    split_name = filename.split('_')
    name = "".join(split_name[i] + "_" for i in range(len(split_name) - 2))
    name = name[0:-1]
    timestamp = split_name[-2]
    uid = split_name[-1].split(".")[0]
    return {
        'name': name,
        'timestamp': timestamp,
        'uid': uid
    }


def process_file(filename: str):
    """
    Processes the uploaded file by extracting text from presentation slides,
    handling the slides asynchronously, and saving the responses as JSON.

    Args:
        filename (str): The filename of the uploaded file to be processed.
    """
    upload_path = f"uploads/{filename}"
    slides = PresentationParser.extract_text(upload_path)
    responses = asyncio.run(SlideHandler.response_handler(slides))
    output_path = f"outputs/{filename}"
    OutputManage.save_to_json(responses, output_path)


def get_output_path(filename: str) -> str:
    """
    Retrieves the path to the output file associated with the given filename.

    Args:
        filename (str): The filename for which to retrieve the output path.

    Returns:
        str: The path to the output file.
    """
    name, _ = os.path.splitext(filename)
    return os.path.join(OUTPUTS_FOLDER, f"{name}.json")


def load_output(filename: str) -> Dict:
    """
    Loads the content of the output file associated with the given filename as a JSON object.

    Args:
        filename (str): The filename of the output file to be loaded.

    Returns:
        Dict: The loaded JSON content as a dictionary.
    """
    output_path = get_output_path(filename)
    with open(output_path, 'r') as file:
        return json.load(file)


def is_file_processed(filename: str) -> bool:
    """
    Checks if the output file associated with the given filename exists,
    indicating whether the file has been processed.

    Args:
        filename (str): The filename for which to check the processing status.

    Returns:
        bool: True if the output file exists, False otherwise.
    """
    output_path = get_output_path(filename)
    return os.path.exists(output_path)


def save_to_json(upload_status, name, timestamp, explanation=None):
    """
    Creates a dictionary object to represent the upload status, including the
    filename, timestamp, processing status, and an optional explanation.

    Args:
        upload_status: The status of the upload.
        name: The name of the file.
        timestamp: The timestamp of the upload.
        explanation: An optional explanation for the upload status.

    Returns:
        Dict: A dictionary representing the upload status.
    """
    return {
        'status': upload_status,
        'filename': name,
        'timestamp': timestamp,
        'explanation': explanation
    }


@app.route('/')
def home():
    """
    Renders the home.html template and returns the rendered HTML page.
    This function is associated with the root URL '/'.

    Returns:
        str: The rendered HTML page.
    """
    return render_template("home.html")


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """
    Handles the file upload functionality. Accepts both GET and POST requests.
    If a POST request is received with a file attached, it saves the file,
    generates a UID, and returns the UID as a JSON response.
    If a GET request is received, it renders the upload.html template.

    Returns:
        str: The rendered HTML page or a JSON response with the UID.
    """
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        uid = save_upload(file)
        response = {'uid': uid}
        return jsonify(response)
    return render_template("upload.html")


@app.route('/status/<uid>')
def status(uid):
    """
    Retrieves the processing status of the file associated with the given UID.
    If the file is processed, it loads the output and generates a JSON response
    with the processing status, filename, timestamp, and output.
    If the file is not found or not processed, it generates a JSON response
    indicating the status as 'not found'.

    Args:
        uid (str): The UID of the file.

    Returns:
        Response: A JSON response with the processing status and information.
    """
    for filename in os.listdir(UPLOADS_FOLDER):
        file_info = get_file_info(filename)
        if file_info['uid'] == uid:
            if is_file_processed(filename):
                output = load_output(filename)
                status_info = save_to_json("done", file_info['name'], file_info['timestamp'], output)
            else:
                status_info = save_to_json("padding", file_info['name'], file_info['timestamp'])
            return Response(json.dumps(status_info),  mimetype='application/json')
    return jsonify({'status': 'not found'}), 404


def explainer_system():
    """
    Implements the background explainer system that continuously processes
    files in the uploads folder that are not yet processed.
    This function runs in an infinite loop until the stop event is set.
    It processes the files using the process_file() function and sleeps for
    TIME_TO_SLEEP seconds between iterations.
    """
    while True:
        filenames = [filename for filename in os.listdir(UPLOADS_FOLDER)
                     if not is_file_processed(filename)]
        for filename in filenames:
            if stop_event.is_set():
                break
            try:
                process_file(filename)
            except KeyError:
                continue
        if stop_event.is_set():
            break
        time.sleep(TIME_TO_SLEEP)


def main():
    """
    The entry point of the application.
    It sets up the Flask app, starts the explainer system in a separate thread,
    runs the Flask app, and waits for the app to complete.
    Finally, it raises the stop event to terminate the explainer system thread.
    """
    setup_app()
    t1 = Thread(target=explainer_system)
    t1.start()
    app.run()
    # If flask app Its completed raise stop event
    stop_event.set()
    t1.join()


if __name__ == '__main__':
    main()
