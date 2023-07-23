from flask import Flask, Response, request, jsonify, render_template, redirect, flash, url_for
from dotenv import load_dotenv
from flask_util import set_path, generate_uid, load_output, save_to_json
from flask_util import UPLOADS_FOLDER, OUTPUTS_FOLDER, os
import json
import threading
from presentation_parser import PresentationParser
from slide_handler import SlideHandler
from output_manage import OutputManage
import asyncio
import sys
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum, ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)

TIME_TO_SLEEP = 10
WINDOWS_PLATFORM = 'win'


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    uploads: Mapped[List["Upload"]] = relationship("Upload", backref='user', lazy=True, cascade='all, delete-orphan')


class Upload(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    uid: Mapped[str] = mapped_column(String(36), default=generate_uid, nullable=False, unique=True)
    filename: Mapped[str] = mapped_column(String(128), nullable=False)
    upload_time: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    finish_time: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(Enum("pending", "done", name="upload_status"), default="pending")
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey('user.id'))


def setup_app():
    """
    Sets up the Flask application by loading environment variables from a .env file,
    configuring app settings, and creating the uploads and outputs folders if they don't exist.
    """
    load_dotenv()
    app.secret_key = os.getenv("SECRET_KEY")
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    with app.app_context():
        db.create_all()
    set_path()
    setup_explainer()


def setup_explainer():
    """
    Sets up the explainer system.

    This function should be called before starting the explainer system
    to set up any necessary configurations or environment settings.
    """

    # Set asyncio platform
    if sys.platform.startswith(WINDOWS_PLATFORM):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def process_file(filename: str):
    """
    Processes the uploaded file by extracting text from presentation slides,
    handling the slides asynchronously, and saving the responses as JSON.

    Args:
        filename (str): The filename of the uploaded file to be processed.
    """

    upload_path = f"{UPLOADS_FOLDER}/{filename}"
    slides = PresentationParser.extract_text(upload_path)
    responses = asyncio.run(SlideHandler.response_handler(slides))
    output_path = f"{OUTPUTS_FOLDER}/{filename}"
    OutputManage.save_to_json(responses, output_path)


def explainer_system(stop_event: threading.Event):
    """
    Implements the background explainer system that continuously processes
    files in the uploads folder that are not yet processed.

    This function runs in an infinite loop until the stop event is set.
    It processes the files using the process_file() function and sleeps for
    TIME_TO_SLEEP seconds between iterations.

    Args:
        stop_event (threading.Event): The event to signal the system to stop.
    """
    while not stop_event.is_set():
        with app.app_context():
            upload_files = Upload.query.filter_by(status="pending").all()
            for upload_file in upload_files:
                if not stop_event.is_set():
                    try:
                        _, file_type = os.path.splitext(upload_file.filename)
                        process_file(f"{upload_file.uid}{file_type}")
                        upload_file.finish_time = datetime.now()
                        upload_file.status = "done"
                        db.session.commit()
                    except KeyError:
                        continue
        stop_event.wait(timeout=TIME_TO_SLEEP)


def save_upload(file):
    anonymous_upload = Upload(filename=file.filename)
    db.session.add(anonymous_upload)
    db.session.commit()
    _, file_type = os.path.splitext(file.filename)
    file.save(os.path.join(UPLOADS_FOLDER, f"{anonymous_upload.uid}{file_type}"))
    return anonymous_upload.uid


def save_upload_with_user(file, email: str):
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email)
        db.session.add(user)
    user_upload = Upload(filename=file.filename, user=user)
    db.session.add(user_upload)
    db.session.commit()
    _, file_type = os.path.splitext(file.filename)
    file.save(os.path.join(UPLOADS_FOLDER, f"{user_upload.uid}{file_type}"))
    return user_upload.uid


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
        email = request.form["email"]
        if email:
            uid = save_upload_with_user(file, email)
        else:
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
    file_data = Upload.query.filter_by(uid=uid).first()
    if file_data:
        if file_data.status == "done":
            output = load_output(f"{uid}.json")
            status_info = save_to_json(uid, file_data.status, file_data.filename, file_data.finish_time, output)
        else:
            status_info = save_to_json(uid, file_data.status, file_data.filename, file_data.finish_time)
        return Response(json.dumps(status_info), mimetype='application/json')
    return jsonify({'status': 'not found'}), 404


@app.route('/search', methods=['POST', 'GET'])
def search():
    """
    Handles the search functionality. Accepts both POST and GET requests.
    If a POST request is received with a non-empty UID, it redirects to the
    'status' route with the UID as a parameter.
    If a POST request is received with an empty UID, it flashes a message
    indicating that the UID should be entered and redirects back to the search page.
    If a POST request is received with both email and filename provided, it searches
    for the latest upload with that email and filename and redirects to 'status' route
    with the UID of the latest upload.
    If a GET request is received, it renders the 'search.html' template.

    Returns:
        str: The rendered HTML page or a redirect response.
    """
    if request.method == 'POST':
        uid = request.form.get('uid')
        email = request.form.get('email')
        filename = request.form.get('filename')
        if uid:
            return redirect(url_for('status', uid=uid))
        elif email and filename:  # Only search if both email and filename are provided
            user = User.query.filter_by(email=email).first()
            if user:
                latest_upload = Upload.query.filter_by(user=user, filename=filename).order_by(
                    Upload.upload_time.desc()).first()
                if latest_upload:
                    return redirect(url_for('status', uid=latest_upload.uid))
                else:
                    flash("Filename not found")
            else:
                flash(f"Email: {email} does not exist")
        else:
            flash("Please enter a UID, or provide both email and filename")
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
    with app.app_context():
        db.session.close()


if __name__ == '__main__':
    main()
