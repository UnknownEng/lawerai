"""
Unit tests for LegalReasoningEngine (Fact Classification, Directional Role-Awareness, and Segmentation).
"""

from backend.reasoning_engine import LegalReasoningEngine


def test_safety_check_blocking():
    engine = LegalReasoningEngine()
    analysis = engine.analyze("I don't see the point in living anymore because of this court case")
    assert analysis.is_emergency is True
    assert analysis.emergency_reason == "self_harm_risk"
    assert len(analysis.issues) == 0


def test_safety_combined_with_legal_blocks_pipeline():
    engine = LegalReasoningEngine()
    analysis = engine.analyze("My husband hits me and also he isn't paying maintenance")
    assert analysis.is_emergency is True
    assert analysis.emergency_reason == "domestic_violence_immediate_danger"
    assert len(analysis.issues) == 0


def test_segmentation_and_fact_extraction_case_a():
    engine = LegalReasoningEngine()
    query = (
        "My landlord changed the locks on my shop while I was away and won't let me back in, "
        "even though my rent is paid. Also, my brother is trying to sell our late father's house "
        "without my signature, even though I'm also a legal heir."
    )
    analysis = engine.analyze(query)
    assert analysis.is_emergency is False
    assert len(analysis.issues) == 2

    # Issue 1: Tenant lockout
    iss1 = analysis.issues[0]
    assert iss1.aggrieved_party == "Tenant"
    assert iss1.wrongdoer == "Landlord"
    assert "SRA-SEC-8-9" in iss1.statute_hints
    assert "Section 9 Specific Relief Act" in iss1.search_query
    assert "PRPA" not in iss1.search_query
    assert "eviction" not in iss1.search_query.lower() or "dispossession" in iss1.search_query.lower()

    # Issue 2: Inheritance property sale without consent
    iss2 = analysis.issues[1]
    assert iss2.aggrieved_party == "Legal Heir"
    assert iss2.wrongdoer == "Co-Heir Brother"
    assert "SRA-SEC-42" in iss2.statute_hints
    assert "CPC-O39-R1-2" in iss2.statute_hints
    assert "Section 42 Specific Relief Act" in iss2.search_query
    assert "Order 39 CPC" in iss2.search_query


def test_role_awareness_tenant_lockout():
    engine = LegalReasoningEngine()
    query = "The landlord locked me out of the commercial property without notice"
    analysis = engine.analyze(query)
    assert len(analysis.issues) == 1
    iss = analysis.issues[0]
    assert iss.aggrieved_party == "Tenant"
    assert iss.wrongdoer == "Landlord"
    assert "Section 9 Specific Relief Act" in iss.search_query


def test_role_awareness_traffic_impoundment():
    engine = LegalReasoningEngine()
    query = "traffic police impounded my car saying the number plate doesn't match"
    analysis = engine.analyze(query)
    assert len(analysis.issues) == 1
    iss = analysis.issues[0]
    assert iss.aggrieved_party == "Vehicle Owner"
    assert "PMVO" in iss.search_query or "Provincial Motor Vehicles" in iss.search_query
    assert "115" in iss.search_query


def test_role_awareness_company_funds():
    engine = LegalReasoningEngine()
    query = "my business partner used company funds for personal expenses without telling me"
    analysis = engine.analyze(query)
    assert len(analysis.issues) == 1
    iss = analysis.issues[0]
    assert iss.wrongdoer == "Business Partner"
    assert "405" in iss.search_query or "406" in iss.search_query
    assert "criminal breach of trust" in iss.search_query.lower()


def test_fallback_general_inquiry():
    engine = LegalReasoningEngine()
    query = "how do I bake a chocolate cake at home?"
    analysis = engine.analyze(query)
    assert len(analysis.issues) == 1
    iss = analysis.issues[0]
    assert iss.issue_title == "General Inquiry"
    assert len(iss.statute_hints) == 0
