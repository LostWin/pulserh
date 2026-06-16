import base64
import hashlib
import io
import logging
import os
import uuid
from pathlib import Path

from cryptography.fernet import Fernet

from app.config import settings

logger = logging.getLogger(__name__)


class SecureDocumentStorage:
    def __init__(self):
        self._client = None
        self._ready = False
        self.upload_bucket = settings.MINIO_DOCUMENTS_UPLOAD_BUCKET
        self.generated_bucket = settings.MINIO_DOCUMENTS_GENERATED_BUCKET
        self._fernet = Fernet(self._build_fernet_key())

    def _build_fernet_key(self) -> bytes:
        if settings.DOCUMENTS_ENCRYPTION_KEY:
            key = settings.DOCUMENTS_ENCRYPTION_KEY.encode()
            try:
                Fernet(key)
                return key
            except Exception:
                logger.warning("DOCUMENTS_ENCRYPTION_KEY invalide, fallback sur une clé dérivée.")

        seed = f"{settings.MINIO_SECRET_KEY}:{settings.PROJECT_NAME}:documents".encode()
        digest = hashlib.sha256(seed).digest()
        return base64.urlsafe_b64encode(digest)

    def _sanitize_name(self, filename: str) -> str:
        safe = filename.replace("/", "-").replace("\\", "-").replace(" ", "_")
        return safe or f"document_{uuid.uuid4().hex}"

    def _build_object_key(self, filename: str) -> str:
        suffix = Path(filename).suffix or ".bin"
        stem = Path(filename).stem or "document"
        safe = self._sanitize_name(stem)
        return f"{safe}_{uuid.uuid4().hex}{suffix}.enc"

    def _client_instance(self):
        if self._client is None:
            from minio import Minio

            self._client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE,
            )
        return self._client

    def ensure_ready(self):
        if self._ready:
            return

        client = self._client_instance()
        for bucket_name in (self.upload_bucket, self.generated_bucket):
            if not client.bucket_exists(bucket_name):
                client.make_bucket(bucket_name)
                logger.info("Bucket MinIO créé: %s", bucket_name)
        self._ready = True

    def encrypt_bytes(self, payload: bytes) -> bytes:
        return self._fernet.encrypt(payload)

    def decrypt_bytes(self, payload: bytes) -> bytes:
        return self._fernet.decrypt(payload)

    def upload_bytes(self, payload: bytes, filename: str, bucket_kind: str) -> str:
        self.ensure_ready()
        bucket_name = self.upload_bucket if bucket_kind == "uploaded" else self.generated_bucket
        object_key = self._build_object_key(filename)
        encrypted_payload = self.encrypt_bytes(payload)
        stream = io.BytesIO(encrypted_payload)

        self._client_instance().put_object(
            bucket_name=bucket_name,
            object_name=object_key,
            data=stream,
            length=len(encrypted_payload),
            content_type="application/octet-stream",
            metadata={
                "original-filename": self._sanitize_name(filename),
                "encrypted": "true",
            },
        )
        return f"minio://{bucket_name}/{object_key}"

    def download_bytes(self, document_uri: str) -> bytes:
        if not self.is_minio_uri(document_uri):
            return Path(document_uri).read_bytes()

        self.ensure_ready()
        bucket_name, object_key = self.parse_uri(document_uri)
        response = self._client_instance().get_object(bucket_name, object_key)
        try:
            encrypted_payload = response.read()
        finally:
            response.close()
            response.release_conn()
        return self.decrypt_bytes(encrypted_payload)

    def delete(self, document_uri: str) -> None:
        if not document_uri:
            return

        if not self.is_minio_uri(document_uri):
            if os.path.exists(document_uri):
                os.remove(document_uri)
            return

        self.ensure_ready()
        bucket_name, object_key = self.parse_uri(document_uri)
        self._client_instance().remove_object(bucket_name, object_key)

    def exists(self, document_uri: str) -> bool:
        if not document_uri:
            return False

        if not self.is_minio_uri(document_uri):
            return os.path.exists(document_uri)

        try:
            self.ensure_ready()
            bucket_name, object_key = self.parse_uri(document_uri)
            self._client_instance().stat_object(bucket_name, object_key)
            return True
        except Exception:
            return False

    @staticmethod
    def is_minio_uri(document_uri: str) -> bool:
        return (document_uri or "").startswith("minio://")

    @staticmethod
    def parse_uri(document_uri: str) -> tuple[str, str]:
        raw = document_uri.removeprefix("minio://")
        bucket_name, object_key = raw.split("/", 1)
        return bucket_name, object_key


secure_document_storage = SecureDocumentStorage()
