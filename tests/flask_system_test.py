import pytest
import subprocess
import requests
import time
from tests.test_util import clear_resource


# Define the base URL for the running Flask app
BASE_URL = 'http://localhost:5000'
# Define the path to your file
FILE_PATH = 'can you.pptx'


@pytest.fixture(scope='session', autouse=True)
def run_flask_app():
    # Start the Flask app as a subprocess
    process = subprocess.Popen(['python', '../flask_app.py', 'test'])
    # Wait for the app to start up
    time.sleep(2)
    # Yield the process object to the tests
    yield process
    # After the tests are finished, terminate the Flask app process
    process.terminate()


def test_system():
    """
    System test for the Flask app.
    Performs an upload test, retrieves the status, and waits for the status to change to 'done' with a timeout mechanism.
    """
    # Upload test
    with open(FILE_PATH, 'rb') as file:
        response = requests.post(f'{BASE_URL}/upload', files={'file': file})
    assert response.status_code == 200
    data = response.json()
    uid_upload = data.get('uid')

    # Status test
    status_url = f'{BASE_URL}/status/{uid_upload}'
    for _ in range(10):  # Gives the system 2*10 = 20 seconds to finish
        response = requests.get(status_url)
        assert response.status_code == 200
        data = response.json()
        status = data.get('status')
        print(status)
        if status == 'done':
            break
        time.sleep(2)
    else:  # If the 20 seconds are over without the status changing to 'done'
        pytest.fail("Timeout exceeded. Status did not change to 'done'.")
    clear_resource(upload_uid=uid_upload)
