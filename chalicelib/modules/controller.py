from datetime import datetime
from bson import ObjectId
from chalice import Blueprint, Response, BadRequestError, NotFoundError
from chalicelib.modules.services import ConversationService

api = Blueprint(__name__)
service = ConversationService()

@api.route("/audio-messages", methods=["POST"])
def create_audio_message():
    request = api.current_request
    body = request.json_body

    required_fields = [
        "candidate_id", "job_title", "company_name",
        "sender", "file_name", "file_size", "format"
    ]
    for field in required_fields:
        if field not in body:
            raise BadRequestError(f"Missing required field: {field}")

    conversation_id = body.get("conversation_id")

    audio_message_data = {
        "sender": body["sender"],
        "content": body.get("content"),
        "audio_url": body.get("audio_url"),
        "file_name": body["file_name"],
        "file_size": body["file_size"],
        "duration": body.get("duration"),
        "format": body["format"],
        "timestamp": datetime.utcnow(),
        "candidate_id": body["candidate_id"],
        "job_title": body["job_title"],
        "company_name": body["company_name"],
    }

    conversation = service.create_audio_message(conversation_id, audio_message_data)
    if not conversation:
        raise BadRequestError("Could not create or update conversation")

    response_body = service.to_json_safe_dict(conversation)

    return Response(
        body={"conversation": response_body, "message": "Audio message added"},
        status_code=201,
        headers={"Content-Type": "application/json"},
    )

@api.route("/audio-messages", methods=["GET"])
def get_audio_messages():
    request = api.current_request
    params = request.query_params or {}

    candidate_id = params.get("candidate_id")
    conversation_id = params.get("conversation_id")
    sender = params.get("sender")

    messages = service.get_audio_messages(candidate_id, conversation_id, sender)
    messages_data = service.to_json_safe_dict(messages)

    return {"count": len(messages_data), "messages": messages_data}

@api.route("/audio-messages/{message_id}", methods=["DELETE"])
def delete_audio_message(message_id: str):
    # Validation de l'ID
    if not ObjectId.is_valid(message_id):
        raise BadRequestError("Invalid message ID format")
    
    success = service.delete_audio_message(message_id)
    if not success:
        raise NotFoundError(f"Audio message with ID {message_id} not found or could not be deleted")
    return {"message": "Audio message deleted successfully", "message_id": message_id}