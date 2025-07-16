import os
from pymongo import MongoClient
from pymongoose.mongo_types import Types, Schema
from pymongoose import methods

def init_db():
    mongo_uri = os.getenv('MONGODB_URI', 'mongodb://portago-UAT:Idzh4PLGpZ2vOO8KRY0E@mongo.allence.cloud/portago-UAT')
    database_name = os.getenv('DATABASE_NAME', 'portago-UAT')
    
    try:
        client = MongoClient(mongo_uri)
        database = client[database_name]
        methods.database = database
        
        print(f"Connected to MongoDB at {mongo_uri}")
        print(f"Using database: {database_name}")
        
        return database
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise e

class ConversationMessageSchema(Schema):
    schema_name = "ConversationMessageModel"
    
    def __init__(self, **kwargs):
        self.schema = {
            "sender": {"type": Types.String, "required": True},
            "content": {"type": Types.String, "required": False},
            "audio_url": {"type": Types.String, "required": False},
            "file_name": {"type": Types.String, "required": False},
            "file_size": {"type": Types.Number, "required": False},
            "duration": {"type": Types.Number, "required": False},
            "format": {"type": Types.String, "required": False},
            "timestamp": {"type": Types.Date, "default": "datetime.utcnow"},
        }
        super().__init__(self.schema_name, self.schema, kwargs)

class ConversationSchema(Schema):
    schema_name = "ConversationModel"
    
    def __init__(self, **kwargs):
        self.schema = {
            "candidate_id": {"type": Types.String, "required": True},
            "job_title": {"type": Types.String, "required": True},
            "company_name": {"type": Types.String, "required": True},
            "interview_phase": {"type": Types.String, "default": "welcome"},
            "messages": {"type": [ConversationMessageSchema().schema], "required": False},
            "created_at": {"type": Types.Date, "default": "datetime.utcnow"},
            "updated_at": {"type": Types.Date, "default": "datetime.utcnow"}
        }
        super().__init__(self.schema_name, self.schema, kwargs)

methods.schemas = {
    "ConversationModel": ConversationSchema(),
    "ConversationMessageModel": ConversationMessageSchema()
}
init_db()