"""
Integration tests for FastAPI endpoints (using standard asyncio.run)
"""

import asyncio
import uuid
from httpx import AsyncClient, ASGITransport
from backend.main import app


def test_health_check_endpoint():
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/health")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "online"
            assert "Qanoon Sahayak" in data["app"]
            assert "disclaimer" in data
    asyncio.run(run())


def test_lawyer_directory_endpoint():
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/lawyers")
            assert resp.status_code == 200
            data = resp.json()
            assert data["count"] > 0
            assert len(data["results"]) > 0
    asyncio.run(run())


def test_emergency_resources_endpoint():
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/emergency/resources")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "active"
            assert len(data["resources"]) >= 5
            # Ensure Police 15 is listed
            assert any(r.get("short_code") == "15" or "Police" in r.get("name", "") for r in data["resources"])
    asyncio.run(run())


def test_corpus_search_and_section_detail_endpoints():
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. Search for PPC 420
            search_resp = await client.get("/api/corpus/search", params={"q": "cheating 420"})
            assert search_resp.status_code == 200
            s_data = search_resp.json()
            assert s_data["count"] > 0
            assert any("420" in r.get("section_number", "") for r in s_data["results"])

            # 2. Get specific section details
            sec_resp = await client.get("/api/corpus/section/PPC-420")
            assert sec_resp.status_code == 200
            sec_data = sec_resp.json()
            assert sec_data["act_code"] == "PPC"
            assert sec_data["section_number"] == "420"
            assert "evidence_required" in sec_data
    asyncio.run(run())


def test_chat_session_lifecycle():
    async def run():
        from backend.database import init_db
        await init_db()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. Create session
            create_resp = await client.post("/api/chat/sessions", json={"title": "Test Cheque Dispute", "language": "en"})
            assert create_resp.status_code == 200
            session_id = create_resp.json()["session_id"]
            assert session_id is not None

            # 2. Send message
            msg_resp = await client.post(
                f"/api/chat/sessions/{session_id}/messages",
                json={"content": "Someone gave me a cheque of 300,000 PKR and the bank dishonoured it with funds insufficient memo."}
            )
            assert msg_resp.status_code == 200
            msg_data = msg_resp.json()
            assert msg_data["is_emergency"] is False
            assert "assistant_message" in msg_data
            assert "489" in msg_data["assistant_message"]["content"] or any("489" in c.get("section_number", "") for c in msg_data["assistant_message"].get("citations", []))

            # 3. Check Case Summary
            detail_resp = await client.get(f"/api/chat/sessions/{session_id}")
            assert detail_resp.status_code == 200
            detail = detail_resp.json()
            assert "case_summary" in detail
            assert len(detail["case_summary"]["applicable_laws"]) > 0

            # 4. Check HTML export
            export_resp = await client.get(f"/api/chat/sessions/{session_id}/export/html")
            assert export_resp.status_code == 200
            assert "QANOON SAHAYAK" in export_resp.text

            # 5. Check JSON export
            export_json_resp = await client.get(f"/api/chat/sessions/{session_id}/export/json")
            assert export_json_resp.status_code == 200
            jdata = export_json_resp.json()
            assert jdata["dossier_id"] == session_id
            assert "summary" in jdata
            assert "applicable_laws" in jdata["summary"]
            assert "disclaimer" in jdata
    asyncio.run(run())


def test_auth_registration_and_login_flow():
    async def run():
        from backend.database import init_db
        await init_db()
        transport = ASGITransport(app=app)
        unique_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
        password = "SecurePassword123!"

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. Register new user
            reg_resp = await client.post("/api/auth/register", json={
                "email": unique_email,
                "password": password,
                "full_name": "Tariq Mehmood"
            })
            assert reg_resp.status_code == 200
            reg_data = reg_resp.json()
            assert "access_token" in reg_data
            token = reg_data["access_token"]

            # 2. Query /api/auth/me with bearer token
            me_resp = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
            assert me_resp.status_code == 200
            assert me_resp.json()["email"] == unique_email

            # 3. Login with correct credentials
            login_resp = await client.post("/api/auth/login", json={
                "email": unique_email,
                "password": password
            })
            assert login_resp.status_code == 200
            assert "access_token" in login_resp.json()

            # 4. Login with incorrect password
            bad_login = await client.post("/api/auth/login", json={
                "email": unique_email,
                "password": "WrongPassword!"
            })
            assert bad_login.status_code == 401
    asyncio.run(run())


def test_chat_emergency_interception_exact_phrases():
    """
    PRIORITY 1 Regression: Messages describing domestic violence and suicidal ideation
    must trigger emergency interception BEFORE any legal retrieval, returning crisis resources and NO citations.
    """
    async def run():
        from backend.database import init_db
        await init_db()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            sess_resp = await client.post("/api/chat/sessions", json={"title": "Emergency Test"})
            session_id = sess_resp.json()["session_id"]

            # 1. Domestic violence exact phrase
            dv_resp = await client.post(
                f"/api/chat/sessions/{session_id}/messages",
                json={"content": "my husband hits me and I don't feel safe at home"}
            )
            assert dv_resp.status_code == 200
            dv_data = dv_resp.json()
            assert dv_data["is_emergency"] is True
            assert dv_data["assistant_message"]["citations"] == []
            assert "15" in dv_data["assistant_message"]["content"]
            assert "1043" in dv_data["assistant_message"]["content"]
            # Formatting checks (Priority 4): no emojis, no markdown bold
            content = dv_data["assistant_message"]["content"]
            assert "🚨" not in content
            assert "📞" not in content
            assert "**" not in content

            # 2. Self-harm / suicidal ideation exact phrase
            sh_resp = await client.post(
                f"/api/chat/sessions/{session_id}/messages",
                json={"content": "I don't see the point in living anymore because of this court case"}
            )
            assert sh_resp.status_code == 200
            sh_data = sh_resp.json()
            assert sh_data["is_emergency"] is True
            assert sh_data["assistant_message"]["citations"] == []
            sh_content = sh_data["assistant_message"]["content"]
            assert "🚨" not in sh_content
            assert "**" not in sh_content
    asyncio.run(run())


def test_chat_car_impoundment_cites_motor_vehicles_ordinance():
    """
    PRIORITY 3 Regression: Car impoundment query must cite Provincial Motor Vehicles Ordinance,
    NOT PPC 324 (Attempted murder).
    """
    async def run():
        from backend.database import init_db
        await init_db()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            sess_resp = await client.post("/api/chat/sessions", json={"title": "Car Impound Test"})
            session_id = sess_resp.json()["session_id"]

            resp = await client.post(
                f"/api/chat/sessions/{session_id}/messages",
                json={"content": "traffic police impounded my car saying the number plate doesn't match"}
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["is_emergency"] is False
            citations = data["assistant_message"]["citations"]
            assert len(citations) > 0
            assert any(c.get("act_code") == "PMVO" for c in citations)
            assert not any("324" in str(c.get("section_number", "")) for c in citations)
            # Output formatting check
            asst_text = data["assistant_message"]["content"]
            assert "**" not in asst_text
            assert "###" not in asst_text
            assert "👉" not in asst_text
            assert "⚖️" not in asst_text
    asyncio.run(run())


def test_chat_company_funds_cites_breach_of_trust():
    """
    PRIORITY 3 Regression: Business partner misusing company funds must cite PPC 405/406,
    NOT Muslim Family Laws Ordinance Section 9.
    """
    async def run():
        from backend.database import init_db
        await init_db()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            sess_resp = await client.post("/api/chat/sessions", json={"title": "Company Funds Test"})
            session_id = sess_resp.json()["session_id"]

            resp = await client.post(
                f"/api/chat/sessions/{session_id}/messages",
                json={"content": "my business partner used company funds for personal expenses without telling me"}
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["is_emergency"] is False
            citations = data["assistant_message"]["citations"]
            assert len(citations) > 0
            assert any(c.get("act_code") == "PPC" and ("405" in str(c.get("section_number", "")) or "406" in str(c.get("section_number", ""))) for c in citations)
            assert not any(c.get("act_code") == "MFLO" for c in citations)
            # Formatting check
            asst_text = data["assistant_message"]["content"]
            assert "**" not in asst_text
            assert "###" not in asst_text
    asyncio.run(run())


def test_chat_low_confidence_safeguard():
    """
    PRIORITY 2 Regression: When query confidence is low, do NOT commit to random statutes.
    Must return empty citations and ask a clarifying question.
    """
    async def run():
        from backend.database import init_db
        await init_db()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            sess_resp = await client.post("/api/chat/sessions", json={"title": "Low Confidence Test"})
            session_id = sess_resp.json()["session_id"]

            resp = await client.post(
                f"/api/chat/sessions/{session_id}/messages",
                json={"content": "how do I bake a chocolate cake at home?"}
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["assistant_message"]["citations"] == []
            asst_text = data["assistant_message"]["content"]
            # Must state need for more information or ask clarifying question
            assert "more" in asst_text.lower() or "clarify" in asst_text.lower() or "detail" in asst_text.lower()
            # Must NOT cite PPC 324 or MFLO 9
            assert "324" not in asst_text
            assert "Muslim Family Laws" not in asst_text
    asyncio.run(run())


def test_multi_issue_reasoning_and_retrieval_case_a():
    """
    CASE A Verification:
    Multi-issue message containing tenant lockout and brother selling late father's house:
    - Must address both issues separately and clearly.
    - Issue 1 must cite Specific Relief Act Section 9 (restoration of possession), NOT landlord eviction (PRPA/SRPO Section 15).
    - Issue 2 must cite CPC Order 39 (stay order) and Specific Relief Act Section 42 (suit for declaration of inheritance share).
    - Plain text formatting: no emojis, no markdown bold, no markdown headers.
    """
    async def run():
        from backend.database import init_db
        await init_db()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            sess_resp = await client.post("/api/chat/sessions", json={"title": "Multi-Issue Case A Test"})
            session_id = sess_resp.json()["session_id"]

            user_msg = (
                "My landlord changed the locks on my shop while I was away and won't let me back in, "
                "even though my rent is paid. Also, my brother is trying to sell our late father's house "
                "without my signature, even though I'm also a legal heir."
            )
            resp = await client.post(
                f"/api/chat/sessions/{session_id}/messages",
                json={"content": user_msg}
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["is_emergency"] is False

            citations = data["assistant_message"]["citations"]
            citation_ids = [c["id"] for c in citations]

            # Issue 1: Specific Relief Act Section 9 (Illegal dispossession / recovery of possession)
            assert "SRA-SEC-8-9" in citation_ids
            # MUST NOT cite landlord eviction statutes
            assert "PRPA-SEC-15" not in citation_ids
            assert "SRPO-SEC-15" not in citation_ids

            # Issue 2: CPC Order 39 stay order and/or SRA Section 42 declaration of title
            assert "CPC-O39-R1-2" in citation_ids or "SRA-SEC-42" in citation_ids

            # Content structure
            content = data["assistant_message"]["content"]
            assert "Issue 1" in content
            assert "Issue 2" in content
            assert "Specific Relief Act" in content
            # Disclaimer must NOT be repeated in subsequent replies
            assert "Legal Disclaimer:" not in content

            # Strict formatting rules
            assert "**" not in content
            assert "###" not in content
            assert "⚖️" not in content
            assert "🚨" not in content
            assert "👉" not in content

            # Case Summary check
            detail_resp = await client.get(f"/api/chat/sessions/{session_id}")
            # Disclaimer must be present in the initial welcome message of the session
            assert "Legal Disclaimer:" in detail_resp.json()["messages"][0]["content"]
            summary = detail_resp.json()["case_summary"]
            assert len(summary["applicable_laws"]) >= 2
            app_law_ids = [l["id"] for l in summary["applicable_laws"]]
            assert "SRA-SEC-8-9" in app_law_ids
            assert "PRPA-SEC-15" not in app_law_ids
    asyncio.run(run())


def test_safety_preempts_legal_issues_case_b():
    """
    CASE B Verification:
    Combined safety and legal message ('My husband hits me and also he isn't paying maintenance'):
    Emergency interceptor MUST fire immediately and block all legal retrieval.
    Zero legal citations returned.
    """
    async def run():
        from backend.database import init_db
        await init_db()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            sess_resp = await client.post("/api/chat/sessions", json={"title": "Case B Safety Priority Test"})
            session_id = sess_resp.json()["session_id"]

            user_msg = "My husband hits me and also he isn't paying maintenance"
            resp = await client.post(
                f"/api/chat/sessions/{session_id}/messages",
                json={"content": user_msg}
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["is_emergency"] is True
            assert data["assistant_message"]["citations"] == []
            assert len(data.get("emergency_helplines", [])) >= 3

            content = data["assistant_message"]["content"]
            assert "15" in content
            assert "1043" in content
            # Ensure no civil maintenance statutes are cited or advised
            assert "MFLO" not in content
            assert "Muslim Family Laws" not in content
            assert "**" not in content
            assert "🚨" not in content
    asyncio.run(run())


