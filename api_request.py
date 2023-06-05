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
        # Set OpenAI API key
        openai.api_key = os.getenv("API_KEY")

        # Set engine and parameters
        engine = "gpt-3.5-turbo"
        max_tokens = 128

        # Generate text from prompt asynchronously
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                "https://api.openai.com/v1/chat/completions",  # Updated endpoint URL
                headers={
                    "Authorization": f"Bearer {openai.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "messages": [{"role": "system", "content": "You are a helpful assistant."},
                                 {"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "model": "gpt-3.5-turbo"  # Add the model parameter
                }
            )
            return await response.json()
