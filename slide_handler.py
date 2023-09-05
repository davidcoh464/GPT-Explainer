"""
slide_handler.py

This module handles the processing and handling of slides.

Classes:
- SlideHandler

"""

from prompt_generator import PromptGenerator
from api_request import ApiRequest
import asyncio


class SlideHandler:
    @staticmethod
    async def process_slide(slide_content: str, slide_index: int):
        """
        Processes a slide by generating a prompt and requesting text generation from the OpenAI API.

        Args:
            slide_content (str): The content of the slide.
            slide_index (int): The index of the slide.

        Returns:
            dict: The response received from the OpenAI API.

        """
        prompt = PromptGenerator(slide_content, slide_index + 1).get_prompt()
        return await ApiRequest.generate_text(prompt)

    @staticmethod
    async def response_handler(slides: list[str]) -> list[dict]:
        """
        Handles the responses from the OpenAI API for each slide.

        Args:
            slides (list[str]): A list of slide contents.

        Returns:
            list[dict]: A list of response dictionaries.

        """
        tasks = []
        for slide_index, slide_content in enumerate(slides):
            task = asyncio.create_task(SlideHandler.process_slide(slide_content, slide_index))
            tasks.append(task)

        # Wait for all tasks to complete
        responses = await asyncio.gather(*tasks)
        return responses
