import base64
import requests
import os

file_path = "/home/chaima/Downloads/melody-intro-oct-1-252160.mp3"

# Lire le fichier audio
with open(file_path, "rb") as f:
    encoded = base64.b64encode(f.read()).decode("utf-8")

file_size = os.path.getsize(file_path)

# Construire la payload JSON
payload = {
    "candidate_id": "cand123",
    "question_id": "qst456",
    "file_name": "test_audio.mp3",
    "file_size": file_size,
    "duration": 3.5,
    "format": "mp3",
    "file_content": encoded
}

# Envoyer la requête POST
response = requests.post("http://localhost:8000/audio-responses", json=payload)

print("Status code:", response.status_code)
print(response.text)
