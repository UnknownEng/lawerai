"""
Tests for structured intake tracking state machine.
"""

from backend.intake_tracker import update_case_state, extract_parties_mention, extract_timeline_mention


def test_initial_intake_categorization():
    initial_state = {
        "issue_type": "General Legal Inquiry",
        "parties": "Undisclosed",
        "dates": "Undisclosed",
        "location_province": "Federal / Unspecified",
        "documents_mentioned": [],
        "stage": "intake_clarifying"
    }

    user_msg = "My landlord in Lahore is trying to evict me without any notice and says he will throw my luggage out"
    retrieved = [{
        "id": "PRPA-SEC-15",
        "act_code": "PRPA",
        "act_title": "Punjab Rented Premises Act 2009",
        "section_number": "Section 15",
        "section_title": "Application for eviction",
        "category": "Property Law / Tenancy",
        "evidence_required": ["Registered Tenancy Agreement", "Rent receipts"],
        "practical_steps": ["File reply before Rent Tribunal"]
    }]

    new_state = update_case_state(initial_state, user_msg, retrieved)

    assert "Tenancy" in new_state["issue_type"] or "Eviction" in new_state["issue_type"]
    assert "Punjab" in new_state["location_province"] or "Lahore" in new_state["location_province"]
    assert len(new_state["applicable_laws"]) > 0
    assert "PRPA-SEC-15" == new_state["applicable_laws"][0]["id"]
    # Verify it asks ONE clarifying question
    assert "next_clarifying_question" in new_state
    assert len(new_state["next_clarifying_question"]) > 10


def test_document_extraction():
    initial_state = {
        "documents_mentioned": []
    }
    user_msg = "I have the original bounced cheque and the bank return memo slip with me"
    new_state = update_case_state(initial_state, user_msg, [])

    assert any("Cheque" in d for d in new_state["documents_mentioned"])
    assert any("Return Memo" in d or "Slip" in d for d in new_state["documents_mentioned"])


def test_party_and_timeline_extraction():
    initial_state = {
        "parties": "Undisclosed",
        "dates": "Undisclosed",
        "location_province": "Federal / Unspecified"
    }
    user_msg = "My business partner in Karachi took 5 lakh rupees last month on 15th January 2026"
    new_state = update_case_state(initial_state, user_msg, [])

    assert "Business Partner" in new_state["parties"]
    assert "Karachi" in new_state["location_province"] or "Sindh" in new_state["location_province"]
    assert new_state["dates"] != "Undisclosed"


def test_cyber_crime_and_bail_categorization():
    initial_state = {}
    cyber_msg = "A blackmailer created a fake profile with my WhatsApp photos and is threatening me"
    cyber_state = update_case_state(initial_state, cyber_msg, [])
    assert "PECA" in cyber_state["issue_type"] or "Cyber" in cyber_state["issue_type"]

    bail_msg = "The police are threatening to arrest me under false allegations, I need urgent pre-arrest bail"
    bail_state = update_case_state(initial_state, bail_msg, [])
    assert "Bail" in bail_state["issue_type"] or "498" in bail_state["issue_type"]
