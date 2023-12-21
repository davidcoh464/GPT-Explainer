"""
prompt_generator.py

This module generates prompts for slide rewriting.
"""


def get_prompt(slide_content: str, slide_index: int, custom_prompt: str = "") -> str:
    """
    Generates a prompt for rewriting a slide in a more improved way.
    Args:
        slide_content (str): The content of the slide to be rewritten.
        slide_index (int): The index or page number of the slide.
        custom_prompt (str, optional): An optional custom prompt provided by the user.
                                       If not specified, a default prompt will be used.
    Returns:
        str: The generated prompt for rewriting the slide.
    """
    if custom_prompt == "":
        custom_prompt = f"Rewrite the following page in a better way:"
    page_slide = 'Slide' if 'slide' in custom_prompt else 'Page'
    prompt = f"{custom_prompt}\n{page_slide} number: {slide_index}\n{slide_content}"
    return prompt
