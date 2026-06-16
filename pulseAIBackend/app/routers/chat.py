"""
Router Chat — Assistant conversationnel IA avec RAG et tool-calling.

Endpoints :
  POST /chat/           — Réponse non-streaming
  POST /chat/stream     — Réponse en streaming SSE
  GET  /chat/conversations  — Liste des conversations de l'utilisateur
  GET  /chat/conversations/{id}/messages — Messages d'une conversation
  DELETE /chat/conversations/{id}  — Supprimer une conversation
  POST /chat/{conversation_id}/feedback — Feedback
"""

import logging
import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.schemas.chat import ChatRequest, ChatResponse, FeedbackRequest
from app.schemas.auth import CurrentUser
from app.dependencies import get_current_user
from app.core.rbac import require_any_role
from app.services.rag_service import rag_service
from app.models.domain import Conversation, ChatMessage
from app.database import get_db

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = logging.getLogger(__name__)

# Dépendance d'accès : Autorisé pour tout collaborateur, manager ou RH
chat_access_roles = require_any_role("collaborator", "manager", "hr")


@router.post("/", response_model=ChatResponse, dependencies=[Depends(chat_access_roles)])
async def send_message(
    request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Envoyer un message à l'assistant (non-streaming)."""
    logger.info(
        f"POST /chat/ | user={current_user.email}, "
        f"conversation_id={request.conversation_id}, msg_len={len(request.message)}"
    )

    # 1. Gérer la conversation (créer ou reprendre)
    conversation_id = request.conversation_id
    if conversation_id:
        conv_result = await db.execute(
            select(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id,
            )
        )
        conversation = conv_result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation introuvable")
    else:
        conversation = Conversation(
            user_id=current_user.id,
            title=request.message[:80],
        )
        db.add(conversation)
        await db.flush()
        conversation_id = conversation.id

    # 2. Sauvegarder le message utilisateur
    user_msg = ChatMessage(
        conversation_id=conversation_id,
        role="user",
        content=request.message,
    )
    db.add(user_msg)

    # 3. Charger l'historique de conversation
    history_result = await db.execute(
        select(ChatMessage)
        .filter(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at)
    )
    history_msgs = history_result.scalars().all()
    conversation_history = [
        {"role": m.role, "content": m.content}
        for m in history_msgs
        if m.role in ("user", "assistant") and m.content
    ]
    # Exclure le dernier message (c'est celui qu'on vient d'ajouter)
    if conversation_history:
        conversation_history = conversation_history[:-1]

    # 4. Appeler le RAG
    rag_result = await rag_service.answer(
        question=request.message,
        user_role=current_user.roles,
        user_id=current_user.id,
        conversation_id=conversation_id,
        conversation_history=conversation_history[-10:],  # Garder les 10 derniers échanges
        db=db,
    )

    # 5. Sauvegarder la réponse assistant
    assistant_msg = ChatMessage(
        conversation_id=conversation_id,
        role="assistant",
        content=rag_result.get("answer", ""),
        sources=rag_result.get("sources"),
        tool_calls=rag_result.get("tool_results"),
        tokens_used=rag_result.get("tokens_used", 0),
    )
    db.add(assistant_msg)
    await db.commit()

    # 6. Logger pour audit
    logger.info(
        f"WAZUH_SEC_LOG: Chat interaction | user={current_user.email}, "
        f"conversation_id={conversation_id}, tokens={rag_result.get('tokens_used', 0)}"
    )

    return ChatResponse(
        answer=rag_result.get("answer", ""),
        conversation_id=conversation_id,
        sources=rag_result.get("sources", []),
        tokens_used=rag_result.get("tokens_used", 0),
        tool_results=rag_result.get("tool_results", []),
        confidence=rag_result.get("confidence", 0.0),
        warning=rag_result.get("warning"),
    )


@router.post("/stream", dependencies=[Depends(chat_access_roles)])
async def stream_message(
    request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Envoyer un message et recevoir la réponse en streaming SSE."""
    logger.info(f"POST /chat/stream | user={current_user.email}")

    # Gérer la conversation
    conversation_id = request.conversation_id
    if conversation_id:
        conv_result = await db.execute(
            select(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id,
            )
        )
        conversation = conv_result.scalar_one_or_none()
        if not conversation:
            conversation_id = None

    if not conversation_id:
        conversation = Conversation(
            user_id=current_user.id,
            title=request.message[:80],
        )
        db.add(conversation)
        await db.flush()
        conversation_id = conversation.id

    # Sauvegarder le message utilisateur
    user_msg = ChatMessage(
        conversation_id=conversation_id,
        role="user",
        content=request.message,
    )
    db.add(user_msg)
    await db.flush()

    # Historique
    history_result = await db.execute(
        select(ChatMessage)
        .filter(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at)
    )
    history_msgs = history_result.scalars().all()
    conversation_history = [
        {"role": m.role, "content": m.content}
        for m in history_msgs
        if m.role in ("user", "assistant") and m.content
    ]
    if conversation_history:
        conversation_history = conversation_history[:-1]

    async def event_generator():
        full_answer = ""
        sources = []
        tool_results = []
        tokens_used = 0

        # Envoyer le conversation_id immédiatement
        yield f"data: {json.dumps({'type': 'conversation_id', 'content': conversation_id})}\n\n"

        try:
            async for chunk in rag_service.stream_answer(
                question=request.message,
                user_role=current_user.roles,
                user_id=current_user.id,
                conversation_history=conversation_history[-10:],
                db=db,
            ):
                chunk_type = chunk.get("type", "text")

                if chunk_type == "text":
                    full_answer += chunk["content"]
                elif chunk_type == "source":
                    sources.append(chunk["content"])
                elif chunk_type == "tool_call":
                    tool_results.append(chunk["content"])
                elif chunk_type == "done":
                    tokens_used = chunk["content"].get("tokens_used", 0)
                    if chunk["content"].get("sources"):
                        sources = chunk["content"]["sources"]

                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

        except Exception as e:
            logger.error(f"Erreur dans le streaming SSE : {e}")
            yield f"data: {json.dumps({'type': 'text', 'content': 'Erreur technique. Veuillez réessayer.'})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'content': {'tokens_used': 0}})}\n\n"

        # Sauvegarder la réponse complète en DB
        try:
            assistant_msg = ChatMessage(
                conversation_id=conversation_id,
                role="assistant",
                content=full_answer,
                sources=sources if sources else None,
                tool_calls=tool_results if tool_results else None,
                tokens_used=tokens_used,
            )
            db.add(assistant_msg)
            await db.commit()
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du message streaming : {e}")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/conversations", dependencies=[Depends(chat_access_roles)])
async def list_conversations(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Récupérer la liste des conversations de l'utilisateur."""
    logger.info(f"GET /chat/conversations | user={current_user.email}")

    result = await db.execute(
        select(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = result.scalars().all()

    summaries = []
    for conv in conversations:
        # Compter les messages
        count_result = await db.execute(
            select(func.count(ChatMessage.id)).filter(
                ChatMessage.conversation_id == conv.id
            )
        )
        msg_count = count_result.scalar() or 0

        summaries.append({
            "id": conv.id,
            "title": conv.title,
            "created_at": conv.created_at.isoformat() if conv.created_at else None,
            "updated_at": conv.updated_at.isoformat() if conv.updated_at else None,
            "message_count": msg_count,
        })

    return summaries


@router.get("/conversations/{conversation_id}/messages", dependencies=[Depends(chat_access_roles)])
async def get_conversation_messages(
    conversation_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Récupérer les messages d'une conversation."""
    logger.info(f"GET /chat/conversations/{conversation_id}/messages | user={current_user.email}")

    # Vérifier que la conversation appartient à l'utilisateur
    conv_result = await db.execute(
        select(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    if not conv_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Conversation introuvable")

    result = await db.execute(
        select(ChatMessage)
        .filter(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()

    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "sources": m.sources,
            "tool_calls": m.tool_calls,
            "tokens_used": m.tokens_used,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in messages
    ]


@router.delete("/conversations/{conversation_id}", dependencies=[Depends(chat_access_roles)])
async def delete_conversation(
    conversation_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Supprimer une conversation."""
    logger.info(f"DELETE /chat/conversations/{conversation_id} | user={current_user.email}")

    conv_result = await db.execute(
        select(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    conversation = conv_result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation introuvable")

    await db.delete(conversation)
    await db.commit()
    return {"message": "Conversation supprimée"}


@router.post("/{conversation_id}/feedback", dependencies=[Depends(chat_access_roles)])
async def submit_feedback(
    conversation_id: str,
    feedback: FeedbackRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Soumettre un feedback utile/inutile."""
    logger.info(f"Feedback received for conversation {conversation_id}: {feedback.rating}")
    return {"status": "Feedback recorded", "conversation_id": conversation_id}
from pydantic import BaseModel

class ConversationTitleUpdate(BaseModel):
    title: str

@router.put("/conversations/{id}/title")
async def update_conversation_title(
    id: str,
    payload: ConversationTitleUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv_result = await db.execute(
        select(Conversation).filter(
            Conversation.id == id,
            Conversation.user_id == current_user.id,
        )
    )
    conversation = conv_result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation introuvable")

    conversation.title = payload.title
    await db.commit()
    return {"status": "success", "title": conversation.title}
