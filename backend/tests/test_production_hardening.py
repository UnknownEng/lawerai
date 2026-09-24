"""
Tests for Production Hardening, Beta Gates, Storage Service, and Feedback Mechanisms
"""

import pytest
import os
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.config import settings
from backend.storage_service import storage_service
from backend.encryption import derive_strong_fernet_key, encrypt_sensitive_text, decrypt_sensitive_text


def test_production_secrets_validation_fails_on_insecure_defaults():
    # Simulate production environment with default keys
    prev_env = settings.ENVIRONMENT
    prev_jwt = settings.JWT_SECRET_KEY
    prev_enc = settings.CASE_DATA_ENCRYPTION_KEY

    try:
        settings.ENVIRONMENT = "production"
        settings.JWT_SECRET_KEY = "replace-this-with-a-random-secure-secret-key-in-production"
        with pytest.raises(RuntimeError, match="Insecure default or placeholder JWT_SECRET_KEY detected|JWT_SECRET_KEY is empty or using an insecure test value"):
            settings.validate_production_secrets()

        # Fix JWT but leave encryption key default
        settings.JWT_SECRET_KEY = "valid-production-jwt-key-with-sufficient-entropy-12345"
        settings.CASE_DATA_ENCRYPTION_KEY = "replace-this-with-a-32-byte-base64-or-passphrase-key"
        with pytest.raises(RuntimeError, match="Insecure default or placeholder CASE_DATA_ENCRYPTION_KEY detected|CASE_DATA_ENCRYPTION_KEY is empty or using an insecure test value"):
            settings.validate_production_secrets()
    finally:
        settings.ENVIRONMENT = prev_env
        settings.JWT_SECRET_KEY = prev_jwt
        settings.CASE_DATA_ENCRYPTION_KEY = prev_enc


def test_strong_fernet_key_derivation_and_roundtrip():
    # PBKDF2 key derivation from passphrase
    passphrase = "my-secure-production-passphrase-12345678"
    key1 = derive_strong_fernet_key(passphrase)
    key2 = derive_strong_fernet_key(passphrase)
    assert key1 == key2
    assert len(key1) == 44  # Base64-encoded 32-byte key

    # Encrypt and decrypt roundtrip
    secret_text = "Confidential FIR details for advocate review"
    encrypted = encrypt_sensitive_text(secret_text)
    assert encrypted.startswith("enc::")
    decrypted = decrypt_sensitive_text(encrypted)
    assert decrypted == secret_text


def test_storage_service_save_and_retrieve_local():
    test_content = b"Affidavit of Evidence for Case Intake #101"
    filename = "affidavit_test.txt"
    key, path = storage_service.save_file(test_content, filename, "text/plain")

    assert os.path.exists(path)
    retrieved_bytes = storage_service.get_file_bytes(key)
    assert retrieved_bytes == test_content

    # Clean up test file
    if os.path.exists(path):
        os.remove(path)


@pytest.mark.asyncio
async def test_beta_invite_code_verification():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Invalid code
        res_bad = await client.post("/api/auth/verify-beta-code", json={"code": "WRONG-CODE"})
        assert res_bad.status_code == 403

        # Valid code
        res_good = await client.post("/api/auth/verify-beta-code", json={"code": settings.BETA_ACCESS_CODE})
        assert res_good.status_code == 200
        data = res_good.json()
        assert data["valid"] is True


@pytest.mark.asyncio
async def test_feedback_submission_and_summary():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Submit feedback
        fb_payload = {
            "feedback_type": "citation_wrong",
            "category": "statute_accuracy",
            "comment": "Advocate note: SRA Section 9 should be cited instead of Section 8.",
            "query_excerpt": "Landlord locked me out of the shop...",
            "citations_flagged": [{"act_code": "PRPA 2009", "section_number": "15"}]
        }
        res = await client.post("/api/feedback", json=fb_payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        feedback_id = data["feedback_id"]
        assert feedback_id is not None

        # Fetch feedback summary
        summary_res = await client.get("/api/feedback/summary")
        assert summary_res.status_code == 200
        summary = summary_res.json()
        assert summary["total_feedbacks"] >= 1
        assert "citation_wrong" in summary["by_type"]
