from flask import Flask, Response, request, jsonify, render_template, redirect, flash, url_for
from dotenv import load_dotenv
from flask_util import set_path, save_upload, save_to_json, UPLOADS_FOLDER
from flask_util import load_output, get_file_info, is_file_processed
import threading
import os
import json
from flask_explainer import setup_explainer, explainer_system

app = Flask(__name__)


def setup_app():
    """
    Sets up the Flask application by loading environment variables from a .env file,
    configuring app settings, and creating the uploads and outputs folders if they don't exist.
    """
    load_dotenv()
    app.secret_key = os.getenv("SECRET_KEY")
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    set_path()
    setup_explainer()


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
                status_info = save_to_json("pending", file_info['name'], file_info['timestamp'])
            return Response(json.dumps(status_info),  mimetype='application/json')
    return jsonify({'status': 'not found'}), 404


@app.route('/search', methods=['POST', 'GET'])
def search():
    """
    Handles the search functionality. Accepts both POST and GET requests.
    If a POST request is received with a non-empty UID, it redirects to the
    'status' route with the UID as a parameter.
    If a POST request is received with an empty UID, it flashes a message
    indicating that the UID should be entered and redirects back to the search page.
    If a GET request is received, it renders the 'search.html' template.

    Returns:
        str: The rendered HTML page or a redirect response.
    """
    if request.method == 'POST':
        uid = request.form['uid']
        if uid:
            return redirect(url_for('status', uid=uid))
        else:
            flash("Enter the UID")
            return redirect(request.url)
    return render_template("search.html")


def main():
    """
    The entry point of the application.
    It sets up the Flask app, starts the explainer system in a separate thread,
    runs the Flask app, and waits for the app to complete.
    Finally, it raises the stop event to terminate the explainer system thread.
    """
    setup_app()
    stop_event = threading.Event()
    t1 = threading.Thread(target=explainer_system, args=(stop_event,))
    t1.start()
    app.run()
    stop_event.set()
    t1.join()


if __name__ == '__main__':
    main()
