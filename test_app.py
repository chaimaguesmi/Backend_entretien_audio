import json
import base64
import pytest
from chalice.test import Client
from app import app

@pytest.fixture
def client():
    with Client(app) as client:
        yield client

def test_create_audio_response(client):
    fake_audio = base64.b64encode(b"FakeAudioContent").decode('utf-8')

    payload = {
        "candidate_id": "test-candidate",
        "question_id": "question-1",
        "file_name": "test_audio.mp3",
        "file_size": 12345,
        "duration": 8.0,
        "format": "mp3",
        "file_content": fake_audio
    }

    response = client.http.post(
        '/audio-responses',
        headers={"Content-Type": "application/json"},
        body=json.dumps(payload)
    )

    assert response.status_code == 201
    data = json.loads(response.body.decode())
    assert data["candidate_id"] == "test-candidate"

def test_create_conversation(client):
    payload = {
        "candidate_id": "test-candidate",
        "job_title": "Développeur Frontend",
        "company_name": "Facebook"
    }

    response = client.http.post(
        '/conversations',
        headers={"Content-Type": "application/json"},
        body=json.dumps(payload)
    )

    assert response.status_code == 201
    data = json.loads(response.body.decode())
    assert data["candidate_id"] == "test-candidate"
    assert data["company_name"] == "Facebook"

def test_get_conversations_by_candidate(client):
    # Crée d'abord la conversation
    payload = {
        "candidate_id": "test-candidate",
        "job_title": "Développeur Frontend",
        "company_name": "Facebook"
    }

    client.http.post(
        '/conversations',
        headers={"Content-Type": "application/json"},
        body=json.dumps(payload)
    )

    # Lis les conversations
    response = client.http.get('/conversations/candidate/test-candidate')

    assert response.status_code == 200
    data = json.loads(response.body.decode())
    assert data["count"] > 0
    assert data["conversations"][0]["candidate_id"] == "test-candidate"
