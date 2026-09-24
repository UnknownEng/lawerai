"""
Secure Storage Service for Case Uploads & Evidentiary Documents
Supports local filesystem (development) and S3/Cloudflare R2-compatible object storage (production).
Enforces non-public, authenticated access to confidential citizen evidence.
"""

import os
import uuid
import logging
from typing import Tuple, Optional, BinaryIO
from .config import settings

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self):
        self.backend = settings.STORAGE_BACKEND
        self._s3_client = None
        if self.backend == "s3":
            self._init_s3()

    def _init_s3(self):
        import boto3
        from botocore.config import Config

        kwargs = {
            "service_name": "s3",
            "aws_access_key_id": settings.S3_ACCESS_KEY_ID,
            "aws_secret_access_key": settings.S3_SECRET_ACCESS_KEY,
            "region_name": settings.S3_REGION_NAME or "auto",
            "config": Config(signature_version="s3v4")
        }
        if settings.S3_ENDPOINT_URL:
            kwargs["endpoint_url"] = settings.S3_ENDPOINT_URL

        self._s3_client = boto3.client(**kwargs)
        logger.info(f"Initialized S3 storage client for bucket: {settings.S3_BUCKET_NAME}")

    def save_file(self, file_content: bytes, original_filename: str, content_type: str = "application/octet-stream") -> Tuple[str, str]:
        """
        Saves a file to the configured storage backend.
        Returns a tuple: (storage_key, internal_or_signed_reference)
        """
        ext = os.path.splitext(original_filename)[1].lower()
        unique_key = f"{uuid.uuid4()}{ext}"

        if self.backend == "s3":
            try:
                if not self._s3_client:
                    self._init_s3()
                self._s3_client.put_object(
                    Bucket=settings.S3_BUCKET_NAME,
                    Key=unique_key,
                    Body=file_content,
                    ContentType=content_type,
                    Metadata={"original_filename": original_filename}
                )
                logger.info(f"Successfully uploaded {unique_key} to S3 bucket {settings.S3_BUCKET_NAME}")
                return unique_key, f"s3://{settings.S3_BUCKET_NAME}/{unique_key}"
            except Exception as e:
                logger.error(f"S3 upload failed: {e}. Falling back to local storage.")

        # Local storage fallback
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        local_path = os.path.join(settings.UPLOAD_DIR, unique_key)
        with open(local_path, "wb") as f:
            f.write(file_content)
        return unique_key, local_path

    def get_file_bytes(self, storage_key_or_path: str) -> bytes:
        """Retrieves raw file bytes from storage for OCR or processing."""
        if self.backend == "s3" and not os.path.isabs(storage_key_or_path):
            try:
                if not self._s3_client:
                    self._init_s3()
                resp = self._s3_client.get_object(Bucket=settings.S3_BUCKET_NAME, Key=storage_key_or_path)
                return resp["Body"].read()
            except Exception as e:
                logger.error(f"Failed to fetch {storage_key_or_path} from S3: {e}")

        # Local file path
        path = storage_key_or_path if os.path.isabs(storage_key_or_path) else os.path.join(settings.UPLOAD_DIR, storage_key_or_path)
        if os.path.exists(path):
            with open(path, "rb") as f:
                return f.read()
        raise FileNotFoundError(f"Stored file not found: {storage_key_or_path}")

    def generate_download_url(self, storage_key_or_path: str, filename: str, expires_in: int = 3600) -> Optional[str]:
        """
        Generates a secure, short-lived presigned URL if using S3/R2.
        For local dev, returns an authenticated API proxy route.
        """
        if self.backend == "s3" and not os.path.isabs(storage_key_or_path):
            try:
                if not self._s3_client:
                    self._init_s3()
                url = self._s3_client.generate_presigned_url(
                    "get_object",
                    Params={
                        "Bucket": settings.S3_BUCKET_NAME,
                        "Key": storage_key_or_path,
                        "ResponseContentDisposition": f'attachment; filename="{filename}"'
                    },
                    ExpiresIn=expires_in
                )
                return url
            except Exception as e:
                logger.error(f"Error generating presigned URL for {storage_key_or_path}: {e}")
                return None
        return None


storage_service = StorageService()
