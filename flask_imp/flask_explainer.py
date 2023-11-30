import asyncio
import os
import sys
import threading
from datetime import datetime

from flask_imp.db_model import Session, Upload
from flask_imp.flask_util import UPLOADS_FOLDER, OUTPUTS_FOLDER, status_pending, status_done
from output_manage import OutputManage
from read_data import extract_text
from api.slide_handler import SlideHandler

TIME_TO_SLEEP = 10
WINDOWS_PLATFORM = 'win'


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
    slides = extract_text(upload_path)
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
        with Session() as session:
            upload_files = session.query(Upload).filter_by(status=status_pending).all()
            for upload_file in upload_files:
                if not stop_event.is_set():
                    try:
                        _, file_type = os.path.splitext(upload_file.filename)
                        process_file(f"{upload_file.uid}{file_type}")
                        upload_file.finish_time = datetime.now()
                        upload_file.status = status_done
                        session.commit()
                    except KeyError:
                        continue
        stop_event.wait(timeout=TIME_TO_SLEEP)
