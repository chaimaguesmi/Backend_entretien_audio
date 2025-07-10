# chalicelib/modules/constants.py

# --- Messages d'erreurs ---
ERR_MISSING_FIELD = "Champ requis manquant: {field}"
ERR_DECODE_AUDIO = "Erreur lors du décodage du fichier: {error}"
ERR_AUDIO_NOT_FOUND = "Réponse audio non trouvée"
ERR_AUDIO_NOT_FOUND_QUESTION = "Réponse audio non trouvée pour cette question"
ERR_AUDIO_DOWNLOAD_S3 = "Téléchargement depuis S3 non implémenté"
ERR_AUDIO_FILE_MISSING = "Fichier audio non trouvé"
ERR_AUDIO_CREATE = "Erreur lors de la création de la réponse audio: {error}"
ERR_AUDIO_RETRIEVE = "Erreur lors de la récupération: {error}"
ERR_AUDIO_DELETE = "Erreur lors de la suppression: {error}"
ERR_AUDIO_DOWNLOAD = "Erreur lors du téléchargement: {error}"

ERR_CONVERSATION_NOT_FOUND = "Conversation non trouvée"
ERR_CONVERSATION_CREATE = "Erreur lors de la création de la conversation: {error}"
ERR_CONVERSATION_UPDATE = "Erreur lors de la mise à jour: {error}"
ERR_CONVERSATION_RETRIEVE = "Erreur lors de la récupération: {error}"
ERR_CONVERSATION_DELETE = "Erreur lors de la suppression: {error}"
ERR_CONVERSATION_ACTIVE_NOT_FOUND = "Aucune conversation active trouvée"
ERR_CONVERSATION_ADD_MESSAGE = "Erreur lors de l'ajout du message: {error}"

# --- Messages de succès ---
MSG_AUDIO_DELETED = "Réponse audio supprimée avec succès"
MSG_CONVERSATION_DELETED = "Conversation supprimée avec succès"
MSG_MESSAGE_ADDED = "Message ajouté avec succès"

# --- Divers ---
HEALTH_OK = {
    "status": "healthy",
    "service": "careere-audio-responses",
    "version": "1.0.0"
}
