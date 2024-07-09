# Flask Upload and Processing App

Welcome to the Flask Upload and Processing App, a robust solution for explaining and processing pptx and pdf files.
This application provides users with a seamless experience to upload files, incorporating optional prompts and email information.
Behind the scenes, an explanation system utilizes ChatGPT API to analyze each slide/page asynchronously using asyncio.

## Table of Contents

- [Features](#features)
- [How it works](#how-it-works)
- [Installation](#installation)
- [Requirements](#requirements)
- [Usage](#usage)
- [Endpoints](#endpoints)

## Features

- **File Upload:** Users can easily upload pptx and pdf files, including optional prompts and email information.
- **Background Explanation System:** The application processes each slide/page in the uploaded files using the ChatGPT API, ensuring a comprehensive analysis in the background.
- **Unique UID:** Upon uploading a file, users receive a unique UID, enabling them to conveniently search for the file output.
- **Search Functionality:** Users can search for file outputs using the UID, file name, or email associated with the upload.
- **Status Page:** Once the file output is ready, users can view a detailed HTML table representation on the status page.
- **Download Options:** The processed output can be downloaded in various formats, including pdf, docx, json, or txt.

## How it works

1. **Upload a File:**
   - Navigate to the upload page.
   - Select a pptx or pdf file.
   - Optionally provide a prompt and email.
   - Upon submission, a unique UID is generated.
    ![alt text](https://raw.githubusercontent.com/davidcoh464/GPT-Explainer/main/app%20images/upload%20page%20.png)

2. **Background Processing:**
   - The application utilizes asyncio to asynchronously send each slide/page to the ChatGPT API for analysis.

3. **Search and Retrieve:**
   - Users can search for the output file by the unique uid for the file or by the file name + email (if provided).
   ![alt text](https://raw.githubusercontent.com/davidcoh464/GPT-Explainer/main/app%20images/serach%20page.png)

4. **View and Download:**
   - Once the file output is ready, users can view a comprehensive HTML table representation on the status page.
   - Download the processed output in pdf, docx, json, or txt format.
   ![alt text](https://raw.githubusercontent.com/davidcoh464/GPT-Explainer/main/app%20images/explainer%20status%20page.png)


## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   ```

2. Navigate to the project directory:

   ```bash
   cd <project-directory>
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Requirements

Before running the application, ensure you have set up the necessary environment variables by creating an `.env` file in the project root directory. Follow the steps below:

1. Create an `.env` file in the project root directory.

2. Open the `.env` file and add the following lines, replacing `"your_openai_key"` and `"your_flask_secret_key"` with your actual API key for OpenAI and a secure secret key for Flask:

   ```dotenv
   API_KEY="your_openai_key"
   SECRET_KEY="your_flask_secret_key"

## Usage

1. Run the Flask application:

   ```bash
   python flask_app.py
   ```

2. Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Endpoints

- **Home Page:** [http://127.0.0.1:5000](http://127.0.0.1:5000)
- **Upload Page:** [http://127.0.0.1:5000/upload](http://127.0.0.1:5000/upload)
- **Status Page:** [http://127.0.0.1:5000/status/<uid>](http://127.0.0.1:5000/status/<uid>)
- **Search Page:** [http://127.0.0.1:5000/search](http://127.0.0.1:5000/search)
