import threading
from flask_util import UPLOADS_FOLDER, OUTPUTS_FOLDER, is_file_processed, os
from presentation_parser import PresentationParser
from slide_handler import SlideHandler
from output_manage import OutputManage
import asyncio
import sys

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
        filenames = [filename for filename in os.listdir(UPLOADS_FOLDER) if not is_file_processed(filename)]
        for filename in filenames:
            if not stop_event.is_set():
                try:
                    process_file(filename)
                except KeyError:
                    continue
        stop_event.wait(timeout=TIME_TO_SLEEP)
