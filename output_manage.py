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
        with open(output_file, 'w') as f:
            json.dump(responses, f)
        return output_file
