"""
prompt_generator.py

This module generates prompts for slide rewriting.
"""


def get_prompt(slide_content, slide_index) -> str:
    """
    Generates a prompt for rewriting a slide in a better way.
    Returns:
        str: The generated prompt.
    """
    prompt = f"Rewrite the following page in a better way:\n"
    prompt += f"Page number: {slide_index}\n"
    prompt += f"{slide_content}"
    return prompt
