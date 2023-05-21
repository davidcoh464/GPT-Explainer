"""
prompt_generator.py

This module generates prompts for slide rewriting.

Classes:
- PromptGenerator

"""


class PromptGenerator:
    def __init__(self, slide_content: str, slide_index: int):
        """
        Initializes a PromptGenerator object.

        Args:
            slide_content (str): The content of the slide.
            slide_index (int): The index of the slide.

        """
        self.slide_content = slide_content
        self.slide_index = slide_index

    def get_prompt(self) -> str:
        """
        Generates a prompt for rewriting a slide in a better way.

        Returns:
            str: The generated prompt.

        """
        prompt = f"Can you rewrite the following slide in a better way?\n"
        prompt += f"Slide number: {self.slide_index}\n"
        prompt += f"{self.slide_content}"

        return prompt
