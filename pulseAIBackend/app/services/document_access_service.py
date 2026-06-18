import asyncio
import mimetypes
import re
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Document, DocumentAccessEvent
from app.services.embedding_service import embedding_service
from app.services.rag_service import rag_service
from app.services.secure_document_storage import secure_document_storage


ALL_DOCUMENT_ROLES = ["collaborator", "manager", "hr", "director", "admin"]
_rag_init_lock = asyncio.Lock()


def normalize_roles(roles: Iterable[str]) -> list[str]:
    normalized = []
    for role in roles:
        lowered = (role or "").lower()
        if lowered and lowered not in normalized:
            normalized.append(lowered)
    return normalized


def user_can_access_document(document: Document, user_roles: Iterable[str], user_id: str | None = None) -> bool:
    normalized_roles = normalize_roles(user_roles)
    if "hr" in normalized_roles or "admin" in normalized_roles:
        return True
    
    if document.employee_id and user_id and document.employee_id != user_id:
        return False
        
    allowed_roles = normalize_roles(document.allowed_roles or [])
    return any(role in allowed_roles for role in normalized_roles)


async def log_document_event(
    db: AsyncSession,
    document: Document,
    user_email: str,
    user_roles: Iterable[str],
    action: str,
    details: dict | None = None,
) -> DocumentAccessEvent:
    event = DocumentAccessEvent(
        document_id=document.id,
        user_email=user_email,
        action=action,
        roles=normalize_roles(user_roles),
        details=details or {},
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


def document_can_preview(document: Document) -> bool:
    return Path(document.name).suffix.lower() == ".pdf"


def guess_media_type(document: Document) -> str:
    media_type, _ = mimetypes.guess_type(document.name)
    return media_type or "application/octet-stream"


def read_document_bytes(document: Document) -> bytes:
    return secure_document_storage.download_bytes(document.file_path)


def extract_text_from_document(file_path: str) -> str:
    suffix = Path(file_path).suffix.lower()
    if suffix == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()

    if suffix == ".docx":
        from docx import Document as DocxDocument
        doc = DocxDocument(file_path)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs if paragraph.text).strip()

    if suffix in {".odt", ".ott"}:
        from odf import teletype
        from odf.opendocument import load
        odt_doc = load(file_path)
        return teletype.extractText(odt_doc.text).strip()

    if suffix == ".rtf":
        raw = Path(file_path).read_text(encoding="utf-8", errors="ignore")
        text = re.sub(r"\\'[0-9a-fA-F]{2}", "", raw)
        text = re.sub(r"\\[a-zA-Z]+\d* ?", "", text)
        text = text.replace("{", "").replace("}", "")
        return re.sub(r"\s+", " ", text).strip()

    raise ValueError("Format non supporté pour l'ingestion RAG.")


def split_text_into_chunks(text: str, chunk_size: int = 900, overlap: int = 120) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return []

    chunks = []
    start = 0
    text_length = len(normalized)
    while start < text_length:
        end = min(text_length, start + chunk_size)
        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= text_length:
            break
        start = max(end - overlap, start + 1)
    return chunks


async def sync_document_to_rag(document: Document) -> None:
    async with _rag_init_lock:
        if not embedding_service.model and not embedding_service._openai_client:
            await embedding_service.initialize()
        if not rag_service.qdrant_client:
            await rag_service.initialize()

    if not rag_service.qdrant_client:
        raise RuntimeError("Qdrant n'est pas initialisé.")

    document_bytes = read_document_bytes(document)
    suffix = Path(document.name).suffix.lower() or ".bin"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as temp_file:
        temp_file.write(document_bytes)
        temp_file.flush()
        text = extract_text_from_document(temp_file.name)
    if not text:
        raise ValueError("Le document ne contient pas de texte exploitable.")

    chunks = split_text_into_chunks(text)
    if not chunks:
        raise ValueError("Aucun contenu textuel exploitable après découpage.")

    from qdrant_client.models import PointStruct

    embeddings = await embedding_service.encode_batch(chunks)
    delete_document_from_rag(document.id)

    points = []
    for index, (chunk, vector) in enumerate(zip(chunks, embeddings)):
        points.append(
            PointStruct(
                id=str(uuid.uuid5(uuid.UUID(document.id), str(index))),
                vector=vector,
                payload={
                    "document_id": document.id,
                    "title": document.name,
                    "source": document.name,
                    "text": chunk,
                    "allowed_roles": normalize_roles(document.allowed_roles or []),
                },
            )
        )

    rag_service.qdrant_client.upsert(
        collection_name=rag_service.collection_name,
        points=points,
    )


def delete_document_from_rag(document_id: str) -> None:
    if not rag_service.qdrant_client:
        return

    from qdrant_client.models import Filter, FieldCondition, MatchValue

    rag_service.qdrant_client.delete(
        collection_name=rag_service.collection_name,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id),
                )
            ]
        ),
    )


def mark_document_rag_state(document: Document, enabled: bool, status: str, error: str | None = None) -> None:
    document.rag_enabled = enabled
    document.rag_status = status
    document.rag_error = error
    document.rag_last_synced_at = datetime.now(timezone.utc) if status == "ready" else document.rag_last_synced_at
