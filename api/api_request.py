import aiohttp
import os
import openai


class ApiRequest:
    @staticmethod
    async def generate_text(prompt: str):
        """
        Generates text using the OpenAI API based on the given prompt.
        Args:
            prompt (str): The prompt for text generation.
        Returns:
            dict: The response JSON object containing the generated text.
        Raises:
            aiohttp.ClientError: If there is an error during the API request.
        """
        openai.api_key = os.getenv("API_KEY")
        engine = "gpt-3.5-turbo"
        max_tokens = 512
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {openai.api_key}", "Content-Type": "application/json"},
                json={
                    "messages": [{"role": "system", "content": "You are a helpful assistant."},
                                 {"role": "user", "content": prompt}], "max_tokens": max_tokens, "model": engine})
            return await response.json()
