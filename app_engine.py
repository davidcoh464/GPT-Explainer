import asyncio
import tkinter as tk
import os
import sys
from tkinter import filedialog
from dotenv import load_dotenv
from file_reader import read_file
from api_handler.slide_handler import SlideHandler
from output_manage import OutputManage

WINDOWS_PLATFORM = 'win'


def configure():
    """
    Loads the variables from the .env file.
    """
    load_dotenv()
    # Set asyncio platform
    if sys.platform.startswith(WINDOWS_PLATFORM):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def get_user_path() -> str:
    """
    Opens a file dialog to prompt the user for a PowerPoint file (.pptx) path.

    Returns:
        str: The path of the selected PowerPoint file.

    Raises:
        ValueError: If an invalid file type is selected or no file is selected.
    """
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select PowerPoint or pdf file",
        filetypes=[("PowerPoint files", "*.pptx"), ("pdf files", "*.pdf")]
    )
    if not file_path:
        raise ValueError("No file selected.")
    elif not os.path.exists(file_path):
        raise ValueError("The selected file does not exist.")
    elif not file_path.lower().endswith(('.pptx', '.pdf')):
        raise ValueError("Invalid file type. Please select a .pptx or .pdf file.")
    else:
        return file_path


def main():
    """
    Main function to process the PowerPoint presentation.

    Parses the presentation, extracts text from each slide,
    sends it to the OpenAI API for response, and saves the responses to a JSON file.
    """
    configure()
    user_path = get_user_path()
    slides = read_file.extract_text(user_path)
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(SlideHandler.response_handler(slides))
    output_file = OutputManage.save_to_json(responses, user_path)
    print(f"Saving the output file in {output_file}")


if __name__ == "__main__":
    main()
