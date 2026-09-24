"""
Tests for RAG statutory retrieval accuracy, coverage, and confidence safeguards.
"""

import pytest
from ingestion.vector_store import LegalVectorStore


@pytest.fixture(scope="module")
def vector_store():
    store = LegalVectorStore()
    if not store.documents:
        store.load()
    return store


def test_retrieval_ppc_420_cheating(vector_store):
    query = "Someone took 500,000 rupees by making false promises and disappeared"
    results = vector_store.search_hybrid(query, top_k=3)
    assert len(results) > 0
    top = results[0]
    assert top["act_code"] == "PPC"
    assert "420" in top["section_number"]


def test_retrieval_ppc_489f_cheque_bounce(vector_store):
    query = "The buyer gave me a bank cheque for payment and it bounced due to insufficient funds"
    results = vector_store.search_hybrid(query, top_k=3)
    assert len(results) > 0
    top = results[0]
    assert top["act_code"] == "PPC"
    assert "489" in top["section_number"]


def test_retrieval_crpc_refusal_fir(vector_store):
    query = "The SHO at the local police station is refusing to register an FIR"
    results = vector_store.search_hybrid(query, top_k=3)
    assert len(results) > 0
    matched = any(r["act_code"].upper() == "CRPC" for r in results)
    assert matched


def test_retrieval_mflo_maintenance(vector_store):
    query = "Husband abandoned wife and children and stopped paying monthly maintenance and child expenses"
    results = vector_store.search_hybrid(query, top_k=3)
    assert len(results) > 0
    assert any("maintenance" in r.get("section_title", "").lower() or r.get("act_code") == "MFLO" for r in results)


def test_retrieval_cpc_stay_order(vector_store):
    query = "Neighbor is doing illegal construction on my plot, I need urgent stay order"
    results = vector_store.search_hybrid(query, top_k=3)
    assert len(results) > 0
    top = results[0]
    assert top["act_code"] == "CPC"
    assert "XXXIX" in top["section_number"] or "39" in top["section_number"]


def test_retrieval_peca_cyber_blackmail(vector_store):
    query = "Someone is blackmailing a girl on WhatsApp by threatening to leak pictures"
    results = vector_store.search_hybrid(query, top_k=3)
    assert len(results) > 0
    top = results[0]
    assert top["act_code"] == "PECA"


def test_regression_motor_vehicles_car_impoundment(vector_store):
    """
    Regression test for car impoundment query.
    Must cite Provincial Motor Vehicles Ordinance (PMVO Section 115 / Section 23).
    Must NEVER cite PPC 324 (Attempted Murder).
    """
    query = "traffic police impounded my car saying the number plate doesn't match"
    results = vector_store.search_hybrid(query, top_k=3)
    assert len(results) > 0
    top = results[0]
    assert top["act_code"] == "PMVO"
    assert any(sec in top["section_number"] for sec in ["115", "23"])
    # Ensure no unrelated criminal sections like 324 (Attempted murder) are returned
    for r in results:
        assert "324" not in str(r.get("section_number", ""))
        assert r.get("act_code") != "PPC"


def test_regression_company_funds_misuse_breach_of_trust(vector_store):
    """
    Regression test for business partner misusing company funds.
    Must cite PPC Section 405 / 406 (criminal breach of trust).
    Must NEVER cite Muslim Family Laws Ordinance Section 9 (wife maintenance).
    """
    query = "my business partner used company funds for personal expenses without telling me"
    results = vector_store.search_hybrid(query, top_k=3)
    assert len(results) > 0
    top = results[0]
    assert top["act_code"] == "PPC"
    assert "405" in top["section_number"] or "406" in top["section_number"]
    # Ensure MFLO Section 9 is not returned
    for r in results:
        assert r.get("act_code") != "MFLO"
        assert "maintenance" not in r.get("section_title", "").lower()


def test_regression_confidence_threshold_safeguard(vector_store):
    """
    Low confidence / unrelated queries must return zero results.
    The system must NOT commit to random statutes when confidence is low.
    """
    unrelated_queries = [
        "how do I bake a chocolate cake at home?",
        "what is the weather like in Islamabad today?",
        "my bicycle was painted blue and my neighbor likes green"
    ]
    for q in unrelated_queries:
        results = vector_store.search_hybrid(q, top_k=3, min_score=0.45)
        assert len(results) == 0, f"Expected 0 results for unrelated query '{q}', got {len(results)}"


def test_retrieval_tenant_lockout_sra_9(vector_store):
    """
    Tenant locked out of shop without court decree must retrieve Specific Relief Act Section 9,
    NOT landlord eviction under PRPA / SRPO Section 15.
    """
    query = "tenant locked out shop illegal dispossession restoration of possession without due process Section 9 Specific Relief Act"
    results = vector_store.search_hybrid(query, top_k=3, min_score=0.45)
    assert len(results) > 0
    top = results[0]
    assert top["id"] == "SRA-SEC-8-9"
    assert "Specific Relief Act" in top["act_title"]
    # Ensure landlord eviction is not the top result
    assert "PRPA" not in top["act_code"]
    assert "SRPO" not in top["act_code"]


def test_retrieval_unauthorized_inheritance_sale_sra_42_cpc_39(vector_store):
    """
    Brother selling late father's house without consent must retrieve CPC Order 39 stay order
    and Specific Relief Act Section 42 declaration of title.
    """
    query = "brother selling late father house without signature legal heir declaration of share Section 42 Specific Relief Act stay order temporary injunction Order 39 CPC"
    results = vector_store.search_hybrid(query, top_k=3, min_score=0.45)
    assert len(results) >= 2
    sec_ids = [r["id"] for r in results]
    assert "CPC-O39-R1-2" in sec_ids
    assert "SRA-SEC-42" in sec_ids

