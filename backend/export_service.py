"""
Export Service for Qanoon Sahayak
Generates printable, beautiful Intake Dossiers and JSON summaries for clients to take to their advocates.
"""

from typing import Dict, Any, List
from datetime import datetime, timezone
from .safety import LEGAL_DISCLAIMER


def generate_html_dossier(session_title: str, case_state: Dict[str, Any], messages: List[Dict[str, Any]]) -> str:
    """Generate professional printable HTML legal intake dossier."""
    issue_type = case_state.get("issue_type", "General Consultation")
    parties = case_state.get("parties", "Undisclosed")
    dates = case_state.get("dates", "Undisclosed")
    location = case_state.get("location_province", "Federal / Unspecified")
    laws = case_state.get("applicable_laws", [])
    evidence = case_state.get("evidence_checklist", [])
    steps = case_state.get("next_steps", [])
    date_str = datetime.now(timezone.utc).strftime("%d %B %Y, %I:%M %p UTC")

    laws_html = ""
    for law in laws:
        laws_html += f"""
        <div style="background: #f8fafc; border-left: 4px solid #1b4332; padding: 12px 16px; margin-bottom: 12px; border-radius: 4px;">
            <h4 style="margin: 0 0 6px 0; color: #1b4332;">{law.get('act_title')} — Section {law.get('section_number')}: {law.get('section_title')}</h4>
            <p style="margin: 0 0 6px 0; font-size: 14px; color: #334155;"><strong>Forum / Jurisdiction:</strong> {law.get('forum_court', 'Competent Court')}</p>
            <p style="margin: 0; font-size: 14px; color: #475569;">{law.get('summary_plain', '')}</p>
        </div>
        """

    evidence_html = "".join([f"<li style='margin-bottom: 6px; color: #334155;'>{item}</li>" for item in evidence])
    steps_html = "".join([f"<li style='margin-bottom: 8px; color: #334155;'><strong>Step {i+1}:</strong> {step}</li>" for i, step in enumerate(steps)])

    # Recent chat conversation
    conversation_html = ""
    for msg in messages[-8:]:
        role = "User / Client" if msg.get("role") == "user" else "Qanoon Sahayak"
        bg = "#ffffff" if msg.get("role") == "user" else "#f1f5f9"
        border = "#cbd5e1" if msg.get("role") == "user" else "#94a3b8"
        content = msg.get("content", "").replace("\n", "<br>")
        conversation_html += f"""
        <div style="margin-bottom: 12px; padding: 10px 14px; background: {bg}; border: 1px solid {border}; border-radius: 6px;">
            <strong style="color: #1e293b; font-size: 13px;">{role}:</strong>
            <div style="font-size: 13px; color: #334155; margin-top: 4px;">{content}</div>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Legal Intake Dossier — {issue_type}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            margin: 40px;
            color: #1e293b;
            line-height: 1.5;
            background: #ffffff;
        }}
        .header {{
            border-bottom: 2px solid #1b4332;
            padding-bottom: 16px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }}
        .brand-title {{
            color: #1b4332;
            font-size: 26px;
            font-weight: bold;
            margin: 0;
        }}
        .brand-urdu {{
            font-size: 18px;
            color: #2d6a4f;
            margin: 4px 0 0 0;
        }}
        .badge {{
            background: #e2e8f0;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}
        .meta-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 24px;
            background: #f8fafc;
            padding: 16px;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }}
        .section-title {{
            color: #1b4332;
            border-bottom: 1px solid #cbd5e1;
            padding-bottom: 6px;
            margin-top: 28px;
            font-size: 18px;
        }}
        .disclaimer-box {{
            margin-top: 36px;
            padding: 14px 18px;
            background: #fffbeb;
            border-left: 4px solid #d97706;
            font-size: 12px;
            color: #92400e;
            border-radius: 4px;
        }}
        @media print {{
            body {{ margin: 20px; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1 class="brand-title">QANOON SAHAYAK</h1>
            <div class="brand-urdu">قانون معاون — Preliminary Legal Intake Dossier</div>
            <p style="margin: 4px 0 0 0; font-size: 13px; color: #64748b;">Prepared for Client Consultation with Licensed Advocate</p>
        </div>
        <div style="text-align: right;">
            <span class="badge">CONFIDENTIAL</span>
            <p style="margin: 6px 0 0 0; font-size: 12px; color: #64748b;">Date: {date_str}</p>
        </div>
    </div>

    <div class="meta-grid">
        <div><strong>Primary Matter:</strong> {issue_type}</div>
        <div><strong>Jurisdiction / Province:</strong> {location}</div>
        <div><strong>Parties Involved:</strong> {parties}</div>
        <div><strong>Incident Timeline:</strong> {dates}</div>
    </div>

    <h3 class="section-title">1. Applicable Pakistani Statutory Provisions (Grounded Citations)</h3>
    {laws_html if laws_html else "<p style='color: #64748b;'>No statutory sections finalized yet.</p>"}

    <h3 class="section-title">2. Suggested Practical Action Plan</h3>
    <ul style="padding-left: 20px;">
        {steps_html if steps_html else "<li>Consult with an Advocate for procedural initiation.</li>"}
    </ul>

    <h3 class="section-title">3. Key Evidence & Documentation Checklist</h3>
    <ul style="padding-left: 20px;">
        {evidence_html if evidence_html else "<li>Gather all relevant transaction records, CNIC copy, and correspondence.</li>"}
    </ul>

    <h3 class="section-title">4. Intake Consultation Excerpt</h3>
    {conversation_html}

    <div class="disclaimer-box">
        <strong>IMPORTANT STATUTORY DISCLAIMER:</strong><br>
        {LEGAL_DISCLAIMER}
    </div>

    <div class="no-print" style="margin-top: 30px; text-align: center;">
        <button onclick="window.print()" style="background: #1b4332; color: #ffffff; border: none; padding: 10px 24px; font-size: 14px; font-weight: bold; border-radius: 6px; cursor: pointer;">
            Print / Save as PDF
        </button>
    </div>
</body>
</html>
"""
