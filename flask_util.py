from pathlib import Path
from typing import Dict
from datetime import datetime
from db_model import Session, Upload, User, UploadStatus
import os
import json


UPLOADS_FOLDER = "uploads"
OUTPUTS_FOLDER = "outputs"
status_done = UploadStatus.done
status_pending = UploadStatus.pending


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


def save_to_json(uid: str, upload_status: str, name: str, finish_time: datetime = None, explanation=None):
    """
    Creates a dictionary object to represent the upload status, including the
    filename, timestamp, processing status, and an optional explanation.

    Args:
        uid: the uid of the upload.
        upload_status: The status of the upload.
        name: The name of the file.
        finish_time: ThAn optional finish time of the upload.
        explanation: An optional explanation for the upload status.

    Returns:
        Dict: A dictionary representing the upload status.
    """
    return {
        'uid': uid,
        'status': upload_status,
        'filename': name,
        'finish time': str(finish_time),
        'explanation': explanation
    }


def set_path():
    """
    Create the uploads and outputs folders if they don't exist
    """
    Path('db').mkdir(parents=True, exist_ok=True)
    Path(UPLOADS_FOLDER).mkdir(parents=True, exist_ok=True)
    Path(OUTPUTS_FOLDER).mkdir(parents=True, exist_ok=True)


def save_upload(file):
    """
    Saves the uploaded file as an anonymous upload.

    This function creates an Upload object in the database to represent the uploaded file
    and saves the file to the uploads folder using a generated UID. The function returns
    the UID associated with the uploaded file.

    Args:
        file (FileStorage): The uploaded file to be saved.

    Returns:
        str: The UID associated with the uploaded file.
    """
    with Session() as session:
        anonymous_upload = Upload(filename=file.filename, upload_time=datetime.now())
        session.add(anonymous_upload)
        session.commit()
        _, file_type = os.path.splitext(file.filename)
        file.save(os.path.join(UPLOADS_FOLDER, f"{anonymous_upload.uid}{file_type}"))
        return anonymous_upload.uid


def save_upload_with_user(file, email: str):
    """
    Saves the uploaded file with the associated user.

    This function creates a User object in the database if the user with the provided
    email doesn't exist. It then creates an Upload object associated with the user and
    saves the file to the uploads folder using a generated UID. The function returns
    the UID associated with the uploaded file.

    Args:
        file (FileStorage): The uploaded file to be saved.
        email (str): The email of the user associated with the uploaded file.

    Returns:
        str: The UID associated with the uploaded file.
    """
    with Session() as session:
        user = session.query(User).filter_by(email=email).first()
        if not user:
            user = User(email=email)
            session.add(user)
            session.commit()
        user_upload = Upload(filename=file.filename, upload_time=datetime.now(), user=user)
        session.add(user_upload)
        session.commit()
        _, file_type = os.path.splitext(file.filename)
        file.save(os.path.join(UPLOADS_FOLDER, f"{user_upload.uid}{file_type}"))
        return user_upload.uid
