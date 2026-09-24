"""
Tests for safety, emergency detection, and guardrails.
"""

from backend.safety import (
    detect_emergency,
    sanitize_court_predictions,
    enforce_drafting_guardrail,
    strip_formatting_and_emojis,
    LEGAL_DISCLAIMER
)


def test_emergency_detection_domestic_violence():
    text = "My husband has locked me in the room and is beating me violently right now"
    is_emergency, reason, helplines = detect_emergency(text)
    assert is_emergency is True
    assert reason == "domestic_violence_immediate_danger"
    assert any("15" in h["phone"] for h in helplines)


def test_emergency_detection_self_harm():
    text = "I have lost all hope and I want to commit suicide"
    is_emergency, reason, helplines = detect_emergency(text)
    assert is_emergency is True
    assert reason == "self_harm_risk"
    assert len(helplines) > 0


def test_emergency_exact_phrase_domestic_violence():
    """Regression test for exact user-reported domestic violence phrasing."""
    text = "my husband hits me and I don't feel safe at home"
    is_emergency, reason, helplines = detect_emergency(text)
    assert is_emergency is True
    assert reason == "domestic_violence_immediate_danger"
    assert any("1043" in h["phone"] or "15" in h["phone"] for h in helplines)


def test_emergency_exact_phrase_self_harm():
    """Regression test for exact user-reported self-harm / suicidal ideation phrasing."""
    text = "I don't see the point in living anymore because of this court case"
    is_emergency, reason, helplines = detect_emergency(text)
    assert is_emergency is True
    assert reason == "self_harm_risk"
    assert any("0800" in h["phone"] or "115" in h["phone"] for h in helplines)


def test_emergency_with_legal_context_interception():
    """Ensure emergency triggers even when other legal topics (custody, court case) are in same message."""
    text = "We have a family court custody case pending, but my husband hits me and I do not feel safe at home"
    is_emergency, reason, helplines = detect_emergency(text)
    assert is_emergency is True
    assert reason == "domestic_violence_immediate_danger"


def test_non_emergency_normal_case():
    text = "Someone took a loan of 200,000 and has not returned it. What legal action can I take?"
    is_emergency, reason, helplines = detect_emergency(text)
    assert is_emergency is False
    assert reason == ""


def test_sanitize_court_predictions():
    prediction_text = "Do not worry, the court will definitely rule in your favor and you will 100% win the case."
    sanitized = sanitize_court_predictions(prediction_text)
    assert "will definitely rule" not in sanitized
    assert "100% win" not in sanitized


def test_enforce_drafting_guardrail():
    draft = "IN THE COURT OF SENIOR CIVIL JUDGE, LAHORE\nPlaint under Section 9 of Specific Relief Act\nRespectfully sheweth..."
    flagged = enforce_drafting_guardrail(draft)
    assert "Legal Drafting Advisory" in flagged or "MANDATORY LEGAL DRAFTING ADVISORY" in flagged
    assert "Bar Council" in flagged


def test_plain_text_formatting_sanitization():
    """Verify that all markdown bold, headers, blockquotes, and emojis are completely removed."""
    raw_ai_output = (
        "### Legal Assessment & Statutory Grounding\n\n"
        "Based on the facts, **Section 420 of the Pakistan Penal Code** applies. ⚖️\n"
        "> ⚠️ Mandatory advisory for drafting\n"
        "Here are the steps:\n"
        "1. File complaint\n"
        "👉 Next question: Which city did this happen in?"
    )
    clean = strip_formatting_and_emojis(raw_ai_output)
    assert "**" not in clean
    assert "###" not in clean
    assert "⚖️" not in clean
    assert "⚠️" not in clean
    assert "👉" not in clean
    assert ">" not in clean
    assert "Section 420 of the Pakistan Penal Code applies." in clean


def test_plain_disclaimer_no_emojis():
    """Verify disclaimer is a plain sentence with no emojis or bolding."""
    assert "⚖️" not in LEGAL_DISCLAIMER
    assert "**" not in LEGAL_DISCLAIMER
    assert "Legal Disclaimer:" in LEGAL_DISCLAIMER
