import os
import uuid
import boto3
from typing import List, Optional
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

from chalicelib.modules.models import AudioResponseCreate, AudioResponseModel, AudioResponseUpdate, ConversationCreate, ConversationMessage, ConversationModel, ConversationUpdate

from dotenv import load_dotenv
load_dotenv()

class AudioResponseService:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGODB_URL"))
        self.db = self.client.get_default_database()
        self.collection = self.db.audio_responses
        
        # Configuration S3 pour le stockage des fichiers (optionnel)
        self.s3_client = boto3.client('s3') if os.getenv('AWS_ACCESS_KEY_ID') else None
        self.s3_bucket = os.getenv('S3_BUCKET_NAME', 'careere-audio-responses')
        
        # Dossier local pour le stockage si S3 n'est pas configuré
        self.local_storage_path = os.getenv('LOCAL_STORAGE_PATH', '/tmp/audio_responses')
        os.makedirs(self.local_storage_path, exist_ok=True)
    
    def save_audio_file(self, file_content: bytes, file_name: str, candidate_id: str) -> str:
        """Sauvegarde le fichier audio localement ou sur S3"""
   
        file_extension = file_name.split('.')[-1]
        unique_filename = f"{candidate_id}_{uuid.uuid4()}.{file_extension}"
        
        if self.s3_client:
            # Sauvegarder sur S3
            try:
                self.s3_client.put_object(
                    Bucket=self.s3_bucket,
                    Key=f"audio_responses/{unique_filename}",
                    Body=file_content
                )
                return f"s3://{self.s3_bucket}/audio_responses/{unique_filename}"
            except Exception as e:
                print(f"Erreur lors de l'upload S3: {e}")
                # Fallback vers stockage local
                pass
        
        # Sauvegarder localement
        file_path = os.path.join(self.local_storage_path, unique_filename)
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return file_path
    
    def delete_audio_file(self, file_path: str) -> bool:
       
        try:
            if file_path.startswith('s3://') and self.s3_client:
                # Supprimer de S3
                bucket_name = file_path.split('/')[2]
                key = '/'.join(file_path.split('/')[3:])
                self.s3_client.delete_object(Bucket=bucket_name, Key=key)
            else:
                # Supprimer localement
                if os.path.exists(file_path):
                    os.remove(file_path)
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression du fichier: {e}")
            return False
    
    def create_audio_response(self, audio_data: AudioResponseCreate, file_content: bytes) -> AudioResponseModel:
   

        file_path = self.save_audio_file(file_content, audio_data.file_name, audio_data.candidate_id)
        
        audio_response = AudioResponseModel(
            candidate_id=audio_data.candidate_id,
            question_id=audio_data.question_id,
            file_path=file_path,
            file_name=audio_data.file_name,
            file_size=audio_data.file_size,
            duration=audio_data.duration,
            format=audio_data.format
        )
        
        # Insérer en base
        result = self.collection.insert_one(audio_response.dict(by_alias=True))
        audio_response.id = result.inserted_id
        
        return audio_response
    
    def get_audio_response_by_id(self, audio_id: str) -> Optional[AudioResponseModel]:
        
        if not ObjectId.is_valid(audio_id):
            return None
            
        doc = self.collection.find_one({"_id": ObjectId(audio_id)})
        if doc:
            return AudioResponseModel(**doc)
        return None
    
    def get_audio_responses_by_candidate(self, candidate_id: str) -> List[AudioResponseModel]:
      
        docs = self.collection.find({"candidate_id": candidate_id}).sort("created_at", -1)
        return [AudioResponseModel(**doc) for doc in docs]
    
    def get_audio_response_by_question(self, candidate_id: str, question_id: str) -> Optional[AudioResponseModel]:
   
        doc = self.collection.find_one({
            "candidate_id": candidate_id,
            "question_id": question_id
        })
        if doc:
            return AudioResponseModel(**doc)
        return None
    
    def update_audio_response(self, audio_id: str, update_data: AudioResponseUpdate) -> Optional[AudioResponseModel]:
        
        if not ObjectId.is_valid(audio_id):
            return None
            
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        update_dict["updated_at"] = datetime.utcnow()
        
        result = self.collection.update_one(
            {"_id": ObjectId(audio_id)},
            {"$set": update_dict}
        )
        
        if result.modified_count > 0:
            return self.get_audio_response_by_id(audio_id)
        return None
    
    def delete_audio_response(self, audio_id: str) -> bool:
    
        if not ObjectId.is_valid(audio_id):
            return False
        
        audio_response = self.get_audio_response_by_id(audio_id)
        if not audio_response:
            return False
        
       
        file_deleted = self.delete_audio_file(audio_response.file_path)

        result = self.collection.delete_one({"_id": ObjectId(audio_id)})
        
        return result.deleted_count > 0
    
    def get_all_audio_responses(self, skip: int = 0, limit: int = 100) -> List[AudioResponseModel]:
        
        docs = self.collection.find().sort("created_at", -1).skip(skip).limit(limit)
        return [AudioResponseModel(**doc) for doc in docs]
    
    def count_audio_responses(self) -> int:
        
        return self.collection.count_documents({})
    
    def count_audio_responses_by_candidate(self, candidate_id: str) -> int:
        
        return self.collection.count_documents({"candidate_id": candidate_id})
    

    
class ConversationService:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGODB_URL"))
        self.db = self.client.get_default_database()
        self.collection = self.db.conversations
    
    def create_conversation(self, conversation_data: ConversationCreate) -> ConversationModel:
   
        conversation = ConversationModel(
            candidate_id=conversation_data.candidate_id,
            job_title=conversation_data.job_title,
            company_name=conversation_data.company_name,
            interview_phase=conversation_data.interview_phase,
            question_categories=conversation_data.question_categories
        )
        
        result = self.collection.insert_one(conversation.dict(by_alias=True))
        conversation.id = result.inserted_id
        return conversation
    
    def get_conversation_by_id(self, conversation_id: str) -> Optional[ConversationModel]:
       
        if not ObjectId.is_valid(conversation_id):
            return None
        
        doc = self.collection.find_one({"_id": ObjectId(conversation_id)})
        if doc:
            return ConversationModel(**doc)
        return None
    
    def get_conversations_by_candidate(self, candidate_id: str) -> List[ConversationModel]:
     
        docs = self.collection.find({"candidate_id": candidate_id}).sort("created_at", -1)
        return [ConversationModel(**doc) for doc in docs]
    
    def update_conversation(self, conversation_id: str, update_data: ConversationUpdate) -> Optional[ConversationModel]:
    
        if not ObjectId.is_valid(conversation_id):
            return None
        
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        update_dict["updated_at"] = datetime.utcnow()
        
        result = self.collection.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": update_dict}
        )
        
        if result.modified_count > 0:
            return self.get_conversation_by_id(conversation_id)
        return None
    
    def add_message_to_conversation(self, conversation_id: str, message: ConversationMessage) -> Optional[ConversationModel]:
    
        if not ObjectId.is_valid(conversation_id):
            return None
        
        result = self.collection.update_one(
            {"_id": ObjectId(conversation_id)},
            {
                "$push": {"messages": message.dict()},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        if result.modified_count > 0:
            return self.get_conversation_by_id(conversation_id)
        return None
    
    def delete_conversation(self, conversation_id: str) -> bool:
        if not ObjectId.is_valid(conversation_id):
            return False
        
        result = self.collection.delete_one({"_id": ObjectId(conversation_id)})
        return result.deleted_count > 0
    
    def get_active_conversation_by_candidate(self, candidate_id: str) -> Optional[ConversationModel]:
     
        doc = self.collection.find_one({
            "candidate_id": candidate_id,
            "interview_completed": False
        })
        if doc:
            return ConversationModel(**doc)
        return None