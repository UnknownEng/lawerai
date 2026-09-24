import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.database import init_db
from backend.reasoning_engine import LegalReasoningEngine
from ingestion.vector_store import LegalVectorStore
from backend.config import settings


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    asyncio.run(init_db())


# ==============================================================================
# PRIORITY 1: Stale Citation Carryover (Multi-Turn Conversation Isolation)
# ==============================================================================

def test_priority_1_stale_citation_carryover_partnership_then_wapda():
    """
    Simulate a multi-turn conversation where:
    Turn 1: Business partner verbal profit agreement dispute (gets PPC 405/406).
    Turn 2: Topically unrelated query: 'meri shop ka bijli ka bill bohat zyada aa raha hai, WAPDA se kya kar sakta hoon'.
    Turn 2 MUST NEVER return PPC 405/406. It MUST return fresh NEPRA billing citations.
    Case summary applicable_laws must NOT retain PPC 405/406.
    """
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            sess_resp = await client.post("/api/chat/sessions", json={"title": "Multi-Turn Carryover Test 1"})
            session_id = sess_resp.json()["session_id"]

            # Turn 1: Partnership dispute
            m1 = "My business partner and I verbally agreed to split profits 50/50... he's giving me only 20%"
            r1 = await client.post(f"/api/chat/sessions/{session_id}/messages", json={"content": m1})
            assert r1.status_code == 200
            d1 = r1.json()
            turn1_citation_ids = [c["id"] for c in d1["assistant_message"]["citations"]]
            assert "PPC-405-406" in turn1_citation_ids

            # Turn 2: Unrelated WAPDA electricity billing
            m2 = "meri shop ka bijli ka bill bohat zyada aa raha hai, WAPDA se kya kar sakta hoon"
            r2 = await client.post(f"/api/chat/sessions/{session_id}/messages", json={"content": m2})
            assert r2.status_code == 200
            d2 = r2.json()
            turn2_citations = [c["id"] for c in d2["assistant_message"]["citations"]]

            # MUST NOT carry over PPC 405/406
            assert "PPC-405-406" not in turn2_citations
            # MUST return NEPRA electricity billing
            assert "NEPRA-CONSUMER-BILLING" in turn2_citations

            # Case Summary check: applicable_laws must not contain Turn 1 citations
            case_laws = [l["id"] for l in d2["case_summary"]["applicable_laws"]]
            assert "PPC-405-406" not in case_laws
            assert "NEPRA-CONSUMER-BILLING" in case_laws

    asyncio.run(run())


def test_priority_1_stale_citation_carryover_divorce_then_court_notice():
    """
    Simulate a multi-turn conversation where:
    Turn 1: Divorce/Talaq procedure (gets MFLO Section 7).
    Turn 2: 'I received a court notice, 7 days to respond, don't know what the case is about'.
    Turn 2 MUST NOT return MFLO Section 7. It MUST return CPC summons / notice citations.
    """
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            sess_resp = await client.post("/api/chat/sessions", json={"title": "Multi-Turn Carryover Test 2"})
            session_id = sess_resp.json()["session_id"]

            # Turn 1: Talaq / Divorce procedure
            m1 = "My husband pronounced talaq last week, what is the legal procedure under Pakistani law?"
            r1 = await client.post(f"/api/chat/sessions/{session_id}/messages", json={"content": m1})
            assert r1.status_code == 200
            d1 = r1.json()
            turn1_citation_ids = [c["id"] for c in d1["assistant_message"]["citations"]]
            assert "MFLO-SEC-7" in turn1_citation_ids

            # Turn 2: Unrelated Court Notice
            m2 = "I received a court notice, 7 days to respond, don't know what the case is about"
            r2 = await client.post(f"/api/chat/sessions/{session_id}/messages", json={"content": m2})
            assert r2.status_code == 200
            d2 = r2.json()
            turn2_citations = [c["id"] for c in d2["assistant_message"]["citations"]]

            # MUST NOT carry over MFLO Section 7
            assert "MFLO-SEC-7" not in turn2_citations
            # MUST return CPC Court Notice / Summons
            assert "CPC-O5-O8-SUMMONS" in turn2_citations

            # Case Summary check: applicable_laws must not contain MFLO-SEC-7
            case_laws = [l["id"] for l in d2["case_summary"]["applicable_laws"]]
            assert "MFLO-SEC-7" not in case_laws
            assert "CPC-O5-O8-SUMMONS" in case_laws

    asyncio.run(run())


# ==============================================================================
# PRIORITY 2: Multi-Issue Segmentation
# ==============================================================================

def test_priority_2_multi_issue_tenant_and_joint_business():
    """
    'My tenant hasn't paid rent in 4 months, and while dealing with that I also got into a dispute with my brother over our joint business account'
    Must address BOTH:
    Issue 1: Tenant eviction / default
    Issue 2: Joint business account / partnership dispute
    Must label 'Issue 1' and 'Issue 2'.
    """
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            sess_resp = await client.post("/api/chat/sessions", json={"title": "Multi-Issue Tenant & Business"})
            session_id = sess_resp.json()["session_id"]

            user_msg = (
                "My tenant hasn't paid rent in 4 months, and while dealing with that "
                "I also got into a dispute with my brother over our joint business account"
            )
            resp = await client.post(f"/api/chat/sessions/{session_id}/messages", json={"content": user_msg})
            assert resp.status_code == 200
            data = resp.json()

            citations = [c["id"] for c in data["assistant_message"]["citations"]]
            content = data["assistant_message"]["content"]

            # Must contain citations for both rent eviction and joint business breach of trust
            assert any(c in citations for c in ["PRPA-SEC-15", "SRPO-SEC-15"])
            assert "PPC-405-406" in citations

            # Must have explicit Issue 1 and Issue 2 labels
            assert "Issue 1" in content
            assert "Issue 2" in content

    asyncio.run(run())


def test_priority_2_multi_issue_divorce_debt_jewelry():
    """
    'I want a divorce from my husband, he also owes me money he borrowed before marriage, and my father-in-law is refusing to return my jewelry'
    Must address ALL THREE issues:
    Issue 1: Divorce / Khula
    Issue 2: Pre-marriage debt / borrowed money
    Issue 3: Return of bridal jewelry / dowry articles
    Must label 'Issue 1', 'Issue 2', and 'Issue 3'.
    """
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            sess_resp = await client.post("/api/chat/sessions", json={"title": "Multi-Issue Divorce Debt Jewelry"})
            session_id = sess_resp.json()["session_id"]

            user_msg = (
                "I want a divorce from my husband, he also owes me money he borrowed before marriage, "
                "and my father-in-law is refusing to return my jewelry"
            )
            resp = await client.post(f"/api/chat/sessions/{session_id}/messages", json={"content": user_msg})
            assert resp.status_code == 200
            data = resp.json()

            citations = [c["id"] for c in data["assistant_message"]["citations"]]
            content = data["assistant_message"]["content"]

            # All 3 statutory areas must be cited
            assert any(c in citations for c in ["FCA-SEC-10", "FCA-SEC-5", "MFLO-SEC-7", "MFLO-SEC-8"])
            assert any(c in citations for c in ["CONTRACT-SEC-73", "CONTRACT-SEC-73-74", "PPC-420"])
            assert any(c in citations for c in ["FCA-DOWRY-ARTICLES", "PPC-405-406"])

            # Labels for all 3 issues
            assert "Issue 1" in content
            assert "Issue 2" in content
            assert "Issue 3" in content

    asyncio.run(run())


# ==============================================================================
# PRIORITY 3: Limitation Period & Procedural Posture Reasoning
# ==============================================================================

def test_priority_3_limitation_delayed_land_claim():
    """
    'My father passed away 12 years ago and I just found out my uncle transferred agricultural land... Can I still claim it?'
    Must cite Limitation Act 1908 and Section 42 Specific Relief Act.
    Must explicitly discuss limitation period and delay in the content.
    """
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            sess_resp = await client.post("/api/chat/sessions", json={"title": "Limitation 12 Years Test"})
            session_id = sess_resp.json()["session_id"]

            user_msg = "My father passed away 12 years ago and I just found out my uncle transferred agricultural land... Can I still claim it?"
            resp = await client.post(f"/api/chat/sessions/{session_id}/messages", json={"content": user_msg})
            assert resp.status_code == 200
            data = resp.json()

            citations = [c["id"] for c in data["assistant_message"]["citations"]]
            content = data["assistant_message"]["content"]

            assert "LIMITATION-ACT-1908" in citations
            assert "SRA-SEC-42" in citations
            assert "Limitation Act" in content

    asyncio.run(run())


def test_priority_3_unpaid_decree_execution():
    """
    'I won a court case 4 years ago but the other party never paid the decree amount. What do I do now?'
    Must advise EXECUTION of decree under CPC Order XXI, NOT a fresh suit, and NEVER divorce/Khula.
    """
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            sess_resp = await client.post("/api/chat/sessions", json={"title": "Decree Execution Test"})
            session_id = sess_resp.json()["session_id"]

            user_msg = "I won a court case 4 years ago but the other party never paid the decree amount. What do I do now?"
            resp = await client.post(f"/api/chat/sessions/{session_id}/messages", json={"content": user_msg})
            assert resp.status_code == 200
            data = resp.json()

            citations = [c["id"] for c in data["assistant_message"]["citations"]]
            content = data["assistant_message"]["content"]

            assert "CPC-O21-EXEC" in citations
            # Must not cite divorce
            assert "MFLO" not in content
            assert "Khula" not in content
            assert "Order XXI" in content or "Execution" in content

    asyncio.run(run())


# ==============================================================================
# PRIORITY 4: Jurisdiction Defaults & Non-Punjab/Sindh Isolation
# ==============================================================================

def test_priority_4_islamabad_tenancy_uses_irro():
    """
    'I'm a tenant in Islamabad and my landlord is trying to evict me'
    Must cite Islamabad Rent Restriction Ordinance 2001 (IRRO-SEC-17), NOT Punjab PRPA or Sindh SRPO.
    """
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            sess_resp = await client.post("/api/chat/sessions", json={"title": "Islamabad Tenancy Test"})
            session_id = sess_resp.json()["session_id"]

            user_msg = "I'm a tenant in Islamabad and my landlord is trying to evict me"
            resp = await client.post(f"/api/chat/sessions/{session_id}/messages", json={"content": user_msg})
            assert resp.status_code == 200
            data = resp.json()

            citations = [c["id"] for c in data["assistant_message"]["citations"]]
            assert "IRRO-SEC-17" in citations
            assert "PRPA-SEC-15" not in citations
            assert "SRPO-SEC-15" not in citations

    asyncio.run(run())


def test_priority_4_kpk_balochistan_gracefully_declines_without_substitution():
    """
    'I'm a tenant in Peshawar and my landlord is trying to evict me'
    Must NOT silently substitute Punjab or Sindh rent law.
    Must state provincial rent law is not currently indexed, with 0 citations.
    """
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            sess_resp = await client.post("/api/chat/sessions", json={"title": "KPK Tenancy Test"})
            session_id = sess_resp.json()["session_id"]

            user_msg = "I am a tenant in Peshawar and my landlord is trying to evict me"
            resp = await client.post(f"/api/chat/sessions/{session_id}/messages", json={"content": user_msg})
            assert resp.status_code == 200
            data = resp.json()

            citations = [c["id"] for c in data["assistant_message"]["citations"]]
            content = data["assistant_message"]["content"]

            # Zero citations returned
            assert citations == []
            assert "PRPA-SEC-15" not in citations
            assert "SRPO-SEC-15" not in citations
            # Content explains KPK Rented Premises Act is not currently indexed
            assert "Khyber Pakhtunkhwa Rented Premises Act" in content or "not currently indexed" in content

    asyncio.run(run())


# ==============================================================================
# PRIORITY 5: Roman Urdu Parity
# ==============================================================================

def test_priority_5_roman_urdu_parity_ppc_420():
    """
    'mera dost mujhse paisay udhar le kar gaya tha, ab wo phone hi nahi utha raha'
    Must return PPC 420 with high confidence, equivalent to English query.
    """
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            sess_resp = await client.post("/api/chat/sessions", json={"title": "Roman Urdu PPC 420 Test"})
            session_id = sess_resp.json()["session_id"]

            user_msg = "mera dost mujhse paisay udhar le kar gaya tha, ab wo phone hi nahi utha raha"
            resp = await client.post(f"/api/chat/sessions/{session_id}/messages", json={"content": user_msg})
            assert resp.status_code == 200
            data = resp.json()

            citations = [c["id"] for c in data["assistant_message"]["citations"]]
            assert "PPC-420" in citations

    asyncio.run(run())


# ==============================================================================
# PRIORITY 6: Corpus Additions & Graceful Decline
# ==============================================================================

def test_priority_6_attempted_robbery_pharmacy():
    """
    Pharmacy attempted robbery at gunpoint with no actual loss.
    Must cite PPC 392/393/397.
    """
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            sess_resp = await client.post("/api/chat/sessions", json={"title": "Attempted Robbery Test"})
            session_id = sess_resp.json()["session_id"]

            user_msg = "Two armed men entered my pharmacy with pistols demanding cash, but fled when an alarm went off. No money was taken. What case can I file?"
            resp = await client.post(f"/api/chat/sessions/{session_id}/messages", json={"content": user_msg})
            assert resp.status_code == 200
            data = resp.json()

            citations = [c["id"] for c in data["assistant_message"]["citations"]]
            assert "PPC-392-393" in citations

    asyncio.run(run())


def test_priority_6_motor_vehicle_accident_insurance_graceful_decline():
    """
    Motor vehicle accident and insurance claim dispute.
    Must gracefully decline with outside coverage message and 0 citations (do NOT hallucinate PPC 279).
    """
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            sess_resp = await client.post("/api/chat/sessions", json={"title": "Insurance Accident Test"})
            session_id = sess_resp.json()["session_id"]

            user_msg = "meri gari ka accident ho gaya aur insurance company claim nahi de rahi"
            resp = await client.post(f"/api/chat/sessions/{session_id}/messages", json={"content": user_msg})
            assert resp.status_code == 200
            data = resp.json()

            citations = [c["id"] for c in data["assistant_message"]["citations"]]
            content = data["assistant_message"]["content"]

            assert citations == []
            assert "PPC-279-337G" not in citations
            assert "Insurance Ordinance" in content or "outside current coverage" in content or "insurance" in content.lower()

    asyncio.run(run())


def test_priority_6_unpaid_employee_wages():
    """
    Unpaid employee wages for 3 months.
    Must cite Payment of Wages Act 1936 (PWA-SEC-15).
    """
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            sess_resp = await client.post("/api/chat/sessions", json={"title": "Unpaid Wages Test"})
            session_id = sess_resp.json()["session_id"]

            user_msg = "My company has not paid my salary for the last 3 months and my manager is refusing to answer"
            resp = await client.post(f"/api/chat/sessions/{session_id}/messages", json={"content": user_msg})
            assert resp.status_code == 200
            data = resp.json()

            citations = [c["id"] for c in data["assistant_message"]["citations"]]
            assert "PWA-SEC-15" in citations

    asyncio.run(run())


# ==============================================================================
# NON-REGRESSION VERIFICATIONS
# ==============================================================================

def test_non_regression_uncovered_topics_and_safety_calibration():
    """
    Preserve working behaviors:
    1. Confidence gate declines to guess on genuinely uncovered topics:
       - neighbor's dog damaging garden -> 0 citations
       - tampered car odometer -> 0 citations
       - workplace rumor-spreading -> 0 citations
    2. Emergency interceptor does NOT over-trigger on:
       - husband raised his voice during an argument -> is_emergency is False
       - my business is failing and I feel like I've lost everything -> is_emergency is False
    """
    engine = LegalReasoningEngine()
    vs = LegalVectorStore(storage_path=settings.VECTOR_STORE_PATH)

    # 1. Uncovered topics
    for topic in [
        "neighbor's dog damaging garden",
        "tampered car odometer",
        "workplace rumor-spreading"
    ]:
        analysis = engine.analyze(topic)
        assert analysis.is_emergency is False
        secs = vs.search_hybrid(topic, top_k=2, min_score=0.45)
        assert len(secs) == 0, f"Expected 0 citations for uncovered topic '{topic}', got {secs}"

    # 2. Safety non-emergencies
    for safe_msg in [
        "husband raised his voice during an argument",
        "my business is failing and I feel like I've lost everything"
    ]:
        analysis = engine.analyze(safe_msg)
        assert analysis.is_emergency is False, f"Expected non-emergency for '{safe_msg}', got True"


# ==============================================================================
# USER-REPORTED BUGS 1-5 & PLAIN LANGUAGE / SINGLE-DISCLAIMER REGRESSIONS
# ==============================================================================

def test_bug_1a_security_deposit_refund_not_eviction():
    """
    Bug 1(a): 'landlord is refusing to return my security deposit'
    Must cite tenant's right to deposit recovery (PRPA Section 13 / SRPO Section 7 / Contract Act),
    NOT landlord eviction procedure (PRPA/SRPO Section 15).
    """
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            s = (await client.post("/api/chat/sessions", json={"title": "Deposit Recovery"})).json()["session_id"]
            r = (await client.post(f"/api/chat/sessions/{s}/messages", json={"content": "landlord is refusing to return my security deposit"})).json()
            citations = [c["id"] for c in r["assistant_message"]["citations"]]
            assert "PRPA-SEC-15" not in citations
            assert "SRPO-SEC-15" not in citations
            assert any(c in citations for c in ["PRPA-SEC-13", "SRPO-SEC-7", "CONTRACT-SEC-73-74"])
    asyncio.run(run())


def test_bug_1b_roman_urdu_unlawful_dispossession_not_eviction():
    """
    Bug 1(b): Roman Urdu: 'mera landlord kehta hai agreement khatam ho gaya hai lekin maine renew karwaya tha, ab wo zabardasti nikal raha hai'
    Must cite illegal dispossession / injunction, NOT landlord-eviction Section 15.
    """
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            s = (await client.post("/api/chat/sessions", json={"title": "Roman Urdu Lockout"})).json()["session_id"]
            msg = "mera landlord kehta hai agreement khatam ho gaya hai lekin maine renew karwaya tha, ab wo zabardasti nikal raha hai"
            r = (await client.post(f"/api/chat/sessions/{s}/messages", json={"content": msg})).json()
            citations = [c["id"] for c in r["assistant_message"]["citations"]]
            assert "PRPA-SEC-15" not in citations
            assert "SRPO-SEC-15" not in citations
            assert any(c in citations for c in ["SRA-SEC-8-9", "CPC-O39-R1-2", "PPC-441-447-448"])
    asyncio.run(run())


def test_bug_2a_verbal_loan_no_cheque_citation():
    """
    Bug 2(a): 'My brother took a loan from me, signed an agreement — actually no, just a verbal promise'
    Must NEVER cite PPC 489-F (dishonoured cheque) when no cheque exists.
    """
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            s = (await client.post("/api/chat/sessions", json={"title": "Verbal Loan"})).json()["session_id"]
            msg = "My brother took a loan from me, signed an agreement — actually no, just a verbal promise"
            r = (await client.post(f"/api/chat/sessions/{s}/messages", json={"content": msg})).json()
            citations = [c["id"] for c in r["assistant_message"]["citations"]]
            assert "PPC-489F" not in citations
    asyncio.run(run())


def test_bug_2b_family_insult_no_child_custody_citation():
    """
    Bug 2(b): 'My sister-in-law says I insulted her at a family function, I was just asking her to stop shouting at my child'
    Must NEVER cite Guardian and Wards Act (child custody).
    """
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            s = (await client.post("/api/chat/sessions", json={"title": "Family Insult"})).json()["session_id"]
            msg = "My sister-in-law says I insulted her at a family function, I was just asking her to stop shouting at my child"
            r = (await client.post(f"/api/chat/sessions/{s}/messages", json={"content": msg})).json()
            citations = [c["id"] for c in r["assistant_message"]["citations"]]
            assert "GWA-SEC-17-25" not in citations
    asyncio.run(run())


def test_bug_2c_and_bug_3_coercive_control_third_party_advisory():
    """
    Bug 2(c) & Bug 3: 'My friend's husband locks her out of the house and takes her phone so she can't call anyone'
    - Must NOT cite PPC 420 (cheating/fraud).
    - Must NOT trigger immediate emergency lock (user is not in danger, 3rd party report).
    - Must provide supportive coercive-control advisory with helplines (1043, 1098, 15) and protective statutes (PWAWA / PPC 340-342).
    """
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            s = (await client.post("/api/chat/sessions", json={"title": "Friend Coercive Control"})).json()["session_id"]
            msg = "My friend's husband locks her out of the house and takes her phone so she can't call anyone"
            r = (await client.post(f"/api/chat/sessions/{s}/messages", json={"content": msg})).json()
            citations = [c["id"] for c in r["assistant_message"]["citations"]]
            content = r["assistant_message"]["content"]
            assert "PPC-420" not in citations
            assert r["is_emergency"] is False
            assert "1043" in content or "1098" in content or "15" in content
            assert "Protection of Women" in content or "wrongful" in content.lower()
    asyncio.run(run())


def test_bug_4_khula_divorce_mechanism_and_reconciliation_withdrawal():
    """
    Bug 4: 'I filed for khula five years ago but withdrew because we reconciled, now I want to file again — does withdrawing count against me?'
    - Must cite Khula (Family Courts Act Sec 10/5), NOT Talaq (MFLO Sec 7).
    - Must directly answer procedural question: withdrawing for reconciliation does NOT count against her or prejudice filing a fresh case.
    """
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            s = (await client.post("/api/chat/sessions", json={"title": "Khula Withdrawal"})).json()["session_id"]
            msg = "I filed for khula five years ago but withdrew because we reconciled, now I want to file again — does withdrawing count against me?"
            r = (await client.post(f"/api/chat/sessions/{s}/messages", json={"content": msg})).json()
            citations = [c["id"] for c in r["assistant_message"]["citations"]]
            content = r["assistant_message"]["content"]
            assert "MFLO-SEC-7" not in citations
            assert any(c in citations for c in ["FCA-SEC-10", "FCA-SEC-5"])
            assert "withdrawing" in content.lower()
            assert "not" in content.lower() or "fresh" in content.lower()
    asyncio.run(run())


def test_bug_5a_multi_issue_deposit_and_crashed_car():
    """
    Bug 5(a): 'landlord is refusing to return my security deposit, also my cousin crashed my borrowed car'
    Must identify and label BOTH issues: Issue 1 (rent deposit) and Issue 2 (crashed borrowed car).
    """
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            s = (await client.post("/api/chat/sessions", json={"title": "Deposit and Car"})).json()["session_id"]
            msg = "landlord is refusing to return my security deposit, also my cousin crashed my borrowed car"
            r = (await client.post(f"/api/chat/sessions/{s}/messages", json={"content": msg})).json()
            content = r["assistant_message"]["content"]
            assert "Issue 1" in content
            assert "Issue 2" in content
            assert "deposit" in content.lower()
            assert "car" in content.lower() or "vehicle" in content.lower()
    asyncio.run(run())


def test_bug_5b_three_issues_shop_lockout_partnership_profit_notice_deadline():
    """
    Bug 5(b): 'My shop is locked by my landlord even though rent was paid, also my business partner is not paying my profit share from our joint account, and I also got a legal notice yesterday with 10 days to reply'
    Must identify and label ALL THREE issues without dropping the 10-day notice deadline.
    """
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            s = (await client.post("/api/chat/sessions", json={"title": "Three Issues"})).json()["session_id"]
            msg = (
                "My shop is locked by my landlord even though rent was paid, "
                "also my business partner is not paying my profit share from our joint account, "
                "and I also got a legal notice yesterday with 10 days to reply"
            )
            r = (await client.post(f"/api/chat/sessions/{s}/messages", json={"content": msg})).json()
            content = r["assistant_message"]["content"]
            assert "Issue 1" in content
            assert "Issue 2" in content
            assert "Issue 3" in content
            assert "PRPA-SEC-15" not in [c["id"] for c in r["assistant_message"]["citations"]]
            assert "notice" in content.lower()
    asyncio.run(run())


def test_language_simplification_and_no_repeated_disclaimer():
    """
    Verifies that:
    1. Full legal disclaimer appears ONLY in the initial welcome message of a session.
    2. Subsequent replies do NOT repeat the full 'Legal Disclaimer:' paragraph or drafting advisory.
    3. Forbidden technical jargon ('ad-interim restraining order', 'prima facie case', 'balance of convenience', 'rendition of accounts') is absent.
    """
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            sess_resp = await client.post("/api/chat/sessions", json={"title": "Plain Language Test"})
            session_id = sess_resp.json()["session_id"]

            # Welcome message must have the disclaimer
            detail = (await client.get(f"/api/chat/sessions/{session_id}")).json()
            assert "Legal Disclaimer:" in detail["messages"][0]["content"]

            # Turn 1 reply
            r1 = (await client.post(f"/api/chat/sessions/{session_id}/messages", json={"content": "landlord is refusing to return my security deposit"})).json()
            content1 = r1["assistant_message"]["content"]
            assert "Legal Disclaimer:" not in content1
            assert "Legal Drafting Advisory" not in content1

            # Check jargon absence
            forbidden_terms = [
                "ad-interim restraining order",
                "prima facie case",
                "balance of convenience",
                "rendition of accounts"
            ]
            for term in forbidden_terms:
                assert term not in content1.lower(), f"Forbidden jargon '{term}' found in response"
    asyncio.run(run())


# ==============================================================================
# PRIORITY 6: Factual Relevance & Hallucination Prevention on Novel Scenarios
# ==============================================================================

def test_jirga_union_council_no_nepra():
    """
    Scenario 1: Union Council chairman dissolving jirga decision on land dispute.
    Must NOT return NEPRA electricity billing law. Citations must be empty [].
    Must address Jirga illegality and civil court jurisdiction.
    """
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            s = (await client.post("/api/chat/sessions", json={"title": "Jirga Test"})).json()["session_id"]
            msg = (
                "Our local Union Council chairman dissolved our jirga's decision on a land dispute "
                "saying he had emergency powers to do so, even though nobody followed the normal complaint procedure. "
                "Is his cancellation legally valid?"
            )
            r = (await client.post(f"/api/chat/sessions/{s}/messages", json={"content": msg})).json()
            citations = [c["id"] for c in r["assistant_message"]["citations"]]
            content = r["assistant_message"]["content"]

            assert "NEPRA-CONSUMER-BILLING" not in citations
            assert len(citations) == 0
            assert "jirga" in content.lower()
            assert "civil court" in content.lower() or "supreme court" in content.lower()
    asyncio.run(run())


def test_co_ownership_shop_3_years_adverse_possession_no_mflo():
    """
    Scenario 2: Uncle running shared family shop for 3 years claiming sole ownership.
    Must NOT return MFLO Section 7 (divorce/talaq).
    Must return Limitation Act 1908 and/or Specific Relief Act Section 42.
    """
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            s = (await client.post("/api/chat/sessions", json={"title": "Shop Adverse Possession Test"})).json()["session_id"]
            msg = (
                "My uncle took over our shared family shop and says that since he's been running it "
                "for 3 years without anyone stopping him, it's legally his now. Is that true?"
            )
            r = (await client.post(f"/api/chat/sessions/{s}/messages", json={"content": msg})).json()
            citations = [c["id"] for c in r["assistant_message"]["citations"]]
            content = r["assistant_message"]["content"]

            assert "MFLO-SEC-7" not in citations
            assert "LIMITATION-ACT-1908" in citations or "SRA-SEC-42" in citations
            assert "co-owner" in content.lower() or "limitation" in content.lower() or "declaration" in content.lower()
    asyncio.run(run())


def test_police_pressured_confession_qso_no_ppc_theft():
    """
    Scenario 3: Police custodial confession under pressure.
    Must return QSO Articles 38 & 39.
    Must NOT return PPC 378-380 (theft) with zero factual connection.
    """
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            s = (await client.post("/api/chat/sessions", json={"title": "Confession Test"})).json()["session_id"]
            msg = (
                "My cousin was arrested and the police say a confession was recorded, "
                "but he says he was pressured... Can a confession like that be used against him?"
            )
            r = (await client.post(f"/api/chat/sessions/{s}/messages", json={"content": msg})).json()
            citations = [c["id"] for c in r["assistant_message"]["citations"]]
            content = r["assistant_message"]["content"]

            assert "PPC-379-380" not in citations
            assert "QSO-ART-38-39" in citations
            assert "inadmissible" in content.lower() or "magistrate" in content.lower()
    asyncio.run(run())


def test_religious_remark_single_witness_qso17_crpc408_no_ppc506():
    """
    Scenario 4: Disrespectful remark allegation based on single overheard witness and appeal rights.
    Must NOT return PPC 503-506 (threats).
    Must return QSO Article 17 and CrPC Sections 408 & 410.
    """
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            s = (await client.post("/api/chat/sessions", json={"title": "Single Witness & Appeal Test"})).json()["session_id"]
            msg = (
                "My neighbor accused me of saying something disrespectful about his religion, "
                "based on what one person overheard. Can I be prosecuted just on one person's word, "
                "and what if the lower court believes him but I think I'm innocent?"
            )
            r = (await client.post(f"/api/chat/sessions/{s}/messages", json={"content": msg})).json()
            citations = [c["id"] for c in r["assistant_message"]["citations"]]
            content = r["assistant_message"]["content"]

            assert "PPC-503-506" not in citations
            assert "QSO-ART-17" in citations
            assert "CRPC-408-410" in citations
            assert "Issue 1" in content
            assert "Issue 2" in content
    asyncio.run(run())


def test_real_time_legislative_currency_limitation_zero_citations():
    """
    Scenario 5: Inquiring whether a law changed last year or was reversed recently.
    Must acknowledge that real-time statutory currency cannot be verified reliably.
    Must return ZERO citations ([]).
    """
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            s = (await client.post("/api/chat/sessions", json={"title": "Currency Test"})).json()["session_id"]
            msg = (
                "My lawyer told me a law changed last year that affects my case, "
                "but then said it might have been reversed again recently. How do I know which version applies to me right now?"
            )
            r = (await client.post(f"/api/chat/sessions/{s}/messages", json={"content": msg})).json()
            citations = [c["id"] for c in r["assistant_message"]["citations"]]
            content = r["assistant_message"]["content"]

            assert len(citations) == 0
            assert "cannot reliably determine" in content.lower() or "gazette" in content.lower()
    asyncio.run(run())


def test_out_of_corpus_topics_zero_hallucinations():
    """
    Novel out-of-corpus topics (maritime admiralty salvage, aviation pilot license, customs textile seizure).
    Must return ZERO citations ([]) without hallucinating unrelated corpus statutes.
    """
    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            queries = [
                "A foreign cargo vessel collided with a local fishing trawler in Pakistani territorial waters near Port Qasim, and maritime salvors are claiming salvage lien. How is salvage lien enforced?",
                "The Civil Aviation Authority suspended my commercial pilot license without an inquiry board following an alleged airprox incident. How do I appeal this suspension?",
                "Customs authorities seized raw textile yarn at dry port alleging misdeclaration of tariff heading under SRO. What is the procedure before the Customs Appellate Tribunal?"
            ]
            for q in queries:
                s = (await client.post("/api/chat/sessions", json={"title": "Out of Corpus Test"})).json()["session_id"]
                r = (await client.post(f"/api/chat/sessions/{s}/messages", json={"content": q})).json()
                citations = [c["id"] for c in r["assistant_message"]["citations"]]
                assert len(citations) == 0, f"Expected 0 citations for out-of-corpus query '{q[:40]}...', got {citations}"
    asyncio.run(run())

