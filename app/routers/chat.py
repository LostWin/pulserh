import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse, FeedbackRequest
from app.schemas.auth import CurrentUser
from app.dependencies import get_current_user
from app.core.rbac import require_any_role
from app.services import rag_service

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = logging.getLogger(__name__)

# Dépendance d'accès : Autorisé pour tout collaborateur, manager ou RH
chat_access_roles = require_any_role("collaborator", "manager", "hr")

@router.post("/", response_model=ChatResponse, dependencies=[Depends(chat_access_roles)])
def send_message(request: ChatRequest, current_user: CurrentUser = Depends(get_current_user)):
    """Envoyer un message à l'assistant"""
    # 1. La validation Pydantic est déjà effectuée via `request: ChatRequest`

    # 2. Stub: Appliquer le rate limiting (30 req/min via Redis)
    # redis_client.check_rate_limit(key=f"rate_limit:chat:{current_user.id}", limit=30, window=60)
    
    # 3. Stub: Appeler le service RAG
    rag_result = rag_service.answer(
        question=request.message, 
        user_role=current_user.roles, 
        user_id=current_user.id
    )
    
    # 4. Logger l'interaction anonymisée dans PostgreSQL (Stub)
    conversation_id = request.conversation_id or str(uuid.uuid4())
    # db_service.log_interaction_anonymously(conversation_id, anonymized_text)
    
    # 5. Envoyer le log à Wazuh (Stub)
    logger.info(f"WAZUH_SEC_LOG: User interacted with Assistant. Conversation ID: {conversation_id}")
    
    # 6. Retourner la réponse
    return ChatResponse(
        answer=rag_result.get("answer", ""),
        conversation_id=conversation_id,
        sources=rag_result.get("sources", [])
    )

@router.get("/history", dependencies=[Depends(chat_access_roles)])
def get_chat_history(current_user: CurrentUser = Depends(get_current_user)):
    """Récupérer l'historique de ses conversations"""
    return {"status": "Not Implemented", "history": []}

@router.post("/{conversation_id}/feedback", dependencies=[Depends(chat_access_roles)])
def submit_feedback(conversation_id: str, feedback: FeedbackRequest, current_user: CurrentUser = Depends(get_current_user)):
    """Soumettre un feedback utile/inutile"""
    # Stub: Sauvegarde du feedback en DB pour améliorer le modèle
    logger.info(f"Feedback received for conversation {conversation_id}: {feedback.rating}")
    return {"status": "Feedback recorded", "conversation_id": conversation_id}