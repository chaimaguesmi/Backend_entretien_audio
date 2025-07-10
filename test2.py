import pytest
import base64
import os
import json
from chalice.test import Client
from app import app

@pytest.fixture
def test_client():
    with Client(app) as client:
        yield client

TEST_AUDIO_PATH = '/home/chaima/Downloads/melody-intro-oct-1-252160.mp3'

def test_full_audio_response_flow(test_client):
    # 1. Vérifier que le fichier test existe
    if not os.path.exists(TEST_AUDIO_PATH):
        pytest.skip(f"Fichier audio de test manquant: {TEST_AUDIO_PATH}")

    # 2. Lire et encoder le fichier audio
    with open(TEST_AUDIO_PATH, 'rb') as f:
        encoded_content = base64.b64encode(f.read()).decode('utf-8')

    # 3. Préparer les données de la requête
    payload = {
        "candidate_id": "cand_test",
        "question_id": "quest_test",
        "file_name": os.path.basename(TEST_AUDIO_PATH),
        "file_size": os.path.getsize(TEST_AUDIO_PATH),
        "format": "mp3",
        "file_content": encoded_content
    }

    # 4. Envoyer la requête POST (version corrigée pour Chalice)
    response = test_client.http.post(
        '/audio-responses',
        headers={'Content-Type': 'application/json'},
        body=json.dumps(payload)
    )
    
    assert response.status_code == 201
    audio_id = response.json_body['id']
    
    # 5. Vérifier la récupération
    response = test_client.http.get(f'/audio-responses/{audio_id}')
    assert response.status_code == 200
    assert response.json_body['candidate_id'] == "cand_test"
    
    # 6. Tester le téléchargement
    response = test_client.http.get(f'/audio-responses/{audio_id}/download')
    assert response.status_code == 200
    assert 'file_content' in response.json_body
    
    # 7. Tester la suppression
    response = test_client.http.delete(f'/audio-responses/{audio_id}')
    assert response.status_code == 200
    
    # 8. Vérifier que la suppression est effective
    response = test_client.http.get(f'/audio-responses/{audio_id}')
    assert response.status_code == 404