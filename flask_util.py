from pathlib import Path
from typing import Dict
from uuid import uuid4
from datetime import datetime
import os
import json

UPLOADS_FOLDER = "uploads"
OUTPUTS_FOLDER = "outputs"


def generate_uid() -> str:
    """
    Generates a unique identifier (UID) using the UUID4 algorithm.

    Returns:
        str: The generated unique identifier.
    """
    return str(uuid4())


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
    Path(UPLOADS_FOLDER).mkdir(parents=True, exist_ok=True)
    Path(OUTPUTS_FOLDER).mkdir(parents=True, exist_ok=True)
