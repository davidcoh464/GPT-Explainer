import pptx
from pptx import Presentation


def extract_text(path_to_presentation):
    """
    Extracts the text from each shape in each slide of a PowerPoint presentation.

    Args:
        path_to_presentation (str): The file path to the PowerPoint presentation.

    Returns:
        A list of slides, where each slide is a list of shapes, where each shape is a list of paragraphs,
        where each paragraph is a list of text runs.
    """
    prs = Presentation(path_to_presentation)

    # text_runs will be populated with a list of strings,
    # one for each text run in presentation

    slide_text = {}
    for slide_index, slide in enumerate(prs.slides):
        shape_text = []
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            paragraph_text = []
            for paragraph in shape.text_frame.paragraphs:
                run_text = ""
                for run in paragraph.runs:
                    run_text = run_text + run.text
                if run_text != "":
                    paragraph_text.append(run_text)
            if paragraph_text:
                shape_text.append(paragraph_text)
        slide_text[slide_index] = shape_text
    return slide_text


if __name__ == "__main__":
    text_runs = extract_text("C://Users//user//Downloads//logging.pptx")
    for k, v in text_runs.items():
        print(f" {k+1} : {v}")