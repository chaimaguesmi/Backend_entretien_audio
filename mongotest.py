import pymongo
from pymongo import MongoClient

def test_mongodb_connection():
    # 1. Test connexion
    client = MongoClient("mongodb://portago-UAT:Idzh4PLGpZ2vOO8KRY0E@mongo.allence.cloud/portago-UAT")
    db = client.get_database()
    assert db.name == "portago-UAT"
    
    # 2. Test collection
    collection = db.audio_responses
    assert 'audio_responses' in db.list_collection_names()
    
    # 3. Test insertion
    test_doc = {
        "candidate_id": "test_cand",
        "question_id": "test_quest",
        "file_path": "/tmp/test.mp3",
        "file_name": "test.mp3",
        "file_size": 1024,
        "format": "mp3"
    }
    inserted_id = collection.insert_one(test_doc).inserted_id
    assert inserted_id is not None
    
    # 4. Test lecture
    doc = collection.find_one({"_id": inserted_id})
    assert doc['candidate_id'] == "test_cand"
    
    collection.delete_one({"_id": inserted_id})

if __name__ == "__main__":
    test_mongodb_connection()
    print("Tous les tests MongoDB ont réussi!")