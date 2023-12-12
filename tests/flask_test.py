import pytest
from flask_app import app, setup_app
from tests.test_util import clear_resource
import json

# Define the path to your file
FILE_PATH = 'can you.pptx'


@pytest.fixture
def client():
    """
    Fixture to provide a test client for the Flask app.
    It sets the app's testing configuration and yields the test client.
    """
    setup_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home(client):
    """
    Test case for the home route ("/").
    It sends a GET request to the home route and asserts the response.
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome" in response.data


def test_upload(client):
    """
    Test case for the upload route ("/upload").
    It sends a POST request with a file to the upload route and asserts the response.
    """
    with open(FILE_PATH, 'rb') as file:
        response = client.post('/upload', data={'file': (file, FILE_PATH)})
    assert response.status_code == 200
    assert b"uid" in response.data
    data = json.loads(response.data)
    clear_resource(data['uid'])


def test_status(client):
    """
    Test case for the status route ("/status/<uid>").
    It sends a GET request to the status route with a non-existent UID and asserts the response.
    """
    response = client.get('/status/12345')
    assert response.status_code == 404
    assert b"not found" in response.data


def test_upload_status(client):
    """
    Test case for checking the status of an uploaded file.
    It uploads a file and then sends a GET request to the status route using the uploaded UID.
    It asserts the response to check if the status is "pending".
    """
    response = client.post('/upload', data={'file': (open(f'{FILE_PATH}', 'rb'), f'{FILE_PATH}')})
    assert response.status_code == 200
    data = json.loads(response.data)
    uid = data.get('uid')
    response = client.get(f'/status/{uid}')
    assert response.status_code == 200
    data = json.loads(response.data)
    status = data["status"]
    assert status == "pending"
    clear_resource(uid)
