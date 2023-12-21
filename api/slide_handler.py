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
        if slide_content.strip():
            return await ApiRequest.generate_text(get_prompt(slide_content, slide_index, custom_prompt))
        return {"choices": {"message": {"content": f"{slide_index}"}}}

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
        async_tasks = []
        for slide_index, slide_content in enumerate(slides, start=1):
            async_task = asyncio.create_task(SlideHandler.process_slide(slide_content, slide_index, custom_prompt))
            async_tasks.append(async_task)
        try:
            responses = await asyncio.gather(*async_tasks)
            return [response for response in responses]
        except Exception as e:
            print(f"Error in response_handler: {e}")
            return []
