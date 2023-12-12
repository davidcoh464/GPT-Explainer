"""
output_manage.py

This module handles the output management, including saving responses to a JSON file.

Classes:
- OutputManage

"""

import json
import os


class OutputManage:
    @staticmethod
    def save_to_json(responses: list[dict], user_path: str) -> str:
        """
        Saves the responses to a JSON file.

        Args:
            responses (list[dict]): The list of responses to be saved.
            user_path (str): The path of the user's input file.

        Returns:
            str: The path of the saved JSON file.
        """
        output_file = os.path.splitext(user_path)[0] + ".json"
        # Extract the content from the API responses
        content_list = [response["choices"][0]["message"]["content"] for response in responses]
        # Change to a more orderly form of slide number, content
        slide_list = [{"slide_number": i, "content": content} for i, content in enumerate(content_list, start=1)]

        with open(output_file, 'w') as f:
            json.dump(slide_list, f, indent=4)
        return output_file
