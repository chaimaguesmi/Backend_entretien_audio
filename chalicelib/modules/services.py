from datetime import datetime
from typing import Optional, List
from bson import ObjectId
from pydantic import BaseModel
from pymongoose import methods
from chalicelib.modules.models import ConversationModel, ConversationMessage
from chalicelib.utils.filters import build_message_filters
from chalicelib.modules.schemas import init_db


class ConversationService:
    def __init__(self):
        init_db()

    def create_audio_message(
        self,
        conversation_id: Optional[str],
        audio_message_data: dict
    ) -> Optional[ConversationModel]:
        now = datetime.utcnow()
        
        message_doc = {
            "_id": ObjectId(),
            "sender": audio_message_data["sender"],
            "content": audio_message_data.get("content"),
            "audio_url": audio_message_data.get("audio_url"),
            "file_name": audio_message_data.get("file_name"),
            "file_size": audio_message_data.get("file_size"),
            "duration": audio_message_data.get("duration"),
            "format": audio_message_data.get("format"),
            "timestamp": now
        }
        
        try:
            if conversation_id and ObjectId.is_valid(conversation_id):
                results = methods.find(
                    "ConversationModel",
                    {"_id": ObjectId(conversation_id)}
                )
                existing = next(results, None)
                if not existing:
                    return None
                
                update_result = methods.update(
                    "ConversationModel",
                    {"_id": ObjectId(conversation_id)},
                    {
                        "$push": {"messages": message_doc},
                        "$set": {"updated_at": now}
                    }
                )
                
                if update_result > 0:
                    return self.get_conversation_by_id(conversation_id)
                else:
                    return None
            else:
                conversation_doc = {
                    "_id": ObjectId(),
                    "candidate_id": audio_message_data["candidate_id"],
                    "job_title": audio_message_data["job_title"],
                    "company_name": audio_message_data["company_name"],
                    "interview_phase": "welcome",
                    "messages": [message_doc],
                    "created_at": now,
                    "updated_at": now
                }
                
                inserted_id = methods.insert_one("ConversationModel", conversation_doc)
                
                if inserted_id:
                    return self.get_conversation_by_id(str(inserted_id))
                else:
                    return None
                    
        except Exception as e:
            import traceback
            traceback.print_exc()
            return None

    def get_conversation_by_id(self, conversation_id: str) -> Optional[ConversationModel]:
        if not ObjectId.is_valid(conversation_id):
            return None
    
        try:
            results = methods.find(
                "ConversationModel",
                {"_id": ObjectId(conversation_id)}
            )
            doc = next(results, None)
        
            if doc:
                # Convertir les ObjectId en string pour Pydantic
                if "_id" in doc:
                    doc["_id"] = str(doc["_id"])
                
                if "messages" in doc:
                    for message in doc["messages"]:
                        if "_id" in message and isinstance(message["_id"], ObjectId):
                            message["_id"] = str(message["_id"])
                
                return ConversationModel(**doc)
            else:
                return None
        except Exception as e:
            import traceback
            traceback.print_exc()
            return None

    def get_audio_messages(
        self,
        candidate_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        sender: Optional[str] = None
    ) -> List[ConversationMessage]:
        filters = build_message_filters(candidate_id, conversation_id, sender)
        docs = methods.find("ConversationModel", filters)
        messages = []
        
        for doc in docs:
            for msg in doc.get("messages", []):
                if msg.get("timestamp") is None:
                    msg["timestamp"] = datetime.utcnow()
            conv = ConversationModel(**doc)
            for msg in conv.messages:
                if sender and msg.sender != sender:
                    continue
                messages.append(msg)
        
        return messages

    def delete_audio_message(self, conversation_id: str, message_id: str) -> bool:
        if not ObjectId.is_valid(conversation_id) or not ObjectId.is_valid(message_id):
            return False
        
        result = methods.update(
            "ConversationModel",
            {"_id": ObjectId(conversation_id)},
            {"$pull": {"messages": {"_id": ObjectId(message_id)}}}
        )
        
        return result > 0
    def delete_audio_message(self, message_id: str) -> bool:
       """Supprime un message audio directement par son ID"""
       if not ObjectId.is_valid(message_id):
           print(f"Invalid message ID: {message_id}")
           return False
     
       try:
           # Ajout de logs pour le débogage
           print(f"Searching for message with ID: {message_id}")
        
        # Trouver la conversation contenant le message
           results = methods.find(
            "ConversationModel",  # Note: Vérifiez que le nom de la collection est correct
            {"messages._id": ObjectId(message_id)},
            {"messages.$": 1}  # Ne récupérer que le message concerné
        )
           conversation = next(results, None)
        
           if not conversation:
               print(f"No conversation found containing message {message_id}")
               return False
            
           print(f"Found conversation: {conversation['_id']}")
        
        # Supprimer le message de la conversation
           result = methods.update(
            "ConversationModel",
            {"_id": conversation["_id"]},
            {
                "$pull": {"messages": {"_id": ObjectId(message_id)}},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
           print(f"Delete operation result: {result}")
           return result > 0
        
       except Exception as e:
           print(f"Error deleting message {message_id}: {str(e)}")
           import traceback
           traceback.print_exc()
           return False
    def to_json_safe_dict(self, model_or_list) -> dict:
        """
        Convertit un modèle Pydantic ou liste en dict JSON-safe,
        en transformant ObjectId en str et datetime en ISO string.
        """
        def convert_value(val):
            from bson import ObjectId
            if isinstance(val, ObjectId):
                return str(val)
            elif isinstance(val, datetime):
                return val.isoformat()
            elif isinstance(val, list):
                return [convert_value(i) for i in val]
            elif isinstance(val, dict):
                return {k: convert_value(v) for k, v in val.items()}
            elif hasattr(val, 'dict'):  # Modèle Pydantic
                return convert_value(val.dict(by_alias=True))
            else:
                return val

        if isinstance(model_or_list, list):
            return [convert_value(item) for item in model_or_list]
        else:
            return convert_value(model_or_list)
