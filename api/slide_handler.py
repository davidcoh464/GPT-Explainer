from api.prompt_generator import get_prompt
from api.api_request import ApiRequest
import asyncio


class SlideHandler:
    @staticmethod
    async def process_slide(slide_content: str, slide_index: int, custom_prompt: str = "") -> dict:
        """
        Processes a slide by generating a prompt and requesting text generation from the OpenAI API.

        Args:
            slide_content (str): The content of the slide to be processed.
            slide_index (int): The index or page number of the slide.
            custom_prompt (str, optional): An optional custom prompt for text generation.
                                           If not specified, a default prompt will be used.

        Returns:
            dict: The response received from the OpenAI API.
        """
        return await ApiRequest.generate_text(get_prompt(slide_content, slide_index + 1, custom_prompt))

    @staticmethod
    async def response_handler(slides: list[str], custom_prompt: str = "") -> list[dict]:
        """
        Handles the responses from the OpenAI API for each slide.
        Args:
            slides (list[str]): A list of slide contents.
            custom_prompt (str, optional): An optional custom prompt for text generation.
                                          If not specified, a default prompt will be used.
        Returns:
            list[dict]: A list of response dictionaries.
        """
        tasks = []
        for slide_index, slide_content in enumerate(slides):
            task = asyncio.create_task(SlideHandler.process_slide(slide_content, slide_index, custom_prompt))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
        return [response for response in responses]
