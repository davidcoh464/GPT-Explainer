import asyncio
import tkinter as tk
import os
import sys
from tkinter import filedialog
from dotenv import load_dotenv
import read_data
from api.slide_handler import SlideHandler
from write_data.output_manage import OutputManage

WINDOWS_PLATFORM = 'win'


def configure():
    """Load variables from the .env file and set asyncio platform."""
    load_dotenv()
    if sys.platform.startswith(WINDOWS_PLATFORM):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def get_user_path() -> str:
    """
    Prompt user to select a PowerPoint (.pptx) or PDF (.pdf) file.
    Returns:
        str: Path of the selected file.
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
    Process PowerPoint presentation (or pdf file).
    Parse the presentation, extract text from each slide,
    send it to the OpenAI API for response, and save responses to a PDF file.
    """
    configure()
    user_path = get_user_path()
    slides = read_data.extract_text(user_path)
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(SlideHandler.response_handler(slides))
    output_file = OutputManage.save_to_pdf(responses, user_path)
    print(f"Saving the output file in {output_file}")


if __name__ == "__main__":
    main()
