"""
Structured Legal Intake Tracker & Case State Machine
Maintains and updates live Case Summary state based on conversational turns.
Enforces asking ONE clarifying question at a time.
"""

import re
from typing import Dict, Any, List, Optional


def extract_timeline_mention(text: str) -> Optional[str]:
    """Detect dates, durations, or temporal references in user message."""
    lower = text.lower()
    patterns = [
        r"\b(?:on\s+)?(\d{1,2}(?:st|nd|rd|th)?\s+(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)(?:\s*,?\s*\d{4})?)\b",
        r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b",
        r"\b(yesterday|today|last\s+(?:night|week|month|year))\b",
        r"\b(\d+\s+(?:days?|weeks?|months?|years?)\s+ago)\b",
        r"\b(since\s+\d{4})\b",
        r"\b(in\s+(?:202[0-9]|201[0-9]))\b",
        r"\b(گزشتہ\s*(?:ہفتے|ماہ|سال)|کل|پرسوں|پچھلے\s*(?:ہفتے|مہینے))\b",
        r"\b(kal|parso|pichle\s*(?:hafte|mahine|saal))\b"
    ]
    for pat in patterns:
        m = re.search(pat, lower, re.IGNORECASE)
        if m:
            return m.group(0).strip()
    return None


def extract_parties_mention(text: str) -> Optional[str]:
    """Detect opposing party or relationship mentioned in user message."""
    lower = text.lower()
    party_map = [
        (["business partner", "partner", "sharikaat"], "Complainant & Business Partner"),
        (["tenant", "kirayedar", "کرایہ دار"], "Landlord & Tenant"),
        (["landlord", "owner", "malik makan", "مالک مکان"], "Tenant & Landlord"),
        (["husband", "shohar", "شوہر"], "Wife (Petitioner) & Husband (Respondent)"),
        (["wife", "biwi", "بیوی"], "Husband & Wife"),
        (["neighbor", "parosi", "پڑوسی"], "Complainant & Neighbor"),
        (["contractor", "thekedaar", "ٹھیکیدار"], "Client & Contractor"),
        (["buyer", "purchaser", "gahak", "گاہک"], "Seller & Buyer"),
        (["seller", "vendor", "bechne wala"], "Buyer & Seller"),
        (["sho", "police station", "police", "پولیس"], "Citizen / Complainant & Police / SHO"),
        (["brother", "bhai", "bhen", "sister", "cousin", "relative"], "Family Members / Relatives Dispute"),
        (["employer", "boss", "company", "malik"], "Employee & Employer")
    ]
    for keywords, label in party_map:
        if any(k in lower for k in keywords):
            return label
    return None


def update_case_state(
    current_state: Dict[str, Any],
    user_message: str,
    retrieved_sections: List[Dict[str, Any]],
    llm_extracted_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Progressively refine structured case data from conversation history and statutory findings.
    """
    state = dict(current_state) if current_state else {}
    msg_lower = user_message.lower()

    # If LLM provided extracted metadata, merge it
    if llm_extracted_data:
        for k, v in llm_extracted_data.items():
            if v and v not in ["Undisclosed", "Pending Clarification", "Unspecified"]:
                state[k] = v

    # 1. Infer/Refine Issue Type if pending
    if not state.get("issue_type") or state.get("issue_type") in ["Pending Clarification", "General Legal Inquiry"]:
        if any(w in msg_lower for w in ["cheque", "check", "bounce", "bounced", "bank slip", "489-f", "چیک"]):
            if any(w in msg_lower for w in ["i gave", "i wrote", "i issued", "my cheque"]) and any(w in msg_lower for w in ["arrest", "threaten", "police", "jail"]):
                state["issue_type"] = "Defense Against Threatened PPC 489-F Cheque Prosecution & Pre-Arrest Bail"
            else:
                state["issue_type"] = "Dishonoured Cheque & Recovery (PPC 489-F)"
        elif any(w in msg_lower for w in ["rumor", "rumour", "rumors", "rumours", "defamation", "slander"]) or ("rival" in msg_lower and "rumor" in msg_lower):
            state["issue_type"] = "Defamation & Malicious False Rumors (Defamation Ordinance 2002 / PPC 500)"
        elif any(w in msg_lower for w in ["falsely accused", "false accusation", "wrongfully accused", "framed"]) and any(w in msg_lower for w in ["theft", "steal", "stolen", "employer"]):
            state["issue_type"] = "False Accusation of Theft & Safeguard Against Arrest (CrPC 498)"
        elif any(w in msg_lower for w in ["seller didn't", "didn't actually own", "full plot", "defective title", "not own the full"]):
            state["issue_type"] = "Defective Property Title & Recovery of Purchase Price"
        elif any(w in msg_lower for w in ["machinery for my factory", "factory machinery", "industrial equipment", "commercial equipment"]):
            state["issue_type"] = "Commercial Equipment & Breach of Warranty (Contract Act / Sale of Goods Act)"
        elif any(w in msg_lower for w in ["fraud", "cheat", "cheated", "dhoka", "scam", "lakh rupees", "420", "دھوکہ"]):
            state["issue_type"] = "Cheating & Criminal Fraud (PPC 420)"
        elif any(w in msg_lower for w in ["fir", "sho", "police station", "refusing fir", "refuse fir", "22-a", "ایف آئی آر"]):
            state["issue_type"] = "Police Refusal to Register FIR (CrPC 154 / 22-A)"
        elif any(w in msg_lower for w in ["khula", "divorce", "talaq", "maintenance", "iddat", "خلع", "نان نفقہ"]):
            state["issue_type"] = "Family Dispute / Khula & Maintenance"
        elif any(w in msg_lower for w in ["rent", "tenant", "landlord", "evict", "eviction", "kiraya", "کرایہ"]):
            state["issue_type"] = "Tenancy Dispute & Eviction"
        elif any(w in msg_lower for w in ["stay", "stay order", "construction", "plot", "encroach", "qabza", "trespass", "سٹے"]):
            state["issue_type"] = "Property Dispute / Stay Order (CPC O.39 / PPC 448)"
        elif any(w in msg_lower for w in ["whatsapp", "blackmail", "photos", "cyber", "online harassment", "fake profile", "بلیک میل"]):
            state["issue_type"] = "Cyber Crime & Harassment (PECA 2016)"
        elif any(w in msg_lower for w in ["breach of trust", "company funds", "misappropriat", "embezzle", "امانت میں خیانت"]) or (
            "business partner" in msg_lower and any(w in msg_lower for w in ["funds", "misappropriat", "stole", "diverted", "theft", "embezzle", "personal expenses"])
        ):
            state["issue_type"] = "Criminal Breach of Trust & Misappropriation (PPC 405/406)"
        elif any(w in msg_lower for w in ["business partner", "partnership", "silent partner"]):
            state["issue_type"] = "Partnership Governance & Decision-Making Dispute"
        elif any(w in msg_lower for w in ["impound", "impounded", "traffic police", "number plate", "numberplate", "challan", "registration plate"]):
            state["issue_type"] = "Motor Vehicle Impoundment & Registration (PMVO 1965)"
        elif any(w in msg_lower for w in ["bail", "pre-arrest", "post-arrest", "arrest", "ضمانت"]):
            state["issue_type"] = "Bail Application / Safeguard Against Arrest (CrPC 497/498)"
        elif retrieved_sections:
            state["issue_type"] = f"{retrieved_sections[0].get('category', 'Legal Matter')} - {retrieved_sections[0].get('section_title', '')}"

    # 2. Infer Location / Province
    if not state.get("location_province") or "Unspecified" in state.get("location_province", ""):
        provinces = {
            # Punjab
            "lahore": "Punjab (Lahore)", "لاہور": "Punjab (Lahore)",
            "rawalpindi": "Punjab (Rawalpindi)", "راولپنڈی": "Punjab (Rawalpindi)",
            "multan": "Punjab (Multan)", "ملتان": "Punjab (Multan)",
            "faisalabad": "Punjab (Faisalabad)", "فیصل آباد": "Punjab (Faisalabad)",
            "gujranwala": "Punjab (Gujranwala)", "sialkot": "Punjab (Sialkot)",
            "sargodha": "Punjab (Sargodha)", "bahawalpur": "Punjab (Bahawalpur)",
            "gujrat": "Punjab (Gujrat)", "sheikhupura": "Punjab (Sheikhupura)",
            "punjab": "Punjab Province", "پنجاب": "Punjab Province",
            # Sindh
            "karachi": "Sindh (Karachi)", "کراچی": "Sindh (Karachi)",
            "hyderabad": "Sindh (Hyderabad)", "حیدرآباد": "Sindh (Hyderabad)",
            "sukkur": "Sindh (Sukkur)", "سکھر": "Sindh (Sukkur)",
            "larkana": "Sindh (Larkana)", "sindh": "Sindh Province", "سندھ": "Sindh Province",
            # Federal Capital
            "islamabad": "Islamabad Capital Territory (ICT)", "اسلام آباد": "Islamabad Capital Territory (ICT)",
            # KP
            "peshawar": "Khyber Pakhtunkhwa (Peshawar)", "پشاور": "Khyber Pakhtunkhwa (Peshawar)",
            "abbottabad": "Khyber Pakhtunkhwa (Abbottabad)", "mardan": "Khyber Pakhtunkhwa (Mardan)",
            "swat": "Khyber Pakhtunkhwa (Swat)", "kpk": "Khyber Pakhtunkhwa Province", "خیبر پختونخوا": "Khyber Pakhtunkhwa Province",
            # Balochistan
            "quetta": "Balochistan (Quetta)", "کوئٹہ": "Balochistan (Quetta)",
            "gwadar": "Balochistan (Gwadar)", "balochistan": "Balochistan Province", "بلوچستان": "Balochistan Province",
            # AJK & GB
            "muzaffarabad": "Azad Jammu & Kashmir (Muzaffarabad)", "mirpur": "Azad Jammu & Kashmir (Mirpur)",
            "gilgit": "Gilgit-Baltistan (Gilgit)"
        }
        for city, prov in provinces.items():
            if city in msg_lower:
                state["location_province"] = prov
                break

    # 3. Detect Parties
    if not state.get("parties") or state.get("parties") in ["Undisclosed", "Pending Clarification"]:
        detected_parties = extract_parties_mention(user_message)
        if detected_parties:
            state["parties"] = detected_parties

    # 4. Detect Timeline / Dates
    if not state.get("dates") or state.get("dates") in ["Undisclosed", "Pending"]:
        detected_time = extract_timeline_mention(user_message)
        if detected_time:
            state["dates"] = detected_time

    # 5. Detect Documents Mentioned
    docs = list(state.get("documents_mentioned") or [])
    doc_markers = [
        ("cheque", "Original Bounced Cheque"),
        ("memo", "Bank Dishonour Return Memo"),
        ("slip", "Bank Deposit / Transaction Slip"),
        ("fir", "First Information Report (FIR) Copy"),
        ("nikahnama", "Nikahnama / Marriage Certificate"),
        ("contract", "Signed Contract / Stamp Paper"),
        ("agreement", "Written Agreement / Deed"),
        ("rent", "Tenancy Agreement"),
        ("notice", "Legal Notice Copy / Courier Slip"),
        ("whatsapp", "WhatsApp Chat Screenshots"),
        ("messages", "SMS / Communication Records"),
        ("audio", "Audio Recording"),
        ("video", "Video Recording / CCTV"),
        ("mlc", "Medico-Legal Certificate (MLC)"),
        ("fard", "Revenue Fard Malkiat / Registry"),
        ("stamp paper", "Judicial / Non-Judicial Stamp Paper"),
        ("bank statement", "Certified Bank Statement"),
        ("receipt", "Original Payment Receipt")
    ]
    for marker, name in doc_markers:
        if marker in msg_lower and name not in docs:
            docs.append(name)
    state["documents_mentioned"] = docs

    # 6. Integrate Applicable Laws from Retrieved Corpus
    if retrieved_sections:
        current_laws = []
        for sec in retrieved_sections:
            current_laws.append({
                "id": sec["id"],
                "act_code": sec.get("act_code"),
                "act_title": sec.get("act_title"),
                "section_number": sec.get("section_number"),
                "section_title": sec.get("section_title"),
                "category": sec.get("category"),
                "forum_court": sec.get("forum_court"),
                "summary_plain": sec.get("summary_plain"),
                "punishment": sec.get("punishment")
            })
        state["applicable_laws"] = current_laws

        # 7. Populate Evidence Checklist and Next Steps
        evidence_items = []
        for sec in retrieved_sections:
            for ev in sec.get("evidence_required", []):
                if ev not in evidence_items:
                    evidence_items.append(ev)
        state["evidence_checklist"] = evidence_items[:8]

        steps = []
        for sec in retrieved_sections:
            for st in sec.get("practical_steps", []):
                if st not in steps:
                    steps.append(st)
        state["next_steps"] = steps[:6]
    else:
        # Low confidence query: do not commit to random statutes or fabricated steps
        # Reset stale statutes on any substantive query; only keep if user answered a brief clarifying prompt
        is_clarifying_answer = len(user_message.split()) <= 6 and not any(q in msg_lower for q in ["what", "how", "can i", "why", "who", "kya", "kaise", "kab", "konsa", "bill", "notice", "case", "court", "partner"])
        if not is_clarifying_answer:
            state["applicable_laws"] = []
            state["evidence_checklist"] = []
            state["next_steps"] = []
        elif not state.get("applicable_laws"):
            state["applicable_laws"] = []
            state["evidence_checklist"] = []
            state["next_steps"] = []

    # 8. Determine Next Clarifying Question (Intake Logic)
    # Evaluates missing legal dimensions to ask ONLY ONE focused question at a time
    if not retrieved_sections:
        state["stage"] = "intake_clarifying"
        state["next_clarifying_question"] = "Could you share a few more factual details about what happened so I can identify the relevant Pakistani law?"
    elif not state.get("location_province") or "Unspecified" in state.get("location_province", ""):
        state["stage"] = "intake_clarifying"
        state["next_clarifying_question"] = "Which city or province did this take place in? (Pakistani court jurisdictions and certain rent/property statutes differ by province)."
    elif not state.get("dates") or state.get("dates") in ["Undisclosed", "Pending"]:
        state["stage"] = "intake_clarifying"
        state["next_clarifying_question"] = "Approximately when did this incident occur or when was the last interaction/payment? (This helps determine the legal period of limitation)."
    elif not state.get("documents_mentioned"):
        state["stage"] = "intake_clarifying"
        state["next_clarifying_question"] = "Do you have any written documents, receipts, messages, or bank records related to this matter?"
    else:
        state["stage"] = "assessment_ready"
        state["next_clarifying_question"] = "Has any formal FIR, police complaint, or legal notice already been submitted by either party?"

    return state
