import pytest
from flask_app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome" in response.data


def test_upload(client):
    response = client.post('/upload', data={'file': (open('can you.pptx', 'rb'), 'can you.pptx')})
    assert response.status_code == 200
    assert b"uid" in response.data


def test_status(client):
    response = client.get('/status/12345')
    assert response.status_code == 404
    assert b"not found" in response.data
