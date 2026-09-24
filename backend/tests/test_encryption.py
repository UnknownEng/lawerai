"""
Unit & Integration Tests for Case Data Encryption at Rest
Validates requirement: "Do not store sensitive case data unencrypted; treat all user case content as confidential."
"""

import asyncio
import sqlite3
import uuid
from backend.encryption import encrypt_sensitive_text, decrypt_sensitive_text, get_cipher
from backend.database import init_db, AsyncSessionLocal, Message, UploadedDocument, EmergencyLog
from backend.config import settings


def test_encryption_roundtrip():
    secret_note = "Confidential: Client CNIC 35201-9988776-1, bank account PK36HABB0001234567890"
    encrypted = encrypt_sensitive_text(secret_note)
    assert encrypted != secret_note
    assert encrypted.startswith("enc::")

    decrypted = decrypt_sensitive_text(encrypted)
    assert decrypted == secret_note


def test_encryption_handles_empty_and_plain():
    assert encrypt_sensitive_text("") == ""
    assert decrypt_sensitive_text("") == ""
    # Plain string without enc:: prefix is passed through safely
    assert decrypt_sensitive_text("Legacy unencrypted message") == "Legacy unencrypted message"


def test_database_persistence_encryption_at_rest():
    """Verify that records in the SQLite / Postgres database are physically encrypted on disk."""
    async def run():
        await init_db()
        test_session_id = f"test-enc-{uuid.uuid4()}"
        confidential_text = "Private FIR allegation regarding stolen asset PKR 1,500,000"

        # 1. Insert via SQLAlchemy
        async with AsyncSessionLocal() as session:
            msg = Message(
                session_id=test_session_id,
                role="user",
                content=confidential_text
            )
            session.add(msg)
            await session.commit()
            msg_id = msg.id

        # 2. Inspect raw bytes in SQLite database directly (bypassing SQLAlchemy)
        db_path = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT content FROM messages WHERE id = ?", (msg_id,))
        raw_row = cur.fetchone()
        assert raw_row is not None
        raw_disk_content = raw_row[0]

        # Assert disk content is encrypted ciphertext starting with enc::
        assert raw_disk_content.startswith("enc::")
        assert confidential_text not in raw_disk_content

        # 3. Read back through SQLAlchemy TypeDecorator
        async with AsyncSessionLocal() as session:
            loaded_msg = await session.get(Message, msg_id)
            assert loaded_msg.content == confidential_text

        # Cleanup
        cur.execute("DELETE FROM messages WHERE session_id = ?", (test_session_id,))
        conn.commit()
        conn.close()

    asyncio.run(run())
