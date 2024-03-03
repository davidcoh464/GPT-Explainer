import os
import sys
import threading
from json2html import json2html

from dotenv import load_dotenv
from flask import Flask, Response, request, jsonify, send_file
from flask import render_template, redirect, flash, url_for, send_from_directory, make_response

from flask_imp.db_model import Session, User, Upload, create_all
from flask_imp.flask_explainer import explainer_system, setup_explainer
from flask_imp.flask_util import set_path, load_json_file, save_to_json, get_output_path
from flask_imp.flask_util import status_done, save_upload, save_upload_with_user

app = Flask(__name__)


def setup_app():
    """
    Sets up the Flask application by loading environment variables,
    configuring app settings, and creating necessary folders.
    """
    load_dotenv()
    app.secret_key = os.getenv("SECRET_KEY")
    set_path()
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000  # Sets the maximum content length to 16 megabytes
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True  # Enable pretty-printing for JSON responses
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/db.sqlite3'  # Set SQLite database URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking
    # Enable testing mode if 'test' is provided as a command-line argument
    if len(sys.argv) > 1 and str(sys.argv[1]).lower() == "test":
        app.config['TESTING'] = True
    create_all()
    setup_explainer()


@app.route('/static/<filename>')
def static_files(filename):
    """
    Serves static files from the Flask application's static directory with caching enabled.

    This route function serves static files (such as CSS, JavaScript, images, etc.) located
    in the Flask application's static directory. It sets the appropriate cache control headers
    to enable caching in the client's browser, improving performance by reducing the need
    to fetch static files on subsequent requests.
    Args:
        filename (str): The name of the static file to be served.
    Returns:
        Response: A Flask response object containing the static file to be served with caching headers.
    """
    cache_timeout = 360  # Cache files for 6 minutes
    response = make_response(send_from_directory(app.static_folder, filename))
    response.headers['Cache-Control'] = f"max-age={cache_timeout}, public"
    return response


@app.route('/')
@app.route('/home', alias=True)
def home():
    """
    Renders the home.html template.
    This function is associated with the root URL '/' or '/home'.
    Returns:
        str: The rendered HTML page.
    """
    return render_template("home.html")


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """
    Handles file upload functionality. Accepts GET and POST requests.
    If a POST request is received with a file attached, it saves the file,
    generates a UID, and returns the UID as a JSON response.
    If a GET request is received, it renders the upload.html template.
    Returns:
        str: Rendered HTML page or JSON response with UID and HTTP status code 200.
    """
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files.get('file')
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        email = request.form.get('email')
        prompt = request.form.get('prompt', '')
        if email:
            uid = save_upload_with_user(file, email, prompt)
        else:
            uid = save_upload(file, prompt)
        return jsonify({'uid': uid}), 200
    return render_template("upload.html")


@app.route('/status/<uid>', methods=['GET'])
def status_get(uid):
    """
    Retrieves the processing status and information of the file with the given UID.
    If the file is processed, it returns a JSON response with status, filename,
    timestamp, and output. If not found or not processed, it returns a 'not found' JSON response.
    Args:
        uid (str): The UID of the file.
    Returns:
        Response: JSON response with processing status and information.
    """
    with Session() as session:
        file_data = session.query(Upload).filter_by(uid=uid).first()
        if file_data:
            if file_data.status == status_done:
                output = load_json_file(f"{uid}.json")
                status_info = save_to_json(uid, file_data.status, file_data.filename, file_data.finish_time, output)
            else:
                status_info = save_to_json(uid, file_data.status, file_data.filename, file_data.finish_time)
            if app.config.get('TESTING'):
                return jsonify(status_info), 200
            else:
                status_info = json2html.convert(json=status_info)
                return render_template("status.html", status_info=status_info)
    return jsonify({'status': 'not found'}), 404


@app.route('/status/<uid>', methods=['POST'])
def status_post(uid):
    """
    Handles file download functionality based on the processing status of the file.
    If the file is processed and available, it triggers a file download response.
    If the file is not ready or the status UID is not found, it provides appropriate feedback.
    Args:
        uid (str): The UID of the file.
    Returns:
        Response: File download response or redirection with feedback.
    """
    with Session() as session:
        file_data = session.query(Upload).filter_by(uid=uid).first()
        if file_data:
            if file_data.status == status_done:
                file_path = get_output_path(f"{uid}.{request.form.get('file_type')}")
                if file_path != "":
                    return send_file(file_path, as_attachment=True)
            else:
                flash("The file is not ready yet")
        else:
            flash("status uid is not exist")
    return redirect(request.url)


@app.route('/search', methods=['POST', 'GET'])
def search():
    """
    Handles search functionality for file status. Accepts POST and GET requests.
    For POST requests, if a UID is provided, it redirects to the 'status' route with the UID parameter.
    For GET requests, it renders the 'search.html' template.
    Returns:
        str: Rendered HTML page or a redirect response.
    """
    if request.method == 'POST':
        uid = request.form.get('uid')
        email = request.form.get('email')
        filename = request.form.get('filename')
        if uid:
            return redirect(url_for('status_get', uid=uid))
        elif email and filename:  # Search only if both email and filename are provided
            with Session() as session:
                user = session.query(User).filter_by(email=email).first()
                if user:
                    latest_upload = session.query(Upload).filter_by(user=user, filename=filename).order_by(
                        Upload.upload_time.desc()).first()
                    if latest_upload:
                        return redirect(url_for('status_get', uid=latest_upload.uid))
                    else:
                        flash("Filename not found")
                else:
                    flash(f"Email: {email} does not exist")
        else:
            flash("Please enter a UID, or provide both email and file name")
        return redirect(request.url)
    return render_template("search.html")


def main():
    """
    Entry point of the application. Sets up the Flask app,
    starts the explainer system in a separate thread,
    runs the Flask app, and waits for the app to complete.
    Finally, raises the stop event to terminate the explainer system thread.
    """
    setup_app()
    stop_event = threading.Event()
    t1 = threading.Thread(target=explainer_system, args=(stop_event,))
    t1.start()
    app.run(debug=True)
    stop_event.set()
    t1.join()


if __name__ == '__main__':
    main()
