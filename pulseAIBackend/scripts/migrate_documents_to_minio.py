import asyncio
from pathlib import Path

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.domain import Document
from app.services.secure_document_storage import secure_document_storage


def resolve_bucket_kind(document: Document) -> str:
    if document.uploaded_by:
        return "uploaded"
    return "generated"


async def migrate_documents() -> None:
    async with AsyncSessionLocal() as db:
        documents = (
            await db.execute(
                select(Document).order_by(Document.created_at.asc())
            )
        ).scalars().all()

        migrated = 0
        skipped = 0

        for document in documents:
            if secure_document_storage.is_minio_uri(document.file_path):
                skipped += 1
                continue

            source_path = Path(document.file_path)
            if not source_path.exists():
                print(f"SKIP missing file: {document.id} -> {document.file_path}")
                skipped += 1
                continue

            payload = source_path.read_bytes()
            bucket_kind = resolve_bucket_kind(document)
            storage_uri = secure_document_storage.upload_bytes(payload, document.name, bucket_kind)
            document.file_path = storage_uri
            migrated += 1
            print(f"MIGRATED {document.id} -> {storage_uri}")

        await db.commit()
        print(f"Done. migrated={migrated} skipped={skipped}")


if __name__ == "__main__":
    asyncio.run(migrate_documents())
