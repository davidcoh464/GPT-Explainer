import json
import os
import re
from fpdf import FPDF
from docx import Document
from bidi.algorithm import get_display


class OutputManage:
    @staticmethod
    def contains_hebrew(text):
        hebrew_pattern = re.compile(r'[\u0590-\u05FF]+')
        return bool(hebrew_pattern.search(text))

    @staticmethod
    def reverse_hebrew(text):
        hebrew_pattern = re.compile(r'([:,.?/&#!_-]?\s?[\u0590-\u05FF]+)+')
        reversed_text = hebrew_pattern.sub(lambda match: match.group(0)[::-1], text)
        return reversed_text

    @staticmethod
    def get_content(responses: list[dict]) -> list[str]:
        """
        retrieve the content that inside of the dictionary and make the list
        to be flattened with only the content values
        Args:
            responses (list[dict]): The list of responses to retrieve the content from.
        Returns:
            list[str]: The flattened list.
        """
        if len(responses) > 0 and responses[0].get("choices"):
            return [response["choices"][0]["message"]["content"] for response in responses]
        return [response.get("content") for response in responses]

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
        content_list = OutputManage.get_content(responses)
        # Change to a more orderly form of slide number, content
        slide_list = [{"slide_number": i, "content": content} for i, content in enumerate(content_list, start=1)]

        with open(output_file, 'w') as f:
            json.dump(slide_list, f, indent=4)
        return output_file

    @staticmethod
    def save_to_pdf(responses: list[dict], user_path: str) -> str:
        """
        Saves the responses to a pdf file.

        Args:
            responses (list[dict]): The list of responses to be saved.
            user_path (str): The path of the user's input file.

        Returns:
            str: The path of the saved pdf file.
        """
        output_file = os.path.splitext(user_path)[0] + ".pdf"
        content_list = OutputManage.get_content(responses)
        pdf = FPDF('P', 'mm', 'Letter')
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_font('Arial', '', 'write_data/Arial.ttf', uni=True)
        pdf.set_font("Arial", size=12)
        for page_number, page_content in enumerate(content_list, start=1):
            pdf.add_page()
            lines = page_content.split('\n')
            for line_number, line in enumerate(lines, start=1):
                align = 'R' if OutputManage.contains_hebrew(line) else 'L'
                line = get_display(line) if align == 'R' else line
                pdf.multi_cell(0, 10, txt=line, ln=1, align='C' if line_number == 1 and len(lines) > 1 else align)
        pdf.output(output_file)
        return output_file

    @staticmethod
    def save_to_txt(responses: list[dict], user_path: str) -> str:
        """
        Saves the responses to a txt file.

        Args:
            responses (list[dict]): The list of responses to be saved.
            user_path (str): The path of the user's input file.

        Returns:
            str: The path of the saved txt file.
        """
        output_file = os.path.splitext(user_path)[0] + ".txt"
        content_list = OutputManage.get_content(responses)
        with open(output_file, 'w') as f:
            f.write('\n\n'.join(content_list))
        return output_file

    @staticmethod
    def save_to_docx(responses: list[dict], user_path: str) -> str:
        """
        Saves the responses to a docx file.
        Args:
            responses (list[dict]): The list of responses to be saved.
            user_path (str): The path of the user's input file.
            Returns:
                str: The path of the saved docx file.
        """
        output_file = os.path.splitext(user_path)[0] + ".docx"
        content_list = OutputManage.get_content(responses)
        document = Document()
        for page_number, page_content in enumerate(content_list, start=1):
            lines = page_content.split('\n')
            for line in lines:
                document.add_paragraph(line)
            if page_number < len(content_list):
                document.add_page_break()
        document.save(output_file)
        return output_file