from datetime import datetime
from typing import Optional,List
from pydantic import BaseModel, Field
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, values=None, **kwargs): 
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema):
        return {
            'type': 'string',
            'title': 'ObjectId',
        }

class AudioResponseModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    candidate_id: str = Field(..., description="ID du candidat")
    question_id: str = Field(..., description="ID de la question")
    file_path: str = Field(..., description="Chemin du fichier audio")
    file_name: str = Field(..., description="Nom du fichier")
    file_size: int = Field(..., description="Taille du fichier en bytes")
    duration: Optional[float] = Field(None, description="Durée en secondes")
    format: str = Field(..., description="Format du fichier audio (mp3, wav, etc.)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True  
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        
class AudioResponseCreate(BaseModel):
    candidate_id: str
    question_id: str
    file_name: str
    file_size: int
    duration: Optional[float] = None
    format: str

class AudioResponseUpdate(BaseModel):
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    duration: Optional[float] = None
    format: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AudioResponseResponse(BaseModel):
    id: str
    candidate_id: str
    question_id: str
    file_path: str
    file_name: str
    file_size: int
    duration: Optional[float]
    format: str
    created_at: datetime
    updated_at: datetime
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }
class ConversationMessage(BaseModel):
    sender: str = Field(..., description="'bot' ou 'user'")
    content: str = Field(..., description="Contenu du message")
    audio_url: Optional[str] = Field(None, description="URL de l'audio si applicable")
    is_question: Optional[bool] = Field(False, description="Si c'est une question")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    is_playing: Optional[bool] = Field(False, description="État de lecture audio")
    progress: Optional[float] = Field(0, description="Progression de lecture")
    current_time: Optional[float] = Field(0, description="Temps actuel")
    duration: Optional[float] = Field(0, description="Durée totale")
    duration_loaded: Optional[bool] = Field(False, description="Durée chargée")

class ConversationModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    candidate_id: str = Field(..., description="ID du candidat")
    job_title: str = Field(..., description="Titre du poste")
    company_name: str = Field(..., description="Nom de l'entreprise")
    interview_phase: str = Field(..., description="Phase de l'entretien")
    current_category_index: int = Field(0, description="Index de la catégorie actuelle")
    current_question_in_category: int = Field(0, description="Question actuelle dans la catégorie")
    messages: List[ConversationMessage] = Field(default_factory=list, description="Messages de la conversation")
    question_categories: List[dict] = Field(default_factory=list, description="Catégories de questions")
    interview_started: bool = Field(False, description="Entretien commencé")
    interview_completed: bool = Field(False, description="Entretien terminé")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ConversationCreate(BaseModel):
    candidate_id: str
    job_title: str
    company_name: str
    interview_phase: str = "welcome"
    question_categories: List[dict] = []

class ConversationUpdate(BaseModel):
    interview_phase: Optional[str] = None
    current_category_index: Optional[int] = None
    current_question_in_category: Optional[int] = None
    messages: Optional[List[ConversationMessage]] = None
    question_categories: Optional[List[dict]] = None
    interview_started: Optional[bool] = None
    interview_completed: Optional[bool] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ConversationResponse(BaseModel):
    id: str
    candidate_id: str
    job_title: str
    company_name: str
    interview_phase: str
    current_category_index: int
    current_question_in_category: int
    messages: List[ConversationMessage]
    question_categories: List[dict]
    interview_started: bool
    interview_completed: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }