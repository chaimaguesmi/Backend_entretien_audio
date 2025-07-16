from bson import ObjectId
from typing import Optional

def build_message_filters(
    candidate_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    sender: Optional[str] = None
) -> dict:
    filters = {}

    if candidate_id:
        filters["candidate_id"] = candidate_id

    if conversation_id:
        try:
            filters["_id"] = ObjectId(conversation_id)
        except:
            # Peut-être logger l'erreur ici
            pass

    if sender:
        filters["messages.sender"] = sender  # Syntaxe simplifiée

    return filters